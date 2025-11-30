from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Candidate, WorkCard, ProfessionalExperience, QuestionnaireTemplate
from .forms import CandidateApplicationForm, ProfessionalExperienceFormSet, get_empty_experience_formset
from django.contrib.auth.hashers import check_password, make_password
from datetime import timedelta
from .integrations.zapi_messages import send_text_to_phone
import json
import requests
from django.conf import settings
import os


def position_selection_view(request):
    """
    Step 0: Position selection page (first page of the form).
    """
    if request.method == 'POST':
        position = request.POST.get('position')
        if position:
            # Store position in session
            request.session['selected_position'] = position
            
            # Fetch questionnaire count for this position
            questionnaires = QuestionnaireTemplate.objects.filter(
                position_key=position,
                is_active=True
            )
            questionnaire_count = questionnaires.count()
            
            # Debug logging
            print(f"DEBUG: Selected position: '{position}'")
            print(f"DEBUG: Found {questionnaire_count} questionnaires")
            for q in questionnaires:
                print(f"  - ID: {q.id}, Title: {q.title}, Step: {q.step_number}")
            
            # Calculate total steps: 1 (position) + 1 (basic info) + N (questionnaires)
            total_steps = 1 + 1 + questionnaire_count
            request.session['total_steps'] = total_steps
            
            print(f"DEBUG: Total steps calculated: {total_steps}")
            
            # Redirect to the main application form (Step 1)
            return redirect('application_form')
        else:
            messages.error(request, 'Por favor, selecione um cargo.')
    
    return render(request, 'candidate/position_selection.html', {
        'total_steps': request.session.get('total_steps', 2)
    })


