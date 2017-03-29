"""phaceology URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from lp import api, views

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    # Django REST Framework API entry point: http://www.django-rest-framework.org/
    url(r'^api/classes/', include(api.router.urls)),
    # Django REST Framework login page: http://www.django-rest-framework.org/
    url(r'^api-auth/', include('rest_framework.urls')),

    # REST actions
    #url(r'^api/fblogin/', api.FacebookLogin.as_view(), name='api-fblogin'),
    url(r'^api/users/', api.SocialLogin.as_view(), name='api-social-login'),
    url(r'^api/login/?', api.EmailLogin.as_view(), name='api-login'),
    url(r'^api/logout/', api.Logout.as_view(), name='api-logout'),
    url(r'^api/functions/(?P<function>\w+)/$', api.CloudCode.as_view(), name='api-cloudcode'),
]

urlpatterns += static('/static/', document_root=settings.STATIC_ROOT)

def url_plain(url_part, view=None, name=None):
    if not view: view = url_part.replace('/', '_').replace('-', '_')
    if not name: name = 'lp/' + url_part.replace('-', '/').replace('_', '/')
    if url_part:
        url_part += '/'
    return url('^' + url_part + r'$', view, name=name)

urlpatterns += [
    url_plain('portal', views.portal),
    url_plain('learn', views.learn),
    url_plain('codes', views.codes),
]
