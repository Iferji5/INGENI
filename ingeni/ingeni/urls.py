"""
URL configuration for ingeni project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('productos/', views.productos, name='productos'),
    path('productos/<slug:slug>/', views.product_detail, name='product_detail'),  # ← NUEVA
    path('sobre/', views.sobre, name='sobre'),
    path('contacto/', views.contacto, name='contacto'),
    path('proyectos/<slug:slug>/', views.project_detail, name='project_detail'),
    path('panel/login/', auth_views.LoginView.as_view(template_name="panel_login.html"), name='panel_login'),
    path('panel/logout/', auth_views.LogoutView.as_view(), name='panel_logout'),
    path('panel/proyectos/', views.panel_project_list, name='panel_project_list'),
    path('panel/proyectos/nuevo/', views.panel_project_create, name='panel_project_create'),
    path('panel/proyectos/<int:pk>/', views.panel_project_edit, name='panel_project_edit'),
    path('panel/proyectos/<int:pk>/eliminar/', views.panel_project_delete, name='panel_project_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

