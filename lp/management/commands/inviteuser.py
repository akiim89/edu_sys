# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from lp import models

class Command(BaseCommand):
    help = 'Invite a new employee user.'

    def add_arguments(self, parser):
        parser.add_argument('email', nargs=1, type=str)
        parser.add_argument('name', nargs='+', type=str)

    def handle(self, *args, **options):
        email = options['email'][0]
        name = ' '.join(options['name'])

        # For testing purposes, find the CEO and a store
        ceo = models.User.objects.get(email='ceo@company2.com')
        division = models.Division.objects.get(name='Company 2 South West 4')
        self.stdout.write('Making user with name %s email %s by %s' % (name, email, ceo))
        user = models.User.objects.create_user(email=email, name=name, password=None, division=division)
        invite = models.UserInvite.objects.create(user=user, created_by=ceo)

        self.stdout.write('Invite code %s' % invite.invite_code)
