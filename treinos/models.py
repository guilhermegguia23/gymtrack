from django.db import models


class Aluno(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField()
    ativo = models.BooleanField(default=True)

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
    observacoes = models.TextField(blank=True)

    class Meta:
        ordering = ["-data_criacao"]

    def __str__(self) -> str:
        return f"Ficha {self.aluno.nome} - {self.data_criacao:%d/%m/%Y}"


class FichaExercicio(models.Model):
    ficha = models.ForeignKey(FichaTreino, on_delete=models.CASCADE, related_name="exercicios")
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    series = models.PositiveIntegerField()
    repeticoes = models.PositiveIntegerField()
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ["ordem"]
        unique_together = ("ficha", "ordem")

    def __str__(self) -> str:
        return f"{self.ficha} - {self.exercicio.nome}"


class TreinoDiario(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name="treinos_diarios")
    ficha = models.ForeignKey(FichaTreino, on_delete=models.CASCADE, related_name="treinos_diarios")
    data = models.DateField()
    finalizado = models.BooleanField(default=False)

    class Meta:
        ordering = ["-data"]
        unique_together = ("aluno", "data")

    def __str__(self) -> str:
        return f"Treino {self.aluno.nome} - {self.data:%d/%m/%Y}"

    @property
    def estimativa_duracao(self) -> int:
        return self.ficha.exercicios.count() * 5


class TreinoProgresso(models.Model):
    treino = models.ForeignKey(TreinoDiario, on_delete=models.CASCADE, related_name="progresso")
    exercicio = models.ForeignKey(Exercicio, on_delete=models.CASCADE)
    concluido = models.BooleanField(default=False)

    class Meta:
        unique_together = ("treino", "exercicio")
        ordering = ["exercicio__nome"]

    def __str__(self) -> str:
        return f"{self.treino} - {self.exercicio.nome}"

