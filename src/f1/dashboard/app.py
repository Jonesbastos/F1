"""Servidor HTTP e roteador web para o Dashboard local da Fórmula 1."""

import os

# Limitar pools de threads matemáticas para prevenir exaustão de memória no Windows
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from urllib.parse import parse_qs, urlparse

from f1.dashboard.data_provider import DashboardDataProvider
from f1.dashboard.templates import render_dashboard_html
from f1.utils.logger import get_logger

logger = get_logger("f1.dashboard.app")


class DashboardHandler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP para a interface web e endpoints da API REST."""

    data_provider: ClassVar[DashboardDataProvider] = DashboardDataProvider()

    def do_OPTIONS(self) -> None:
        """Responde a requisições pre-flight de CORS."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        """Processa requisições HTTP do tipo POST para ações administrativas."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/api/sync":
            logger.info("Requisição de sincronização recebida via Dashboard...")

            def _sync_worker() -> None:
                try:
                    from f1.pipelines.session_pipeline import SessionPipeline

                    pipeline = SessionPipeline()
                    pipeline.run(session_key="latest")
                    logger.info("Sincronização em background concluída com sucesso.")
                except Exception as exc:
                    logger.warning("Falha na sincronização via OpenF1: %s", exc)

            sync_thread = threading.Thread(target=_sync_worker, daemon=True)
            sync_thread.start()

            self._send_json(
                {
                    "status": "sync_started",
                    "message": "Sincronização com OpenF1 iniciada em segundo plano.",
                }
            )
            return

        self._send_response(
            404,
            "application/json",
            json.dumps({"error": "Rota POST não encontrada"}).encode("utf-8"),
        )

    def do_GET(self) -> None:
        """Processa requisições HTTP do tipo GET."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        session_key = (
            int(query["session_key"][0])
            if "session_key" in query and query["session_key"][0].isdigit()
            else None
        )
        driver_number = (
            int(query["driver_number"][0])
            if "driver_number" in query and query["driver_number"][0].isdigit()
            else None
        )

        if path in ("/", "/index.html"):
            html_content = render_dashboard_html()
            self._send_response(200, "text/html; charset=utf-8", html_content.encode("utf-8"))
            return

        if path == "/api/stats":
            data = self.data_provider.get_overview_stats()
            self._send_json(data)
            return

        if path == "/api/meetings":
            data = self.data_provider.get_meetings()
            self._send_json(data)
            return

        if path == "/api/sessions":
            data = self.data_provider.get_sessions()
            self._send_json(data)
            return

        if path == "/api/drivers":
            data = self.data_provider.get_drivers(session_key=session_key)
            self._send_json(data)
            return

        if path == "/api/laps":
            data = self.data_provider.get_laps(session_key=session_key)
            self._send_json(data)
            return

        if path == "/api/fastest_laps":
            data = self.data_provider.get_fastest_laps(session_key=session_key)
            self._send_json(data)
            return

        if path == "/api/weather":
            data = self.data_provider.get_weather(session_key=session_key)
            self._send_json(data)
            return

        if path == "/api/telemetry":
            data = self.data_provider.get_telemetry_samples(
                session_key=session_key,
                driver_number=driver_number,
            )
            self._send_json(data)
            return

        # Rota não encontrada
        self._send_response(
            404,
            "application/json",
            json.dumps({"error": "Rota não encontrada"}).encode("utf-8"),
        )

    def _send_response(self, status: int, content_type: str, body: bytes) -> None:
        """Envia resposta HTTP estruturada com headers padrão.

        Args:
            status: Código de status HTTP.
            content_type: Tipo MIME do conteúdo.
            body: Bytes do payload da resposta.
        """
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: object, status: int = 200) -> None:
        """Serializa e envia dados em formato JSON.

        Args:
            data: Objeto Python serializável.
            status: Código de status HTTP (padrão 200).
        """
        encoded = json.dumps(data, default=str).encode("utf-8")
        self._send_response(status, "application/json; charset=utf-8", encoded)

    def log_message(self, format: str, *args: object) -> None:
        """Redireciona os logs nativos do servidor para o logger estruturado da aplicação."""
        logger.debug(
            "%s - - [%s] %s",
            self.address_string(),
            self.log_date_time_string(),
            format % args,
        )


def create_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    data_dir: Path | str | None = None,
) -> ThreadingHTTPServer:
    """Instancia e configura o servidor HTTP do Dashboard.

    Args:
        host: Endereço de escuta (padrão: 127.0.0.1).
        port: Porta de escuta (padrão: 8080).
        data_dir: Diretório raiz do Data Lake.

    Returns:
        Instância de ThreadingHTTPServer configurada.
    """
    DashboardHandler.data_provider = DashboardDataProvider(base_dir=data_dir)
    return ThreadingHTTPServer((host, port), DashboardHandler)


def run_dashboard(
    host: str = "127.0.0.1",
    port: int = 8080,
    data_dir: Path | str | None = None,
) -> None:
    """Inicia o servidor web do Dashboard e bloqueia a execução até interrupção do usuário.

    Args:
        host: Endereço de escuta (padrão: 127.0.0.1).
        port: Porta TCP de escuta (padrão: 8080).
        data_dir: Diretório raiz do Data Lake para leitura dos dados.
    """
    server = create_server(host=host, port=port, data_dir=data_dir)
    url = f"http://localhost:{port}" if host in ("127.0.0.1", "0.0.0.0") else f"http://{host}:{port}"
    logger.info("🏎️  F1 Dashboard iniciado com sucesso!")
    logger.info("Acesse a interface no navegador: %s", url)
    logger.info("Pressione Ctrl+C para encerrar o servidor.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Encerrando o servidor do Dashboard...")
    finally:
        server.server_close()
        logger.info("Servidor encerrado.")


def main(argv: list[str] | None = None) -> int:
    """Função CLI para inicialização direta do Dashboard.

    Args:
        argv: Argumentos de linha de comando.

    Returns:
        Código de saída da aplicação.
    """
    parser = argparse.ArgumentParser(description="F1 Data Platform — Dashboard Web")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Endereço de escuta (padrão: 127.0.0.1)"
    )
    parser.add_argument("--port", type=int, default=8080, help="Porta TCP (padrão: 8080)")
    parser.add_argument("--data-dir", default=None, help="Caminho customizado para data/processed")

    args = parser.parse_args(argv)
    run_dashboard(host=args.host, port=args.port, data_dir=args.data_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
