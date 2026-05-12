// Profile Page Interactive Logic
document.addEventListener('DOMContentLoaded', function() {
    // 1. Tab Switching for Edit Button
    const editBtn = document.querySelector('button.btn-primary.shadow-sm');
    if (editBtn) {
        editBtn.addEventListener('click', function() {
            const cvTab = new bootstrap.Tab(document.getElementById('cv-tab'));
            cvTab.show();
        });
    }

    // 2. Tab Navigation Contrast Sync
    const tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabButtons.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', function (event) {
            tabButtons.forEach(link => {
                link.classList.remove('active-tab-custom');
                link.classList.add('text-secondary');
            });
            event.target.classList.add('active-tab-custom');
            event.target.classList.remove('text-secondary');
        });
    });

    // 3. Skills Radar Chart
    const ctxSkills = document.getElementById('skillsChart');
    if (ctxSkills) {
        new Chart(ctxSkills.getContext('2d'), {
            type: 'radar',
            data: {
                labels: ['Kỹ năng giao tiếp', 'Kỹ năng đàm phán', 'Kỹ năng giải quyết', 'Chuyên môn', 'Kiến thức SP', 'Cầu tiến'],
                datasets: [{
                    label: 'Nhân viên',
                    data: [85, 90, 75, 80, 70, 95],
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: 'rgb(99, 102, 241)',
                    pointBackgroundColor: 'rgb(99, 102, 241)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(99, 102, 241)'
                }, {
                    label: 'Trung bình Đội',
                    data: [75, 70, 80, 85, 75, 80],
                    fill: true,
                    backgroundColor: 'rgba(209, 213, 219, 0.2)',
                    borderColor: 'rgb(156, 163, 175)',
                    pointBackgroundColor: 'rgb(156, 163, 175)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(156, 163, 175)'
                }]
            },
            options: {
                elements: { line: { borderWidth: 3 } },
                scales: {
                    r: {
                        angleLines: { display: true },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: { display: false }
                    }
                },
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }
});
