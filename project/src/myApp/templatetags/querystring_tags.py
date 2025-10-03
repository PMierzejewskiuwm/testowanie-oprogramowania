from django import template
from urllib.parse import urlencode


register = template.Library()

@register.simple_tag
def querystring(request, **params):
    """
    Returns the current URL query string updated with the given parameters.
    For use in templates for building links with modified query parameters.
    """
    query_dict = request.GET.copy()
    query_dict.update(params)
    return query_dict.urlencode()