"""cardcraft URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from cardcraft import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", views.loginUser),
    path("change-password/", views.changePassword),
    path("signup/", views.createUser),
    path("cardset/", views.makeCardSet),
    path("cardset/delete/", views.deleteCardSet),
    path("cardset/save/", views.saveCardSet),
    path("userInfo/", views.userInfo),
    path("cardset/get/", views.getCardSet),
    path("cardset/delete/", views.deleteCardSet),
    path("cardset/get/user/",views.getCardSetsByUser)
]
