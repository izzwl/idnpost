import json

from django import template
from django.template.loader import get_template

from django.template.context import Context

register = template.Library()

# @register.tag(name='render_nav_items')
# def render_nav_items(context):
#     pass