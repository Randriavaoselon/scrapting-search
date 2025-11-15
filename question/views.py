from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from django.http import JsonResponse


from .models import RechercheUtilisateur, Commentaire, CompteurVisiteurs
from .serializers import RechercheUtilisateurSerializer, CommentaireSerializer, CompteurVisiteursSerializer
from .services import GoogleSearchService, StackOverflowService
import threading


class RechercheUtilisateurViewSet(viewsets.ModelViewSet):
    queryset = RechercheUtilisateur.objects.all()
    serializer_class = RechercheUtilisateurSerializer
    
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = serializer.save()
        
        thread = threading.Thread(
            target=self.lancer_recherche_automatique,
            args=(instance.id,)
        )
        thread.daemon = True
        thread.start()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def lancer_recherche_automatique(self, recherche_id):
        try:
            recherche = RechercheUtilisateur.objects.get(id=recherche_id)
            recherche.statut = 'en_cours'
            recherche.save()
            
            resultats_google = GoogleSearchService.search_google(
                recherche.question_recherche
            )
            
            resultats_stackoverflow = StackOverflowService.search_stackoverflow(
                recherche.question_recherche
            )
            
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
            
            recherche.resultats_recherche = resultats_complets
            recherche.statut = 'termine'
            recherche.save()
            
        except Exception as e:
            try:
                recherche = RechercheUtilisateur.objects.get(id=recherche_id)
                recherche.statut = 'erreur'
                recherche.resultats_recherche = {'erreur': str(e)}
                recherche.save()
            except:
                pass


    @action(detail=False, methods=['post'])
    def recherche_immediate(self, request):
        question = request.data.get('question_recherche')
        email = request.data.get('email_utilisateur')
        
        if not question:
            return Response(
                {"error": "Le champ 'question_recherche' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultats_google = GoogleSearchService.search_google(question)
        resultats_stackoverflow = StackOverflowService.search_stackoverflow(question)
        
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
        recherche = self.get_object()
        return Response({
            'id': recherche.id,
            'question': recherche.question_recherche,
            'statut': recherche.statut,
            'resultats': recherche.resultats_recherche or {}
        })
    
    @action(detail=False, methods=['get'])
    def rechercher_solutions(self, request):
        query = request.query_params.get('q', '')
        email_utilisateur = request.query_params.get('email', 'anonymous@example.com')
        
        if not query:
            return Response(
                {"error": "Le paramètre 'q' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resultats_google = GoogleSearchService.search_google(query)
        resultats_stackoverflow = StackOverflowService.search_stackoverflow(query)
        
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
        email = request.query_params.get('email', '')
        
        if not email:
            return Response(
                {"error": "Le paramètre 'email' est requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recherches = RechercheUtilisateur.objects.filter(
            email_utilisateur=email
        ).order_by('-date_creation')[:50]
        
        serializer = self.get_serializer(recherches, many=True)
        return Response({
            'email': email,
            'total_recherches': recherches.count(),
            'historique': serializer.data
        })


# Vue Commentaire avec CSRF exempt
@method_decorator(csrf_exempt, name='dispatch')
class CommentaireViewSet(viewsets.ModelViewSet):
    queryset = Commentaire.objects.all()
    serializer_class = CommentaireSerializer
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_queryset(self):
        # Trier par date de création décroissante (les plus récents en premier)
        return Commentaire.objects.filter(approuve=True).order_by('-date_creation')
    
    def list(self, request):
        # Surcharger la méthode list pour retourner une liste
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer le commentaire avec seulement le username
        commentaire = Commentaire.objects.create(
            username=serializer.validated_data['username'],
            message=serializer.validated_data['message'],
            approuve=True
        )
        
        # Sérialiser le nouveau commentaire pour la réponse
        response_serializer = self.get_serializer(commentaire)
        
        return Response({
            'message': 'Votre commentaire a été publié avec succès!',
            'commentaire': response_serializer.data
        }, status=status.HTTP_201_CREATED)


class CompteurVisiteursViewSet(viewsets.ViewSet):
    def list(self, request):
        compteur, created = CompteurVisiteurs.objects.get_or_create(
            id=1,
            defaults={'nombre_visites': 0}
        )
        
        serializer = CompteurVisiteursSerializer(compteur)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class SearchFrontendView(View):
    def get(self, request):
        compteur, created = CompteurVisiteurs.objects.get_or_create(
            id=1,
            defaults={'nombre_visites': 0}
        )
        compteur.nombre_visites += 1
        compteur.save()
        
        return render(request, 'index.html')


# Vue pour obtenir le token CSRF
@method_decorator(csrf_exempt, name='dispatch')
class GetCSRFToken(View):
    def get(self, request):
        return JsonResponse({'csrfToken': get_token(request)})