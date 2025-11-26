from __future__ import annotations

from datetime import date
from functools import wraps

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from treinos.models import Aluno, Exercicio, FichaTreino, Treino, TreinoDiario, TreinoProgresso


def usuario_eh_aluno(user) -> bool:
    if not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return False
    return user.groups.filter(name="aluno").exists()


def bloquear_para_aluno(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs):
        if usuario_eh_aluno(request.user):
            messages.error(request, _("Voce nao tem permissao para acessar este modulo."))
            return redirect("treinos:treino_do_dia")
        return view_func(request, *args, **kwargs)

    return _wrapped


def obter_aluno_logado(user) -> Aluno | None:
    if not user.is_authenticated:
        return None
    email = user.email or user.username
    if not email:
        return None
    try:
        return Aluno.objects.get(email__iexact=email)
    except Aluno.DoesNotExist:
        return None


def preparar_progresso(treino_diario: TreinoDiario) -> None:
    for treino_exercicio in treino_diario.treino.exercicios.all():
        TreinoProgresso.objects.get_or_create(
            treino_diario=treino_diario,
            exercicio=treino_exercicio.exercicio,
        )


def selecionar_treino_do_dia(aluno: Aluno) -> Treino | None:
    ficha = (
        FichaTreino.objects.filter(aluno=aluno, ativa=True)
        .order_by("-data_criacao")
        .prefetch_related("treinos")
        .first()
    )
    if not ficha:
        return None
    if not ficha.treinos.exists():
        treino = Treino.objects.create(ficha=ficha, nome="A", ordem=1)
        return treino

    ultimo = (
        TreinoDiario.objects.filter(aluno=aluno)
        .select_related("treino", "treino__ficha")
        .order_by("-data")
        .first()
    )
    if not ultimo or ultimo.treino.ficha_id != ficha.id:
        return ficha.treinos.order_by("ordem").first()

    prox = ficha.treinos.filter(ordem__gt=ultimo.treino.ordem).order_by("ordem").first()
    return prox or ficha.treinos.order_by("ordem").first()


def listar_grupos_musculares() -> list[str]:
    return list(
        Exercicio.objects.order_by("grupo_muscular")
        .values_list("grupo_muscular", flat=True)
        .distinct()
    )


def ordenar_e_paginar(
    request: HttpRequest,
    queryset,
    allowed_fields: tuple[str, ...],
    default_field: str,
    *,
    default_direction: str = "asc",
    per_page: int = 10,
):
    from django.core.paginator import Paginator

    sort_field = request.GET.get("ordenar") or default_field
    if sort_field not in allowed_fields:
        sort_field = default_field

    direction = request.GET.get("direcao") or default_direction
    if direction not in {"asc", "desc"}:
        direction = default_direction

    ordering = sort_field if direction == "asc" else f"-{sort_field}"
    paginator = Paginator(queryset.order_by(ordering), per_page)
    page_obj = paginator.get_page(request.GET.get("page"))
    return page_obj, sort_field, direction
