## Descrição do Projeto
O GymTrack é um projeto acadêmico desenvolvido pelos alunos do 4º semestre do curso de Programação Web Backend com Python. O objetivo do sistema é oferecer uma plataforma moderna e integrada para gerenciamento de academias, permitindo o controle eficiente de alunos, fichas de treino, exercícios e histórico de evolução física.

## Contexto Institucional
- **Instituição:** IFMT Campus Cel. Octayde Jorge da Silva
- **Disciplina:** Programação BackEnd

## 👥Equipe
- **Discentes:** Guilherme
- **Docente:** Profª Alberto


## ⚙Instalação e Configuração

### Pré-requisitos
- Python 3.10+
- Django 4.0+
- Git

### Passo a Passo
```
# Clone o repositório

git clone repo_url

1 - Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\Activate

2 - Instalar dependências
python -m pip install --upgrade pip
pip install Django

3 - Configure o banco de dados no arquivo settings.py

4 -  Aplicar migrações
python manage.py makemigrations
python manage.py migrate

5 - Criar superuser
 python manage.py createsuperuser

7 - Rodar o servidor de desenvolvimento
python manage.py runserver

```