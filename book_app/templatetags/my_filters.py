from django import template
from pytils.translit import slugify
from transliterate import translit

register = template.Library()

@register.filter(name='slugify_ru')
def slugify_ru(value):
    return slugify(value)

@register.filter(name='reverslugify')
def revers_slugify(slug):
    return translit(slug, 'ru').title().replace('-', ' ')

