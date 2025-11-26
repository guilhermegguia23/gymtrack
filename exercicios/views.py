from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from exercicios.forms import ExercicioForm
from treinos.models import Exercicio
from treinos.utils import bloquear_para_aluno, listar_grupos_musculares, ordenar_e_paginar


@login_required
@bloquear_para_aluno
def lista_exercicios(request: HttpRequest) -> HttpResponse:
    sortable_fields = ("nome", "grupo_muscular")
    page_obj, sort_field, direction = ordenar_e_paginar(
        request,
        Exercicio.objects.all(),
        sortable_fields,
        "nome",
        per_page=12,
    )
    sort_options = {field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields}
    return render(
        request,
        "exercicios/lista.html",
        {
            "page_obj": page_obj,
            "exercicios": page_obj.object_list,
            "current_sort": sort_field,
            "current_direction": direction,
            "sort_options": sort_options,
        },
    )


@login_required
@bloquear_para_aluno
def exercicio_create(request: HttpRequest) -> HttpResponse:
    form = ExercicioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Exercicio salvo com sucesso."))
        return redirect("treinos:lista_exercicios")
    return render(request, "exercicios/form.html", {"form": form, "grupos_musculares": listar_grupos_musculares()})


@login_required
@bloquear_para_aluno
def exercicio_update(request: HttpRequest, pk: int) -> HttpResponse:
    exercicio = get_object_or_404(Exercicio, pk=pk)
    form = ExercicioForm(request.POST or None, instance=exercicio)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Exercicio atualizado."))
        return redirect("treinos:lista_exercicios")
    return render(
        request,
        "exercicios/form.html",
        {"form": form, "exercicio": exercicio, "grupos_musculares": listar_grupos_musculares()},
    )


@login_required
@bloquear_para_aluno
def exercicio_delete(request: HttpRequest, pk: int) -> HttpResponse:
    exercicio = get_object_or_404(Exercicio, pk=pk)
    if request.method == "POST":
        exercicio.delete()
        messages.success(request, _("Exercicio removido."))
        return redirect("treinos:lista_exercicios")
    return render(request, "exercicios/confirm_delete.html", {"exercicio": exercicio})
