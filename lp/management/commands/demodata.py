# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from lp.demodata import DemoDataMaker


class Command(BaseCommand):
    help = 'Create demo data.'

    def handle(self, *args, **options):
        ddm = DemoDataMaker() # Default params
        ddm.make_company()
        company2 = DemoDataMaker(user_name='ceo 2',
                                 user_email='ceo@company2.com',
                                 password='Phace Demo',
                                 company_name='Company 2',
                                 slug='company2').make_company()
        self.stdout.write('Successfully created demo data.')
