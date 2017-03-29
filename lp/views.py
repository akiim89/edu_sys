from django.shortcuts import render
from django.conf import settings

from .models import User, UserInvite


def portal(request):
    '''The manager portal.'''
    return render(request, 'lp/base.html', {'bundle':'webpack/portal.bundle.js'})

def learn(request):
    '''The employee portal.'''
    return render(request, 'lp/base.html', {'bundle':'webpack/lms.bundle.js'})

def codes(request):
    return render(request, 'lp/invitecodes.html', {'codes':UserInvite.objects.all()})
