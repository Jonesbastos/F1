# ruff: noqa: E501
"""Templates e interface HTML moderna para o F1 Data Platform Dashboard."""


def render_dashboard_html() -> str:
    """Gera o código HTML completo da interface web do Dashboard da Fórmula 1.

    Returns:
        String contendo a página web com estilos CSS, layout responsivo e scripts.
    """
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏎️ F1 Data Platform — Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --f1-red: #E10600;
            --f1-dark: #121218;
            --f1-panel: #1A1A24;
            --f1-card: #222230;
            --f1-border: #2D2D3D;
            --f1-text: #F3F3F7;
            --f1-muted: #A0A0B2;
            --f1-accent: #00D2BE;
            --f1-yellow: #FFC107;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Titillium Web', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background-color: var(--f1-dark);
            color: var(--f1-text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: linear-gradient(90deg, #181822 0%, var(--f1-panel) 100%);
            border-bottom: 2px solid var(--f1-red);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .badge-f1 {
            background: var(--f1-red);
            color: #fff;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 1.2rem;
            letter-spacing: 1px;
        }

        .title {
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .btn-sync {
            background-color: var(--f1-red);
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.1s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .btn-sync:hover {
            background-color: #B50500;
            transform: translateY(-1px);
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: var(--f1-accent);
            background: rgba(0, 210, 190, 0.1);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid rgba(0, 210, 190, 0.3);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: var(--f1-accent);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--f1-accent);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.4; }
            50% { opacity: 1; }
            100% { opacity: 0.4; }
        }

        .demo-banner {
            display: none;
            background: rgba(255, 193, 7, 0.15);
            border-left: 4px solid var(--f1-yellow);
            color: #FFE082;
            padding: 0.75rem 2rem;
            font-size: 0.9rem;
            font-weight: 600;
            align-items: center;
            justify-content: space-between;
        }

        nav {
            background-color: var(--f1-panel);
            border-bottom: 1px solid var(--f1-border);
            padding: 0 2rem;
            display: flex;
            gap: 1.5rem;
            overflow-x: auto;
        }

        .nav-tab {
            padding: 1rem 0.5rem;
            color: var(--f1-muted);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .nav-tab:hover, .nav-tab.active {
            color: #fff;
            border-bottom-color: var(--f1-red);
        }

        main {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .grid-kpi {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background-color: var(--f1-card);
            border: 1px solid var(--f1-border);
            border-radius: 8px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background-color: var(--f1-red);
        }

        .kpi-title {
            font-size: 0.85rem;
            color: var(--f1-muted);
            text-transform: uppercase;
            font-weight: 600;
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: 900;
            color: #fff;
        }

        .panel {
            background-color: var(--f1-card);
            border: 1px solid var(--f1-border);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .panel-header {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--f1-border);
            padding-bottom: 0.75rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th {
            text-align: left;
            padding: 0.75rem;
            color: var(--f1-muted);
            border-bottom: 1px solid var(--f1-border);
            text-transform: uppercase;
            font-size: 0.8rem;
        }

        td {
            padding: 0.85rem 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        tr:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }

        .team-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .grid-drivers {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.25rem;
        }

        .driver-card {
            background-color: var(--f1-card);
            border: 1px solid var(--f1-border);
            border-radius: 8px;
            padding: 1.25rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            position: relative;
        }

        .driver-card-strip {
            position: absolute;
            top: 0;
            left: 0;
            bottom: 0;
            width: 6px;
            border-radius: 8px 0 0 8px;
        }

        .driver-avatar {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            object-fit: cover;
            background: #2A2A38;
            border: 2px solid var(--f1-border);
        }

        .driver-info h3 {
            font-size: 1.1rem;
            font-weight: 700;
        }

        .driver-info p {
            font-size: 0.85rem;
            color: var(--f1-muted);
        }

        .driver-number {
            position: absolute;
            top: 1rem;
            right: 1.2rem;
            font-size: 1.8rem;
            font-weight: 900;
            color: rgba(255, 255, 255, 0.1);
        }

        .chart-box {
            position: relative;
            height: 350px;
            width: 100%;
        }

        footer {
            border-top: 1px solid var(--f1-border);
            padding: 1.25rem 2rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--f1-muted);
            background-color: var(--f1-panel);
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span class="badge-f1">F1</span>
            <span class="title">Data Platform & Analytics Dashboard</span>
        </div>
        <div class="header-actions">
            <button class="btn-sync" id="btn-sync" onclick="syncOpenF1Data()">📥 Sincronizar com OpenF1</button>
            <div class="status-badge">
                <span class="status-dot" id="status-indicator"></span>
                <span id="status-text">Online &bull; Localhost</span>
            </div>
        </div>
    </header>

    <div class="demo-banner" id="demo-banner">
        <span>⚠️ Modo de Demonstração Ativo: O Data Lake local ainda não possui dados persistidos. Exibindo dados prévios de exemplo.</span>
    </div>

    <nav>
        <div class="nav-tab active" onclick="switchTab('overview')">📊 Visão Geral</div>
        <div class="nav-tab" onclick="switchTab('drivers')">🏎️ Pilotos & Grid</div>
        <div class="nav-tab" onclick="switchTab('timing')">⏱️ Voltas & Cronometragem</div>
        <div class="nav-tab" onclick="switchTab('telemetry')">📈 Telemetria Veicular</div>
        <div class="nav-tab" onclick="switchTab('weather')">🌦️ Meteorologia</div>
    </nav>

    <main>
        <!-- Tab: Visão Geral -->
        <section id="overview" class="tab-content active">
            <div class="grid-kpi">
                <div class="kpi-card">
                    <span class="kpi-title">Grandes Prêmios</span>
                    <span class="kpi-value" id="kpi-meetings">-</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Sessões Processadas</span>
                    <span class="kpi-value" id="kpi-sessions">-</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Pilotos Mapeados</span>
                    <span class="kpi-value" id="kpi-drivers">-</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Voltas Cronometradas</span>
                    <span class="kpi-value" id="kpi-laps">-</span>
                </div>
                <div class="kpi-card">
                    <span class="kpi-title">Amostras Telemetria</span>
                    <span class="kpi-value" id="kpi-telemetry">-</span>
                </div>
            </div>

            <div class="panel">
                <div class="panel-header">
                    <span>🏁 Sessões de Pista Registradas</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Sessão</th>
                            <th>Tipo</th>
                            <th>Meeting Key</th>
                            <th>Início (UTC)</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="sessions-table-body">
                        <tr><td colspan="5" style="text-align:center;">Carregando dados...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Tab: Pilotos -->
        <section id="drivers" class="tab-content">
            <div class="panel">
                <div class="panel-header">
                    <span>👥 Grid de Pilotos & Equipes</span>
                </div>
                <div class="grid-drivers" id="drivers-grid">
                    <p style="color:var(--f1-muted);">Carregando pilotos...</p>
                </div>
            </div>
        </section>

        <!-- Tab: Timing -->
        <section id="timing" class="tab-content">
            <div class="panel">
                <div class="panel-header">
                    <span>⚡ Melhores Voltas por Piloto</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Piloto</th>
                            <th>Volta</th>
                            <th>Tempo Total</th>
                            <th>Setor 1</th>
                            <th>Setor 2</th>
                            <th>Setor 3</th>
                        </tr>
                    </thead>
                    <tbody id="timing-table-body">
                        <tr><td colspan="6" style="text-align:center;">Carregando tempos de volta...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Tab: Telemetria -->
        <section id="telemetry" class="tab-content">
            <div class="panel">
                <div class="panel-header">
                    <span>🚀 Curva de Velocidade e Aceleração Instantânea</span>
                </div>
                <div class="chart-box">
                    <canvas id="telemetryChart"></canvas>
                </div>
            </div>
        </section>

        <!-- Tab: Weather -->
        <section id="weather" class="tab-content">
            <div class="panel">
                <div class="panel-header">
                    <span>🌡️ Condições Meteorológicas da Pista</span>
                </div>
                <div class="chart-box">
                    <canvas id="weatherChart"></canvas>
                </div>
            </div>
        </section>
    </main>

    <footer>
        F1 Data Platform &bull; Apache Parquet Hive Storage &bull; OpenF1 Integration &bull; Poetry
    </footer>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

            const target = document.getElementById(tabId);
            if (target) target.classList.add('active');

            const activeTabBtn = Array.from(document.querySelectorAll('.nav-tab')).find(
                btn => btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(tabId)
            );
            if (activeTabBtn) activeTabBtn.classList.add('active');
        }

        async function syncOpenF1Data() {
            const btn = document.getElementById('btn-sync');
            if (btn) {
                btn.innerText = '⏳ Sincronizando...';
                btn.disabled = true;
            }
            try {
                const res = await fetch('/api/sync', { method: 'POST' });
                const json = await res.json();
                alert(json.message || 'Sincronização iniciada com a OpenF1!');
                setTimeout(loadDashboardData, 3000);
            } catch (err) {
                alert('Aviso: Não foi possível sincronizar no momento: ' + err);
            } finally {
                if (btn) {
                    btn.innerText = '📥 Sincronizar com OpenF1';
                    btn.disabled = false;
                }
            }
        }

        async function loadDashboardData() {
            try {
                // 1. Carregar contadores gerais
                const resStats = await fetch('/api/stats');
                if (resStats.ok) {
                    const stats = await resStats.json();
                    document.getElementById('kpi-meetings').innerText = stats.meetings || 0;
                    document.getElementById('kpi-sessions').innerText = stats.sessions || 0;
                    document.getElementById('kpi-drivers').innerText = stats.drivers || 0;
                    document.getElementById('kpi-laps').innerText = stats.laps || 0;
                    document.getElementById('kpi-telemetry').innerText = stats.telemetry || 0;

                    const demoBanner = document.getElementById('demo-banner');
                    if (stats.is_demo) {
                        demoBanner.style.display = 'flex';
                    } else {
                        demoBanner.style.display = 'none';
                    }
                }

                // 2. Carregar Sessões
                const resSessions = await fetch('/api/sessions');
                if (resSessions.ok) {
                    const sessions = await resSessions.json();
                    const tbody = document.getElementById('sessions-table-body');
                    if (sessions.length > 0) {
                        tbody.innerHTML = sessions.map(s => `
                            <tr>
                                <td><strong>${s.session_name || 'N/A'}</strong></td>
                                <td>${s.session_type || 'N/A'}</td>
                                <td><code>${s.meeting_key || 'N/A'}</code></td>
                                <td>${s.date_start ? new Date(s.date_start).toLocaleString('pt-BR') : 'N/A'}</td>
                                <td><span style="color:var(--f1-accent); font-weight:600;">Ativo</span></td>
                            </tr>
                        `).join('');
                    } else {
                        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--f1-muted);">Nenhuma sessão processada no momento.</td></tr>';
                    }
                }

                // 3. Carregar Pilotos
                const resDrivers = await fetch('/api/drivers');
                if (resDrivers.ok) {
                    const drivers = await resDrivers.json();
                    const container = document.getElementById('drivers-grid');
                    if (drivers.length > 0) {
                        container.innerHTML = drivers.map(d => {
                            const color = d.team_colour ? '#' + d.team_colour : '#E10600';
                            const headshot = d.headshot_url || 'https://media.formula1.com/d_default_fallback_image.png/content/dam/fom-website/drivers/placeholder.png';
                            return `
                                <div class="driver-card">
                                    <div class="driver-card-strip" style="background-color: ${color};"></div>
                                    <img class="driver-avatar" src="${headshot}" alt="${d.broadcast_name || 'Driver'}" onerror="this.src='https://media.formula1.com/d_default_fallback_image.png/content/dam/fom-website/drivers/placeholder.png'">
                                    <div class="driver-info">
                                        <h3>${d.broadcast_name || d.full_name || 'Driver'}</h3>
                                        <p><span class="team-dot" style="background-color: ${color};"></span> ${d.team_name || 'Escuderia'}</p>
                                    </div>
                                    <span class="driver-number">#${d.driver_number || ''}</span>
                                </div>
                            `;
                        }).join('');
                    } else {
                        container.innerHTML = '<p style="color:var(--f1-muted);">Nenhum piloto registrado.</p>';
                    }
                }

                // 4. Carregar Voltas Rápidas
                const resLaps = await fetch('/api/fastest_laps');
                if (resLaps.ok) {
                    const laps = await resLaps.json();
                    const tbody = document.getElementById('timing-table-body');
                    if (laps.length > 0) {
                        tbody.innerHTML = laps.map(l => `
                            <tr>
                                <td><strong>#${l.driver_number}</strong></td>
                                <td>${l.lap_number || 'N/A'}</td>
                                <td><span style="color:#FFF; font-weight:700;">${l.lap_duration ? l.lap_duration.toFixed(3) + 's' : 'N/A'}</span></td>
                                <td>${l.duration_sector_1 ? l.duration_sector_1.toFixed(3) + 's' : '-'}</td>
                                <td>${l.duration_sector_2 ? l.duration_sector_2.toFixed(3) + 's' : '-'}</td>
                                <td>${l.duration_sector_3 ? l.duration_sector_3.toFixed(3) + 's' : '-'}</td>
                            </tr>
                        `).join('');
                    } else {
                        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--f1-muted);">Nenhuma melhor volta registrada.</td></tr>';
                    }
                }

                // 5. Gráfico de Telemetria
                initTelemetryChart();

                // 6. Gráfico de Meteorologia
                initWeatherChart();

            } catch (err) {
                console.error("Erro ao carregar dados do Dashboard:", err);
            }
        }

        async function initTelemetryChart() {
            let samples = [];
            try {
                const res = await fetch('/api/telemetry');
                if (res.ok) {
                    samples = await res.json();
                }
            } catch(e) {}

            const ctx = document.getElementById('telemetryChart').getContext('2d');
            const labels = samples.map((s, idx) => s.date ? new Date(s.date).toLocaleTimeString() : idx);
            const speedData = samples.map(s => s.speed || 0);
            const throttleData = samples.map(s => s.throttle || 0);

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels.length ? labels : ['0s', '5s', '10s', '15s', '20s', '25s', '30s', '35s'],
                    datasets: [
                        {
                            label: 'Velocidade (km/h)',
                            data: speedData.length ? speedData : [160, 220, 280, 315, 330, 290, 180, 130],
                            borderColor: '#E10600',
                            backgroundColor: 'rgba(225, 6, 0, 0.1)',
                            borderWidth: 2,
                            tension: 0.3,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Acelerador (%)',
                            data: throttleData.length ? throttleData : [100, 100, 100, 100, 100, 40, 0, 50],
                            borderColor: '#00D2BE',
                            borderWidth: 2,
                            tension: 0.3,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: 'km/h', color: '#E10600' },
                            grid: { color: 'rgba(255,255,255,0.05)' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            min: 0,
                            max: 100,
                            title: { display: true, text: '%', color: '#00D2BE' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }

        async function initWeatherChart() {
            let samples = [];
            try {
                const res = await fetch('/api/weather');
                if (res.ok) {
                    samples = await res.json();
                }
            } catch(e) {}

            const ctx = document.getElementById('weatherChart').getContext('2d');
            const labels = samples.map((s, idx) => s.date ? new Date(s.date).toLocaleTimeString() : idx);
            const trackTemp = samples.map(s => s.track_temperature || 0);
            const airTemp = samples.map(s => s.air_temperature || 0);

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels.length ? labels : ['17:00', '17:15', '17:30', '17:45', '18:00'],
                    datasets: [
                        {
                            label: 'Temperatura da Pista (°C)',
                            data: trackTemp.length ? trackTemp : [41, 43, 44, 42, 40],
                            borderColor: '#FF8700',
                            backgroundColor: 'rgba(255, 135, 0, 0.1)',
                            borderWidth: 2,
                            tension: 0.3
                        },
                        {
                            label: 'Temperatura do Ar (°C)',
                            data: airTemp.length ? airTemp : [25, 26, 26, 25, 25],
                            borderColor: '#3671C6',
                            borderWidth: 2,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: '°C' } }
                    }
                }
            });
        }

        window.addEventListener('DOMContentLoaded', loadDashboardData);
    </script>
</body>
</html>
"""
