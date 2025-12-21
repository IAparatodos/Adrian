"""
Módulo para analizar sinergias entre cartas de Magic
Analiza tipos, palabras clave, mecánicas y temas
"""
from typing import Dict, List, Set
import re


class SynergyAnalyzer:
    """Analizador de sinergias entre cartas de Magic"""

    # Palabras clave y mecánicas importantes
    KEYWORDS = {
        'draw': ['draw', 'card draw', 'cantrip'],
        'ramp': ['ramp', 'search.*land', 'add.*mana', 'treasure', 'lotus'],
        'removal': ['destroy', 'exile', 'counter', 'return.*hand', 'sacrifice'],
        'protection': ['indestructible', 'hexproof', 'shroud', 'ward', 'protection'],
        'tribal': ['elf', 'goblin', 'dragon', 'zombie', 'vampire', 'merfolk', 'angel', 'demon'],
        'tokens': ['token', 'create.*creature'],
        'graveyard': ['graveyard', 'return.*from.*graveyard', 'flashback', 'delve'],
        'counter': [r'\+1/\+1 counter', 'proliferate', 'counter'],  # Escapado con r'' y \+
        'combat': ['double strike', 'first strike', 'trample', 'menace', 'vigilance'],
        'etb': ['enters the battlefield', 'when.*enters'],
        'sacrifice': ['sacrifice', 'dies', 'when.*dies'],
        'cost_reduction': ['cost.*less', 'without paying'],
        'storm': ['storm', 'cast.*instant', 'cast.*sorcery'],
    }

    # Tipos de carta importantes
    CARD_TYPES = ['creature', 'instant', 'sorcery', 'artifact', 'enchantment', 'planeswalker', 'land']

    def __init__(self):
        pass

    def calculate_synergy_score(self, card: Dict, reference_cards: List[Dict]) -> float:
        """
        Calcula un score de sinergia entre una carta y un conjunto de cartas de referencia

        Args:
            card: Carta a evaluar
            reference_cards: Cartas del mazo con las que comparar

        Returns:
            Score de sinergia (0-100)
        """
        if not reference_cards:
            return 50.0  # Score neutral si no hay referencia

        scores = []
        for ref_card in reference_cards:
            score = self._compare_cards(card, ref_card)
            scores.append(score)

        # Retorna el promedio de los mejores matches
        scores.sort(reverse=True)
        top_scores = scores[:min(5, len(scores))]
        return sum(top_scores) / len(top_scores) if top_scores else 50.0

    def _compare_cards(self, card1: Dict, card2: Dict) -> float:
        """Compara dos cartas y retorna un score de sinergia"""
        score = 0.0

        # Compara colores (10 puntos)
        color_score = self._compare_colors(card1, card2)
        score += color_score * 10

        # Compara tipos (15 puntos)
        type_score = self._compare_types(card1, card2)
        score += type_score * 15

        # Compara palabras clave y mecánicas (40 puntos)
        keyword_score = self._compare_keywords(card1, card2)
        score += keyword_score * 40

        # Compara texto de habilidades (25 puntos)
        text_score = self._compare_oracle_text(card1, card2)
        score += text_score * 25

        # Compara curva de maná (10 puntos)
        mana_score = self._compare_mana_value(card1, card2)
        score += mana_score * 10

        return min(score, 100.0)

    def _compare_colors(self, card1: Dict, card2: Dict) -> float:
        """Compara la identidad de color entre dos cartas"""
        colors1 = set(card1.get('color_identity', []))
        colors2 = set(card2.get('color_identity', []))

        if not colors1 and not colors2:
            return 1.0

        if not colors1 or not colors2:
            return 0.5

        # Calcula Jaccard similarity
        intersection = len(colors1.intersection(colors2))
        union = len(colors1.union(colors2))

        return intersection / union if union > 0 else 0.0

    def _compare_types(self, card1: Dict, card2: Dict) -> float:
        """Compara tipos de carta"""
        type_line1 = card1.get('type_line', '').lower()
        type_line2 = card2.get('type_line', '').lower()

        # Extrae tipos principales
        types1 = self._extract_types(type_line1)
        types2 = self._extract_types(type_line2)

        if not types1 or not types2:
            return 0.0

        # Bonus si comparten supertipo (legendary, basic, etc)
        if 'legendary' in type_line1 and 'legendary' in type_line2:
            return 0.8

        # Compara tipos principales
        intersection = len(types1.intersection(types2))
        union = len(types1.union(types2))

        return intersection / union if union > 0 else 0.0

    def _extract_types(self, type_line: str) -> Set[str]:
        """Extrae tipos de una línea de tipo"""
        types = set()
        type_line_lower = type_line.lower()

        for card_type in self.CARD_TYPES:
            if card_type in type_line_lower:
                types.add(card_type)

        return types

    def _compare_keywords(self, card1: Dict, card2: Dict) -> float:
        """Compara palabras clave y mecánicas"""
        keywords1 = card1.get('keywords', [])
        keywords2 = card2.get('keywords', [])

        if not keywords1 and not keywords2:
            return 0.0

        keywords1_lower = set(k.lower() for k in keywords1)
        keywords2_lower = set(k.lower() for k in keywords2)

        if not keywords1_lower or not keywords2_lower:
            return 0.0

        intersection = len(keywords1_lower.intersection(keywords2_lower))
        union = len(keywords1_lower.union(keywords2_lower))

        return intersection / union if union > 0 else 0.0

    def _compare_oracle_text(self, card1: Dict, card2: Dict) -> float:
        """Compara el texto de las cartas buscando mecánicas compartidas"""
        text1 = card1.get('oracle_text', '').lower()
        text2 = card2.get('oracle_text', '').lower()

        if not text1 or not text2:
            return 0.0

        # Busca temas compartidos
        shared_themes = 0
        total_themes = 0

        for theme, patterns in self.KEYWORDS.items():
            found_in_1 = any(re.search(pattern, text1) for pattern in patterns)
            found_in_2 = any(re.search(pattern, text2) for pattern in patterns)

            if found_in_1 or found_in_2:
                total_themes += 1
            if found_in_1 and found_in_2:
                shared_themes += 1

        return shared_themes / total_themes if total_themes > 0 else 0.0

    def _compare_mana_value(self, card1: Dict, card2: Dict) -> float:
        """Compara valor de maná para mantener curva equilibrada"""
        cmc1 = card1.get('cmc', 0)
        cmc2 = card2.get('cmc', 0)

        # Penaliza cartas muy diferentes en costo
        diff = abs(cmc1 - cmc2)

        if diff == 0:
            return 1.0
        elif diff <= 2:
            return 0.7
        elif diff <= 4:
            return 0.4
        else:
            return 0.1

    def get_card_themes(self, card: Dict) -> List[str]:
        """Identifica los temas principales de una carta"""
        themes = []
        oracle_text = card.get('oracle_text', '').lower()
        type_line = card.get('type_line', '').lower()

        # Analiza palabras clave
        for theme, patterns in self.KEYWORDS.items():
            if any(re.search(pattern, oracle_text) or re.search(pattern, type_line) for pattern in patterns):
                themes.append(theme)

        return themes

    def find_synergies(self, deck_cards: List[Dict], candidate_cards: List[Dict],
                       top_n: int = 20) -> List[Dict]:
        """
        Encuentra las cartas candidatas con mejor sinergia para el mazo
        Da peso extra a cartas que sinergicen con el comandante

        Args:
            deck_cards: Cartas actuales en el mazo (incluye comandante)
            candidate_cards: Cartas candidatas a añadir
            top_n: Número de mejores cartas a retornar

        Returns:
            Lista de cartas ordenadas por score combinado (sinergia + popularidad)
        """
        scored_cards = []

        # Identifica el comandante (primera carta o la que sea Legendary Creature)
        commander = None
        for card in deck_cards:
            type_line = card.get('type_line', '').lower()
            if 'legendary' in type_line and 'creature' in type_line:
                commander = card
                break

        for candidate in candidate_cards:
            # Evita duplicados
            if any(c.get('name') == candidate.get('name') for c in deck_cards):
                continue

            score = self.calculate_synergy_score(candidate, deck_cards)
            themes = self.get_card_themes(candidate)

            # Bonus: Da peso extra a sinergia con el comandante
            if commander:
                commander_synergy = self._compare_cards(candidate, commander)
                # Bonus de hasta 15% si hay muy buena sinergia con comandante
                commander_bonus = (commander_synergy / 100) * 15
                score = min(score + commander_bonus, 100.0)

            # Calcula score de popularidad basado en EDHREC rank
            popularity_score = self._calculate_popularity_score(candidate)

            # Score final combinado: 75% sinergia + 25% popularidad
            # (Mayor peso a sinergia para priorizar compatibilidad con el mazo)
            combined_score = (score * 0.75) + (popularity_score * 0.25)

            scored_cards.append({
                'card': candidate,
                'synergy_score': score,
                'popularity_score': popularity_score,
                'combined_score': combined_score,
                'themes': themes
            })

        # Ordena por score combinado (sinergia + popularidad)
        scored_cards.sort(key=lambda x: x['combined_score'], reverse=True)

        return scored_cards[:top_n]

    def _calculate_popularity_score(self, card: Dict) -> float:
        """
        Calcula score de popularidad basado en EDHREC rank

        Args:
            card: Carta de Scryfall con campo edhrec_rank

        Returns:
            Score de popularidad (0-100)
        """
        edhrec_rank = card.get('edhrec_rank')

        if edhrec_rank is None:
            # Sin datos de EDHREC, score neutral
            return 50.0

        # EDHREC rank: menor número = más popular
        # Rank 1 = carta más popular
        # Convertimos a score: cartas top 100 -> score alto

        if edhrec_rank <= 100:
            return 100.0  # Top 100 cartas más populares
        elif edhrec_rank <= 500:
            return 90.0 - ((edhrec_rank - 100) / 400 * 20)  # 90-70
        elif edhrec_rank <= 1000:
            return 70.0 - ((edhrec_rank - 500) / 500 * 20)  # 70-50
        elif edhrec_rank <= 5000:
            return 50.0 - ((edhrec_rank - 1000) / 4000 * 30)  # 50-20
        else:
            return max(20.0 - ((edhrec_rank - 5000) / 10000 * 20), 0)  # 20-0
