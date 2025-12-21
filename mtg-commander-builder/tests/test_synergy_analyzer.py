"""
Tests para el módulo de análisis de sinergias
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from synergy_analyzer import SynergyAnalyzer


def test_compare_colors():
    """Test de comparación de colores"""
    analyzer = SynergyAnalyzer()

    card1 = {'color_identity': ['G', 'W']}
    card2 = {'color_identity': ['G', 'W']}
    card3 = {'color_identity': ['U', 'B']}

    score_same = analyzer._compare_colors(card1, card2)
    score_different = analyzer._compare_colors(card1, card3)

    assert score_same == 1.0, "Colores idénticos deberían dar score 1.0"
    assert score_different < 0.5, "Colores diferentes deberían dar score bajo"
    print(f"✅ Test compare_colors: Mismo={score_same}, Diferente={score_different}")


def test_compare_types():
    """Test de comparación de tipos"""
    analyzer = SynergyAnalyzer()

    card1 = {'type_line': 'Creature — Elf Warrior'}
    card2 = {'type_line': 'Creature — Human Soldier'}
    card3 = {'type_line': 'Instant'}

    score_same_type = analyzer._compare_types(card1, card2)
    score_diff_type = analyzer._compare_types(card1, card3)

    assert score_same_type > 0, "Mismo tipo principal debería dar score positivo"
    assert score_diff_type == 0, "Tipos diferentes deberían dar 0"
    print(f"✅ Test compare_types: Criatura={score_same_type}, Diferente={score_diff_type}")


def test_get_card_themes():
    """Test de identificación de temas"""
    analyzer = SynergyAnalyzer()

    card_with_draw = {
        'oracle_text': 'Draw two cards',
        'type_line': 'Instant'
    }

    card_with_tokens = {
        'oracle_text': 'Create a 1/1 token creature',
        'type_line': 'Sorcery'
    }

    themes1 = analyzer.get_card_themes(card_with_draw)
    themes2 = analyzer.get_card_themes(card_with_tokens)

    assert 'draw' in themes1, "Debería identificar tema de draw"
    assert 'tokens' in themes2, "Debería identificar tema de tokens"
    print(f"✅ Test get_card_themes: Draw={themes1}, Tokens={themes2}")


def test_calculate_synergy_score():
    """Test de cálculo de score de sinergia"""
    analyzer = SynergyAnalyzer()

    commander = {
        'name': 'Ezuri, Claw of Progress',
        'color_identity': ['G', 'U'],
        'type_line': 'Legendary Creature — Elf Warrior',
        'oracle_text': 'Whenever a creature with power 2 or less enters the battlefield, you get experience counter',
        'keywords': [],
        'cmc': 4
    }

    synergistic_card = {
        'name': 'Llanowar Elves',
        'color_identity': ['G'],
        'type_line': 'Creature — Elf Druid',
        'oracle_text': '{T}: Add {G}',
        'keywords': [],
        'cmc': 1
    }

    non_synergistic_card = {
        'name': 'Lightning Bolt',
        'color_identity': ['R'],
        'type_line': 'Instant',
        'oracle_text': 'Deal 3 damage to any target',
        'keywords': [],
        'cmc': 1
    }

    score_good = analyzer.calculate_synergy_score(synergistic_card, [commander])
    score_bad = analyzer.calculate_synergy_score(non_synergistic_card, [commander])

    print(f"✅ Test calculate_synergy_score: Sinérgica={score_good:.2f}, No sinérgica={score_bad:.2f}")
    assert score_good > score_bad, "Carta sinérgica debería tener mejor score"


def test_find_synergies():
    """Test de búsqueda de sinergias"""
    analyzer = SynergyAnalyzer()

    deck_cards = [{
        'name': 'Commander',
        'color_identity': ['G', 'U'],
        'type_line': 'Legendary Creature',
        'oracle_text': 'Draw cards',
        'keywords': [],
        'cmc': 4
    }]

    candidates = [
        {
            'name': 'Card A',
            'color_identity': ['G'],
            'type_line': 'Creature',
            'oracle_text': 'Draw a card',
            'keywords': [],
            'cmc': 3
        },
        {
            'name': 'Card B',
            'color_identity': ['R'],
            'type_line': 'Instant',
            'oracle_text': 'Deal damage',
            'keywords': [],
            'cmc': 2
        }
    ]

    recommendations = analyzer.find_synergies(deck_cards, candidates, top_n=2)

    assert len(recommendations) <= 2, "Debería retornar máximo 2 recomendaciones"
    assert all('synergy_score' in r for r in recommendations), "Todas deberían tener score"
    print(f"✅ Test find_synergies: {len(recommendations)} recomendaciones encontradas")


if __name__ == '__main__':
    print("\n🧪 Ejecutando tests de Synergy Analyzer...\n")

    try:
        test_compare_colors()
        test_compare_types()
        test_get_card_themes()
        test_calculate_synergy_score()
        test_find_synergies()

        print("\n✅ Todos los tests pasaron exitosamente!\n")
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
