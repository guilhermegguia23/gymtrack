from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Aluno",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("data_nascimento", models.DateField()),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="Exercicio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=150)),
                ("grupo_muscular", models.CharField(max_length=100)),
                ("descricao", models.TextField()),
            ],
            options={
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="FichaTreino",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data_criacao", models.DateField(auto_now_add=True)),
                ("observacoes", models.TextField(blank=True)),
                ("aluno", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fichas", to="treinos.aluno")),
            ],
            options={
                "ordering": ["-data_criacao"],
            },
        ),
        migrations.CreateModel(
            name="TreinoDiario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField()),
                ("finalizado", models.BooleanField(default=False)),
                ("aluno", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="treinos_diarios", to="treinos.aluno")),
                ("ficha", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="treinos_diarios", to="treinos.fichatreino")),
            ],
            options={
                "ordering": ["-data"],
                "unique_together": {("aluno", "data")},
            },
        ),
        migrations.CreateModel(
            name="FichaExercicio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("series", models.PositiveIntegerField()),
                ("repeticoes", models.PositiveIntegerField()),
                ("ordem", models.PositiveIntegerField()),
                ("exercicio", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="treinos.exercicio")),
                ("ficha", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="exercicios", to="treinos.fichatreino")),
            ],
            options={
                "ordering": ["ordem"],
                "unique_together": {("ficha", "ordem")},
            },
        ),
        migrations.CreateModel(
            name="TreinoProgresso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("concluido", models.BooleanField(default=False)),
                ("exercicio", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="treinos.exercicio")),
                ("treino", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progresso", to="treinos.treinodiario")),
            ],
            options={
                "ordering": ["exercicio__nome"],
                "unique_together": {("treino", "exercicio")},
            },
        ),
    ]

