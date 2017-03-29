#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os, sys

sys.path.extend([os.path.dirname(os.path.dirname(os.path.abspath(__file__)))])

from phaceology_defaults import PhaceologySettings

class PhaceologyLocalSettings(PhaceologySettings):
    # URLs
    url_base = 'http://phaceology.looplingo.com'

    # Cookies
    cookie_domain = 'phaceology.looplingo.com'

    # DB
#    db_postgres = '1'
    # FIXME: Change this in the release version of the server and don't check the PW into source control.
#    db_password = 'kpFWdBV6ZXJXXuZb'

    # Deployment
    django_debug = '1'

    # Email sending
    # TODO: Fill in.
    email_host = 'email-smtp.us-west-2.amazonaws.com'
    email_port = '587'
    email_host_user = 'AKIAII4XRXEJOWMWIRYA'
    email_host_password = 'ApnTevSARclKRBUaNWrIikDviAHG2LnRHQUILq3MUa+Z'

    # Accounts
    facebook_app_id = '193496194451359'
    facebook_app_secret = '03d8045c8f7f8ea6517a0c57641d6e77'
    #facebook_app_id = 'FILL IN'
    #facebook_app_secret = 'FILL IN'


# Run on import
PhaceologyLocalSettings.update_environment()
