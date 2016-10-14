"""CMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url,include
from django.contrib import admin
from CMDB_Server import  views
import settings

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    url(r'^$', views.main),
    url(r'^accounts/login/', views.acclogin, name='login'),
    url(r'^accounts/logout/', views.acclogout, name='logout'),
    url(r'^cmdb/', include('CMDB_Server.urls')),
    url(r'^recv_data/', views.recvdata),
    url(r'^accounts/', views.createuser,name='createuser'),
    #url(r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT})
]

#handler404 = 'CMDB_Server.views.page_not_found'
