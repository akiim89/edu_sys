# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from lp.models import User

ADMIN_EMAIL = 'admin@looplingo.com'
ADMIN_NAME = 'Site Administrator'
ADMIN_PASSWORD = '2Phace'

class Command(BaseCommand):
    help = 'Create the superuser.'

    def handle(self, *args, **options):
        if not User.objects.filter(email=ADMIN_EMAIL).exists():
            User.objects.create_superuser(email=ADMIN_EMAIL, name=ADMIN_NAME, password=ADMIN_PASSWORD)
            self.stdout.write('Successfully created superuser.')
        else:
            self.stdout.write('Superuser already exists.')
