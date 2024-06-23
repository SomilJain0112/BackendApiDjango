"""
URL configuration for credit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# credit/urls.py
from django.contrib import admin
from django.http import JsonResponse
#from . import views
from django.urls import path
from temp.views import *
from transactions.views import *
from user.views import *
from loan.views import *

urlpatterns = [
    path('', temp, name='temp'),
    path('admin/', admin.site.urls),
    path('transactions/initialise/', initialise, name='initialise'),
    path('api/register-user/', create_user, name='register'),
    path('api/get-statement/', get_statement, name='statement'),
    path('api/make-payment/', make_payment, name='payment'),
    path('api/apply-loan/', apply_loan, name='apply'),
]
