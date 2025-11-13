from django.contrib import admin
from .models import RechercheUtilisateur

@admin.register(RechercheUtilisateur)
class RechercheUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('email_utilisateur', 'question_recherche', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    search_fields = ('email_utilisateur', 'question_recherche')
    readonly_fields = ('date_creation',)