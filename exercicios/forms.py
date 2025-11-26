from django import forms

from treinos.models import Exercicio


class ExercicioForm(forms.ModelForm):
    class Meta:
        model = Exercicio
        fields = ["nome", "grupo_muscular", "descricao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control"}),
            "grupo_muscular": forms.TextInput(attrs={"class": "form-control", "list": "grupos-musculares"}),
            "descricao": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }
