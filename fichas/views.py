from __future__ import annotations

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from fichas.forms import FichaTreinoForm, TreinoExercicioFormSet, TreinoForm
from treinos.models import FichaTreino, Treino, TreinoDiario, TreinoProgresso
from treinos.utils import (
    bloquear_para_aluno,
    listar_grupos_musculares,
    obter_aluno_logado,
    ordenar_e_paginar,
    preparar_progresso,
    selecionar_treino_do_dia,
)


@login_required
@bloquear_para_aluno
def criar_ficha(request: HttpRequest) -> HttpResponse:
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
@bloquear_para_aluno
def gerenciar_treinos(request: HttpRequest, ficha_id: int) -> HttpResponse:
    ficha = get_object_or_404(FichaTreino, pk=ficha_id)
    treinos = ficha.treinos.order_by("ordem")

    editar_id = request.GET.get("editar")
    treino_em_edicao = None
    form = TreinoForm()

    if editar_id:
        treino_em_edicao = get_object_or_404(Treino, pk=editar_id, ficha=ficha)
        form = TreinoForm(instance=treino_em_edicao)

    if request.method == "POST":
        treino_id = request.POST.get("treino_id")
        if treino_id:
            treino_em_edicao = get_object_or_404(Treino, pk=treino_id, ficha=ficha)
            form = TreinoForm(request.POST, instance=treino_em_edicao)
            if form.is_valid():
                form.save()
                messages.success(request, _("Treino atualizado."))
                return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)
        else:
            form = TreinoForm(request.POST)
            if form.is_valid():
                treino = form.save(commit=False)
                treino.ficha = ficha
                treino.save()
                messages.success(request, _("Treino adicionado."))
                return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)

    return render(
        request,
        "fichas/gerenciar_treinos.html",
        {"ficha": ficha, "treinos": treinos, "form": form, "treino_em_edicao": treino_em_edicao},
    )


@login_required
@bloquear_para_aluno
def remover_treino(request: HttpRequest, treino_id: int) -> HttpResponse:
    treino = get_object_or_404(Treino, pk=treino_id)
    ficha_id = treino.ficha_id
    if request.method == "POST":
        treino.delete()
        messages.success(request, _("Treino removido."))
    return redirect("treinos:gerenciar_treinos", ficha_id=ficha_id)


@login_required
@bloquear_para_aluno
def editar_treino_exercicios(request: HttpRequest, treino_id: int) -> HttpResponse:
    treino = get_object_or_404(Treino, pk=treino_id)
    formset = TreinoExercicioFormSet(request.POST or None, instance=treino, prefix="exercicios")

    if request.method == "POST":
        if formset.is_valid():
            formset.save()
            messages.success(request, _("Exercicios atualizados."))
            return redirect("treinos:editar_treino_exercicios", treino_id=treino.pk)
        messages.error(request, _("Corrija os erros para salvar."))

    return render(
        request,
        "fichas/editar_treino_exercicios.html",
        {"treino": treino, "ficha": treino.ficha, "formset": formset},
    )


@login_required
@bloquear_para_aluno
def ativar_ficha(request: HttpRequest, ficha_id: int) -> HttpResponse:
    ficha = get_object_or_404(FichaTreino, pk=ficha_id)
    FichaTreino.objects.filter(aluno=ficha.aluno).update(ativa=False)
    ficha.ativa = True
    ficha.save(update_fields=["ativa"])
    messages.success(request, _("Ficha marcada como ativa."))
    return redirect("treinos:gerenciar_treinos", ficha_id=ficha.pk)


@login_required
def treino_do_dia(request: HttpRequest) -> HttpResponse:
    aluno = obter_aluno_logado(request.user)
    if not aluno:
        mensagens = _("Nenhum treino disponivel para hoje.")
        return render(request, "treino_do_dia.html", {"mensagem": mensagens})

    treino_do_dia = selecionar_treino_do_dia(aluno)
    if not treino_do_dia:
        messages.info(request, _("Nenhum treino disponivel para hoje."))
        return render(request, "treino_do_dia.html", {"mensagem": _("Nenhum treino disponivel para hoje.")})

    treino = TreinoDiario.objects.filter(aluno=aluno, data=date.today()).first()
    if not treino:
        treino = TreinoDiario.objects.create(aluno=aluno, treino=treino_do_dia, data=date.today())
        preparar_progresso(treino)

    if treino.finalizado:
        return render(
            request,
            "treino_do_dia.html",
            {
                "mensagem": _("Treino de hoje ta pago!! 😎"),
                "treino": treino,
                "treino_exercicios": treino.treino.exercicios.select_related("exercicio"),
                "progresso": TreinoProgresso.objects.filter(treino_diario=treino).select_related("exercicio"),
            },
        )

    preparar_progresso(treino)
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
                    agora = timezone.now()
                    total_exercicios = len(treino_exercicios) or 1
                    treino.finalizado = True
                    treino.finished_at = agora
                    treino.tempo_total = agora - treino.started_at
                    treino.tempo_medio_exercicio = treino.tempo_total / total_exercicios
                    treino.save(update_fields=["finalizado", "finished_at", "tempo_total", "tempo_medio_exercicio"])
                    messages.success(request, _("Treino finalizado com sucesso."))
                    return render(
                        request,
                        "treino_finalizado.html",
                        {"treino": treino, "treino_exercicios": treino_exercicios},
                    )
        except Exception:
            messages.error(request, _("Nao foi possivel atualizar o progresso."))
            return render(
                request,
                "treino_do_dia.html",
                {
                    "treino": treino,
                    "treino_exercicios": treino_exercicios,
                    "progresso": progresso_map,
                    "mensagem": _("Nao foi possivel atualizar o progresso."),
                },
            )

        messages.success(request, _("Progresso salvo com sucesso."))

    return render(
        request,
        "treino_do_dia.html",
        {"treino": treino, "treino_exercicios": treino_exercicios, "progresso": progresso_map},
    )


