from django.urls import path

from . import views

app_name = "treinos"

urlpatterns = [
    path("", views.lista_alunos, name="lista_alunos"),
    path("alunos/novo/", views.aluno_create, name="aluno_create"),
    path("alunos/<int:pk>/editar/", views.aluno_update, name="aluno_update"),
    path("alunos/<int:pk>/excluir/", views.aluno_delete, name="aluno_delete"),
    path("exercicios/", views.lista_exercicios, name="lista_exercicios"),
    path("exercicios/novo/", views.exercicio_create, name="exercicio_create"),
    path("exercicios/<int:pk>/editar/", views.exercicio_update, name="exercicio_update"),
    path("exercicios/<int:pk>/excluir/", views.exercicio_delete, name="exercicio_delete"),
    path("fichas/criar/", views.criar_ficha, name="criar_ficha"),
    path("treino-do-dia/", views.treino_do_dia, name="treino_do_dia"),
    path("historico/", views.historico_treinos, name="historico"),
    path("historico/<int:pk>/", views.detalhes_treino, name="detalhes_treino"),
    path("lista-treinos/", views.lista_treinos, name="lista_treinos"),
    path("lista-fichas/", views.lista_fichas, name="lista_fichas"),
]

