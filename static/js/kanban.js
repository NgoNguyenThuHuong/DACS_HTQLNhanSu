document.addEventListener('DOMContentLoaded', () => {
    const board = document.getElementById('kanban-board');
    const themeToggle = document.getElementById('theme-toggle');
    const appContainer = document.getElementById('app-container');

    const stages = [
        { id: 'New', title: 'Mới ứng tuyển', color: 'bg-blue-100 text-blue-800' },
        { id: 'Testing', title: 'Đang làm Test', color: 'bg-yellow-100 text-yellow-800' },
        { id: 'Interview', title: 'Phỏng vấn', color: 'bg-purple-100 text-purple-800' },
        { id: 'Offer', title: 'Đề nghị (Offer)', color: 'bg-green-100 text-green-800' },
        { id: 'Hired', title: 'Đã tuyển', color: 'bg-emerald-200 text-emerald-900' },
        { id: 'Rejected', title: 'Từ chối', color: 'bg-red-100 text-red-800' }
    ];

    // Theme logic
    if (localStorage.getItem('theme') === 'dark') {
        appContainer.classList.add('dark');
        themeToggle.checked = true;
    }

    themeToggle.addEventListener('change', (e) => {
        if (e.target.checked) {
            appContainer.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            appContainer.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    });

    async function loadBoard() {
        try {
            const res = await fetch('/api/pipeline/board');
            if (!res.ok) throw new Error('Failed to load board');
            const data = await res.json();
            renderBoard(data);
        } catch (err) {
            console.error(err);
        }
    }

    function renderBoard(data) {
        board.innerHTML = '';
        stages.forEach(stage => {
            const col = document.createElement('div');
            col.className = 'w-80 flex-shrink-0 flex flex-col glass-panel p-4 kanban-col rounded-xl';
            col.dataset.stage = stage.id;
            
            col.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-slate-700 dark:text-slate-200">${stage.title}</h3>
                    <span class="text-xs font-semibold px-2 py-1 rounded-full ${stage.color}">${(data[stage.id] || []).length}</span>
                </div>
                <div class="flex-1 overflow-y-auto space-y-3" id="col-${stage.id}"></div>
            `;
            
            const container = col.querySelector(`#col-${stage.id}`);
            
            (data[stage.id] || []).forEach(candidate => {
                const card = document.createElement('div');
                card.className = 'bg-white dark:bg-slate-800 p-4 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700 kanban-card flex flex-col gap-2 relative';
                card.draggable = true;
                card.dataset.id = candidate.candidate_id;
                
                let badge = '';
                if (candidate.risk_indicator === 'High') {
                    badge = '<span class="absolute top-2 right-2 flex h-3 w-3"><span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span class="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span></span>';
                }
                
                card.innerHTML = `
                    ${badge}
                    <h4 class="font-semibold text-slate-800 dark:text-white text-sm">${candidate.fullname}</h4>
                    <p class="text-xs text-slate-500 dark:text-slate-400">${candidate.email}</p>
                `;
                
                // Drag Events
                card.addEventListener('dragstart', () => {
                    card.classList.add('dragging');
                });
                
                card.addEventListener('dragend', () => {
                    card.classList.remove('dragging');
                });
                
                container.appendChild(card);
            });
            
            // Drop Events
            col.addEventListener('dragover', e => {
                e.preventDefault();
                col.classList.add('drag-over');
            });
            
            col.addEventListener('dragleave', () => {
                col.classList.remove('drag-over');
            });
            
            col.addEventListener('drop', async e => {
                e.preventDefault();
                col.classList.remove('drag-over');
                const draggingCard = document.querySelector('.dragging');
                if (draggingCard) {
                    container.appendChild(draggingCard);
                    const candidateId = draggingCard.dataset.id;
                    const newStage = stage.id;
                    await updateStage(candidateId, newStage);
                }
            });
            
            board.appendChild(col);
        });
    }

    async function updateStage(candidateId, newStage) {
        try {
            const res = await fetch(`/api/pipeline/${candidateId}/stage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ stage: newStage })
            });
            if (!res.ok) throw new Error('Update failed');
            // Re-render to update counts
            loadBoard();
        } catch (err) {
            console.error(err);
            alert('Lỗi cập nhật trạng thái');
            loadBoard(); // Revert
        }
    }

    loadBoard();
});
