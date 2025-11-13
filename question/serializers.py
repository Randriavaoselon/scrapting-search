from rest_framework import serializers
from .models import RechercheUtilisateur

class RechercheUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = RechercheUtilisateur
        fields = [
            'id', 'question_recherche', 'email_utilisateur', 
            'date_creation', 'resultats_recherche', 'statut'
        ]
        read_only_fields = ['id', 'date_creation', 'resultats_recherche', 'statut']

    def validate_question_recherche(self, value):
        """Validation pour le champ question"""
        if not value or not value.strip():
            raise serializers.ValidationError("La question de recherche est requise")
        return value.strip()
    
    def validate_email_utilisateur(self, value):
        """Validation pour l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise")
        return value