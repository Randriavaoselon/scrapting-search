from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("recherches", views.RechercheUtilisateurViewSet)

urlpatterns = [
    path('', views.SearchFrontendView.as_view(), name='frontend'),
    path('api/', include(router.urls))
]