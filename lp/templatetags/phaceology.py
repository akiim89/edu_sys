# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def css(*args, **kwargs):
    '''
    Insert a bunch of CSS files.
    '''
    def translate_url(url):
        return '%s%s' % (settings.CSS_URL, url)
    
    ret = '\n'.join(['<link rel="stylesheet" href="%s" type="text/css" />' %
                     translate_url(url) for url in args])
    return mark_safe(ret)

@register.simple_tag
def js(*args, **kwargs):
    '''
    Insert a bunch of Javascript files.
    '''
    def translate_url(url):
        if url.startswith('webpack/'):
            return '%s%s' % (settings.STATIC_URL, url)
        return '%s%s' % (settings.JAVASCRIPT_URL, url)

    ret = '\n'.join(['<script type="text/javascript" src="%s" ></script>' %
                     translate_url(url) for url in args])
    return mark_safe(ret)
