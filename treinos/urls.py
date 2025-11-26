from django.urls import path

from alunos import views as alunos_views
from exercicios import views as exercicios_views
from fichas import views as fichas_views

app_name = "treinos"

urlpatterns = [
    path("", alunos_views.lista_alunos, name="lista_alunos"),
    path("alunos/novo/", alunos_views.aluno_create, name="aluno_create"),
    path("alunos/<int:pk>/editar/", alunos_views.aluno_update, name="aluno_update"),
    path("alunos/<int:pk>/excluir/", alunos_views.aluno_delete, name="aluno_delete"),
    path("exercicios/", exercicios_views.lista_exercicios, name="lista_exercicios"),
    path("exercicios/novo/", exercicios_views.exercicio_create, name="exercicio_create"),
    path("exercicios/<int:pk>/editar/", exercicios_views.exercicio_update, name="exercicio_update"),
    path("exercicios/<int:pk>/excluir/", exercicios_views.exercicio_delete, name="exercicio_delete"),
    path("fichas/criar/", fichas_views.criar_ficha, name="criar_ficha"),
    path("fichas/<int:ficha_id>/treinos/", fichas_views.gerenciar_treinos, name="gerenciar_treinos"),
    path("fichas/<int:ficha_id>/ativar/", fichas_views.ativar_ficha, name="ativar_ficha"),
    path("treinos/<int:treino_id>/exercicios/", fichas_views.editar_treino_exercicios, name="editar_treino_exercicios"),
    path("treinos/<int:treino_id>/remover/", fichas_views.remover_treino, name="remover_treino"),
    path("perfil/", alunos_views.perfil, name="perfil"),
    path("treino-do-dia/", fichas_views.treino_do_dia, name="treino_do_dia"),
    path("historico/", fichas_views.historico_treinos, name="historico"),
    path("historico/<int:pk>/", fichas_views.detalhes_treino, name="detalhes_treino"),
    path("lista-treinos/", fichas_views.lista_treinos, name="lista_treinos"),
    path("lista-fichas/", fichas_views.lista_fichas, name="lista_fichas"),
]

