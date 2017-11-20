from django import template

register = template.Library()


@register.inclusion_tag('core/bootstrap/form-group.html')
def form_group(field):
    return {'field': field}