@login_required
@bloquear_para_aluno
def lista_treinos(request):
    aluno = obter_aluno_logado(request.user)

    treinos = TreinoDiario.objects.select_related("aluno", "treino", "treino__ficha").prefetch_related(
        "treino__exercicios__exercicio"
    )
    treinos = treinos.exclude(treino__isnull=True)

    if aluno:
        treinos = treinos.filter(aluno=aluno)
    else:
        aluno_nome = request.GET.get("aluno", "").strip()
        if aluno_nome:
            treinos = treinos.filter(Q(aluno__nome__icontains=aluno_nome) | Q(aluno__email__icontains=aluno_nome))

    treinos = treinos.order_by("-data")

    from django.core.paginator import Paginator

    paginator = Paginator(treinos, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/listar_treinos.html", {"page_obj": page_obj, "aluno_nome": request.GET.get("aluno", "")})


@login_required
@bloquear_para_aluno
def lista_fichas(request):
    aluno_id = request.GET.get("aluno")
    ordenar = request.GET.get("ordenar", "data_criacao")
    direcao = request.GET.get("direcao", "asc")
    termo = request.GET.get("q", "")

    if ordenar == "aluno":
        ordem = "aluno__nome" if direcao == "asc" else "-aluno__nome"
    elif ordenar == "nome":
        ordem = "nome" if direcao == "asc" else "-nome"
    else:
        ordem = ordenar if direcao == "asc" else f"-{ordenar}"

    query = Q()
    if aluno_id:
        query &= Q(aluno_id=aluno_id)

    if termo:
        query &= Q(observacoes__icontains=termo) | Q(aluno__nome__icontains=termo)

    fichas = (
        FichaTreino.objects.filter(query)
        .select_related("aluno")
        .prefetch_related("treinos__exercicios__exercicio")
        .order_by(ordem)
    )

    from django.core.paginator import Paginator

    paginator = Paginator(fichas, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
    aluno = obter_aluno_logado(request.user)
    if not aluno:
        return render(request, "historico_treinos.html", {"mensagem": _("Nenhum treino encontrado para este aluno.")})

    try:
        treinos_qs = TreinoDiario.objects.filter(aluno=aluno, finalizado=True, treino__isnull=False).select_related(
            "treino", "treino__ficha"
        )
    except Exception:
        messages.error(request, _("Erro ao carregar historico de treinos."))
        return render(request, "historico_treinos.html", {"treinos": []})

    if not treinos_qs.exists():
        messages.info(request, _("Nenhum treino encontrado para este aluno."))

    sortable_fields = ("data", "finalizado")
    page_obj, sort_field, direction = ordenar_e_paginar(
        request,
        treinos_qs,
        sortable_fields,
        "data",
        default_direction="desc",
        per_page=10,
    )
    sort_options = {field: "desc" if field == sort_field and direction == "asc" else "asc" for field in sortable_fields}

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
    aluno = obter_aluno_logado(request.user)
    treino = get_object_or_404(TreinoDiario.objects.select_related("treino", "treino__ficha", "aluno"), pk=pk)
    if aluno and treino.aluno != aluno:
        return redirect("treinos:historico")

    preparar_progresso(treino)
    progresso_qs = TreinoProgresso.objects.filter(treino_diario=treino).select_related("exercicio")
    progresso_map = {item.exercicio_id: item for item in progresso_qs}
    treino_exercicios = treino.treino.exercicios.select_related("exercicio")

    return render(
        request,
        "detalhes_treino.html",
        {"treino": treino, "progresso": progresso_map, "treino_exercicios": treino_exercicios},
    )


@login_required
@bloquear_para_aluno
def sucesso_ficha(request: HttpRequest) -> HttpResponse:
    return render(request, "sucesso_ficha.html")
