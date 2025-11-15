from rest_framework import serializers
from .models import RechercheUtilisateur, Commentaire, CompteurVisiteurs


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


class CommentaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentaire
        fields = ['id', 'username', 'message', 'date_creation', 'approuve']
        read_only_fields = ['id', 'date_creation', 'approuve']


    def validate_message(self, value):
        """Validation pour le message"""
        if not value or not value.strip():
            raise serializers.ValidationError("Le commentaire ne peut pas être vide")
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Le commentaire doit contenir au moins 10 caractères")
        return value.strip()


class CompteurVisiteursSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteurVisiteurs
        fields = ['nombre_visites', 'date_mise_a_jour']