from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .forms import (
    AlunoForm,
    ExercicioForm,
    FichaTreinoForm,
    PerfilAlunoForm,
    TrocaSenhaForm,
    TreinoExercicioFormSet,
    TreinoForm,
)
from .models import (
    Aluno,
    Exercicio,
    FichaTreino,
    Treino,
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
    return render(
        request,
        "exercicios/form.html",
        {"form": form, "grupos_musculares": _listar_grupos_musculares()},
    )


@login_required
def exercicio_update(request: HttpRequest, pk: int) -> HttpResponse:
    # Atualiza um exercicio existente mantendo o historico.
    exercicio = get_object_or_404(Exercicio, pk=pk)
    form = ExercicioForm(request.POST or None, instance=exercicio)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Exercício atualizado."))
        return redirect("treinos:lista_exercicios")
    return render(
        request,
        "exercicios/form.html",
        {
            "form": form,
            "exercicio": exercicio,
            "grupos_musculares": _listar_grupos_musculares(),
        },
    )


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
    # Cria a ficha; treinos e exercicios são gerenciados em páginas separadas.
    form = FichaTreinoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                ficha = form.save()
                if ficha.ativa:
                    FichaTreino.objects.filter(aluno=ficha.aluno).exclude(pk=ficha.pk).update(ativa=False)
                if not ficha.treinos.exists():
                    Treino.objects.create(ficha=ficha, nome="A", ordem=1)
            messages.success(request, _("Ficha de treino criada. Adicione os treinos (A/B/C...)."))
            return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)
        except Exception:
            messages.error(request, _("Erro ao salvar ficha de treino."))

    return render(request, "fichas/criar.html", {"form": form, "sem_exercicios": False})


@login_required
def gerenciar_treinos(request: HttpRequest, ficha_id: int) -> HttpResponse:
    ficha = get_object_or_404(FichaTreino, pk=ficha_id)
    treinos = ficha.treinos.order_by("ordem")
    form = TreinoForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        treino = form.save(commit=False)
        treino.ficha = ficha
        treino.save()
        messages.success(request, _("Treino adicionado."))
        return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)

    return render(
        request,
        "fichas/gerenciar_treinos.html",
        {"ficha": ficha, "treinos": treinos, "form": form},
    )


@login_required
def remover_treino(request: HttpRequest, treino_id: int) -> HttpResponse:
    treino = get_object_or_404(Treino, pk=treino_id)
    ficha_id = treino.ficha_id
    if request.method == "POST":
        treino.delete()
        messages.success(request, _("Treino removido."))
    return redirect("treinos:gerenciar_treinos", ficha_id=ficha_id)


@login_required
def editar_treino_exercicios(request: HttpRequest, treino_id: int) -> HttpResponse:
    treino = get_object_or_404(Treino, pk=treino_id)
    formset = TreinoExercicioFormSet(request.POST or None, instance=treino, prefix="exercicios")

    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            messages.success(request, _("Exerc?cios atualizados."))
            return redirect("treinos:editar_treino_exercicios", treino_id=treino.pk)
        messages.error(request, _("Corrija os erros para salvar."))

    return render(
        request,
        "fichas/editar_treino_exercicios.html",
        {"treino": treino, "ficha": treino.ficha, "formset": formset},
    )


@login_required
def ativar_ficha(request: HttpRequest, ficha_id: int) -> HttpResponse:
    ficha = get_object_or_404(FichaTreino, pk=ficha_id)
    FichaTreino.objects.filter(aluno=ficha.aluno).update(ativa=False)
    ficha.ativa = True
    ficha.save(update_fields=["ativa"])
    messages.success(request, _("Ficha marcada como ativa."))
    return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)


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


def _preparar_progresso(treino_diario: TreinoDiario) -> None:
    """Ensure there is a progress row per exercise."""
    for treino_exercicio in treino_diario.treino.exercicios.all():
        TreinoProgresso.objects.get_or_create(
            treino_diario=treino_diario,
            exercicio=treino_exercicio.exercicio,
        )


def _selecionar_treino_do_dia(aluno: Aluno) -> Treino | None:
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


def _listar_grupos_musculares() -> list[str]:
    return list(
        Exercicio.objects.order_by("grupo_muscular")
        .values_list("grupo_muscular", flat=True)
        .distinct()
    )


@login_required
def treino_do_dia(request: HttpRequest) -> HttpResponse:
    # Mostra o treino diario do aluno com checkboxes para controlar progresso.
    aluno = _obter_aluno_logado(request.user)
    if not aluno:
        mensagens = _("Nenhum treino dispon?vel para hoje.")
        return render(request, "treino_do_dia.html", {"mensagem": mensagens})

    treino_do_dia = _selecionar_treino_do_dia(aluno)
    if not treino_do_dia:
        messages.info(request, _("Nenhum treino dispon?vel para hoje."))
        return render(request, "treino_do_dia.html", {"mensagem": _("Nenhum treino dispon?vel para hoje.")})

    treino = TreinoDiario.objects.filter(aluno=aluno, data=date.today()).first()
    if not treino:
        treino = TreinoDiario.objects.create(aluno=aluno, treino=treino_do_dia, data=date.today())
        _preparar_progresso(treino)

    _preparar_progresso(treino)
    progresso_qs = TreinoProgresso.objects.filter(treino_diario=treino).select_related("exercicio")
    progresso_map = {item.exercicio_id: item for item in progresso_qs}
    treino_exercicios = list(treino.treino.exercicios.select_related("exercicio"))

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
                        {"treino": treino, "treino_exercicios": treino_exercicios},
                    )
        except Exception:
            messages.error(request, _("N?o foi poss?vel atualizar o progresso."))
            return render(
                request,
                "treino_do_dia.html",
                {
                    "treino": treino,
                    "treino_exercicios": treino_exercicios,
                    "progresso": progresso_map,
                    "mensagem": _("N?o foi poss?vel atualizar o progresso."),
                },
            )

        messages.success(request, _("Progresso salvo com sucesso."))

    return render(
        request,
        "treino_do_dia.html",
        {"treino": treino, "treino_exercicios": treino_exercicios, "progresso": progresso_map},
    )


