from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key)
    except Exception:
        return None


@register.filter
def has_group(user, group_name):
    try:
        if group_name == "aluno" and (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False)):
            return False
        return user.groups.filter(name=group_name).exists()
    except Exception:
        return False


@register.filter
def app_name_of(view_func):
    try:
        return view_func.__module__.split(".")[0]
    except Exception:
        return ""


@register.filter
def humanize_duration(value):
    """
    Converte um timedelta em string hh:mm:ss.
    """
    try:
        total_seconds = int(value.total_seconds())
    except Exception:
        return ""
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

