"""
Módulo para interactuar con la API de Scryfall
Documentación: https://scryfall.com/docs/api
"""
import requests
import time
from typing import Dict, List, Optional


class ScryfallAPI:
    """Cliente para la API de Scryfall"""

    BASE_URL = "https://api.scryfall.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MTGCommanderBuilder/1.0',
            'Accept': 'application/json'
        })
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requests (Scryfall recomienda 50-100ms)

    def _rate_limit(self):
        """Implementa rate limiting para respetar las reglas de Scryfall"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def search_card(self, card_name: str) -> Optional[Dict]:
        """
        Busca una carta exacta por nombre

        Args:
            card_name: Nombre de la carta

        Returns:
            Diccionario con los datos de la carta o None si no se encuentra
        """
        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.BASE_URL}/cards/named",
                params={'exact': card_name}
            )
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                # Intenta búsqueda fuzzy
                return self.fuzzy_search_card(card_name)
            return None
        except Exception as e:
            print(f"Error buscando carta: {e}")
            return None

    def fuzzy_search_card(self, card_name: str) -> Optional[Dict]:
        """Búsqueda fuzzy de carta (encuentra coincidencias aproximadas)"""
        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.BASE_URL}/cards/named",
                params={'fuzzy': card_name}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error en búsqueda fuzzy: {e}")
            return None

    def search_cards_by_query(self, query: str, page: int = 1) -> Dict:
        """
        Busca cartas usando la sintaxis de búsqueda de Scryfall

        Args:
            query: Query de búsqueda (ej: "f:commander c:green")
            page: Número de página

        Returns:
            Diccionario con resultados paginados
        """
        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.BASE_URL}/cards/search",
                params={'q': query, 'page': page}
            )
            if response.status_code == 200:
                return response.json()
            return {'data': [], 'has_more': False}
        except Exception as e:
            print(f"Error en búsqueda avanzada: {e}")
            return {'data': [], 'has_more': False}

    def get_commander_recommendations(self, commander_name: str, colors: List[str], limit: int = 50) -> List[Dict]:
        """
        Busca cartas legales en Commander que compartan colores con el comandante

        Args:
            commander_name: Nombre del comandante
            colors: Lista de colores (W, U, B, R, G)
            limit: Número máximo de cartas a retornar

        Returns:
            Lista de cartas recomendadas
        """
        color_identity = ''.join(sorted(colors))

        # Búsqueda de cartas populares en Commander con esos colores
        queries = [
            f"legal:commander ci<={color_identity} -t:basic -type:land",  # Hechizos generales
            f"legal:commander ci<={color_identity} t:creature",  # Criaturas
            f"legal:commander ci<={color_identity} t:instant OR t:sorcery",  # Instant/Sorcery
            f"legal:commander ci<={color_identity} t:artifact OR t:enchantment"  # Artefactos/Encantamientos
        ]

        all_cards = []
        for query in queries:
            result = self.search_cards_by_query(query)
            all_cards.extend(result.get('data', [])[:limit // 4])
            if len(all_cards) >= limit:
                break

        return all_cards[:limit]

    def get_card_price(self, card_data: Dict) -> Dict[str, Optional[float]]:
        """
        Extrae información de precios de una carta

        Args:
            card_data: Datos de la carta de Scryfall

        Returns:
            Diccionario con precios en diferentes monedas
        """
        prices = card_data.get('prices', {})
        return {
            'usd': float(prices.get('usd')) if prices.get('usd') else None,
            'eur': float(prices.get('eur')) if prices.get('eur') else None,
            'tix': float(prices.get('tix')) if prices.get('tix') else None,
            'cardmarket': float(prices.get('eur')) if prices.get('eur') else None  # EUR es CardMarket
        }

    def get_random_commander(self) -> Optional[Dict]:
        """Obtiene un comandante aleatorio"""
        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.BASE_URL}/cards/random",
                params={'q': 'is:commander'}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error obteniendo comandante aleatorio: {e}")
            return None
