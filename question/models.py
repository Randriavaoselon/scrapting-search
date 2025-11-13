from django.db import models

class RechercheUtilisateur(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours de traitement'),
        ('termine', 'Terminé'),
        ('erreur', 'Erreur')
    ]
    
    question_recherche = models.TextField(verbose_name="Question de recherche")
    email_utilisateur = models.EmailField(verbose_name="Adresse Email")
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