// Dashboard Charts Logic
document.addEventListener('DOMContentLoaded', function() {
    // Admin Charts
    const deptChart = document.getElementById('deptChart');
    if (deptChart && typeof deptData !== 'undefined') {
        new Chart(deptChart, { 
            type: 'doughnut', 
            data: { 
                labels: deptLabels, 
                datasets: [{ 
                    data: deptData, 
                    backgroundColor: ['#0f172a', '#38bdf8', '#64748b', '#94a3b8', '#1e293b'], 
                    borderWidth: 0 
                }] 
            }, 
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                cutout: '75%', 
                plugins: { legend: { position: 'right' } } 
            } 
        });
    }

    const leaveChart = document.getElementById('leaveChart');
    if (leaveChart && typeof leaveData !== 'undefined') {
        new Chart(leaveChart, { 
            type: 'bar', 
            data: { 
                labels: leaveLabels, 
                datasets: [{ 
                    label: 'Yêu cầu', 
                    data: leaveData, 
                    backgroundColor: leaveColors, 
                    borderRadius: 10 
                }] 
            }, 
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                scales: { y: { beginAtZero: true } } 
            } 
        });
    }

    // HR Charts
    const attChart = document.getElementById('attendanceChart');
    if (attChart && typeof attData !== 'undefined') {
        const attCtx = attChart.getContext('2d');
        const grad = attCtx.createLinearGradient(0, 0, 0, 300); 
        grad.addColorStop(0, 'rgba(79, 70, 229, 0.4)'); 
        grad.addColorStop(1, 'rgba(79, 70, 229, 0)');
        new Chart(attCtx, { 
            type: 'line', 
            data: { 
                labels: attDays, 
                datasets: [{ 
                    label: 'Hiện diện', 
                    data: attData, 
                    borderColor: '#4f46e5', 
                    borderWidth: 4, 
                    tension: 0.4, 
                    fill: true, 
                    backgroundColor: grad, 
                    pointRadius: 0 
                }] 
            }, 
            options: { 
                responsive: true, 
                maintainAspectRatio: false, 
                scales: { 
                    y: { beginAtZero: true, grid: { display: false } }, 
                    x: { grid: { display: false } } 
                }, 
                plugins: { legend: { display: false } } 
            } 
        });
    }
});
