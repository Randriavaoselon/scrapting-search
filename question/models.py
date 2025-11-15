from django.db import models
from django.core.validators import MinLengthValidator


class RechercheUtilisateur(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de traitement'),
        ('termine', 'Terminé'),
        ('erreur', 'Erreur')
    ]
    
    question_recherche = models.TextField(verbose_name="Question de recherche", null=True)
    email_utilisateur = models.EmailField(verbose_name="Adresse Email", null=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de creation")
    resultats_recherche = models.JSONField(verbose_name="Résultats de recherche", null=True, blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )


    class Meta:
        verbose_name = "Recherche utilisateur"
        verbose_name_plural = "Recherches utilisateurs"
        ordering = ['-date_creation']


    def __str__(self):
        return f"{self.email_utilisateur} - {self.question_recherche[:50]}"


class Commentaire(models.Model):
    username = models.CharField(max_length=100, verbose_name="Nom d'utilisateur", null=True)
    message = models.TextField(
        verbose_name="Commentaire",
        validators=[MinLengthValidator(10, "Le commentaire doit contenir au moins 10 caractères")]
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création", null=True)
    approuve = models.BooleanField(default=True, verbose_name="Approuvé", null=True)


    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['-date_creation']


    def __str__(self):
        return f"{self.username} - {self.message[:50]}"


class CompteurVisiteurs(models.Model):
    nombre_visites = models.PositiveIntegerField(default=0, verbose_name="Nombre de visites", null=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour", null=True)


    class Meta:
        verbose_name = "Compteur de visiteurs"
        verbose_name_plural = "Compteurs de visiteurs"


    def __str__(self):
        return f"{self.nombre_visites} visites"