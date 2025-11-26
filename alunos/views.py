from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from alunos.forms import AlunoForm, PerfilAlunoForm
from treinos.models import Aluno
from treinos.utils import bloquear_para_aluno, obter_aluno_logado, ordenar_e_paginar


@login_required
@bloquear_para_aluno
def lista_alunos(request: HttpRequest) -> HttpResponse:
    sortable_fields = ("nome", "email", "data_nascimento", "ativo")
    page_obj, sort_field, direction = ordenar_e_paginar(
        request,
        Aluno.objects.all(),
        sortable_fields,
        "nome",
        per_page=12,
    )
    sort_options = {field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields}
    return render(
        request,
        "alunos/lista.html",
        {
            "page_obj": page_obj,
            "alunos": page_obj.object_list,
            "current_sort": sort_field,
            "current_direction": direction,
            "sort_options": sort_options,
        },
    )


@login_required
@bloquear_para_aluno
def aluno_create(request: HttpRequest) -> HttpResponse:
    form = AlunoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Aluno salvo com sucesso."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/form.html", {"form": form})


@login_required
@bloquear_para_aluno
def aluno_update(request: HttpRequest, pk: int) -> HttpResponse:
    aluno = get_object_or_404(Aluno, pk=pk)
    form = AlunoForm(request.POST or None, instance=aluno)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Aluno atualizado com sucesso."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/form.html", {"form": form, "aluno": aluno})


@login_required
@bloquear_para_aluno
def aluno_delete(request: HttpRequest, pk: int) -> HttpResponse:
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == "POST":
        aluno.delete()
        messages.success(request, _("Aluno removido."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/confirm_delete.html", {"aluno": aluno})


@login_required
def perfil(request: HttpRequest) -> HttpResponse:
    aluno = obter_aluno_logado(request.user)
    form = PerfilAlunoForm(request.POST or None, instance=aluno) if aluno else None

    if request.method == "POST":
        if not aluno:
            messages.error(request, _("Perfil disponivel apenas para alunos."))
        elif form and form.is_valid():
            form.save()
            messages.success(request, _("Perfil atualizado com sucesso."))
            return redirect("treinos:perfil")

    return render(request, "perfil.html", {"form": form, "aluno": aluno})
