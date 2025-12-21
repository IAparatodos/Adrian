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

    def search_cards_by_query(self, query: str, page: int = 1, order: str = 'edhrec') -> Dict:
        """
        Busca cartas usando la sintaxis de búsqueda de Scryfall

        Args:
            query: Query de búsqueda (ej: "f:commander c:green")
            page: Número de página
            order: Orden de resultados (edhrec, name, cmc, usd, etc.)

        Returns:
            Diccionario con resultados paginados
        """
        self._rate_limit()
        try:
            response = self.session.get(
                f"{self.BASE_URL}/cards/search",
                params={'q': query, 'page': page, 'order': order}
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
        Ordenadas por popularidad en EDHREC

        Args:
            commander_name: Nombre del comandante
            colors: Lista de colores (W, U, B, R, G)
            limit: Número máximo de cartas a retornar

        Returns:
            Lista de cartas recomendadas ordenadas por popularidad EDHREC
        """
        color_identity = ''.join(sorted(colors))

        # Búsqueda de cartas populares en Commander con esos colores
        # Ordenadas por EDHREC rank (más populares primero)
        queries = [
            # Staples generales (sol ring, command tower, etc)
            f"legal:commander ci<={color_identity} -t:basic -t:land",
            # Criaturas populares
            f"legal:commander ci<={color_identity} t:creature",
            # Instants y Sorceries
            f"legal:commander ci<={color_identity} (t:instant OR t:sorcery)",
            # Artefactos y Encantamientos
            f"legal:commander ci<={color_identity} (t:artifact OR t:enchantment) -t:creature",
        ]

        all_cards = []
        cards_per_category = limit // len(queries)

        for query in queries:
            # Ordena por EDHREC rank (más populares primero)
            result = self.search_cards_by_query(query, order='edhrec')
            category_cards = result.get('data', [])[:cards_per_category]
            all_cards.extend(category_cards)

            if len(all_cards) >= limit:
                break

        # Si necesitamos más cartas, añade una búsqueda general
        if len(all_cards) < limit:
            remaining = limit - len(all_cards)
            general_query = f"legal:commander ci<={color_identity} -t:basic"
            result = self.search_cards_by_query(general_query, order='edhrec')
            all_cards.extend(result.get('data', [])[:remaining])

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
