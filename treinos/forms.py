from django import forms
from django.forms import inlineformset_factory

from .models import Aluno, Exercicio, FichaTreino, Treino, TreinoExercicio


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        # Ensure HTML date inputs render in ISO format so initial values appear.
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(*args, **kwargs)


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ["nome", "email", "data_nascimento", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "data_nascimento": DateInput(attrs={"class": "form-control"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ExercicioForm(forms.ModelForm):
    class Meta:
        model = Exercicio
        fields = ["nome", "grupo_muscular", "descricao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "grupo_muscular": forms.TextInput(attrs={"class": "form-control", "list": "grupos-musculares"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class FichaTreinoForm(forms.ModelForm):
    class Meta:
        model = FichaTreino
        fields = ["nome", "motivo","aluno", "observacoes", "ativa"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "motivo": forms.TextInput(attrs={"class": "form-control", "list": "grupos-musculares"}),
            "aluno": forms.Select(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "ativa": forms.CheckboxInput(attrs={"class": "form-check-input mt-0"}),
        }


class TreinoForm(forms.ModelForm):
    class Meta:
        model = Treino
        fields = ["nome", "ordem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "A, B, C..."}),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


class TreinoExercicioForm(forms.ModelForm):
    class Meta:
        model = TreinoExercicio
        fields = ["exercicio", "series", "repeticoes", "ordem"]
        widgets = {
            "exercicio": forms.Select(attrs={"class": "form-control"}),
            "series": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "repeticoes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }
        labels = {"repeticoes": "Repetições"}


class PerfilAlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ["nome", "email"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


class TrocaSenhaForm(forms.Form):
    senha_atual = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    nova_senha = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


TreinoExercicioFormSet = inlineformset_factory(
    Treino,
    TreinoExercicio,
    form=TreinoExercicioForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
