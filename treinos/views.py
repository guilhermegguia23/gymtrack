from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import (
    AlunoForm,
    ExercicioForm,
    FichaExercicioFormSet,
    FichaTreinoForm,
)
from .models import (
    Aluno,
    Exercicio,
    FichaTreino,
    TreinoDiario,
    TreinoProgresso,
)


@login_required
def lista_alunos(request: HttpRequest) -> HttpResponse:
    # Renderiza a tabela de alunos com ordenacao e paginacao configuraveis.
    sortable_fields = ("nome", "email", "data_nascimento", "ativo")
    page_obj, sort_field, direction = _ordenar_e_paginar(
        request,
        Aluno.objects.all(),
        sortable_fields,
        "nome",
        per_page=12,
    )
    sort_options = {
        field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields
    }
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
def aluno_create(request: HttpRequest) -> HttpResponse:
    # Trata o formulario de cadastro de aluno exibindo mensagens de feedback.
    form = AlunoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Aluno salvo com sucesso."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/form.html", {"form": form})


@login_required
def aluno_update(request: HttpRequest, pk: int) -> HttpResponse:
    # Permite editar dados do aluno selecionado reutilizando o mesmo form.
    aluno = get_object_or_404(Aluno, pk=pk)
    form = AlunoForm(request.POST or None, instance=aluno)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Aluno atualizado com sucesso."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/form.html", {"form": form, "aluno": aluno})


@login_required
def aluno_delete(request: HttpRequest, pk: int) -> HttpResponse:
    # Exibe a confirmacao e remove o aluno escolhido.
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == "POST":
        aluno.delete()
        messages.success(request, _("Aluno removido."))
        return redirect("treinos:lista_alunos")
    return render(request, "alunos/confirm_delete.html", {"aluno": aluno})


@login_required
def lista_exercicios(request: HttpRequest) -> HttpResponse:
    # Lista todos os exercicios em formato tabular com ordenacao dinamica.
    sortable_fields = ("nome", "grupo_muscular")
    page_obj, sort_field, direction = _ordenar_e_paginar(
        request,
        Exercicio.objects.all(),
        sortable_fields,
        "nome",
        per_page=12,
    )
    sort_options = {
        field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields
    }
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
def exercicio_create(request: HttpRequest) -> HttpResponse:
    # Cria um novo exercicio e retorna mensagens de resultado da operacao.
    form = ExercicioForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Exercício salvo com sucesso."))
        return redirect("treinos:lista_exercicios")
    return render(request, "exercicios/form.html", {"form": form})


@login_required
def exercicio_update(request: HttpRequest, pk: int) -> HttpResponse:
    # Atualiza um exercicio existente mantendo o historico.
    exercicio = get_object_or_404(Exercicio, pk=pk)
    form = ExercicioForm(request.POST or None, instance=exercicio)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Exercício atualizado."))
        return redirect("treinos:lista_exercicios")
    return render(request, "exercicios/form.html", {"form": form, "exercicio": exercicio})


@login_required
def exercicio_delete(request: HttpRequest, pk: int) -> HttpResponse:
    # Confirma e exclui um exercicio da base.
    exercicio = get_object_or_404(Exercicio, pk=pk)
    if request.method == "POST":
        exercicio.delete()
        messages.success(request, _("Exercício removido."))
        return redirect("treinos:lista_exercicios")
    return render(request, "exercicios/confirm_delete.html", {"exercicio": exercicio})


@login_required
def criar_ficha(request: HttpRequest) -> HttpResponse:
    # Organiza o fluxo de criacao de fichas e itens relacionados usando formset.
    if not Exercicio.objects.exists():
        messages.warning(request, _("Nenhum exercício cadastrado. Cadastre exercícios antes de prosseguir."))
        return render(
            request,
            "criar_ficha.html",
            {"form": FichaTreinoForm(), "formset": None, "sem_exercicios": True},
        )

    ficha = FichaTreino()
    form = FichaTreinoForm(request.POST or None)
    formset = FichaExercicioFormSet(request.POST or None, instance=ficha, prefix="exercicios")

    if request.method == "POST":
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    ficha = form.save()
                    formset.instance = ficha
                    formset.save()
                messages.success(request, _("Ficha de treino criada com sucesso."))
                return render(request, "sucesso_ficha.html", {"ficha": ficha})
            except Exception:
                messages.error(request, _("Erro ao salvar ficha de treino. Tente novamente mais tarde."))
        else:
            messages.error(request, _("Verifique os dados informados."))

    return render(request, "criar_ficha.html", {"form": form, "formset": formset, "sem_exercicios": False})


def _obter_aluno_logado(user) -> Aluno | None:
    # Busca o aluno com base no email do usuario logado.
    if not user.is_authenticated:
        return None
    email = user.email or user.username
    if not email:
        return None
    try:
        return Aluno.objects.get(email__iexact=email)
    except Aluno.DoesNotExist:
        return None


def _preparar_progresso(treino: TreinoDiario) -> None:
    """Ensure there is a progress row per exercise."""
    for ficha_exercicio in treino.ficha.exercicios.all():
        TreinoProgresso.objects.get_or_create(
            treino=treino,
            exercicio=ficha_exercicio.exercicio,
        )


