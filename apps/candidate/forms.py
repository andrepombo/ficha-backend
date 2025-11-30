from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.hashers import make_password
from .models import Candidate, ProfessionalExperience, WorkCard


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget to handle multiple file uploads."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field to handle multiple file uploads."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CandidateApplicationForm(forms.ModelForm):
    """
    Form for candidates to submit their job application.
    """
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Mín. 8 caracteres, com maiúscula, minúscula e número'
    )
    confirm_password = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    work_cards = MultipleFileField(
        label='Carteira de Trabalho',
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.bmp,.tiff,.txt,.rtf,.odt,.xls,.xlsx'
        }),
        help_text='Você pode selecionar múltiplos arquivos. Formatos aceitos: PDF, DOC, DOCX, JPG, PNG, GIF, BMP, TIFF, TXT, RTF, ODT, XLS, XLSX'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom error messages in Portuguese
        self.fields['full_name'].error_messages = {
            'required': 'Por favor, informe seu nome completo.',
            'max_length': 'O nome completo não pode ter mais de 200 caracteres.',
        }
        self.fields['cpf'].error_messages = {
            'required': 'Por favor, informe seu CPF.',
            'invalid': 'Por favor, informe um CPF válido no formato xxx.xxx.xxx-xx',
        }
        self.fields['email'].error_messages = {
            'invalid': 'Por favor, informe um email válido.',
        }
        self.fields['email'].required = False
        self.fields['phone_number'].error_messages = {
            'required': 'Por favor, informe seu telefone.',
            'invalid': 'Formato de telefone inválido. Use o formato: xx xxxxx-xxxx',
        }
        # Optional alternate phone
        if 'second_phone_number' in self.fields:
            self.fields['second_phone_number'].required = False
        # Make position_applied REQUIRED for questionnaire loading
        self.fields['position_applied'].required = True
        # Make years_of_experience optional
        self.fields['years_of_experience'].required = False
        self.fields['date_of_birth'].error_messages = {
            'required': 'Por favor, informe sua data de nascimento.',
            'invalid': 'Por favor, informe uma data válida.',
        }
        
        # Add empty option with placeholder for gender
        self.fields['gender'].empty_label = 'Selecione uma opção'
        
        # Add empty option with placeholder for disability
        self.fields['disability'].empty_label = 'Selecione uma opção'
        
        # Add empty option with placeholder for has_own_transportation
        self.fields['has_own_transportation'].empty_label = 'Selecione uma opção'
        
        # Add empty option with placeholder for referral fields
        self.fields['has_relatives_in_company'].empty_label = 'Selecione uma opção'
        self.fields['how_found_vacancy'].empty_label = 'Selecione uma opção'
        self.fields['worked_at_pinte_before'].empty_label = 'Selecione uma opção'
        
        # Add empty option with placeholder for education
        self.fields['highest_education'].empty_label = 'Selecione uma opção'
        
        # Add empty option with placeholder for extra information fields
        self.fields['currently_employed'].empty_label = 'Selecione uma opção'
        self.fields['availability_start'].empty_label = 'Selecione uma opção'
        self.fields['travel_availability'].empty_label = 'Selecione uma opção'
        self.fields['height_painting'].empty_label = 'Selecione uma opção'

        # Password requirements: required on create; optional on edit
        instance = getattr(self, 'instance', None)
        is_new = not instance or not getattr(instance, 'pk', None)
        if is_new:
            # New candidate: password is required
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True
        else:
            # Editing existing candidate: password is optional (only if changing it)
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
            # Also remove the required attribute from the widget
            self.fields['password'].widget.attrs.pop('required', None)
            self.fields['confirm_password'].widget.attrs.pop('required', None)
    
    class Meta:
        model = Candidate
        fields = [
            'full_name',
            'cpf',
            'email',
            'phone_number',
            'second_phone_number',
            'whatsapp_opt_in',
            'date_of_birth',
            'gender',
            'disability',
            'has_own_transportation',
            'address',
            'city',
            'state',
            'postal_code',
            'country',
            'position_applied',
            'current_company',
            'current_position',
            'years_of_experience',
            'has_relatives_in_company',
            'referred_by',
            'how_found_vacancy',
            'how_found_vacancy_other',
            'worked_at_pinte_before',
            'highest_education',
            'currently_employed',
            'availability_start',
            'travel_availability',
            'height_painting',
            'resume',
            'photo',
            'cover_letter',
            'skills',
            'certifications',
            'available_start_date',
            'expected_salary',
            # virtual fields (not in model):
            'password',
            'confirm_password',
        ]
        
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite seu nome completo'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123.456.789-01',
                'maxlength': '14'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu.email@exemplo.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '11 98765-4321',
                'maxlength': '13'
            }),
            'second_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '11 98765-4321',
                'maxlength': '13'
            }),
            'whatsapp_opt_in': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }),
            'disability': forms.Select(attrs={
                'class': 'form-control',
            }),
            'has_own_transportation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Endereço completo'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'CEP'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'País'
            }),
            'position_applied': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: Engenheiro de Software'
            }),
            'current_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Empregador atual (opcional)'
            }),
            'current_position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo atual (opcional)'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'has_relatives_in_company': forms.Select(attrs={
                'class': 'form-control',
            }),
            'referred_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da pessoa que indicou'
            }),
            'how_found_vacancy': forms.Select(attrs={
                'class': 'form-control',
            }),
            'how_found_vacancy_other': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especifique aqui'
            }),
            'worked_at_pinte_before': forms.Select(attrs={
                'class': 'form-control',
            }),
            'highest_education': forms.Select(attrs={
                'class': 'form-control',
            }),
            'currently_employed': forms.Select(attrs={
                'class': 'form-control',
            }),
            'availability_start': forms.Select(attrs={
                'class': 'form-control',
            }),
            'travel_availability': forms.Select(attrs={
                'class': 'form-control',
            }),
            'height_painting': forms.Select(attrs={
                'class': 'form-control',
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Conte-nos por que você é ideal para esta posição...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ex: Pintura residencial, Pintura industrial, Textura, Grafiato, Aplicação de verniz, Lixamento'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Liste suas certificações (opcional)'
            }),
            'available_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expected_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Expectativa salarial anual',
                'step': '0.01'
            }),
        }
        
        labels = {
            'full_name': 'Nome Completo *',
            'cpf': 'CPF *',
            'email': 'Endereço de Email',
            'phone_number': 'Telefone *',
            'second_phone_number': 'Telefone alternativo',
            'date_of_birth': 'Data de Nascimento *',
            'gender': 'Sexo',
            'disability': 'Possui deficiência? (PCD)',
            'has_own_transportation': 'Possui transporte próprio?',
            'address': 'Endereço',
            'city': 'Cidade',
            'state': 'Estado',
            'postal_code': 'CEP',
            'country': 'País',
            'position_applied': 'Cargo Pretendido *',
            'current_company': 'Empresa Atual',
            'current_position': 'Cargo Atual',
            'years_of_experience': 'Anos de Experiência *',
            'has_relatives_in_company': 'Possui parentes ou amigos na empresa?',
            'referred_by': 'Indicado Por',
            'how_found_vacancy': 'Como ficou sabendo da vaga?',
            'how_found_vacancy_other': 'Outros - Especificar',
            'worked_at_pinte_before': 'Já trabalhou na Pinte Pinturas antes?',
            'highest_education': 'Escolaridade',
            'currently_employed': 'Atualmente empregado',
            'availability_start': 'Disponibilidade para início',
            'travel_availability': 'Disponibilidade para viagens',
            'height_painting': 'Faz pintura em altura? Balancim/Cadeirinha/Andaimes',
            'resume': 'Currículo',
            'photo': 'Foto do Candidato',
            'cover_letter': 'Carta de Apresentação',
            'skills': 'Habilidades',
            'certifications': 'Certificações',
            'available_start_date': 'Data de Início',
            'expected_salary': 'Salário Esperado (Anual)',
        }

    def clean(self):
        cleaned = super().clean()
        
        # Get password values before removing them, defaulting to empty string if not present
        pwd = cleaned.get('password') or ''
        cpwd = cleaned.get('confirm_password') or ''
        
        # Strip whitespace
        pwd = pwd.strip() if pwd else ''
        cpwd = cpwd.strip() if cpwd else ''
        
        # Only validate passwords if they're required (new candidate) or if user is actively providing them
        # Check if password is required OR if user actually entered something (not just empty strings)
        if self.fields['password'].required:
            # New candidate - password is required
            if not pwd:
                self.add_error('password', 'Informe a senha.')
            if not cpwd:
                self.add_error('confirm_password', 'Confirme a senha.')
        elif pwd or cpwd:
            # Editing - user is trying to change password, so both fields must be filled
            if not pwd:
                self.add_error('password', 'Informe a senha.')
            if not cpwd:
                self.add_error('confirm_password', 'Confirme a senha.')
        
        # Validate password match if both provided
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', 'As senhas não coincidem.')
            
        # Strong password rules - only if password is provided
        if pwd:
            if len(pwd) < 8:
                self.add_error('password', 'A senha deve ter ao menos 8 caracteres.')
            if not any(c.islower() for c in pwd):
                self.add_error('password', 'A senha deve conter ao menos uma letra minúscula.')
            if not any(c.isupper() for c in pwd):
                self.add_error('password', 'A senha deve conter ao menos uma letra maiúscula.')
            if not any(c.isdigit() for c in pwd):
                self.add_error('password', 'A senha deve conter ao menos um número.')
        
        # Store password values for use in save() before removing from cleaned_data
        self._password = pwd if pwd else None
        self._confirm_password = cpwd if cpwd else None
        
        # Remove virtual fields from cleaned_data AFTER validation
        # This prevents Django from trying to assign them to the model during save()
        virtual_fields = ['work_cards', 'password', 'confirm_password']
        for field in virtual_fields:
            cleaned.pop(field, None)
        
        return cleaned

    def save(self, commit=True):
        obj: Candidate = super().save(commit=False)
        # Use stored password values from clean()
        pwd = getattr(self, '_password', None)
        cpwd = getattr(self, '_confirm_password', None)
        if pwd and cpwd and pwd == cpwd:
            obj.password_hash = make_password(pwd)
        
        # Note: work_cards is handled separately in the view, not here
        # It's a virtual field for file upload, not a model field
        
        if commit:
            obj.save()
        return obj


