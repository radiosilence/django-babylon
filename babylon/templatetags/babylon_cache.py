from django import template
register = template.Library()

import babylon

@register.simple_tag
def babylon_get(cache, *args, **kwargs):
    return babylon.get(cache, *args, **kwargs)
