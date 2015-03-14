from django import template

register = template.Library()

@register.filter
def is_checkboxes(value):
    return (value.__class__.__name__ == "CheckboxSelectMultiple")

@register.filter
def is_select(value):
    return (value.__class__.__name__ == "Select")

@register.filter
def is_textarea(value):
    return (value.__class__.__name__ == "Textarea")