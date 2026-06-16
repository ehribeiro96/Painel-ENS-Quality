(() => {
    const hero = document.getElementById("hero-outlook");
    if (!hero) return;

    const simulations = {
        classic: [
            { title: 'Abrir o Outlook', description: 'Inicie o aplicativo Microsoft Outlook no seu computador.', action: 'openOutlook', hint: 'Clique no ícone do Outlook.' },
            { title: 'Escolher Arquivo', description: 'No menu superior, clique em "Arquivo".', action: 'clickFile', hint: 'Fica no canto superior esquerdo.' },
            { title: 'Selecionar Opções', description: 'No menu lateral, clique em "Opções".', action: 'clickOptions', hint: 'Parte inferior da coluna lateral.' },
            { title: 'Ir à aba Email', description: 'Na janela de Opções, vá até a aba "Email".', action: 'clickEmail', hint: 'Aba na lateral esquerda.' },
            { title: 'Clicar em Assinaturas...', description: 'Em "Redigir mensagens", clique em "Assinaturas...".', action: 'clickSignatures', hint: 'Botão no meio da janela.' },
            { title: 'Criar Nova Assinatura', description: 'Clique em "Nova", nomeie como "Assinatura ENS" e cole o conteúdo HTML.', action: 'createSignature', hint: 'Dê um nome claro antes de colar.' },
            { title: 'Escolher assinatura padrão', description: 'Associe a assinatura à conta e marque para novos e/ou respostas.', action: 'setDefault', hint: 'Defina quando usar a assinatura.' },
            { title: 'Confirmar em OK', description: 'Confirme em OK para salvar as configurações.', action: 'confirmOK', hint: 'Clique no botão OK.' },
        ],
        new: [
            { title: 'Clicar em Configurações', description: 'Clique no ícone de engrenagem (configurações).', action: 'clickSettings', hint: 'Canto superior direito.' },
            { title: 'Contas > Assinaturas', description: 'Selecione "Contas" e depois "Assinaturas".', action: 'clickAccountsSignatures', hint: 'Menu de configurações.' },
            { title: 'Escolher conta', description: 'Se houver mais de uma conta, escolha a desejada.', action: 'selectAccount', hint: 'Selecione sua conta de email.' },
            { title: 'Nova assinatura', description: 'Clique em "Nova assinatura", nomeie e insira/cole a assinatura.', action: 'createNewSignature', hint: 'Use o nome "Assinatura ENS".' },
            { title: 'Formatar e Salvar', description: 'Formate se necessário e clique em Salvar.', action: 'formatAndSave', hint: 'Clique em Salvar.' },
            { title: 'Assinaturas predefinidas', description: 'Defina a assinatura para novas mensagens e respostas.', action: 'setDefaultSignature', hint: 'Escolha para novos e respostas.' },
            { title: 'Salvar novamente', description: 'Clique em Salvar para confirmar.', action: 'finalSave', hint: 'Finalize com Salvar.' },
        ],
        web: [
            { title: 'Acessar Outlook Web', description: 'Acesse outlook.office.com no navegador.', action: 'openOutlookWeb', hint: 'Abra o navegador e faça login.' },
            { title: 'Clicar em Configurações', description: 'Clique no ícone de engrenagem no canto superior direito.', action: 'clickSettings', hint: 'Ícone no topo direito.' },
            { title: 'Exibir todas as configurações', description: 'Clique em "Exibir todas as configurações do Outlook".', action: 'viewAllSettings', hint: 'Opção ao fim do painel.' },
            { title: 'Email > Redigir e responder', description: 'Navegue para "Email" > "Redigir e responder".', action: 'navigateCompose', hint: 'Menu lateral esquerdo.' },
            { title: 'Nome e conteúdo', description: 'Nomeie como "Assinatura ENS" e cole o HTML no editor.', action: 'pasteSignature', hint: 'Cole o conteúdo gerado.' },
            { title: 'Assinatura padrão', description: 'Selecione a assinatura padrão para novos emails e respostas.', action: 'setDefaultSignature', hint: 'Defina para enviar/responder.' },
            { title: 'Salvar para concluir', description: 'Clique em "Salvar" para concluir.', action: 'saveChanges', hint: 'Botão Salvar no topo.' },
        ],
    };

    const orderedVersions = ["classic", "new", "web"];
    let activeVersion = orderedVersions[0];

    const storagePrefix = "outlook-simulation";
    const state = orderedVersions.reduce((acc, key) => {
        acc[key] = loadState(key);
        return acc;
    }, {});

    const stepsContainer = hero.querySelector("[data-guide-steps]");
    const tabsContainers = hero.querySelectorAll("[data-guide-tabs]");
    const simulationGrid = hero.querySelector(".guide-simulation-grid");

    function loadState(version) {
        try {
            const saved = localStorage.getItem(`${storagePrefix}-${version}`);
            if (saved) return JSON.parse(saved);
        } catch (_) {
            /* ignore */
        }
        return { stepIndex: 0, started: false, completed: false, confetti: false };
    }

    function saveState(version) {
        try {
            localStorage.setItem(`${storagePrefix}-${version}`, JSON.stringify(state[version]));
        } catch (_) {
            /* ignore */
        }
    }

    const createEl = (tag, className, attrs = {}) => {
        const el = document.createElement(tag);
        if (className) el.className = className;
        Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
        return el;
    };

    const normalizeSimState = (simState, steps) => {
        const total = steps.length;
        const lastIndex = Math.max(0, total - 1);
        let changed = false;

        if (simState.stepIndex < 0) {
            simState.stepIndex = 0;
            changed = true;
        } else if (simState.stepIndex > lastIndex) {
            simState.stepIndex = lastIndex;
            changed = true;
        }

        let completedCount = simState.completed ? total : simState.started ? simState.stepIndex + 1 : 0;
        if (completedCount > total) {
            completedCount = total;
            changed = true;
        }

        const progressPct = total ? Math.min(100, (completedCount / total) * 100) : 0;
        return { completedCount, progressPct, changed };
    };

    const setActiveVersion = (versionKey) => {
        if (!simulations[versionKey] || versionKey === activeVersion) return;
        activeVersion = versionKey;
        renderTabs();
        renderSteps();
        renderSimulation();
    };

    const renderTabs = () => {
        tabsContainers.forEach((container) => {
            container.innerHTML = "";
            orderedVersions.forEach((key) => {
                const button = createEl("button", "guide-tab", {
                    type: "button",
                    role: "tab",
                    "data-version": key,
                    "data-guide-tab": "true",
                    "aria-pressed": String(key === activeVersion),
                });
                button.textContent = key === "classic" ? "Clássico" : key === "new" ? "Novo" : "Web";
                if (key === activeVersion) button.classList.add("is-active");
                button.addEventListener("click", () => setActiveVersion(key));
                container.appendChild(button);
            });
        });
    };

    const renderSteps = () => {
        if (!stepsContainer) return;
        const steps = simulations[activeVersion];
        stepsContainer.innerHTML = "";
        steps.forEach((step, idx) => {
            const card = createEl("div", "guide-step-card");
            const number = createEl("div", "guide-step-number");
            number.textContent = idx + 1;
            const content = createEl("div", "guide-step-card-content");
            const title = createEl("h3");
            title.textContent = step.title;
            const desc = createEl("p");
            desc.textContent = step.description;
            const hint = createEl("div", "guide-step-hint");
            hint.textContent = step.hint;
            content.append(title, desc, hint);
            card.append(number, content);
            stepsContainer.appendChild(card);
        });
    };

    const renderChecklist = (container, steps, simState, completedCount, progressPct) => {
        container.innerHTML = "";
        const card = createEl("div", "checklist-card guide-simulation-card");

        const header = createEl("div", "checklist-header");
        const title = createEl("h3");
        title.textContent = "Checklist";
        const counter = createEl("span", "checklist-count");
        counter.textContent = `${completedCount}/${steps.length}`;
        header.append(title, counter);

        const barWrap = createEl("div", "checklist-progress");
        const bar = createEl("div", "checklist-progress-bar");
        const fill = createEl("span", "checklist-progress-fill");
        const progress = simState.completed ? 100 : progressPct;
        fill.style.width = `${progress}%`;
        bar.appendChild(fill);
        barWrap.appendChild(bar);

        const list = createEl("ul", "checklist-list");
        steps.forEach((step, idx) => {
            const li = createEl("li");
            const done = simState.completed || idx < completedCount;
            if (done) li.classList.add("is-done");
            const marker = createEl("span", "checklist-marker");
            marker.textContent = done ? "✔" : idx + 1;
            const text = createEl("span", "checklist-text");
            text.textContent = step.title;
            li.append(marker, text);
            list.appendChild(li);
        });

        card.append(header, barWrap, list);
        container.appendChild(card);
    };

    const renderSimulation = () => {
        if (!simulationGrid) return;
        const steps = simulations[activeVersion];
        const simState = state[activeVersion];
        const { completedCount, progressPct, changed } = normalizeSimState(simState, steps);
        if (changed) {
            saveState(activeVersion);
        }

        simulationGrid.innerHTML = "";

        const mainCard = createEl("div", "guide-simulation-card sim-main-card");

        const header = createEl("div", "sim-header");
        const left = createEl("div", "sim-header-left");
        const badge = createEl("div", "sim-badge");
        const icon = createEl("span", "sim-icon");
        icon.textContent = "⚡";
        const badgeText = createEl("div");
        badgeText.innerHTML = `<strong>Simulação Interativa</strong><br><small>Pratique antes de fazer no Outlook real</small>`;
        badge.append(icon, badgeText);
        left.appendChild(badge);
        const right = createEl("div", "sim-counter");
        right.innerHTML = `<div>${completedCount}/${steps.length}</div><small>Passos concluídos</small>`;

        if (simState.started && !simState.completed) {
            const restartBtn = createEl("button", "guide-btn ghost");
            restartBtn.textContent = "Refazer do inicio";
            restartBtn.style.marginLeft = "0.75rem";
            restartBtn.style.marginTop = "0.35rem";
            restartBtn.style.padding = "0.35rem 0.9rem";
            restartBtn.style.fontSize = "0.9rem";
            restartBtn.addEventListener("click", () => {
                state[activeVersion] = { stepIndex: 0, started: false, completed: false, confetti: false };
                saveState(activeVersion);
                renderSimulation();
            });
            right.appendChild(restartBtn);
        }
        header.append(left, right);

        const barWrap = createEl("div", "simulation-progress-bar");
        const fill = createEl("span", "simulation-progress-fill");
        const progress = simState.completed ? 100 : progressPct;
        fill.style.width = `${progress}%`;
        barWrap.appendChild(fill);

        mainCard.append(header, barWrap);

        const body = createEl("div", "sim-body");

        if (!simState.started) {
            const start = createEl("div", "sim-start");
            start.innerHTML = `
                <div class="sim-start-icon">🖱️</div>
                <h3>Pronto para começar?</h3>
                <p>Você vai simular a instalação da assinatura passo a passo em um ambiente seguro.</p>
            `;
            const btn = createEl("button", "guide-btn primary");
            btn.textContent = "Iniciar simulação";
            btn.addEventListener("click", () => {
                state[activeVersion] = { stepIndex: 0, started: true, completed: false, confetti: false };
                saveState(activeVersion);
                renderSimulation();
            });
            start.appendChild(btn);
            body.appendChild(start);
        } else if (simState.completed) {
            const done = createEl("div", "sim-complete");
            done.innerHTML = `
                <div class="sim-complete-icon">🎯</div>
                <h3>Parabéns! Simulação concluída</h3>
                <p>Você completou todos os passos e está pronto para aplicar no Outlook real.</p>
            `;
            const actions = createEl("div", "sim-actions");
            const restart = createEl("button", "guide-btn primary");
            restart.textContent = "Refazer simulação";
            restart.addEventListener("click", () => {
                state[activeVersion] = { stepIndex: 0, started: false, completed: false, confetti: false };
                saveState(activeVersion);
                renderSimulation();
            });
            actions.appendChild(restart);
            done.appendChild(actions);
            body.appendChild(done);
            if (simState.confetti) {
                spawnConfetti(mainCard);
                simState.confetti = false;
                saveState(activeVersion);
            }
        } else {
            const step = steps[simState.stepIndex];
            const current = createEl("div", "sim-step");
            current.innerHTML = `
                <div class="sim-pill">Passo ${simState.stepIndex + 1} de ${steps.length}</div>
                <h3>${step.title}</h3>
                <p>${step.description}</p>
            `;
            const shot = createSimulationMock(step, simState, steps);
            const actionBtn = createEl("button", "guide-btn primary");
            actionBtn.textContent = simState.stepIndex === steps.length - 1 ? "Concluir" : "Executar ação";
            actionBtn.addEventListener("click", () => {
                if (simState.stepIndex < steps.length - 1) {
                    simState.stepIndex += 1;
                } else {
                    simState.completed = true; simState.confetti = true;
                }
                normalizeSimState(simState, steps);
                saveState(activeVersion);
                renderSimulation();
            });
            const hint = createEl("div", "sim-hint");
            hint.innerHTML = `<strong>Dica:</strong> ${step.hint}`;
            if (simState.stepIndex === steps.length - 1) {
                const actionsRow = createEl("div", "sim-actions");
                const finishBtn = createEl("button", "guide-btn ghost");
                finishBtn.textContent = "Marcar como concluido";
                finishBtn.addEventListener("click", () => {
                    simState.completed = true; simState.confetti = true;
                    saveState(activeVersion);
                    renderSimulation();
                });
                actionsRow.append(actionBtn, finishBtn);
                current.append(shot, actionsRow, hint);
            } else {
                current.append(shot, actionBtn, hint);
            }
            body.appendChild(current);
        }

        mainCard.appendChild(body);

        const checklistHolder = createEl("div");
        renderChecklist(checklistHolder, steps, simState, completedCount, progressPct);

        simulationGrid.appendChild(mainCard);
        if (checklistHolder.firstChild) {
            checklistHolder.firstChild.classList.add("sim-checklist-row");
            simulationGrid.appendChild(checklistHolder.firstChild);
        }
    };

    const createSimulationMock = (step, simState, steps) => {
        const frame = createEl("div", "sim-window");
        const header = createEl("div", "sim-window-header");
        header.innerHTML = `
            <div class="sim-dots"><span></span><span></span><span></span></div>
            <div class="sim-title">${activeVersion === "classic" ? "Outlook Clássico" : activeVersion === "new" ? "Novo Outlook" : "Outlook Web"}</div>
            <div class="sim-status">${step.action || "ação"}</div>
        `;
        const body = createEl("div", "sim-window-body");
        const sidebar = createEl("div", "sim-window-sidebar");
        ["Geral", "Email", "Calendário", "Avançado"].forEach((item) => {
            const link = createEl("div", "sim-nav-item");
            link.textContent = item;
            if (step.action && item === "Email") link.classList.add("is-active");
            sidebar.appendChild(link);
        });
        const content = createEl("div", "sim-window-content");
        content.innerHTML = `
            <div class="sim-block">
                <div class="sim-block-title">Assinaturas</div>
                <p>Gerencie assinaturas e preferências.</p>
            </div>
            <div class="sim-block grid">
                <div>
                    <div class="sim-label">Nome</div>
                    <div class="sim-input">Assinatura ENS</div>
                </div>
                <div>
                    <div class="sim-label">Conta</div>
                    <div class="sim-input">usuario@empresa.com</div>
                </div>
            </div>
            <div class="sim-window-grid">
                <div class="sim-window-tile is-active">
                    <i class="bi bi-mouse"></i>
                    <div>
                        <strong>Foco atual</strong>
                        <p>${step.title}</p>
                    </div>
                </div>
                <div class="sim-window-tile">
                    <i class="bi bi-lightbulb"></i>
                    <div>
                        <strong>Dica rápida</strong>
                        <p>${step.hint || "Siga o destaque na tela."}</p>
                    </div>
                </div>
                <div class="sim-window-tile">
                    <i class="bi bi-ui-checks"></i>
                    <div>
                        <strong>Próximo passo</strong>
                        <p>${steps[simState.stepIndex + 1]?.title || "Concluir"}</p>
                    </div>
                </div>
            </div>
        `;

        const hotspot = createEl("div", "sim-hotspot");
        const { top, left, label, detail } = getHotspotPosition(step);
        hotspot.style.top = top;
        hotspot.style.left = left;
        hotspot.innerHTML = `<div class="sim-hotspot-pulse"></div><div class="sim-hotspot-core"></div><div class="sim-tooltip"><strong>${label}</strong><span>${detail}</span></div>`;

        const shot = createEl("div", "sim-shot");
        shot.append(header, sidebar, content, hotspot);
        body.appendChild(shot);
        frame.append(body);
        return frame;
    };

    const getHotspotPosition = (step) => {
        const action = step.action;
        switch (action) {
            case "clickFile":
                return { top: "6%", left: "12%", label: "Menu Arquivo", detail: "Acesse Arquivo para abrir opções." };
            case "clickSettings":
                return { top: "6%", left: "82%", label: "Configurações", detail: "Abra a engrenagem no topo direito." };
            case "clickOptions":
                return { top: "28%", left: "18%", label: "Opções", detail: "Menu lateral inferior." };
            case "clickEmail":
                return { top: "38%", left: "18%", label: "Email", detail: "Selecione a aba Email." };
            case "clickSignatures":
                return { top: "46%", left: "55%", label: "Assinaturas...", detail: "Abra a janela de assinaturas." };
            case "typeName":
            case "createSignature":
            case "createNewSignature":
            case "pasteSignature":
                return { top: "60%", left: "52%", label: "Editar assinatura", detail: "Nomeie e cole a assinatura." };
            case "setDefault":
            case "setDefaultSignature":
                return { top: "72%", left: "32%", label: "Assinatura padrão", detail: "Defina novos e respostas." };
            case "saveSignature":
            case "saveChanges":
            case "finalSave":
            case "confirmOK":
                return { top: "85%", left: "78%", label: "Salvar", detail: "Confirme para finalizar." };
            default:
                return { top: "70%", left: "70%", label: "Ação guiada", detail: step.hint || "Siga a indicação na tela." };
        }
    };

    const spawnConfetti = (target) => {
        target.querySelector(".confetti-container")?.remove();
        const container = createEl("div", "confetti-container");
        const colors = ["#2563eb", "#0ea5e9", "#7c3aed", "#10b981", "#f59e0b", "#ef4444"];
        for (let i = 0; i < 50; i++) {
            const piece = createEl("span", "confetti-piece");
            piece.style.background = colors[i % colors.length];
            piece.style.left = `${Math.random() * 100}%`;
            piece.style.animationDelay = `${Math.random() * 0.5}s`;
            piece.style.animationDuration = `${1.6 + Math.random() * 0.8}s`;
            container.appendChild(piece);
        }
        target.appendChild(container);
        setTimeout(() => container.remove(), 2400);
    };

    renderTabs();
    renderSteps();
    renderSimulation();
})();
