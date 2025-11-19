from django.contrib import admin

from .models import Aluno, Exercicio, FichaExercicio, FichaTreino, TreinoDiario, TreinoProgresso


class FichaExercicioInline(admin.TabularInline):
    model = FichaExercicio
    extra = 0


@admin.register(FichaTreino)
class FichaTreinoAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data_criacao")
    list_filter = ("data_criacao",)
    inlines = [FichaExercicioInline]


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "email")


@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ("nome", "grupo_muscular")
    search_fields = ("nome", "grupo_muscular")


@admin.register(TreinoDiario)
class TreinoDiarioAdmin(admin.ModelAdmin):
    list_display = ("aluno", "data", "finalizado")
    list_filter = ("finalizado", "data")


@admin.register(TreinoProgresso)
class TreinoProgressoAdmin(admin.ModelAdmin):
    list_display = ("treino", "exercicio", "concluido")
    list_filter = ("concluido",)