def _ordenar_e_paginar(
    request: HttpRequest,
    queryset,
    allowed_fields: tuple[str, ...],
    default_field: str,
    *,
    default_direction: str = "asc",
    per_page: int = 10,
):
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


@login_required
@login_required
def treino_do_dia(request: HttpRequest) -> HttpResponse:
    # Mostra o treino diario do aluno com checkboxes para controlar progresso.
    aluno = _obter_aluno_logado(request.user)
    if not aluno:
        mensagens = _("Nenhum treino disponível para hoje.")
        return render(request, "treino_do_dia.html", {"mensagem": mensagens})

    try:
        treino = TreinoDiario.objects.select_related("ficha", "aluno").prefetch_related("ficha__exercicios__exercicio").get(
            aluno=aluno,
            data=date.today(),
        )
    except TreinoDiario.DoesNotExist:
        messages.info(request, _("Nenhum treino disponível para hoje."))
        return render(request, "treino_do_dia.html", {"mensagem": _("Nenhum treino disponível para hoje.")})

    _preparar_progresso(treino)
    progresso_qs = TreinoProgresso.objects.filter(treino=treino).select_related("exercicio")
    progresso_map = {item.exercicio_id: item for item in progresso_qs}
    ficha_exercicios = list(treino.ficha.exercicios.select_related("exercicio"))

    if request.method == "POST":
        selecionados = {int(pk) for pk in request.POST.getlist("exercicios")}
        acao = request.POST.get("acao", "salvar")

        try:
            with transaction.atomic():
                for item in progresso_qs:
                    item.concluido = item.exercicio_id in selecionados
                    item.save(update_fields=["concluido"])
                if acao == "finalizar":
                    treino.finalizado = True
                    treino.save(update_fields=["finalizado"])
                    messages.success(request, _("Treino finalizado com sucesso."))
                    return render(
                        request,
                        "treino_finalizado.html",
                        {"treino": treino, "ficha_exercicios": ficha_exercicios},
                    )
        except Exception:
            messages.error(request, _("Não foi possível atualizar o progresso."))
        return render(
            request,
            "treino_do_dia.html",
            {
                "treino": treino,
                "ficha_exercicios": ficha_exercicios,
                "progresso": progresso_map,
                "mensagem": _("Não foi possível atualizar o progresso."),
            },
        )

        messages.success(request, _("Progresso salvo com sucesso."))
        return render(
            request,
            "progresso_atualizado.html",
            {"treino": treino},
        )

    return render(
        request,
        "treino_do_dia.html",
        {"treino": treino, "ficha_exercicios": ficha_exercicios, "progresso": progresso_map},
    )


@login_required
@login_required
def historico_treinos(request: HttpRequest) -> HttpResponse:
    # Listagem de treinos finalizados do aluno com ordenacao e paginacao.
    aluno = _obter_aluno_logado(request.user)
    if not aluno:
        return render(
            request,
            "historico_treinos.html",
            {"mensagem": _("Nenhum treino encontrado para este aluno.")},
        )

    try:
        treinos_qs = TreinoDiario.objects.filter(aluno=aluno, finalizado=True).select_related("ficha")
    except Exception:
        messages.error(request, _("Erro ao carregar hist??rico de treinos."))
        return render(request, "historico_treinos.html", {"treinos": []})

    if not treinos_qs.exists():
        messages.info(request, _("Nenhum treino encontrado para este aluno."))

    sortable_fields = ("data", "finalizado")
    page_obj, sort_field, direction = _ordenar_e_paginar(
        request,
        treinos_qs,
        sortable_fields,
        "data",
        default_direction="desc",
        per_page=10,
    )
    sort_options = {
        field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields
    }

    return render(
        request,
        "historico_treinos.html",
        {
            "treinos": page_obj.object_list,
            "page_obj": page_obj,
            "current_sort": sort_field,
            "current_direction": direction,
            "sort_options": sort_options,
        },
    )

@login_required
@login_required
def detalhes_treino(request: HttpRequest, pk: int) -> HttpResponse:
    # Mostra detalhes de um treino especifico com todos os exercicios.
    aluno = _obter_aluno_logado(request.user)
    treino = get_object_or_404(
        TreinoDiario.objects.select_related("ficha", "aluno"),
        pk=pk,
    )
    if aluno and treino.aluno != aluno:
        return redirect("treinos:historico")

    _preparar_progresso(treino)
    progresso_qs = TreinoProgresso.objects.filter(treino=treino).select_related("exercicio")
    progresso_map = {item.exercicio_id: item for item in progresso_qs}
    ficha_exercicios = treino.ficha.exercicios.select_related("exercicio")

    return render(
        request,
        "detalhes_treino.html",
        {
            "treino": treino,
            "progresso": progresso_map,
            "ficha_exercicios": ficha_exercicios,
        },
    )


@login_required
def sucesso_ficha(request: HttpRequest) -> HttpResponse:
    # Tela simples para confirmar a criacao da ficha.
    return render(request, "sucesso_ficha.html")
