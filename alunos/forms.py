from django import forms

from treinos.models import Aluno


class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
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
