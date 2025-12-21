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
        total_budget: Presupuesto total del mazo (EUR)
        num_recommendations: Número de recomendaciones (default: 20)
    """
    data = request.json
    deck_card_names = data.get('deck_cards', [])
    commander_name = data.get('commander')
    total_budget = data.get('total_budget')
    num_recommendations = data.get('num_recommendations', 20)

    if not commander_name:
        return jsonify({'error': 'Comandante requerido'}), 400

    # Busca el comandante
    commander = scryfall.search_card(commander_name)
    if not commander:
        return jsonify({'error': 'Comandante no encontrado'}), 404

    # Busca las cartas del mazo
    deck_cards = []
    current_deck_cost = 0.0

    for card_name in deck_card_names:
        card = scryfall.search_card(card_name)
        if card:
            deck_cards.append(card)
            # Calcula costo actual del mazo
            prices = scryfall.get_card_price(card)
            card_price = prices.get('eur') or prices.get('usd') or 0
            current_deck_cost += card_price

    # Añade costo del comandante
    commander_prices = scryfall.get_card_price(commander)
    commander_price = commander_prices.get('eur') or commander_prices.get('usd') or 0
    current_deck_cost += commander_price

    # Añade el comandante a las cartas de referencia
    deck_cards.append(commander)

    # Calcula presupuesto restante
    budget_remaining = None
    if total_budget:
        budget_remaining = total_budget - current_deck_cost
        if budget_remaining < 0:
            return jsonify({'error': f'El mazo actual ya supera el presupuesto (Costo actual: {current_deck_cost:.2f} EUR)'}), 400

    # Obtiene colores del comandante
    colors = commander.get('color_identity', [])

    # Busca más candidatos para tener mejor selección
    candidate_cards = scryfall.get_commander_recommendations(
        commander_name,
        colors,
        limit=200
    )

    # Filtra candidatos con precio
    candidates_with_prices = []
    for card in candidate_cards:
        prices = scryfall.get_card_price(card)
        card_price = prices.get('eur') or prices.get('usd')

        # Solo incluye cartas con precio conocido
        if card_price is not None:
            card['_price'] = card_price
            candidates_with_prices.append(card)

    # Analiza sinergias
    recommendations = synergy.find_synergies(deck_cards, candidates_with_prices, top_n=num_recommendations * 3)

    # Si hay presupuesto, optimiza selección
    if budget_remaining:
        recommendations = optimize_recommendations_for_budget(
            recommendations,
            budget_remaining,
            num_recommendations,
            len(deck_cards) - 1  # -1 porque deck_cards incluye el comandante
        )
    else:
        recommendations = recommendations[:num_recommendations]

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
        },
        'budget_info': {
            'current_cost': round(current_deck_cost, 2),
            'total_budget': total_budget,
            'remaining': round(budget_remaining, 2) if budget_remaining else None
        }
    })


def optimize_recommendations_for_budget(recommendations, budget_remaining, num_recs, current_deck_size):
    """
    Optimiza las recomendaciones para que se ajusten al presupuesto total
    Prioriza cartas con mejor ratio sinergia/precio
    """
    # Cartas objetivo para un mazo completo (100 - tamaño actual)
    cards_needed = 100 - current_deck_size

    # Si necesitamos menos cartas de las que pedimos, ajusta
    num_recs = min(num_recs, cards_needed)

    # Calcula presupuesto promedio por carta
    avg_budget_per_card = budget_remaining / cards_needed if cards_needed > 0 else budget_remaining

    # Filtra cartas que están muy por encima del presupuesto promedio
    # Permite cierta flexibilidad (hasta 3x el promedio)
    max_card_price = min(avg_budget_per_card * 3, budget_remaining)

    affordable_recs = []
    for rec in recommendations:
        card_price = rec['card'].get('_price', 0)
        if card_price <= max_card_price:
            # Calcula ratio valor/precio (sinergia dividida por precio)
            if card_price > 0:
                rec['value_ratio'] = rec['synergy_score'] / card_price
            else:
                rec['value_ratio'] = rec['synergy_score'] * 100
            affordable_recs.append(rec)

    # Ordena por mejor ratio valor/precio, pero mantiene algo de peso en sinergia pura
    # 70% peso en sinergia, 30% en ratio valor/precio
    affordable_recs.sort(
        key=lambda x: (x['synergy_score'] * 0.7) + (x['value_ratio'] * 0.3),
        reverse=True
    )

    # Selecciona cartas asegurando no superar presupuesto
    selected = []
    total_cost = 0.0

    for rec in affordable_recs:
        card_price = rec['card'].get('_price', 0)
        if total_cost + card_price <= budget_remaining and len(selected) < num_recs:
            selected.append(rec)
            total_cost += card_price

    return selected


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
