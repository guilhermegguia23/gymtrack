from django import forms
from django.forms import inlineformset_factory

from treinos.models import FichaTreino, Treino, TreinoExercicio


class FichaTreinoForm(forms.ModelForm):
    class Meta:
        model = FichaTreino
        fields = ["nome", "motivo", "aluno", "observacoes", "ativa"]
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
        labels = {"repeticoes": "Repeticoes"}


TreinoExercicioFormSet = inlineformset_factory(
    Treino,
    TreinoExercicio,
    form=TreinoExercicioForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