def application_form_view(request):
    """
    Step 1: View for candidates to submit their job application (Dados Pessoais).
    Position should already be selected in Step 0.
    """
    # Check if position was selected in Step 0
    selected_position = request.session.get('selected_position')
    if not selected_position:
        # Redirect back to position selection if not set
        messages.warning(request, 'Por favor, selecione um cargo primeiro.')
        return redirect('position_selection')
    
    if request.method == 'POST':
        print(f"DEBUG: POST request received for application_form_view")
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        print(f"DEBUG: FILES keys: {list(request.FILES.keys())}")
        
        try:
            form = CandidateApplicationForm(request.POST, request.FILES)
            # For new applications, use helper function to ensure empty formset
            experience_formset = get_empty_experience_formset(prefix='experiences', data=request.POST)
            
            print(f"DEBUG: Form is_valid: {form.is_valid()}")
            print(f"DEBUG: Formset is_valid: {experience_formset.is_valid()}")
            
            if not form.is_valid():
                print(f"ERROR: Form errors: {form.errors}")
            if not experience_formset.is_valid():
                print(f"ERROR: Formset errors: {experience_formset.errors}")
                
        except Exception as e:
            print(f"CRITICAL ERROR in form instantiation/validation: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f'Erro ao processar formulário: {str(e)}')
            # Create empty forms for rendering
            form = CandidateApplicationForm()
            experience_formset = get_empty_experience_formset(prefix='experiences')
            return render(request, 'candidate/application_form.html', {
                'form': form,
                'experience_formset': experience_formset,
                'selected_position': selected_position,
                'total_steps': request.session.get('total_steps', 2),
                'current_step': 2,
            })
        
        if form.is_valid() and experience_formset.is_valid():
            # Check if candidate already exists by CPF to prevent duplicates
            cpf = form.cleaned_data.get('cpf')
            existing_candidate = None
            if cpf:
                try:
                    existing_candidate = Candidate.objects.get(cpf=cpf)
                except Candidate.DoesNotExist:
                    pass
            
            if existing_candidate:
                # Update existing candidate instead of creating a new one
                candidate = existing_candidate
                for field, value in form.cleaned_data.items():
                    setattr(candidate, field, value)
            else:
                # Create new candidate
                candidate = form.save(commit=False)
            
            # Set WhatsApp opt-in date if opted in
            if candidate.whatsapp_opt_in and not candidate.whatsapp_opt_in_date:
                candidate.whatsapp_opt_in_date = timezone.now()
            
            candidate.save()
            
            # Save professional experiences
            experiences = experience_formset.save(commit=False)
            for experience in experiences:
                experience.candidate = candidate
                experience.save()
            
            # Handle multiple work card file uploads
            work_card_files = request.FILES.getlist('work_cards')
            for work_card_file in work_card_files:
                WorkCard.objects.create(
                    candidate=candidate,
                    file=work_card_file
                )
            
            # Handle questionnaire submission (supports multiple questionnaires)
            questionnaire_answers = request.POST.get('questionnaire_answers')
            print(f"DEBUG: questionnaire_answers raw value: {questionnaire_answers}")
            
            if questionnaire_answers:
                try:
                    answers_data = json.loads(questionnaire_answers)
                    print(f"DEBUG: Parsed answers_data: {answers_data}")
                    print(f"DEBUG: Type of answers_data: {type(answers_data)}")
                    
                    if answers_data and isinstance(answers_data, list):
                        # Submit each questionnaire via internal API
                        from .api_views.questionnaire_views import CandidateQuestionnaireResponseViewSet
                        from rest_framework.request import Request
                        from django.http import HttpRequest
                        
                        print(f"DEBUG: Processing {len(answers_data)} questionnaire responses")
                        
                        # Process each questionnaire response
                        for idx, questionnaire_response in enumerate(answers_data):
                            print(f"DEBUG: Processing questionnaire {idx}: {questionnaire_response}")
                            template_id = questionnaire_response.get('template_id')
                            answers = questionnaire_response.get('answers', [])
                            
                            print(f"DEBUG: template_id={template_id}, answers count={len(answers)}")
                            
                            if template_id and answers:
                                submission_data = {
                                    'candidate_id': candidate.id,
                                    'template_id': int(template_id),
                                    'answers': answers
                                }
                                
                                print(f"DEBUG: submission_data={submission_data}")
                                
                                # Create a proper DRF request with data
                                from io import BytesIO
                                mock_request = HttpRequest()
                                mock_request.method = 'POST'
                                mock_request.META['CONTENT_TYPE'] = 'application/json'
                                mock_request._body = json.dumps(submission_data).encode('utf-8')
                                mock_request._stream = BytesIO(mock_request._body)
                                
                                drf_request = Request(mock_request)
                                drf_request._full_data = submission_data
                                
                                viewset = CandidateQuestionnaireResponseViewSet()
                                viewset.request = drf_request
                                
                                try:
                                    result = viewset.submit(drf_request)
                                    print(f"DEBUG: Successfully submitted questionnaire {template_id} for candidate {candidate.id}")
                                    print(f"DEBUG: Result status: {result.status_code}")
                                except Exception as e:
                                    # Log error but don't block candidate submission
                                    print(f"ERROR: Failed to submit questionnaire {template_id}: {e}")
                                    import traceback
                                    traceback.print_exc()
                            else:
                                print(f"DEBUG: Skipping questionnaire {idx} - missing template_id or answers")
                    else:
                        print(f"DEBUG: answers_data is not a list or is empty")
                except json.JSONDecodeError as e:
                    # Log error but don't block candidate submission
                    print(f"ERROR: JSON decode error: {e}")
                    print(f"ERROR: Raw questionnaire_answers: {questionnaire_answers}")
                    import traceback
                    traceback.print_exc()
                except Exception as e:
                    # Log error but don't block candidate submission
                    print(f"ERROR: Unexpected error processing questionnaire: {e}")
                    print(f"ERROR: Type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
            else:
                print("DEBUG: No questionnaire_answers in POST data")
            
            # Calculate and persist the candidate's score after submission
            try:
                candidate.calculate_score()
                candidate.save(update_fields=['score', 'score_breakdown', 'score_updated_at'])
            except Exception as e:
                # Log error but don't block candidate submission
                print(f"Error calculating score after application submission: {e}")
            
            # Store access code in session to display on success page
            request.session['access_code'] = candidate.access_code
            messages.success(
                request,
                f'Obrigado pela sua candidatura, {candidate.get_full_name()}! '
                'Analisaremos sua inscrição e entraremos em contato em breve.'
            )
            return redirect('application_success')
        else:
            pass
    else:
        form = CandidateApplicationForm()
        # For new applications, use helper function to ensure empty formset
        experience_formset = get_empty_experience_formset(prefix='experiences')
    
    return render(request, 'candidate/application_form.html', {
        'form': form,
        'experience_formset': experience_formset,
        'selected_position': selected_position,
        'total_steps': request.session.get('total_steps', 2),
        'current_step': 2,  # Step 2 in the overall flow (after position selection)
    })


def application_success_view(request):
    """
    Success page after submitting an application.
    """
    # Get the access code from session if available
    access_code = request.session.get('access_code', None)
    context = {'access_code': access_code}
    # Clear the access code from session after displaying
    if 'access_code' in request.session:
        del request.session['access_code']
    return render(request, 'candidate/application_success.html', context)


def candidate_login_view(request):
    """
    Login page for candidates to check their application status using CPF only.
    """
    if request.method == 'POST':
        cpf_input = request.POST.get('cpf', '').strip()

        # Normalize CPF to digits only and format as xxx.xxx.xxx-xx if length is 11
        digits = ''.join(filter(str.isdigit, cpf_input))
        formatted_cpf = cpf_input
        if len(digits) == 11:
            formatted_cpf = f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

        # Try to find candidate by CPF (formatted) and fallback to raw input
        try:
            candidate = Candidate.objects.get(cpf=formatted_cpf)
        except Candidate.DoesNotExist:
            try:
                candidate = Candidate.objects.get(cpf=cpf_input)
            except Candidate.DoesNotExist:
                candidate = None

        if candidate:
            request.session['candidate_id'] = candidate.id
            return redirect('candidate_status')
        else:
            messages.error(request, 'CPF não encontrado. Verifique e tente novamente.')
    
    return render(request, 'candidate/login.html')


def candidate_status_view(request):
    """
    Status page showing candidate's application progress.
    """
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        messages.warning(request, 'Por favor, faça login para ver o status da sua candidatura.')
        return redirect('candidate_login')
    
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    # Get scheduled interviews for this candidate
    from .models import Interview
    from datetime import datetime
    
    scheduled_interviews = Interview.objects.filter(
        candidate=candidate,
        status='scheduled',
        scheduled_date__gte=datetime.now().date()
    ).order_by('scheduled_date', 'scheduled_time')
    
    # Status progress mapping
    status_steps = {
        'pending': {'step': 1, 'label': 'Pendente', 'description': 'Sua candidatura foi recebida e está aguardando análise.'},
        'reviewing': {'step': 2, 'label': 'Em Análise', 'description': 'Nossa equipe está analisando sua candidatura.'},
        'shortlisted': {'step': 3, 'label': 'Selecionado para Entrevista', 'description': 'Parabéns! Você foi selecionado para entrevista.'},
        'interviewed': {'step': 4, 'label': 'Entrevistado', 'description': 'Você foi entrevistado. Aguarde o resultado final.'},
        'accepted': {'step': 5, 'label': 'Aceito', 'description': 'Parabéns! Sua candidatura foi aceita.'},
        'rejected': {'step': 5, 'label': 'Não Selecionado', 'description': 'Infelizmente, sua candidatura não foi selecionada desta vez.'},
    }
    
    current_status = status_steps.get(candidate.status, status_steps['pending'])
    
    context = {
        'candidate': candidate,
        'current_status': current_status,
        'status_steps': status_steps,
        'scheduled_interviews': scheduled_interviews,
    }
    
    return render(request, 'candidate/status.html', context)


def candidate_edit_view(request):
    """
    Allow the logged-in candidate to edit their submitted application data.
    """
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        messages.warning(request, 'Por favor, faça login para editar seus dados.')
        return redirect('candidate_login')

    candidate = get_object_or_404(Candidate, id=candidate_id)

    # Require password authentication if a password is set
    session_key = f'candidate_edit_ok_{candidate.id}'
    print(f"DEBUG - Candidate ID: {candidate.id}")
    print(f"DEBUG - Has password_hash: {bool(candidate.password_hash)}")
    print(f"DEBUG - Session key: {session_key}")
    print(f"DEBUG - Session has key: {request.session.get(session_key)}")
    print(f"DEBUG - Should ask for password: {candidate.password_hash and not request.session.get(session_key)}")
    
    if candidate.password_hash and not request.session.get(session_key):
        # If posted password from auth form
        if request.method == 'POST' and request.POST.get('form_type') == 'auth':
            provided = request.POST.get('auth_password', '')
            if provided and check_password(provided, candidate.password_hash):
                request.session[session_key] = True
                messages.success(request, 'Autenticação confirmada. Você pode editar seus dados.')
                return redirect('candidate_edit')
            else:
                messages.error(request, 'Senha incorreta. Tente novamente.')
        return render(request, 'candidate/confirm_password.html', {})

    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, request.FILES, instance=candidate)
        experience_formset = ProfessionalExperienceFormSet(request.POST, prefix='experiences', instance=candidate)

        if form.is_valid() and experience_formset.is_valid():
            # Check if password was changed
            old_password_hash = candidate.password_hash
            
            candidate = form.save(commit=False)

            # Set WhatsApp opt-in date if opted in for the first time
            if candidate.whatsapp_opt_in and not candidate.whatsapp_opt_in_date:
                candidate.whatsapp_opt_in_date = timezone.now()

            candidate.save()

            experiences = experience_formset.save(commit=False)
            # Attach candidate and save new/changed experiences
            for experience in experiences:
                experience.candidate = candidate
                experience.save()
            # Handle deletions
            for deleted in experience_formset.deleted_objects:
                deleted.delete()

            # Handle multiple work card file uploads
            work_card_files = request.FILES.getlist('work_cards')
            for work_card_file in work_card_files:
                WorkCard.objects.create(
                    candidate=candidate,
                    file=work_card_file
                )

            # If password was changed, clear the session authentication flag
            print(f"DEBUG - Old password hash: {old_password_hash}")
            print(f"DEBUG - New password hash: {candidate.password_hash}")
            print(f"DEBUG - Password changed: {old_password_hash != candidate.password_hash}")
            
            if old_password_hash != candidate.password_hash:
                session_key = f'candidate_edit_ok_{candidate.id}'
                print(f"DEBUG - Clearing session key: {session_key}")
                if session_key in request.session:
                    del request.session[session_key]
                    request.session.modified = True  # Force session to be saved
                    print(f"DEBUG - Session key deleted and session marked as modified")
                messages.success(request, 'Seus dados foram atualizados com sucesso! Sua senha foi alterada.')
            else:
                messages.success(request, 'Seus dados foram atualizados com sucesso!')
            
            return redirect('candidate_status')
        else:
            # Show error message when form validation fails
            messages.error(request, 'Há erros no formulário. Por favor, corrija-os e tente novamente.')
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
            if experience_formset.errors:
                for i, form_errors in enumerate(experience_formset.errors):
                    if form_errors:
                        messages.error(request, f'Experiência {i+1}: {form_errors}')
    else:
        form = CandidateApplicationForm(instance=candidate)
        experience_formset = ProfessionalExperienceFormSet(prefix='experiences', instance=candidate)

    return render(request, 'candidate/application_form.html', {
        'form': form,
        'experience_formset': experience_formset,
        'is_edit': True,
    })


def candidate_password_reset_request(request):
    """Step 1: Send OTP code via WhatsApp to candidate phone."""
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        messages.warning(request, 'Por favor, faça login para resetar sua senha.')
        return redirect('candidate_login')

    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        import random
        code = ''.join(random.choices('0123456789', k=6))
        expires_at = (timezone.now() + timedelta(minutes=10)).isoformat()
        request.session['pwd_reset'] = {
            'candidate_id': candidate.id,
            'code': code,
            'expires_at': expires_at,
            'attempts': 0,
        }
        request.session.modified = True

        message = (
            f"Código de verificação Pinte Pinturas: {code}\n"
            "Use este código em até 10 minutos para redefinir sua senha."
        )
        send_result = send_text_to_phone(candidate.phone_number, message)
        if not send_result.get('success'):
            messages.error(request, f"Falha ao enviar código pelo WhatsApp: {send_result.get('error') or send_result}")
        else:
            messages.success(request, 'Enviamos um código via WhatsApp para seu número cadastrado.')
        return redirect('candidate_password_reset_verify')

    # Mask phone for display to avoid exposing full number
    masked = '(**) *****-**'  # default masked pattern
    try:
        digits = ''.join(filter(str.isdigit, candidate.phone_number))
        tail = digits[-2:] if len(digits) >= 2 else ''
        masked = f"(**) *****-**{tail}"
    except Exception:
        pass

    return render(request, 'candidate/password_reset_request.html', {
        'candidate': candidate,
        'masked_phone': masked,
    })


def candidate_password_reset_verify(request):
    """Step 2: Verify OTP and set new password."""
    data = request.session.get('pwd_reset') or {}
    candidate_id = data.get('candidate_id') or request.session.get('candidate_id')
    if not candidate_id:
        messages.warning(request, 'Sessão expirada. Faça login novamente.')
        return redirect('candidate_login')

    candidate = get_object_or_404(Candidate, id=candidate_id)

    if request.method == 'POST':
        code_input = (request.POST.get('code') or '').strip()
        new_password = request.POST.get('new_password') or ''
        new_password2 = request.POST.get('new_password2') or ''

        # Basic validation
        if not code_input:
            messages.error(request, 'Informe o código recebido no WhatsApp.')
        elif not new_password or not new_password2:
            messages.error(request, 'Informe e confirme a nova senha.')
        elif new_password != new_password2:
            messages.error(request, 'As senhas não coincidem.')
        else:
            # Validate code
            stored = request.session.get('pwd_reset')
            if not stored or stored.get('candidate_id') != candidate.id:
                messages.error(request, 'Código inválido ou sessão expirada.')
                return redirect('candidate_password_reset_request')
            # Expiry
            try:
                expires_at = timezone.datetime.fromisoformat(stored.get('expires_at'))
                if timezone.now() > expires_at:
                    messages.error(request, 'Código expirado. Solicite um novo código.')
                    return redirect('candidate_password_reset_request')
            except Exception:
                pass
            # Attempts
            attempts = int(stored.get('attempts') or 0)
            if attempts >= 5:
                messages.error(request, 'Muitas tentativas. Solicite um novo código.')
                return redirect('candidate_password_reset_request')
            if code_input != stored.get('code'):
                stored['attempts'] = attempts + 1
                request.session['pwd_reset'] = stored
                request.session.modified = True
                messages.error(request, 'Código incorreto. Tente novamente.')
            else:
                # Set new password
                candidate.password_hash = make_password(new_password)
                candidate.save(update_fields=['password_hash'])
                # Clear session flags to require new auth
                session_key = f'candidate_edit_ok_{candidate.id}'
                if session_key in request.session:
                    del request.session[session_key]
                if 'pwd_reset' in request.session:
                    del request.session['pwd_reset']
                request.session.modified = True
                messages.success(request, 'Senha redefinida com sucesso! Faça a confirmação novamente para continuar.')
                return redirect('candidate_edit')

    return render(request, 'candidate/password_reset_verify.html', {
        'candidate': candidate,
    })


def candidate_logout_view(request):
    """
    Logout candidate from status tracking.
    """
    if 'candidate_id' in request.session:
        del request.session['candidate_id']
    messages.success(request, 'Você saiu com sucesso.')
    return redirect('candidate_login')


class CandidateApplicationCreateView(CreateView):
    """
    Class-based view for creating candidate applications.
    """
    model = Candidate
    form_class = CandidateApplicationForm
    template_name = 'candidate/application_form.html'
    success_url = reverse_lazy('application_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Thank you for your application, {self.object.get_full_name()}! '
            'We will review your submission and get back to you soon.'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'There were some errors in your application. Please check the form and try again.'
        )
        return super().form_invalid(form)
