from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.views import View

from .models import RechercheUtilisateur
from .serializers import RechercheUtilisateurSerializer
from .services import GoogleSearchService, StackOverflowService
import threading

class RechercheUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = RechercheUtilisateur.objects.all()
    serializer_class = RechercheUtilisateurSerializer
    
    # Autoriser toutes les méthodes HTTP nécessaires
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    def create(self, request, *args, **kwargs):
        """
        Surcharge de la méthode create pour lancer la recherche en arrière-plan
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Sauvegarder l'instance d'abord
        instance = serializer.save()
        
        # Lancer la recherche en arrière-plan
        thread = threading.Thread(
            target=self.lancer_recherche_automatique,
            args=(instance.id,)
        )
        thread.daemon = True
        thread.start()
        
        # Retourner la réponse immédiate
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def lancer_recherche_automatique(self, recherche_id):
        """
        Méthode pour lancer la recherche automatique en arrière-plan
        """
        try:
            recherche = RechercheUtilisateur.objects.get(id=recherche_id)
            recherche.statut = 'en_cours'
            recherche.save()
            
            # Recherche Google
            resultats_google = GoogleSearchService.search_google(
                recherche.question_recherche
            )
            
            # Recherche StackOverflow
            resultats_stackoverflow = StackOverflowService.search_stackoverflow(
                recherche.question_recherche
            )
            
            # Combiner les résultats
            resultats_complets = {
                'google': resultats_google,
                'stackoverflow': resultats_stackoverflow,
                'resume': {
                    'total_resultats': (
                        resultats_google.get('nombre_resultats', 0) + 
                        resultats_stackoverflow.get('nombre_resultats', 0)
                    )
                }
            }
            
            # Sauvegarder les résultats
            recherche.resultats_recherche = resultats_complets
            recherche.statut = 'termine'
            recherche.save()
            
        except Exception as e:
            # Gérer les erreurs
            try:
                recherche = RechercheUtilisateur.objects.get(id=recherche_id)
                recherche.statut = 'erreur'
                recherche.resultats_recherche = {'erreur': str(e)}
                recherche.save()
            except:
                pass
    
    @action(detail=False, methods=['post'])
    def recherche_immediate(self, request):
        """
        Endpoint pour une recherche immédiate avec retour synchrone
        """
        question = request.data.get('question_recherche')
        email = request.data.get('email_utilisateur')
        
        if not question:
            return Response(
                {"error": "Le champ 'question_recherche' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Recherches immédiates
        resultats_google = GoogleSearchService.search_google(question)
        resultats_stackoverflow = StackOverflowService.search_stackoverflow(question)
        
        # Créer l'enregistrement
        recherche = RechercheUtilisateur.objects.create(
            question_recherche=question,
            email_utilisateur=email or "anonymous@example.com",
            resultats_recherche={
                'google': resultats_google,
                'stackoverflow': resultats_stackoverflow
            },
            statut='termine'
        )
        
        serializer = self.get_serializer(recherche)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resultats(self, request, pk=None):
        """
        Récupérer spécifiquement les résultats d'une recherche
        """
        recherche = self.get_object()
        return Response({
            'id': recherche.id,
            'question': recherche.question_recherche,
            'statut': recherche.statut,
            'resultats': recherche.resultats_recherche or {}
        })
    
    @action(detail=False, methods=['get'])
    def rechercher_solutions(self, request):
        """
        Recherche directe avec sauvegarde automatique en base
        """
        query = request.query_params.get('q', '')
        email_utilisateur = request.query_params.get('email', 'anonymous@example.com')
        
        if not query:
            return Response(
                {"error": "Le paramètre 'q' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Recherches simultanées
        resultats_google = GoogleSearchService.search_google(query)
        resultats_stackoverflow = StackOverflowService.search_stackoverflow(query)
        
        # Sauvegarder automatiquement la recherche avec l'email
        recherche = RechercheUtilisateur.objects.create(
            question_recherche=query,
            email_utilisateur=email_utilisateur,
            resultats_recherche={
                'google': resultats_google,
                'stackoverflow': resultats_stackoverflow
            },
            statut='termine'
        )
        
        return Response({
            'query': query,
            'recherche_id': recherche.id,
            'sources': {
                'google': resultats_google,
                'stackoverflow': resultats_stackoverflow
            }
        })
    
    @action(detail=False, methods=['get'])
    def historique_utilisateur(self, request):
        """
        Récupérer l'historique des recherches d'un utilisateur
        """
        email = request.query_params.get('email', '')
        
        if not email:
            return Response(
                {"error": "Le paramètre 'email' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recherches = RechercheUtilisateur.objects.filter(
            email_utilisateur=email
        ).order_by('-date_creation')[:50]  # Limiter à 50 dernières recherches
        
        serializer = self.get_serializer(recherches, many=True)
        return Response({
            'email': email,
            'total_recherches': recherches.count(),
            'historique': serializer.data
        })

class SearchFrontendView(View):
    def get(self, request):
        return render(request, 'index.html')