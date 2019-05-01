"""yqnet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django_registration.backends.one_step.views import RegistrationView
from django.views.generic.base import TemplateView

from ui_yqn import views

urlpatterns = [
    path('', views.PostsView.as_view(), name="index"),

    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('privacy/', TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    path('contact/', TemplateView.as_view(template_name="contact_yqn.html"), name="contact"),
    path('whatsapp/', TemplateView.as_view(template_name="whatsapp.html"), name="whatsapp"),

    path('posts/', views.PostsView.as_view(), name="posts"),
    path('posts/twitter/', views.TwittersView.as_view(), name="twitters"),
    path('posts/instagram/', views.InstagramView.as_view(), name="instagram"),

    path('events/list/', views.EventsListingView.as_view(), name="events"),
    path('events/map/', views.MapView.as_view(), name="map"),
    path('event/<int:pk>/', views.EventView.as_view(), name="event"),

    path('venue/<int:pk>/', views.EventsAtVenueView.as_view(), name="venue"),

    path('groups/', views.GroupPagesView.as_view(), name="pages"),

    path('api/', include('db_yqn.urls', namespace="api")),

    # Acounts stuff
    path('accounts/edit', views.UpdateUserDetailsView.as_view(), name="edit-profile"),
    path('accounts/', include('django.contrib.auth.urls')),

    path('accounts/register/',
        RegistrationView.as_view(success_url=reverse_lazy("index")),
        name='django_registration_register'),

    path('accounts/', include('django_registration.backends.one_step.urls')),


    path('oauth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),


    # Capture all other url paths before this one
    path('<slug:slug>/', views.GroupPageView.as_view(), name="user-pages"),
    path('<slug:slug>/edit/', views.GroupPageEditView.as_view(),
         name="user-page-edit"),
    path('<slug:slug>/events/', views.EventsListingView.as_view(),
         name="user-page-events"),

    # temp
    path("<slug:slug>/permissions/<int:pk>", views.GroupPageEditorsUpdate.as_view(), name="user-page-permissions"),
]


# Dev purposes
# Media upload files serving for dev purposes
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Make sure we don't see 404 errors for the favicon
# In production this would be provided by the webserver
urlpatterns += [
    path('favicon.ico',RedirectView.as_view(url='%simgs/fav/favicon-16x16.png' % settings.STATIC_URL)),
]
