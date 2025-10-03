from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.apps import apps 

register = template.Library()

@register.simple_tag
def edit_tag(app, model, id, position_class, name):
    """
    Method generating dynamic links for specific object,
    leading to django admin
    """
    _model = apps.get_model(app, model)

    url = reverse(
        f'admin:{_model._meta.app_label}_{_model._meta.model_name}_change',
        args=[id]
    )
    return mark_safe(
        f'<a href="{url}" class="{position_class}" title="edit {name}"><i class="fa fa-pencil-square-o" '
        f'aria-hidden="true"></i></a>')
