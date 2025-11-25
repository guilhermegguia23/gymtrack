from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Aluno

User = get_user_model()


def _slugify_username(nome: str) -> str:
    partes = (nome or "").strip().lower().split()
    if not partes:
        return ""
    if len(partes) == 1:
        return partes[0]
    return f"{partes[0]}.{partes[-1]}"


def _unique_username(base: str) -> str:
    """
    Garante um username único; se já existir, acrescenta sufixo numérico.
    """
    candidate = base
    counter = 1
    while User.objects.filter(username=candidate).exists():
        candidate = f"{base}{counter}"
        counter += 1
    return candidate


def _obter_grupo_aluno() -> Group:
    grupo, _ = Group.objects.get_or_create(name="aluno")
    return grupo


@receiver(post_save, sender=Aluno)
def criar_ou_atualizar_usuario_aluno(sender, instance: Aluno, created: bool, **kwargs) -> None:
    """
    Garante que cada Aluno possua um usuário Django vinculado.
    - Cria com username baseado no nome, email do aluno e senha padrão.
    - Vincula ao grupo 'aluno'.
    - Mantém nome/email sincronizados quando o Aluno é atualizado.
    - Não altera senha se o usuário já existir para evitar derrubar sessões.
    """
    username_base = _slugify_username(instance.nome)
    if not username_base:
        return

    user = instance.usuario
    if created or user is None:
        username = _unique_username(username_base)
        user = User.objects.create_user(
            username=username,
            email=instance.email,
            password="123456",
            first_name=instance.nome.split()[0] if instance.nome else "",
            last_name=" ".join(instance.nome.split()[1:]) if instance.nome and len(instance.nome.split()) > 1 else "",
        )
        instance.usuario = user
        instance.save(update_fields=["usuario"])
        _obter_grupo_aluno().user_set.add(user)
    else:
        # Atualiza dados básicos se houver divergência (mantém senha intacta).
        changed = False
        nome_parts = instance.nome.split()
        first_name = nome_parts[0] if nome_parts else ""
        last_name = " ".join(nome_parts[1:]) if len(nome_parts) > 1 else ""
        if user.email != instance.email:
            user.email = instance.email
            changed = True
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if user.last_name != last_name:
            user.last_name = last_name
            changed = True
        if changed:
            user.save(update_fields=["email", "first_name", "last_name"])
        _obter_grupo_aluno().user_set.add(user)
