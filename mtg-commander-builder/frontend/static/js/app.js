/**
 * Constructor de Mazos de Commander - Frontend
 */

// Estado de la aplicación
const state = {
    commander: null,
    deckCards: [],
    totalBudget: null,
    currentCost: 0,
};

// Configuración de la API
const API_BASE = window.location.origin;

// Elementos DOM
const elements = {
    commanderInput: document.getElementById('commander-input'),
    searchCommanderBtn: document.getElementById('search-commander-btn'),
    randomCommanderBtn: document.getElementById('random-commander-btn'),
    commanderDisplay: document.getElementById('commander-display'),
    totalBudgetInput: document.getElementById('total-budget-input'),
    currentCost: document.getElementById('current-cost'),
    budgetRemaining: document.getElementById('budget-remaining'),
    cardInput: document.getElementById('card-input'),
    addCardBtn: document.getElementById('add-card-btn'),
    deckList: document.getElementById('deck-list'),
    deckCount: document.getElementById('deck-count'),
    getRecommendationsBtn: document.getElementById('get-recommendations-btn'),
    numRecommendations: document.getElementById('num-recommendations'),
    recommendationsList: document.getElementById('recommendations-list'),
    loading: document.getElementById('loading'),
    toast: document.getElementById('toast'),
};

// Utilidades
function showLoading() {
    elements.loading.classList.remove('hidden');
}

function hideLoading() {
    elements.loading.classList.add('hidden');
}

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.remove('hidden');

    setTimeout(() => {
        elements.toast.classList.add('hidden');
    }, 4000);
}

