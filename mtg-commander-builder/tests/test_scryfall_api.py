"""
Tests para el módulo de Scryfall API
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scryfall_api import ScryfallAPI


def test_search_card():
    """Test de búsqueda de carta básica"""
    api = ScryfallAPI()

    # Busca una carta famosa
    card = api.search_card("Lightning Bolt")

    assert card is not None, "La carta debería existir"
    assert card.get('name') == "Lightning Bolt", "El nombre debería coincidir"
    print(f"✅ Test search_card: {card.get('name')} encontrada")


def test_fuzzy_search():
    """Test de búsqueda fuzzy"""
    api = ScryfallAPI()

    # Busca con nombre aproximado
    card = api.fuzzy_search_card("Sol Ring")

    assert card is not None, "Debería encontrar la carta"
    assert "Sol Ring" in card.get('name'), "Debería ser Sol Ring"
    print(f"✅ Test fuzzy_search: {card.get('name')} encontrada")


def test_get_card_price():
    """Test de obtención de precios"""
    api = ScryfallAPI()

    card = api.search_card("Lightning Bolt")
    prices = api.get_card_price(card)

    assert 'usd' in prices, "Debería tener precio en USD"
    assert 'eur' in prices, "Debería tener precio en EUR"
    print(f"✅ Test get_card_price: Precios obtenidos (USD: {prices.get('usd')}, EUR: {prices.get('eur')})")


def test_search_commanders():
    """Test de búsqueda de comandantes"""
    api = ScryfallAPI()

    # Busca comandantes verdes
    result = api.search_cards_by_query("is:commander ci=G")

    assert 'data' in result, "Debería tener datos"
    assert len(result['data']) > 0, "Debería encontrar comandantes"
    print(f"✅ Test search_commanders: {len(result['data'])} comandantes encontrados")


def test_random_commander():
    """Test de comandante aleatorio"""
    api = ScryfallAPI()

    commander = api.get_random_commander()

    assert commander is not None, "Debería retornar un comandante"
    assert 'name' in commander, "Debería tener nombre"
    print(f"✅ Test random_commander: {commander.get('name')} obtenido")


if __name__ == '__main__':
    print("\n🧪 Ejecutando tests de Scryfall API...\n")

    try:
        test_search_card()
        test_fuzzy_search()
        test_get_card_price()
        test_search_commanders()
        test_random_commander()

        print("\n✅ Todos los tests pasaron exitosamente!\n")
    except AssertionError as e:
        print(f"\n❌ Test falló: {e}\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
