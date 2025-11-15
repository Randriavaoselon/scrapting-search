from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("recherches", views.RechercheUtilisateurViewSet)
router.register("compteur", views.CompteurVisiteursViewSet, basename='compteur')
router.register("commentaires", views.CommentaireViewSet, basename='commentaires')  # Changé ici

urlpatterns = [
    path('', views.SearchFrontendView.as_view(), name='frontend'),
    path('api/', include(router.urls)),
    path('api/csrf-token/', views.GetCSRFToken.as_view(), name='csrf_token'),  # Nouvelle route
]