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
                datasets: [{
                    label: 'Visitantes',
                    data: window.dashboardData.visitas_data,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59,130,246,0.2)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: true } },
                scales: { y: { beginAtZero: true } }
            }
        });
    }
});
