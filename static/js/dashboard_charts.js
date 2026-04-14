// dashboard_charts.js - Gráficos do dashboard admin
// Requer Chart.js incluído no template

document.addEventListener('DOMContentLoaded', function() {
    // Gráfico de barras: Relatos por status
    if (document.getElementById('relatosStatusChart')) {
        new Chart(document.getElementById('relatosStatusChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Aprovados', 'Pendentes', 'Rejeitados'],
                datasets: [{
                    label: 'Relatos',
                    data: [window.dashboardData.relatos_aprovados, window.dashboardData.relatos_pendentes, window.dashboardData.relatos_rejeitados],
                    backgroundColor: ['#22c55e', '#eab308', '#ef4444']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de barras: Comentários por status
    if (document.getElementById('comentariosStatusChart')) {
        new Chart(document.getElementById('comentariosStatusChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['Aprovados', 'Pendentes', 'Rejeitados'],
                datasets: [{
                    label: 'Comentários',
                    data: [window.dashboardData.comentarios_aprovados, window.dashboardData.comentarios_pendentes, window.dashboardData.comentarios_rejeitados],
                    backgroundColor: ['#67e8f9', '#fde68a', '#fca5a5']
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de linha: Visitantes ao longo do tempo
    if (document.getElementById('visitantesLineChart')) {
        new Chart(document.getElementById('visitantesLineChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: window.dashboardData.visitas_labels,
                datasets: [
                    {
                        label: 'Visitantes',
                        data: window.dashboardData.visitas_data,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59,130,246,0.2)',
                        fill: true,
                        tension: 0.3
                    },
                    {
                        label: 'Downloads',
                        data: window.dashboardData.downloads_data,
                        borderColor: '#a855f7',
                        backgroundColor: 'rgba(168,85,247,0.12)',
                        fill: false,
                        tension: 0.25
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // Gráfico de barras: acessos por hora
    if (document.getElementById('acessosHoraChart')) {
        new Chart(document.getElementById('acessosHoraChart').getContext('2d'), {
            type: 'bar',
            data: {
                labels: window.dashboardData.horas_labels,
                datasets: [{
                    label: 'Acessos por hora',
                    data: window.dashboardData.horas_data,
                    backgroundColor: 'rgba(251, 146, 60, 0.7)',
                    borderColor: '#fb923c',
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // Gráfico de tendência: visitas diarias + media movel
    if (document.getElementById('tendenciaAcessosChart')) {
        new Chart(document.getElementById('tendenciaAcessosChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: window.dashboardData.visitas_labels,
                datasets: [
                    {
                        label: 'Visitas diarias',
                        data: window.dashboardData.visitas_data,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.18)',
                        fill: true,
                        tension: 0.25
                    },
                    {
                        label: 'Downloads diarios',
                        data: window.dashboardData.downloads_data,
                        borderColor: '#c084fc',
                        backgroundColor: 'rgba(192, 132, 252, 0)',
                        fill: false,
                        tension: 0.25
                    },
                    {
                        label: 'Tendencia',
                        data: window.dashboardData.visitas_tendencia,
                        borderColor: '#f97316',
                        backgroundColor: 'rgba(249, 115, 22, 0)',
                        borderDash: [8, 4],
                        fill: false,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
});