def lista_treinos(request):
    """
    Lista todos os treinos. 
    Se o usuário for aluno, lista apenas os treinos dele.
    Mais tarde poderá receber filtros por aluno, por data, etc.
    """

    # Obtém aluno logado (se existir)
    aluno = _obter_aluno_logado(request.user)

    treinos = TreinoDiario.objects.select_related("aluno", "treino", "treino__ficha") \
        .prefetch_related("treino__exercicios__exercicio")
    treinos = treinos.exclude(treino__isnull=True)

    # Se for aluno → só vê os próprios treinos
    if aluno:
        treinos = treinos.filter(aluno=aluno)
    else:
        # Se for instrutor → opcionalmente pesquisar por aluno
        aluno_nome = request.GET.get("aluno", "").strip()
        if aluno_nome:
            treinos = treinos.filter(
                Q(aluno__nome__icontains=aluno_nome) |
                Q(aluno__email__icontains=aluno_nome)
            )

    # Ordenação inicial
    treinos = treinos.order_by("-data")

    # Paginação
    paginator = Paginator(treinos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "admin/listar_treinos.html",
        {
            "page_obj": page_obj,
            "aluno_nome": request.GET.get("aluno", ""),
        }
    )

@login_required
def lista_fichas(request):
    aluno_id = request.GET.get("aluno")
    ordenar = request.GET.get("ordenar", "data_criacao")
    direcao = request.GET.get("direcao", "asc")
    termo = request.GET.get("q", "")

    # Ajusta campos reais para ordenação
    if ordenar == "aluno":
        ordem = "aluno__nome" if direcao == "asc" else "-aluno__nome"
    elif ordenar == "nome":
        ordem = "nome" if direcao == "asc" else "-nome"
    else:
        # Campos válidos: data_criacao, id, observacoes
        ordem = ordenar if direcao == "asc" else f"-{ordenar}"

    # Filtros
    query = Q()
    if aluno_id:
        query &= Q(aluno_id=aluno_id)

    if termo:
        query &= (
            Q(observacoes__icontains=termo)
            | Q(aluno__nome__icontains=termo)
        )

    # Consulta
    fichas = (
        FichaTreino.objects.filter(query)
        .select_related("aluno")
        .prefetch_related("treinos__exercicios__exercicio")
        .order_by(ordem)
    )

    # Paginação
    paginator = Paginator(fichas, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Opções do menu de ordenação (frontend)
    sort_options = {
        "data_criacao": "desc" if ordenar == "data_criacao" and direcao == "asc" else "asc",
        "aluno": "desc" if ordenar == "aluno" and direcao == "asc" else "asc",
        "nome": "desc" if ordenar == "nome" and direcao == "asc" else "asc",
        "id": "desc" if ordenar == "id" and direcao == "asc" else "asc",
    }

    context = {
        "page_obj": page_obj,
        "current_sort": ordenar,
        "current_direction": direcao,
        "sort_options": sort_options,
        "termo": termo,
        "aluno_id": aluno_id,
    }

    return render(request, "fichas/listar_fichas.html", context)

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
        treinos_qs = TreinoDiario.objects.filter(
            aluno=aluno,
            finalizado=True,
            treino__isnull=False,
        ).select_related("treino", "treino__ficha")
    except Exception:
        messages.error(request, _("Erro ao carregar histórico de treinos."))
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
def detalhes_treino(request: HttpRequest, pk: int) -> HttpResponse:
    # Mostra detalhes de um treino especifico com todos os exercicios.
    aluno = _obter_aluno_logado(request.user)
    treino = get_object_or_404(
        TreinoDiario.objects.select_related("treino", "treino__ficha", "aluno"),
        pk=pk,
    )
    if aluno and treino.aluno != aluno:
        return redirect("treinos:historico")

    _preparar_progresso(treino)
    progresso_qs = TreinoProgresso.objects.filter(treino_diario=treino).select_related("exercicio")
    progresso_map = {item.exercicio_id: item for item in progresso_qs}
    treino_exercicios = treino.treino.exercicios.select_related("exercicio")

    return render(
        request,
        "detalhes_treino.html",
        {
            "treino": treino,
            "progresso": progresso_map,
            "treino_exercicios": treino_exercicios,
        },
    )


@login_required
def sucesso_ficha(request: HttpRequest) -> HttpResponse:
    # Tela simples para confirmar a criacao da ficha.
    return render(request, "sucesso_ficha.html")
