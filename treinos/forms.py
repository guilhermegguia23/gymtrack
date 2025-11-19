from django import forms
from django.forms import inlineformset_factory

from .models import Aluno, Exercicio, FichaExercicio, FichaTreino


class DateInput(forms.DateInput):
    input_type = "date"


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
            "grupo_muscular": forms.TextInput(attrs={"class": "form-control"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class FichaTreinoForm(forms.ModelForm):
    class Meta:
        model = FichaTreino
        fields = ["aluno", "observacoes"]
        widgets = {"observacoes": forms.Textarea(attrs={"rows": 3})}


class FichaExercicioForm(forms.ModelForm):
    class Meta:
        model = FichaExercicio
        fields = ["exercicio", "series", "repeticoes", "ordem"]


FichaExercicioFormSet = inlineformset_factory(
    FichaTreino,
    FichaExercicio,
    form=FichaExercicioForm,
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=False,
)
