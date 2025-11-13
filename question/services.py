import requests
import time
import json
import os
from django.conf import settings
import random

class GoogleSearchService:
    @staticmethod
    def search_google(query, num_results=10):
        """
        Recherche Google utilisant l'API Google Custom Search
        """
        try:
            # Configuration de l'API Google Custom Search
            api_key = getattr(settings, 'GOOGLE_API_KEY', 'VOTRE_CLE_API_GOOGLE')
            search_engine_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', 'VOTRE_ID_MOTEUR_RECHERCHE')
            
            if api_key == 'VOTRE_CLE_API_GOOGLE' or search_engine_id == 'VOTRE_ID_MOTEUR_RECHERCHE':
                return GoogleSearchService._get_fallback_results(query, "google")
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    'titre': item.get('title', 'Sans titre'),
                    'url': item.get('link', ''),
                    'description': item.get('snippet', ''),
                    'source': 'google'
                })
            
            return {
                "query_original": query,
                "nombre_resultats": len(results),
                "resultats": results,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Erreur API Google: {e}")
            # Fallback vers des résultats simulés avec des URLs réelles
            return GoogleSearchService._get_fallback_results(query, "google")
    
    @staticmethod
    def _get_fallback_results(query, source):
        """Résultats de fallback avec des URLs réelles et fonctionnelles"""
        # URLs réelles et fonctionnelles pour les résultats simulés
        real_urls = [
            f"https://www.google.com/search?q={requests.utils.quote(query)}",
            f"https://developer.mozilla.org/fr/search?q={requests.utils.quote(query)}",
            f"https://www.w3schools.com/search.php?search={requests.utils.quote(query)}",
            f"https://stackoverflow.com/search?q={requests.utils.quote(query)}",
            f"https://github.com/search?q={requests.utils.quote(query)}",
            f"https://docs.python.org/3/search.html?q={requests.utils.quote(query)}",
            f"https://docs.djangoproject.com/fr/search/?q={requests.utils.quote(query)}",
            f"https://www.youtube.com/results?search_query={requests.utils.quote(query)}",
            f"https://fr.wikipedia.org/wiki/Special:Search?search={requests.utils.quote(query)}",
            f"https://www.reddit.com/search/?q={requests.utils.quote(query)}"
        ]
        
        results = []
        for i in range(5):
            results.append({
                'titre': f"Résultat Google {i+1} pour: {query}",
                'url': real_urls[i % len(real_urls)],
                'description': f"Ceci est un résultat simulé pour votre recherche: '{query}'. Pour obtenir des résultats réels de Google, configurez l'API Google Custom Search avec votre clé API et ID de moteur de recherche.",
                'source': source
            })
        
        return {
            "query_original": query,
            "nombre_resultats": len(results),
            "resultats": results,
            "timestamp": time.time(),
            "note": "⚠️ Résultats simulés - Configurez l'API Google pour des résultats réels"
        }

class StackOverflowService:
    @staticmethod
    def search_stackoverflow(query, num_results=5):
        """
        Recherche spécifique sur StackOverflow via l'API
        """
        try:
            url = "https://api.stackexchange.com/2.3/search"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'intitle': query,
                'site': 'stackoverflow',
                'pagesize': num_results,
                'filter': 'withbody'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                # Créer une description plus informative
                description = f"Score: {item['score']} | Réponses: {item['answer_count']}"
                if item.get('is_answered', False):
                    description += " ✅ Résolu"
                
                results.append({
                    'titre': item['title'],
                    'url': item['link'],
                    'description': description,
                    'tags': item['tags'][:5],  # Limiter à 5 tags
                    'view_count': item.get('view_count', 0),
                    'source': 'stackoverflow'
                })
            
            return {
                "query_original": query,
                "nombre_resultats": len(results),
                "resultats": results,
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Erreur StackOverflow API: {e}")
            return StackOverflowService._get_fallback_results(query, "stackoverflow")
    
    @staticmethod
    def _get_fallback_results(query, source):
        """Résultats de fallback pour StackOverflow avec URLs réelles"""
        # URLs de recherche réelles pour StackOverflow
        search_urls = [
            f"https://stackoverflow.com/search?q={requests.utils.quote(query)}",
            f"https://stackoverflow.com/questions/tagged/{requests.utils.quote(query.split()[0]) if query.split() else 'python'}",
            "https://stackoverflow.com/questions/",
            "https://stackoverflow.com/users/signup?ssrc=product_home",
            "https://stackoverflow.com/jobs"
        ]
        
        results = []
        programming_languages = ["Python", "JavaScript", "Java", "C++", "PHP", "Ruby", "Go", "Rust"]
        frameworks = ["Django", "React", "Vue", "Angular", "Spring", "Laravel", "Rails"]
        
        for i in range(3):
            lang = random.choice(programming_languages)
            framework = random.choice(frameworks)
            
            results.append({
                'titre': f"Comment résoudre '{query}' en {lang} avec {framework} ?",
                'url': search_urls[i % len(search_urls)],
                'description': f"Question simulée sur {query}. Score: {random.randint(1, 50)}, Réponses: {random.randint(1, 10)}, Vues: {random.randint(100, 1000)}",
                'tags': [lang.lower(), framework.lower(), "web", "development", "programming"],
                'source': source
            })
        
        return {
            "query_original": query,
            "nombre_resultats": len(results),
            "resultats": results,
            "timestamp": time.time(),
            "note": "⚠️ Résultats simulés - L'API StackOverflow peut être temporairement indisponible"
        }