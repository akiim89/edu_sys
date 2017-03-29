# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.conf import settings

import json

class Command(BaseCommand):
    help = 'Create demo data.'

    def handle(self, *args, **options):
        d = {}
        for s in dir(settings):
            if not s.startswith('_'):
                a = getattr(settings, s)
                try:
                    json.dumps({s:a})
                except TypeError:
                    pass
                else:
                    d[s] = a
        print(json.dumps(d, sort_keys=True, indent=2))
