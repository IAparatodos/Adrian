"""
Servidor Flask principal para el Constructor de Mazos de Commander
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from scryfall_api import ScryfallAPI
from synergy_analyzer import SynergyAnalyzer
from typing import List, Dict

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# Inicializa servicios
scryfall = ScryfallAPI()
synergy = SynergyAnalyzer()

# Almacenamiento temporal del mazo (en producción usar base de datos)
deck_storage = {}


@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')


@app.route('/api/search-card', methods=['GET'])
def search_card():
    """
    Busca una carta por nombre

    Query params:
        name: Nombre de la carta
    """
    card_name = request.args.get('name', '')

    if not card_name:
        return jsonify({'error': 'Nombre de carta requerido'}), 400

    card = scryfall.search_card(card_name)

    if not card:
        return jsonify({'error': 'Carta no encontrada'}), 404

    # Extrae información relevante
    card_info = {
        'name': card.get('name'),
        'mana_cost': card.get('mana_cost'),
        'cmc': card.get('cmc'),
        'type_line': card.get('type_line'),
        'oracle_text': card.get('oracle_text'),
        'colors': card.get('colors', []),
        'color_identity': card.get('color_identity', []),
        'keywords': card.get('keywords', []),
        'image_uri': card.get('image_uris', {}).get('normal') if card.get('image_uris') else None,
        'prices': scryfall.get_card_price(card),
        'legalities': card.get('legalities', {}),
        'scryfall_uri': card.get('scryfall_uri')
    }

    return jsonify(card_info)


@app.route('/api/get-recommendations', methods=['POST'])
def get_recommendations():
    """
    Obtiene recomendaciones de cartas basadas en el mazo actual

    JSON body:
        deck_cards: Lista de nombres de cartas en el mazo
        commander: Nombre del comandante
        budget_max: Presupuesto máximo por carta (EUR)
        num_recommendations: Número de recomendaciones (default: 20)
    """
    data = request.json
    deck_card_names = data.get('deck_cards', [])
    commander_name = data.get('commander')
    budget_max = data.get('budget_max')
    num_recommendations = data.get('num_recommendations', 20)

    if not commander_name:
        return jsonify({'error': 'Comandante requerido'}), 400

    # Busca el comandante
    commander = scryfall.search_card(commander_name)
    if not commander:
        return jsonify({'error': 'Comandante no encontrado'}), 404

    # Busca las cartas del mazo
    deck_cards = []
    for card_name in deck_card_names:
        card = scryfall.search_card(card_name)
        if card:
            deck_cards.append(card)

    # Añade el comandante a las cartas de referencia
    deck_cards.append(commander)

    # Obtiene colores del comandante
    colors = commander.get('color_identity', [])

    # Busca candidatos
    candidate_cards = scryfall.get_commander_recommendations(
        commander_name,
        colors,
        limit=100
    )

    # Aplica filtro de presupuesto si está definido
    if budget_max:
        filtered_candidates = []
        for card in candidate_cards:
            prices = scryfall.get_card_price(card)
            card_price = prices.get('eur') or prices.get('usd')
            if card_price and card_price <= budget_max:
                filtered_candidates.append(card)
        candidate_cards = filtered_candidates

    # Analiza sinergias
    recommendations = synergy.find_synergies(deck_cards, candidate_cards, top_n=num_recommendations)

    # Formatea respuesta
    result = []
    for rec in recommendations:
        card = rec['card']
        result.append({
            'name': card.get('name'),
            'mana_cost': card.get('mana_cost'),
            'cmc': card.get('cmc'),
            'type_line': card.get('type_line'),
            'oracle_text': card.get('oracle_text'),
            'colors': card.get('colors', []),
            'image_uri': card.get('image_uris', {}).get('small') if card.get('image_uris') else None,
            'prices': scryfall.get_card_price(card),
            'synergy_score': round(rec['synergy_score'], 2),
            'themes': rec['themes'],
            'scryfall_uri': card.get('scryfall_uri')
        })

    return jsonify({
        'recommendations': result,
        'commander': {
            'name': commander.get('name'),
            'colors': commander.get('color_identity', []),
            'image_uri': commander.get('image_uris', {}).get('small') if commander.get('image_uris') else None
        }
    })


@app.route('/api/calculate-deck-cost', methods=['POST'])
def calculate_deck_cost():
    """
    Calcula el costo total del mazo

    JSON body:
        deck_cards: Lista de nombres de cartas
        currency: Moneda (eur, usd) - default: eur
    """
    data = request.json
    deck_card_names = data.get('deck_cards', [])
    currency = data.get('currency', 'eur')

    total_cost = 0.0
    card_costs = []
    missing_prices = []

    for card_name in deck_card_names:
        card = scryfall.search_card(card_name)
        if card:
            prices = scryfall.get_card_price(card)
            price = prices.get(currency)

            if price:
                total_cost += price
                card_costs.append({
                    'name': card.get('name'),
                    'price': price
                })
            else:
                missing_prices.append(card.get('name'))

    return jsonify({
        'total_cost': round(total_cost, 2),
        'currency': currency.upper(),
        'card_costs': card_costs,
        'missing_prices': missing_prices
    })


@app.route('/api/random-commander', methods=['GET'])
def random_commander():
    """Obtiene un comandante aleatorio"""
    commander = scryfall.get_random_commander()

    if not commander:
        return jsonify({'error': 'No se pudo obtener comandante aleatorio'}), 500

    return jsonify({
        'name': commander.get('name'),
        'mana_cost': commander.get('mana_cost'),
        'type_line': commander.get('type_line'),
        'oracle_text': commander.get('oracle_text'),
        'colors': commander.get('color_identity', []),
        'image_uri': commander.get('image_uris', {}).get('normal') if commander.get('image_uris') else None,
        'scryfall_uri': commander.get('scryfall_uri')
    })


@app.route('/api/search-commanders', methods=['GET'])
def search_commanders():
    """
    Busca comandantes por colores

    Query params:
        colors: Colores separados por coma (W,U,B,R,G)
    """
    colors = request.args.get('colors', '')

    query = "is:commander"
    if colors:
        color_list = colors.split(',')
        color_identity = ''.join(sorted(color_list))
        query += f" ci={color_identity}"

    result = scryfall.search_cards_by_query(query)
    commanders = []

    for card in result.get('data', [])[:30]:  # Limita a 30 resultados
        commanders.append({
            'name': card.get('name'),
            'colors': card.get('color_identity', []),
            'type_line': card.get('type_line'),
            'image_uri': card.get('image_uris', {}).get('small') if card.get('image_uris') else None
        })

    return jsonify({'commanders': commanders})


if __name__ == '__main__':
    print("🃏 Iniciando Constructor de Mazos de Commander...")
    print("📡 Servidor disponible en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
