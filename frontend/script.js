document.addEventListener('DOMContentLoaded', () => {
    // Navigation Logic
    const navItems = document.querySelectorAll('.nav-item:not(.spacer)');
    const sections = document.querySelectorAll('.page-section');

    function navigateTo(targetId) {
        if (!targetId) return;

        // Update Sidebar
        navItems.forEach(item => {
            if (item.dataset.target === targetId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Show Section
        sections.forEach(section => {
            if (section.id === targetId) {
                // Add fade-in animation reset
                section.classList.remove('fade-in');
                void section.offsetWidth; // Trigger reflow
                section.classList.add('fade-in');

                section.classList.add('active');
            } else {
                section.classList.remove('active');
            }
        });
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const target = item.dataset.target;
            navigateTo(target);
        });
    });

    // File Upload Logic
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    // Input Change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            Array.from(files).forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'glass-panel file-item'; // Use glass-panel class but we need specific sizing
                // We'll define a specific class in CSS for file-item to avoid inline styles
                fileItem.style.padding = '12px 16px';
                fileItem.style.marginBottom = '8px';
                fileItem.style.display = 'flex';
                fileItem.style.justifyContent = 'space-between';
                fileItem.style.alignItems = 'center';

                fileItem.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 20px;">📄</span>
                        <div>
                            <div style="font-weight: 500; font-size: 14px;">${file.name}</div>
                            <div style="font-size: 12px; color: var(--text-secondary);">${(file.size / 1024).toFixed(2)} KB</div>
                        </div>
                    </div>
                    <span style="color: var(--success); font-weight: 500; font-size: 13px;">Pronto</span>
                `;
                fileList.appendChild(fileItem);
            });
        }
    }

    // Configuration Form
    const configForm = document.getElementById('config-form');
    if (configForm) {
        configForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = configForm.querySelector('button[type="submit"]');
            const originalText = btn.innerText;
            const originalBg = btn.style.backgroundColor;

            btn.innerText = 'Salvo';
            btn.disabled = true;
            btn.style.backgroundColor = 'var(--success)';

            setTimeout(() => {
                btn.innerText = originalText;
                btn.disabled = false;
                btn.style.backgroundColor = originalBg;
            }, 2000);
        });
    }

    // Execution Simulation
    const btnStart = document.getElementById('btn-start');
    const logsOutput = document.getElementById('logs-output');
    const executionStatus = document.getElementById('execution-status');
    const statusInd = document.getElementById('status-ind');

    if (btnStart) {
        btnStart.addEventListener('click', () => {
            if (btnStart.disabled) return;

            btnStart.disabled = true;
            btnStart.innerText = 'Executando...';

            executionStatus.innerText = 'Processando...';
            statusInd.style.color = 'var(--warning)';
            statusInd.querySelector('.icon').innerText = '􀇳'; // Gear spinning or similar

            logsOutput.innerHTML = '';
            addLog('Iniciando script automacao_remessa.py...', 'info');

            const steps = [
                { msg: 'Lendo configurações...', delay: 800 },
                { msg: 'Verificando diretório de entrada...', delay: 1500 },
                { msg: 'Encontrado arquivo: dados_jan_2026.xlsx', delay: 2200 },
                { msg: 'Processando linhas do Excel...', delay: 3500 },
                { msg: 'Gerando arquivos PDF...', delay: 5000 },
                { msg: 'Enviando e-mails...', delay: 7000 },
                { msg: 'Processamento concluído com sucesso!', delay: 8500, type: 'success' }
            ];

            steps.forEach(step => {
                setTimeout(() => {
                    addLog(step.msg, step.type || 'info');
                    if (step.msg.includes('concluído')) {
                        btnStart.disabled = false;
                        btnStart.innerText = 'Iniciar';

                        executionStatus.innerText = 'Concluído';
                        statusInd.style.color = 'var(--success)';
                        statusInd.querySelector('.icon').innerText = '􀆅'; // Checkmark
                    }
                }, step.delay);
            });
        });
    }

    function addLog(message, type) {
        const line = document.createElement('div');
        line.className = 'log-line';
        const timestamp = new Date().toLocaleTimeString([], { hour12: false });

        let colorClass = '';
        if (type === 'success') colorClass = 'color: var(--success);';
        if (type === 'error') colorClass = 'color: var(--danger);';

        line.innerHTML = `<span style="opacity: 0.5; margin-right: 8px;">${timestamp}</span> <span style="${colorClass}">${message}</span>`;

        logsOutput.appendChild(line);
        logsOutput.scrollTop = logsOutput.scrollHeight;
    }
});