class ProfessionalExperienceForm(forms.ModelForm):
    """
    Form for professional experience entries.
    """
    class Meta:
        model = ProfessionalExperience
        fields = ['empresa', 'cargo', 'descricao_atividades', 'data_admissao', 'data_desligamento', 'motivo_saida']
        widgets = {
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da empresa',
                'autocomplete': 'off'
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo ocupado',
                'autocomplete': 'off'
            }),
            'descricao_atividades': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descreva as principais atividades realizadas',
                'autocomplete': 'off'
            }),
            'data_admissao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'autocomplete': 'off'
            }),
            'data_desligamento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'autocomplete': 'off'
            }),
            'motivo_saida': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explique o motivo da saída',
                'autocomplete': 'off'
            }),
        }
        labels = {
            'empresa': 'Empresa',
            'cargo': 'Cargo',
            'descricao_atividades': 'Descrição das Atividades',
            'data_admissao': 'Data de Admissão',
            'data_desligamento': 'Data de Desligamento',
            'motivo_saida': 'Motivo da saída',
        }


# Create a formset for professional experiences
ProfessionalExperienceFormSet = inlineformset_factory(
    Candidate,
    ProfessionalExperience,
    form=ProfessionalExperienceForm,
    extra=1,  # Number of empty forms to display
    can_delete=True,  # Allow deletion of experiences
    min_num=0,  # Minimum number of experiences required
    validate_min=False,
    max_num=10,  # Maximum number of experiences
    validate_max=False,
)


def get_empty_experience_formset(prefix='experiences', data=None):
    """
    Helper function to create a completely empty experience formset for new applications.
    This ensures no data leakage from other candidates.
    """
    # Create a temporary unsaved candidate instance
    temp_candidate = Candidate()
    
    if data:
        formset = ProfessionalExperienceFormSet(
            data,
            instance=temp_candidate,
            prefix=prefix,
            queryset=ProfessionalExperience.objects.none()
        )
    else:
        formset = ProfessionalExperienceFormSet(
            instance=temp_candidate,
            prefix=prefix,
            queryset=ProfessionalExperience.objects.none()
        )
    
    return formset
