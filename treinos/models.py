from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Aluno(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="perfil_aluno")

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class Exercicio(models.Model):
    nome = models.CharField(max_length=150)
    grupo_muscular = models.CharField(max_length=100)
    descricao = models.TextField()

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome


class FichaTreino(models.Model):
    nome = models.CharField(max_length=100, blank=True)
    motivo = models.CharField(max_length=100, blank=True)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="fichas")
    data_criacao = models.DateField(auto_now_add=True)
    ativa = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Ficha {self.aluno.nome} - {self.data_criacao:%d/%m/%Y}"


class Treino(models.Model):
    ficha = models.ForeignKey(FichaTreino, on_delete=models.CASCADE, related_name="treinos")
    nome = models.CharField(max_length=50)
    ordem = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["ordem"]

    def __str__(self) -> str:
        return f"{self.ficha} - Treino {self.nome}"


class TreinoExercicio(models.Model):
    treino = models.ForeignKey(Treino, on_delete=models.CASCADE, related_name="exercicios")
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField()
    repeticoes = models.PositiveIntegerField()
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ["ordem"]
        unique_together = ("treino", "ordem")

    def __str__(self) -> str:
        return f"{self.treino} - {self.exercicio.nome}"


class TreinoDiario(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="treinos_diarios")
    treino = models.ForeignKey(Treino, on_delete=models.CASCADE, related_name="execucoes", null=True, blank=True)
    data = models.DateField()
    finalizado = models.BooleanField(default=False)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    tempo_total = models.DurationField(null=True, blank=True)
    tempo_medio_exercicio = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ["-data"]
        unique_together = ("aluno", "data")

    def __str__(self) -> str:
        return f"Treino {self.aluno.nome} - {self.data:%d/%m/%Y}"

    @property
    def estimativa_duracao(self) -> int:
        return self.treino.exercicios.count() * 5


class TreinoProgresso(models.Model):
    treino_diario = models.ForeignKey(
        TreinoDiario,
        on_delete=models.CASCADE,
        related_name="progresso",
        null=True,
        blank=True,
    )
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)

    class Meta:
        unique_together = ("treino_diario", "exercicio")
        ordering = ["exercicio__nome"]

    def __str__(self) -> str:
        return f"{self.treino_diario} - {self.exercicio.nome}"