// API calls
async function searchCard(cardName) {
    const response = await fetch(`${API_BASE}/api/search-card?name=${encodeURIComponent(cardName)}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error buscando carta');
    }
    return response.json();
}

async function getRecommendations(deckCards, commander, totalBudget, numRecs) {
    const response = await fetch(`${API_BASE}/api/get-recommendations`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            deck_cards: deckCards.map(c => c.name),
            commander: commander,
            total_budget: totalBudget,
            num_recommendations: numRecs,
        }),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Error obteniendo recomendaciones');
    }
    return response.json();
}

async function calculateDeckCost(deckCards) {
    const response = await fetch(`${API_BASE}/api/calculate-deck-cost`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            deck_cards: deckCards.map(c => c.name),
            currency: 'eur',
        }),
    });

    if (!response.ok) {
        throw new Error('Error calculando costo del mazo');
    }
    return response.json();
}

async function getRandomCommander() {
    const response = await fetch(`${API_BASE}/api/random-commander`);
    if (!response.ok) {
        throw new Error('Error obteniendo comandante aleatorio');
    }
    return response.json();
}

// Renderizado
function renderCommander(commander) {
    const colors = commander.colors || [];
    const colorBadges = colors
        .map(color => `<div class="color-badge ${color}"></div>`)
        .join('');

    elements.commanderDisplay.innerHTML = `
        ${commander.image_uri ? `<img src="${commander.image_uri}" alt="${commander.name}">` : ''}
        <div class="commander-info">
            <h3>${commander.name}</h3>
            <p><strong>Tipo:</strong> ${commander.type_line || 'N/A'}</p>
            <p><strong>Coste:</strong> ${commander.mana_cost || 'N/A'}</p>
            <div class="colors">${colorBadges}</div>
            ${commander.oracle_text ? `<p style="margin-top: 10px; font-size: 0.9rem;">${commander.oracle_text}</p>` : ''}
        </div>
    `;
}

function renderDeckList() {
    if (state.deckCards.length === 0) {
        elements.deckList.innerHTML = '<p class="empty-message">No hay cartas en el mazo. Añade algunas para empezar.</p>';
        elements.deckCount.textContent = '0';
        return;
    }

    const cardsHTML = state.deckCards
        .map((card, index) => {
            const price = card.prices?.eur || card.prices?.usd;
            const priceText = price ? `${price.toFixed(2)} EUR` : 'Precio N/A';

            return `
                <div class="deck-card">
                    <div>
                        <span class="card-name">${card.name}</span>
                        <span class="card-cost" style="margin-left: 15px;">${priceText}</span>
                    </div>
                    <button class="remove-btn" data-index="${index}">Eliminar</button>
                </div>
            `;
        })
        .join('');

    elements.deckList.innerHTML = cardsHTML;
    elements.deckCount.textContent = state.deckCards.length;

    // Añade event listeners a botones de eliminar
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const index = parseInt(e.target.dataset.index);
            removeCardFromDeck(index);
        });
    });

    // Actualiza presupuesto
    updateBudget();
}

function renderRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        elements.recommendationsList.innerHTML = '<p class="empty-message">No se encontraron recomendaciones.</p>';
        return;
    }

    const recsHTML = recommendations
        .map(rec => {
            const price = rec.prices?.eur || rec.prices?.usd;
            const priceText = price ? `${price.toFixed(2)} EUR` : 'N/A';
            const themes = rec.themes || [];
            const themeBadges = themes.slice(0, 5)
                .map(theme => `<span class="theme-badge">${theme}</span>`)
                .join('');

            return `
                <div class="recommendation-card">
                    ${rec.image_uri ? `<img src="${rec.image_uri}" alt="${rec.name}">` : ''}
                    <div class="recommendation-header">
                        <h4>${rec.name}</h4>
                        <span class="synergy-score">${rec.synergy_score}%</span>
                    </div>
                    <p><strong>Coste:</strong> ${rec.mana_cost || 'N/A'}</p>
                    <p><strong>Tipo:</strong> ${rec.type_line}</p>
                    <p><strong>Precio:</strong> ${priceText}</p>
                    ${rec.oracle_text ? `<p style="font-size: 0.85rem; margin-top: 8px;">${rec.oracle_text.substring(0, 150)}${rec.oracle_text.length > 150 ? '...' : ''}</p>` : ''}
                    <div class="recommendation-themes">${themeBadges}</div>
                    <button class="add-to-deck-btn" data-card='${JSON.stringify(rec)}'>Añadir al Mazo</button>
                </div>
            `;
        })
        .join('');

    elements.recommendationsList.innerHTML = recsHTML;

    // Añade event listeners a botones de añadir
    document.querySelectorAll('.add-to-deck-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const card = JSON.parse(e.target.dataset.card);
            addCardToDeck(card);
        });
    });
}

// Manejo de eventos
async function handleSearchCommander() {
    const commanderName = elements.commanderInput.value.trim();

    if (!commanderName) {
        showToast('Por favor escribe el nombre de un comandante', 'error');
        return;
    }

    showLoading();
    try {
        const commander = await searchCard(commanderName);
        state.commander = commander;
        renderCommander(commander);
        updateBudget(); // Actualiza presupuesto con el comandante
        showToast(`Comandante encontrado: ${commander.name}`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function handleRandomCommander() {
    showLoading();
    try {
        const commander = await getRandomCommander();
        state.commander = commander;
        elements.commanderInput.value = commander.name;
        renderCommander(commander);
        updateBudget(); // Actualiza presupuesto con el comandante
        showToast(`Comandante aleatorio: ${commander.name}`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function handleAddCard() {
    const cardName = elements.cardInput.value.trim();

    if (!cardName) {
        showToast('Por favor escribe el nombre de una carta', 'error');
        return;
    }

    // Verifica si ya está en el mazo
    if (state.deckCards.some(c => c.name.toLowerCase() === cardName.toLowerCase())) {
        showToast('Esta carta ya está en el mazo', 'error');
        return;
    }

    showLoading();
    try {
        const card = await searchCard(cardName);
        addCardToDeck(card);
        elements.cardInput.value = '';
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

function addCardToDeck(card) {
    // Verifica límite de 100 cartas
    if (state.deckCards.length >= 100) {
        showToast('El mazo ya tiene 100 cartas', 'error');
        return;
    }

    // Verifica duplicados
    if (state.deckCards.some(c => c.name === card.name)) {
        showToast('Esta carta ya está en el mazo', 'error');
        return;
    }

    state.deckCards.push(card);
    renderDeckList();
    showToast(`${card.name} añadido al mazo`, 'success');
}

function removeCardFromDeck(index) {
    const card = state.deckCards[index];
    state.deckCards.splice(index, 1);
    renderDeckList();
    showToast(`${card.name} eliminado del mazo`, 'success');
}

async function handleGetRecommendations() {
    if (!state.commander) {
        showToast('Por favor selecciona un comandante primero', 'error');
        return;
    }

    const totalBudgetValue = elements.totalBudgetInput.value ? parseFloat(elements.totalBudgetInput.value) : null;
    const numRecs = parseInt(elements.numRecommendations.value);

    showLoading();
    try {
        const result = await getRecommendations(
            state.deckCards,
            state.commander.name,
            totalBudgetValue,
            numRecs
        );
        renderRecommendations(result.recommendations);

        // Actualiza información de presupuesto
        if (result.budget_info) {
            showToast(
                `${result.recommendations.length} recomendaciones encontradas. ` +
                `Presupuesto restante: ${result.budget_info.remaining ? result.budget_info.remaining.toFixed(2) : '-'} EUR`,
                'success'
            );
        } else {
            showToast(`${result.recommendations.length} recomendaciones encontradas`, 'success');
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
}

async function updateBudget() {
    if (state.deckCards.length === 0 && !state.commander) {
        elements.currentCost.textContent = '0.00 EUR';
        elements.budgetRemaining.textContent = '-';
        state.currentCost = 0;
        return;
    }

    try {
        // Incluye comandante en el cálculo
        const allCards = state.commander ? [...state.deckCards, state.commander] : state.deckCards;
        const result = await calculateDeckCost(allCards);

        state.currentCost = result.total_cost;
        elements.currentCost.textContent = `${result.total_cost.toFixed(2)} EUR`;

        // Calcula presupuesto restante
        if (state.totalBudget) {
            const remaining = state.totalBudget - result.total_cost;
            const color = remaining >= 0 ? 'var(--color-green)' : 'var(--color-red)';
            elements.budgetRemaining.style.color = color;
            elements.budgetRemaining.textContent = `${remaining.toFixed(2)} EUR`;
        } else {
            elements.budgetRemaining.textContent = '-';
        }
    } catch (error) {
        console.error('Error calculando presupuesto:', error);
    }
}

// Event Listeners
elements.searchCommanderBtn.addEventListener('click', handleSearchCommander);
elements.randomCommanderBtn.addEventListener('click', handleRandomCommander);
elements.addCardBtn.addEventListener('click', handleAddCard);
elements.getRecommendationsBtn.addEventListener('click', handleGetRecommendations);

// Enter key support
elements.commanderInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSearchCommander();
});

elements.cardInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleAddCard();
});

elements.totalBudgetInput.addEventListener('change', () => {
    state.totalBudget = elements.totalBudgetInput.value ? parseFloat(elements.totalBudgetInput.value) : null;
    updateBudget(); // Recalcula presupuesto restante
});

// Inicialización
console.log('🃏 Constructor de Mazos de Commander iniciado');
