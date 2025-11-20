from django import forms
from django.forms import inlineformset_factory

from .models import Aluno, Exercicio, FichaExercicio, FichaTreino


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
        fields = ["aluno", "observacoes"]
        widgets = {
            "aluno": forms.Select(attrs={"class": "form-control"}),
            "observacoes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class FichaExercicioForm(forms.ModelForm):
    class Meta:
        model = FichaExercicio
        fields = ["exercicio", "series", "repeticoes", "ordem"]
        widgets = {
            "exercicio": forms.Select(attrs={"class": "form-control"}),
            "series": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "repeticoes": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "ordem": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


FichaExercicioFormSet = inlineformset_factory(
    FichaTreino,
    FichaExercicio,
    form=FichaExercicioForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
