from django.contrib import admin

from .models import Aluno, Exercicio, FichaTreino, Treino, TreinoDiario, TreinoExercicio, TreinoProgresso


class TreinoExercicioInline(admin.TabularInline):
    model = TreinoExercicio
    extra = 0


class TreinoInline(admin.TabularInline):
    model = Treino
    extra = 0


@admin.register(FichaTreino)
class FichaTreinoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data_criacao", "ativa")
    list_filter = ("data_criacao", "ativa")
    inlines = [TreinoInline]


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")


@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo_muscular")
    search_fields = ("nome", "grupo_muscular")


@admin.register(Treino)
class TreinoAdmin(admin.ModelAdmin):
    list_display = ("ficha", "nome", "ordem")
    list_filter = ("ficha",)
    inlines = [TreinoExercicioInline]


@admin.register(TreinoDiario)
class TreinoDiarioAdmin(admin.ModelAdmin):
    list_display = ("aluno", "treino", "data", "finalizado")
    list_filter = ("finalizado", "data", "treino__ficha")


@admin.register(TreinoProgresso)
class TreinoProgressoAdmin(admin.ModelAdmin):
    list_display = ("treino_diario", "exercicio", "concluido")
    list_filter = ("concluido",)

