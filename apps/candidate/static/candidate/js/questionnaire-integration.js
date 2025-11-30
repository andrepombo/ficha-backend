/**
 * Questionnaire Integration for Candidate Application Form
 * Adds a second page with questionnaire before final submission
 */

(function() {
    'use strict';
    
    let currentStep = 1;
    let questionnaireSteps = []; // Array of questionnaire templates
    let selectedAnswers = {}; // Format: { templateId: { questionId: [optionIds] } }
    let originalSubmitButton = null;
    let hasQuestionnaires = false;
    let totalSteps = 3; // 1 = Dados Pessoais, 2 = Dados Extras, Last = Review (3 when no questionnaires)
    
    // Initialize multi-step form
    function initMultiStepForm() {
        const form = document.querySelector('form[method="post"]');
        if (!form) return;
        
        // Store original submit button
        originalSubmitButton = form.querySelector('button[type="submit"]');
        if (!originalSubmitButton) return;
        
        // Split content into Step 1 (before marker) and Step 2 (after marker)
        const children = Array.from(form.children);
        const marker = document.getElementById('extras_split_marker');
        const markerIndex = marker ? children.indexOf(marker) : -1;

        const step1 = document.createElement('div');
        step1.className = 'form-step active';
        step1.dataset.step = '1';

        const step2 = document.createElement('div');
        step2.className = 'form-step';
        step2.dataset.step = '2';
        step2.dataset.stepType = 'extras';

        // Helper to decide if node is movable (skip hidden fields and track link)
        const isMovable = (el) => !(
            (el.tagName === 'INPUT' && el.type === 'hidden') ||
            el.classList?.contains('track-link') ||
            el === originalSubmitButton
        );

        if (markerIndex >= 0) {
            // Move nodes before marker into step1
            for (let i = 0; i < markerIndex; i++) {
                const el = children[i];
                if (isMovable(el)) step1.appendChild(el);
            }
            // Remove marker itself
            marker.parentElement && marker.parentElement.removeChild(marker);
            // Move nodes after marker into step2
            for (let i = markerIndex; i < children.length; i++) {
                const el = children[i];
                if (isMovable(el)) step2.appendChild(el);
            }
        } else {
            // Fallback: if no marker, put everything into step1
            children.forEach(el => { if (isMovable(el)) step1.appendChild(el); });
        }
        
        // Create step indicator
        const stepIndicator = createStepIndicator();
        form.insertBefore(stepIndicator, form.firstChild);

        // Add step 1 back to form
        form.appendChild(step1);

        // Add Step 2: Dados Extras (only if we actually moved content)
        if (step2.children.length > 0) {
            // Add navigation to step 1
            const nav1 = document.createElement('div');
            nav1.className = 'step-navigation no-border';
            nav1.innerHTML = `
                <div></div>
                <button type="button" class="btn btn-primary btn-lg" id="step1NextBtn">
                    Próximo <i class="bi bi-arrow-right ms-2"></i>
                </button>
            `;
            step1.appendChild(nav1);

            // No explicit header for step 2; start directly with the next form sections

            // Navigation for step 2
            const nav2 = document.createElement('div');
            nav2.className = 'step-navigation no-border';
            nav2.innerHTML = `
                <button type="button" class="btn btn-outline-primary btn-lg" id="step2BackBtn">
                    <i class="bi bi-arrow-left me-2"></i> Voltar
                </button>
                <button type="button" class="btn btn-primary btn-lg" id="step2NextBtn">
                    Próximo <i class="bi bi-arrow-right ms-2"></i>
                </button>
            `;
            step2.appendChild(nav2);

            form.appendChild(step2);
        }
        
        // Create review step (questionnaire steps will be created dynamically)
        const reviewStep = createReviewStep();
        form.appendChild(reviewStep);

        // Move WhatsApp opt-in and Privacy Policy block to Review step if present
        try {
            const whatsappInput = form.querySelector('input[name="whatsapp_opt_in"]');
            if (whatsappInput) {
                const container = whatsappInput.closest('.mt-4.mb-4') || whatsappInput.closest('.form-check')?.parentElement || whatsappInput.parentElement;
                const consentsTarget = reviewStep.querySelector('#consentsContainer');
                if (container && consentsTarget) {
                    consentsTarget.appendChild(container);
                }
            }
        } catch (e) {
            console.warn('Could not move WhatsApp opt-in block to review step:', e);
        }
        
        // Add hidden fields for questionnaire data
        const templateIdField = document.createElement('input');
        templateIdField.type = 'hidden';
        templateIdField.name = 'template_id';
        templateIdField.id = 'template_id';
        form.appendChild(templateIdField);
        
        const answersField = document.createElement('input');
        answersField.type = 'hidden';
        answersField.name = 'questionnaire_answers';
        answersField.id = 'questionnaire_answers';
        form.appendChild(answersField);
        
        // Hide original submit button
        originalSubmitButton.style.display = 'none';
        
        // Add CSS
        addStyles();

        // Wire navigation buttons
        const btnNext1 = document.getElementById('step1NextBtn');
        const btnBack2 = document.getElementById('step2BackBtn');
        const btnNext2 = document.getElementById('step2NextBtn');
        if (btnNext1) btnNext1.addEventListener('click', handleStep1Next);
        if (btnBack2) btnBack2.addEventListener('click', () => window.questionnaireGoToStep(1));
        if (btnNext2) btnNext2.addEventListener('click', handleExtrasNext);
    }
    
    // Create step indicator
    function createStepIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'step-indicator';
        indicator.id = 'stepIndicator';
        indicator.innerHTML = `
            <div class="step active" data-step="1">
                <div class="step-number">1</div>
                <div class="step-label">Dados Pessoais</div>
            </div>
            <div class="step-separator"></div>
            <div class="step" data-step="2">
                <div class="step-number">2</div>
                <div class="step-label">Dados Extras</div>
            </div>
        `;
        return indicator;
    }
    
    // Update step indicator with questionnaire steps
    function updateStepIndicator() {
        const indicator = document.getElementById('stepIndicator');
        if (!indicator) return;
        
        let html = `
            <div class="step ${currentStep === 1 ? 'active' : currentStep > 1 ? 'completed' : ''}" data-step="1">
                <div class="step-number">1</div>
                <div class="step-label">Dados Pessoais</div>
            </div>
            <div class="step-separator"></div>
            <div class="step ${currentStep === 2 ? 'active' : currentStep > 2 ? 'completed' : ''}" data-step="2">
                <div class="step-number">2</div>
                <div class="step-label">Dados Extras</div>
            </div>
        `;
        
        // Add questionnaire steps (start from step 3)
        questionnaireSteps.forEach((template, index) => {
            const stepNum = index + 3;
            const isActive = currentStep === stepNum;
            const isCompleted = currentStep > stepNum;
            html += `
                <div class="step-separator"></div>
                <div class="step ${isActive ? 'active' : isCompleted ? 'completed' : ''}" data-step="${stepNum}">
                    <div class="step-number">${stepNum}</div>
                    <div class="step-label">${template.title}</div>
                </div>
            `;
        });
        
        indicator.innerHTML = html;
    }
    
    // Create questionnaire steps dynamically
    function createQuestionnaireSteps() {
        const form = document.querySelector('form[method="post"]');
        if (!form) return;
        
        // Remove any existing questionnaire steps
        document.querySelectorAll('.form-step[data-step-type="questionnaire"]').forEach(el => el.remove());
        
        questionnaireSteps.forEach((template, index) => {
            const stepNum = index + 3; // questionnaires start at step 3
            const step = document.createElement('div');
            step.className = 'form-step';
            step.dataset.step = stepNum;
            step.dataset.stepType = 'questionnaire';
            step.dataset.templateId = template.id;
            
            const nextStepNum = stepNum + 1;
            const prevStepNum = stepNum - 1;
            const isLast = stepNum === totalSteps - 1;
            
            step.innerHTML = `
                <div class="form-section">
                    <h3>${template.title}</h3>
                    <p class="text-muted">${template.description || 'Responda às perguntas abaixo.'}</p>
                    
                    <div id="questionnaireContainer_${template.id}">
                        <div class="questionnaire-loading">
                            <div class="spinner-border text-primary" role="status">
                                <span class="sr-only">Carregando questionário...</span>
                            </div>
                            <p class="mt-3">Carregando questionário...</p>
                        </div>
                    </div>
                </div>
                
                <div class="step-navigation">
                    <button type="button" class="btn btn-outline-primary btn-lg" onclick="window.questionnaireGoToStep(${prevStepNum})">
                        <i class=\"bi bi-arrow-left me-2\"></i> Voltar
                    </button>
                    <button type="button" class="btn btn-primary btn-lg" onclick="window.questionnaireGoToStep(${nextStepNum})">
                        ${isLast ? 'Revisão <i class=\\"bi bi-arrow-right ms-2\\"></i>' : 'Próximo <i class=\\"bi bi-arrow-right ms-2\\"></i>'}
                    </button>
                </div>
            `;
            
            // Insert before review step using stable selector
            const reviewStep = document.querySelector('.form-step[data-step-type="review"]');
            if (reviewStep) {
                form.insertBefore(step, reviewStep);
            } else {
                form.appendChild(step);
            }
        });
    }
    
    // Create review step
    function createReviewStep() {
        const step = document.createElement('div');
        step.className = 'form-step';
        step.dataset.step = totalSteps;
        step.dataset.stepType = 'review';
        step.innerHTML = `
            <div class="form-section">
                <h3>Revisão da Candidatura</h3>
                <p class="text-muted">Revise suas informações antes de enviar.</p>
                
                <div id="reviewContainer"></div>

                <div id="consentsContainer" class="mt-4"></div>
                
                <div class="alert alert-info mt-4">
                    <strong>Atenção:</strong> Ao clicar em "Enviar Candidatura", você confirma que todas as informações fornecidas são verdadeiras.
                </div>
            </div>
            
            <div class="step-navigation">
                <button type="button" class="btn btn-secondary btn-lg" id="stepReviewBackBtn" onclick="handleReviewBack()">
                    ← Voltar
                </button>
                <button type="button" class="btn btn-success btn-lg" id="finalSubmitBtn">
                    Enviar Candidatura ✓
                </button>
            </div>
        `;
        return step;
    }
    
    // Check if position has questionnaires
    async function checkQuestionnaireAvailability(position) {
        if (!position) {
            hideQuestionnaireSteps();
            return false;
        }
        
        try {
            const response = await fetch(`/api/questionnaires/steps-for-position/?position_key=${encodeURIComponent(position)}`);
            
            if (response.ok) {
                const data = await response.json();
                if (data && data.steps && data.steps.length > 0) {
                    questionnaireSteps = data.steps;
                    totalSteps = 2 + questionnaireSteps.length + 1; // Personal + Extras + Questionnaires + Review
                    showQuestionnaireSteps();
                    return true;
                }
            }
            
            hideQuestionnaireSteps();
            return false;
        } catch (error) {
            console.error('Error checking questionnaires:', error);
            hideQuestionnaireSteps();
            return false;
        }
    }
    
    // Show questionnaire steps
    function showQuestionnaireSteps() {
        hasQuestionnaires = true;
        createQuestionnaireSteps();
        updateStepIndicator();
        
        // Update review step number using stable selector
        const reviewStep = document.querySelector('.form-step[data-step-type="review"]');
        if (reviewStep) {
            reviewStep.dataset.step = totalSteps;
        }
    }
    
    // Hide questionnaire steps
    function hideQuestionnaireSteps() {
        hasQuestionnaires = false;
        questionnaireSteps = [];
        selectedAnswers = {};
        totalSteps = 3; // Personal + Extras + Review
        
        // Remove questionnaire step elements
        document.querySelectorAll('.form-step[data-step-type="questionnaire"]').forEach(el => el.remove());
        
        // Reset review step number back to 2
        const reviewStep = document.querySelector('.form-step[data-step-type="review"]');
        if (reviewStep) {
            reviewStep.dataset.step = totalSteps;
        }
        
        updateStepIndicator();
    }
    
    // Handle step 1 next button
    async function handleStep1Next() {
        if (!validateStep(1)) {
            return;
        }
        
        // Partial save: create draft candidate with status='incomplete'
        const payload = {
            full_name: (document.getElementById('id_full_name')?.value || '').trim(),
            cpf: (document.getElementById('id_cpf')?.value || '').trim(),
            email: (document.getElementById('id_email')?.value || '').trim(),
            phone_number: (document.getElementById('id_phone_number')?.value || '').trim(),
            position_applied: (document.querySelector('[name="position_applied"]')?.value || '').trim(),
        };
        
        if (payload.full_name && payload.cpf && payload.phone_number) {
            try {
                const res = await fetch('/api/candidates/public/partial-save/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                });
                const data = await res.json();
                if (res.ok) {
                    console.log('Partial save successful:', data);
                    showToast('Dados pessoais salvos!', 'success');
                } else {
                    console.warn('Partial save failed:', data);
                }
            } catch (e) {
                console.error('Partial save error:', e);
            }
        }
        
        window.questionnaireGoToStep(2); // Always go to Extras
    }
    
    // Simple toast notification
    function showToast(message, variant) {
        const el = document.createElement('div');
        el.className = `alert alert-${variant || 'info'} position-fixed top-0 start-50 translate-middle-x mt-3 shadow`;
        el.style.zIndex = 2000;
        el.textContent = message;
        document.body.appendChild(el);
        setTimeout(() => { el.remove(); }, 2500);
    }

    // Handle extras next button
    async function handleExtrasNext() {
        const positionField = document.querySelector('[name="position_applied"]');
        const position = positionField ? positionField.value : '';
        const hasQuest = await checkQuestionnaireAvailability(position);
        if (hasQuest) {
            window.questionnaireGoToStep(3); // First questionnaire after extras
        } else {
            window.questionnaireGoToStep(totalSteps); // Review
        }
    }
    
    // Handle review back button
    function handleReviewBack() {
        if (hasQuestionnaires) {
            window.questionnaireGoToStep(totalSteps - 1); // Last questionnaire
        } else {
            window.questionnaireGoToStep(2); // Dados Extras when no questionnaires
        }
    }
    
    // Expose functions globally
    window.handleStep1Next = handleStep1Next;
    window.handleExtrasNext = handleExtrasNext;
    window.handleReviewBack = handleReviewBack;
    
    // Go to step
    window.questionnaireGoToStep = function(step) {
        // Validate current step
        if (step > currentStep && !validateStep(currentStep)) {
            return;
        }
        
        // Load questionnaire if it's a questionnaire step
        if (step >= 3 && step < totalSteps) {
            const templateIndex = step - 3;
            if (questionnaireSteps[templateIndex]) {
                loadQuestionnaire(questionnaireSteps[templateIndex]);
            }
        }
        
        // Populate review on last step
        if (step === totalSteps) {
            populateReview();
        }
        
        // Update UI
        document.querySelectorAll('.form-step').forEach(el => el.classList.remove('active'));
        const targetStep = document.querySelector(`.form-step[data-step="${step}"]`);
        if (targetStep) {
            targetStep.classList.add('active');
        }
        
        currentStep = step;
        updateStepIndicator();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    
    // Validate step
    function validateStep(step) {
        if (step === 1) {
            const requiredFields = document.querySelectorAll('.form-step[data-step="1"] [required]');
            let isValid = true;
            let firstInvalid = null;
            
            requiredFields.forEach(field => {
                if (!field.value || !field.value.trim()) {
                    field.classList.add('is-invalid');
                    if (!firstInvalid) firstInvalid = field;
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                alert('Por favor, preencha todos os campos obrigatórios marcados com *');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalid.focus();
                }
                return false;
            }
        }
        
        // Validate questionnaire steps
        if (step >= 3 && step < totalSteps) {
            const templateIndex = step - 3;
            const template = questionnaireSteps[templateIndex];
            if (template && template.questions && template.questions.length > 0) {
                const templateAnswers = selectedAnswers[template.id] || {};
                const allAnswered = template.questions.every(q => {
                    return templateAnswers[q.id] && templateAnswers[q.id].length > 0;
                });
                
                if (!allAnswered) {
                    alert('Por favor, responda todas as questões deste questionário.');
                    return false;
                }
            }
        }
        
        return true;
    }
    
    // Load questionnaire for a specific template
    async function loadQuestionnaire(template) {
        if (!template) {
            console.error('No template provided');
            return;
        }
        
        const containerId = `questionnaireContainer_${template.id}`;
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }
        
        // Check if already loaded
        if (container.querySelector('.question-card')) {
            return; // Already rendered
        }
        
        // Render the questionnaire
        renderQuestionnaire(template, containerId);
    }
    
    // Show empty message
    function showQuestionnaireEmpty(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="questionnaire-empty">
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    // Render questionnaire
    function renderQuestionnaire(template, containerId) {
        if (!template || !template.questions || template.questions.length === 0) {
            showQuestionnaireEmpty(containerId, 'Não há questões disponíveis. Você pode continuar.');
            return;
        }
        
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        template.questions.forEach((question, index) => {
            const questionCard = document.createElement('div');
            questionCard.className = 'question-card';
            
            const questionText = document.createElement('div');
            questionText.className = 'question-text';
            questionText.textContent = `${index + 1}. ${question.question_text}`;
            questionCard.appendChild(questionText);
            
            const optionsContainer = document.createElement('div');
            optionsContainer.className = 'question-options';
            
            question.options.forEach(option => {
                const label = document.createElement('label');
                label.className = 'option-label';
                
                const input = document.createElement('input');
                input.type = question.question_type === 'multi_select' ? 'checkbox' : 'radio';
                input.name = `question_${template.id}_${question.id}`;
                input.value = option.id;
                input.onchange = () => handleAnswerChange(template.id, question.id, option.id, question.question_type);
                
                const span = document.createElement('span');
                span.textContent = option.option_text;
                
                label.appendChild(input);
                label.appendChild(span);
                optionsContainer.appendChild(label);
            });
            
            questionCard.appendChild(optionsContainer);
            container.appendChild(questionCard);
        });
    }
    
    // Handle answer change
    function handleAnswerChange(templateId, questionId, optionId, questionType) {
        // Initialize template answers if needed
        if (!selectedAnswers[templateId]) {
            selectedAnswers[templateId] = {};
        }
        
        if (questionType === 'multi_select') {
            if (!selectedAnswers[templateId][questionId]) {
                selectedAnswers[templateId][questionId] = [];
            }
            
            const index = selectedAnswers[templateId][questionId].indexOf(optionId);
            if (index > -1) {
                selectedAnswers[templateId][questionId].splice(index, 1);
            } else {
                selectedAnswers[templateId][questionId].push(optionId);
            }
        } else {
            selectedAnswers[templateId][questionId] = [optionId];
        }
        
        // Update hidden field with all answers
        updateHiddenAnswersField();
    }
    
    // Update hidden answers field
    function updateHiddenAnswersField() {
        // Format: Array of { template_id, answers: [{question_id, selected_option_ids}] }
        const allAnswers = Object.entries(selectedAnswers).map(([tId, questions]) => ({
            template_id: parseInt(tId),
            answers: Object.entries(questions).map(([qId, optIds]) => ({
                question_id: parseInt(qId),
                selected_option_ids: optIds
            }))
        }));
        document.getElementById('questionnaire_answers').value = JSON.stringify(allAnswers);
    }
    
    // Populate review
    function populateReview() {
        const container = document.getElementById('reviewContainer');
        container.innerHTML = '';
        
        // Personal info
        const personalInfo = document.createElement('div');
        personalInfo.className = 'alert alert-secondary';
        personalInfo.innerHTML = `
            <h5>Dados Pessoais</h5>
            <p><strong>Nome:</strong> ${document.querySelector('[name="full_name"]')?.value || 'N/A'}</p>
            <p><strong>Email:</strong> ${document.querySelector('[name="email"]')?.value || 'N/A'}</p>
            <p><strong>Posição:</strong> ${document.querySelector('[name="position_applied"]')?.value || 'N/A'}</p>
        `;
        container.appendChild(personalInfo);
        
        // Questionnaire summaries
        if (questionnaireSteps.length > 0 && Object.keys(selectedAnswers).length > 0) {
            questionnaireSteps.forEach((template) => {
                const templateAnswers = selectedAnswers[template.id] || {};
                let answeredCount = 0;
                
                template.questions.forEach((question) => {
                    if (templateAnswers[question.id] && templateAnswers[question.id].length > 0) {
                        answeredCount++;
                    }
                });
                
                const questionnaireInfo = document.createElement('div');
                questionnaireInfo.className = 'alert alert-secondary mt-3';
                questionnaireInfo.innerHTML = `
                    <h5>${template.title}</h5>
                    <p>${answeredCount} de ${template.questions.length} questões respondidas</p>
                `;
                container.appendChild(questionnaireInfo);
            });
        }
    }
    
    // Add styles
    function addStyles() {
        // Ensure Bootstrap Icons is available for arrow icons
        if (!document.querySelector('link[href*="bootstrap-icons"]')) {
            const biLink = document.createElement('link');
            biLink.rel = 'stylesheet';
            biLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css';
            document.head.appendChild(biLink);
        }

        const style = document.createElement('style');
        style.textContent = `
            .step-indicator {
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 30px 0;
                gap: 10px;
                flex-wrap: nowrap; /* keep in one row */
                overflow: hidden; /* hide scrollbar and avoid scroll */
            }
            .step {
                display: flex;
                align-items: center;
                gap: 10px;
                flex: 0 0 auto; /* prevent flex wrapping */
            }
            .step.hidden {
                display: none;
            }
            .step-separator.hidden {
                display: none;
            }
            .step-number {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #e0e0e0;
                color: #666;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                transition: all 0.3s;
            }
            .step.active .step-number {
                background: #007bff;
                color: white;
            }
            .step.completed .step-number {
                background: #28a745;
                color: white;
            }
            .step-label {
                font-size: 0.9rem;
                color: #666;
                white-space: nowrap; /* keep labels in one line */
            }
            .step.active .step-label {
                color: #007bff;
                font-weight: bold;
            }
            .step-separator {
                width: 50px;
                height: 2px;
                background: #e0e0e0;
                flex: 0 0 auto;
            }
            .step.completed + .step-separator {
                background: #28a745;
            }
            .form-step {
                display: none;
            }
            .form-step.active {
                display: block;
            }
            .step-navigation {
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 2px solid #e0e0e0;
            }
            .step-navigation.no-border {
                border-top: none;
                padding-top: 10px;
            }
            .question-card {
                background: white;
                border-radius: 6px;
                padding: 20px;
                margin-bottom: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .question-text {
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
            }
            .question-options {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .option-label {
                display: flex;
                align-items: center;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
            }
            .option-label:hover {
                border-color: #007bff;
                background: #f8f9fa;
            }
            .option-label input {
                margin-right: 10px;
            }
            .questionnaire-loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .questionnaire-empty {
                text-align: center;
                padding: 40px;
                background: white;
                border-radius: 6px;
                color: #666;
            }
            @media (max-width: 768px) {
                .step-number { width: 34px; height: 34px; }
                .step-separator { width: 30px; }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Load positions into dropdown
    async function loadPositions() {
        const select = document.getElementById('id_position_applied');
        if (!select) {
            console.log('Position select not found');
            return;
        }
        
        console.log('Loading positions from API...');
        
        let positions = [];
        
        try {
            // Fetch positions from API
            const response = await fetch('/api/positions/');
            
            if (response.ok) {
                const data = await response.json();
                if (data && Array.isArray(data)) {
                    positions = data;
                    console.log('Loaded', positions.length, 'positions from API');
                } else {
                    console.log('API returned invalid data');
                }
            } else {
                console.log('API error:', response.status);
            }
        } catch (error) {
            console.error('Error fetching positions:', error);
        }
        
        // Filter only active positions
        const activePositions = positions.filter(p => p.is_active);
        
        // Clear existing options
        select.innerHTML = '<option value="">Selecione um cargo...</option>';
        
        // Add positions
        if (activePositions.length > 0) {
            activePositions.forEach(position => {
                const option = document.createElement('option');
                option.value = position.name;
                option.textContent = position.name;
                select.appendChild(option);
            });
            console.log('Added', activePositions.length, 'active positions to dropdown');
        } else {
            // No positions available
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'Nenhum cargo cadastrado - Configure em /painel/positions';
            option.disabled = true;
            select.appendChild(option);
            console.log('No positions available');
        }
    }
    
    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        // Load positions first
        loadPositions();
        
        // Only initialize if we're on the application form page
        const form = document.querySelector('form[method="post"]');
        const submitBtn = form?.querySelector('button[type="submit"]');
        
        if (form && submitBtn && submitBtn.textContent.includes('Enviar Candidatura')) {
            initMultiStepForm();
            
            // Check if position is already selected (from Step 0)
            const positionField = document.querySelector('[name="position_applied"]');
            if (positionField && positionField.value) {
                console.log('Position already selected:', positionField.value);
                // Check for questionnaires for this position
                checkQuestionnaireAvailability(positionField.value)
                    .then(hasQuest => {
                        if (hasQuest) {
                            console.log(`Found ${questionnaireSteps.length} questionnaire(s) for this position`);
                        } else {
                            console.log('No questionnaires for this position');
                        }
                    })
                    .catch(error => {
                        console.log('Error checking questionnaires:', error);
                    });
            }
            
            // Handle final submission
            document.addEventListener('click', function(e) {
                if (e.target && e.target.id === 'finalSubmitBtn') {
                    e.preventDefault();
                    if (originalSubmitButton) {
                        originalSubmitButton.click();
                    }
                }
            });
        }
    });
})();
