// ==========================================
// Configuration
// ==========================================

const API_BASE_URL = 'http://localhost:5000/api';

// ==========================================
// DOM Elements
// ==========================================

const elements = {
    // Input
    shoppingListInput: document.getElementById('shoppingListInput'),
    optimizeBtn: document.getElementById('optimizeBtn'),
    clearBtn: document.getElementById('clearBtn'),
    
    // Loading
    loadingIndicator: document.getElementById('loadingIndicator'),
    loadingStatus: document.getElementById('loadingStatus'),
    
    // Results
    resultsSection: document.getElementById('resultsSection'),
    resultsContainer: document.getElementById('resultsContainer'),
    summaryPills: document.getElementById('summaryPills'),
    exportBtn: document.getElementById('exportBtn'),
    
    // Error
    errorSection: document.getElementById('errorSection'),
    errorMessage: document.getElementById('errorMessage'),
    closeErrorBtn: document.getElementById('closeErrorBtn'),
    
    // Stats
    totalProducts: document.getElementById('totalProducts'),
    totalStores: document.getElementById('totalStores'),
    apiStatus: document.getElementById('apiStatus')
};

// ==========================================
// State Management
// ==========================================

let currentResults = null;

// ==========================================
// API Functions
// ==========================================

async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'ok') {
            elements.apiStatus.innerHTML = '<span class="status-dot"></span>Online';
            elements.apiStatus.classList.remove('offline');
            return true;
        }
    } catch (error) {
        elements.apiStatus.innerHTML = '<span class="status-dot"></span>Offline';
        elements.apiStatus.classList.add('offline');
        return false;
    }
}

async function fetchDatabaseStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        if (data.success) {
            elements.totalProducts.textContent = data.data.totale_prodotti || '0';
            elements.totalStores.textContent = data.data.totale_supermercati || '0';
        }
    } catch (error) {
        console.error('Errore nel recupero statistiche:', error);
        elements.totalProducts.textContent = 'N/A';
        elements.totalStores.textContent = 'N/A';
    }
}

async function optimizeShoppingList(items) {
    const response = await fetch(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ items })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Errore durante ottimizzazione');
    }
    
    return await response.json();
}

// ==========================================
// UI Functions
// ==========================================

function showLoading(status = 'Analisi prodotti con AI ibrido...') {
    elements.loadingStatus.textContent = status;
    elements.loadingIndicator.style.display = 'block';
    elements.optimizeBtn.disabled = true;
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
}

function hideLoading() {
    elements.loadingIndicator.style.display = 'none';
    elements.optimizeBtn.disabled = false;
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';
}

function hideError() {
    elements.errorSection.style.display = 'none';
}

function showResults(data) {
    currentResults = data;
    
    // Render summary
    renderSummary(data.summary);
    
    // Render results (prima i dettagli)
    renderResults(data.results);
    
    // Render recap per supermercato (poi il recap in cima)
    renderStoreRecap(data.results);
    
    // Show results section
    elements.resultsSection.style.display = 'block';
    
    // Scroll to results
    elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderSummary(summary) {
    elements.summaryPills.innerHTML = `
        <div class="pill">
            <span class="pill-icon">📦</span>
            <span>Prodotti cercati: <span class="pill-value">${summary.total_products}</span></span>
        </div>
        <div class="pill">
            <span class="pill-icon">✅</span>
            <span>Alternative trovate: <span class="pill-value">${summary.total_matches}</span></span>
        </div>
        <div class="pill">
            <span class="pill-icon">📊</span>
            <span>Media per prodotto: <span class="pill-value">${summary.avg_matches_per_product}</span></span>
        </div>
        ${summary.best_store !== 'N/A' ? `
        <div class="pill">
            <span class="pill-icon">🏪</span>
            <span>Supermercato migliore: <span class="pill-value">${summary.best_store}</span></span>
        </div>
        ` : ''}
        ${summary.total_price ? `
        <div class="pill">
            <span class="pill-icon">💰</span>
            <span>Totale stimato: <span class="pill-value">€${summary.total_price.toFixed(2)}</span></span>
        </div>
        ` : ''}
        ${summary.coverage !== 'N/A' ? `
        <div class="pill">
            <span class="pill-icon">📈</span>
            <span>Copertura: <span class="pill-value">${summary.coverage}</span></span>
        </div>
        ` : ''}
    `;
}

function renderResults(results) {
    if (!results || results.length === 0) {
        elements.resultsContainer.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <p>Nessun risultato trovato</p>
            </div>
        `;
        return;
    }
    
    elements.resultsContainer.innerHTML = results.map((result, resultIdx) => {
        const alternativesHTML = result.alternatives.length > 0
            ? result.alternatives.slice(0, 3).map((alt, index) => `
                <div class="alternative-card ${index > 0 ? 'alternative-hidden' : ''}" data-index="${index}">
                    <div class="alternative-rank">${index + 1}</div>
                    <div class="alternative-content">
                        <div class="alternative-name">${escapeHtml(alt.nome)}</div>
                        <div class="alternative-meta">
                            ${alt.categoria ? `<span class="meta-badge">📂 ${escapeHtml(alt.categoria)}</span>` : ''}
                            ${alt.marca ? `<span class="meta-badge">🏷️ ${escapeHtml(alt.marca)}</span>` : ''}
                            ${alt.unita_misura ? `<span class="meta-badge">📏 ${escapeHtml(alt.unita_misura)}</span>` : ''}
                        </div>
                    </div>
                    <div class="alternative-price">
                        <div class="price-value">€${alt.prezzo.toFixed(2)}</div>
                        <div class="price-store">${escapeHtml(alt.supermercato)}</div>
                    </div>
                </div>
            `).join('')
            : `
                <div class="no-results">
                    <p>Nessuna alternativa trovata per questo prodotto</p>
                </div>
            `;
        
        const showMoreBtn = result.alternatives.length > 1 ? `
            <button class="btn-show-more" onclick="toggleAlternatives(${resultIdx})">
                <span class="expand-icon">▼</span> Mostra altre ${result.alternatives.length - 1} alternative
            </button>
        ` : '';
        
        return `
            <div class="product-result" id="product-${resultIdx}">
                <div class="product-header">
                    <div class="product-query">🔍 ${escapeHtml(result.original_query)}</div>
                    <div class="product-matches">${result.total_found} alternative trovate</div>
                </div>
                <div class="alternatives-list">
                    ${alternativesHTML}
                </div>
                ${showMoreBtn}
            </div>
        `;
    }).join('');
}

// Funzione globale per espandere alternative
window.toggleAlternatives = function(resultIdx) {
    const product = document.getElementById(`product-${resultIdx}`);
    const hiddenCards = product.querySelectorAll('.alternative-card[data-index]');
    const btn = product.querySelector('.btn-show-more');
    const icon = btn.querySelector('.expand-icon');
    
    // Check se è espanso guardando la seconda card
    const secondCard = product.querySelector('.alternative-card[data-index="1"]');
    const isExpanded = !secondCard.classList.contains('alternative-hidden');
    
    // Toggle tutte le card tranne la prima (data-index="0")
    hiddenCards.forEach(card => {
        const index = parseInt(card.getAttribute('data-index'));
        if (index > 0) {
            if (isExpanded) {
                card.classList.add('alternative-hidden');
            } else {
                card.classList.remove('alternative-hidden');
            }
        }
    });
    
    // Update button
    if (isExpanded) {
        const count = hiddenCards.length - 1; // -1 perché la prima è sempre visibile
        icon.textContent = '▼';
        btn.innerHTML = `<span class="expand-icon">▼</span> Mostra altre ${count} alternative`;
    } else {
        icon.textContent = '▲';
        btn.innerHTML = `<span class="expand-icon">▲</span> Nascondi alternative`;
    }
}

function renderStoreRecap(results) {
    const storeProducts = {};
    
    // Raggruppa prodotti per supermercato (usa prima opzione)
    results.forEach(result => {
        if (result.alternatives.length > 0) {
            const best = result.alternatives[0];
            const store = best.supermercato;
            
            if (!storeProducts[store]) {
                storeProducts[store] = [];
            }
            
            storeProducts[store].push({
                query: result.original_query,
                nome: best.nome,
                prezzo: best.prezzo
            });
        }
    });
    
    // Crea HTML recap
    let recapHTML = '<div class="store-recap">';
    recapHTML += '<h3>📍 Dove Comprare</h3>';
    recapHTML += '<div class="store-columns">';
    
    Object.keys(storeProducts).sort().forEach(store => {
        const products = storeProducts[store];
        const total = products.reduce((sum, p) => sum + p.prezzo, 0);
        
        recapHTML += `
            <div class="store-column">
                <div class="store-header">
                    <h4>🏪 ${escapeHtml(store)}</h4>
                    <span class="store-count">${products.length} prodotti</span>
                </div>
                <div class="store-items">
                    ${products.map(p => `
                        <div class="store-item">
                            <span class="item-name">${escapeHtml(p.nome)}</span>
                            <span class="item-price">€${p.prezzo.toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="store-total">
                    <strong>Totale:</strong> €${total.toFixed(2)}
                </div>
            </div>
        `;
    });
    
    recapHTML += '</div></div>';
    
    // Inserisci prima dei risultati dettagliati
    const container = document.getElementById('resultsContainer');
    container.insertAdjacentHTML('afterbegin', recapHTML);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function exportResults() {
    if (!currentResults) return;
    
    let exportText = '='.repeat(60) + '\n';
    exportText += 'RISULTATI OTTIMIZZAZIONE LISTA SPESA\n';
    exportText += `Data: ${new Date().toLocaleString('it-IT')}\n`;
    exportText += '='.repeat(60) + '\n\n';
    
    exportText += `Prodotti cercati: ${currentResults.summary.total_products}\n`;
    exportText += `Alternative trovate: ${currentResults.summary.total_matches}\n`;
    exportText += `Media per prodotto: ${currentResults.summary.avg_matches_per_product}\n\n`;
    
    currentResults.results.forEach((result, idx) => {
        exportText += `\n${idx + 1}. ${result.original_query.toUpperCase()}\n`;
        exportText += '-'.repeat(60) + '\n';
        
        if (result.alternatives.length === 0) {
            exportText += '   Nessuna alternativa trovata\n';
        } else {
            result.alternatives.slice(0, 3).forEach((alt, altIdx) => {
                exportText += `   ${altIdx + 1}) ${alt.nome}\n`;
                exportText += `      Prezzo: €${alt.prezzo.toFixed(2)} - ${alt.supermercato}\n`;
                if (alt.categoria) exportText += `      Categoria: ${alt.categoria}\n`;
                if (alt.marca) exportText += `      Marca: ${alt.marca}\n`;
                if (alt.unita_misura) exportText += `      Unità: ${alt.unita_misura}\n`;
                if (alt.reasoning) exportText += `      Motivazione: ${alt.reasoning}\n`;
                exportText += '\n';
            });
        }
    });
    
    // Download file
    const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `lista_spesa_ottimizzata_${new Date().getTime()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ==========================================
// Event Handlers
// ==========================================

async function handleOptimize() {
    hideError();
    
    // Get input
    const input = elements.shoppingListInput.value.trim();
    
    if (!input) {
        showError('Inserisci almeno un prodotto nella lista della spesa');
        return;
    }
    
    // Parse items (one per line)
    const items = input
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);
    
    if (items.length === 0) {
        showError('Nessun prodotto valido nella lista');
        return;
    }
    
    // Show loading
    showLoading(`Ottimizzazione ${items.length} prodotti...`);
    
    try {
        // Simulate processing steps
        setTimeout(() => {
            elements.loadingStatus.textContent = '🤖 FunctionGemma estrae keywords...';
        }, 500);
        
        setTimeout(() => {
            elements.loadingStatus.textContent = '🔍 Ricerca nel database...';
        }, 1500);
        
        setTimeout(() => {
            elements.loadingStatus.textContent = '🧠 Gemini analizza risultati...';
        }, 2500);
        
        // Call API
        const response = await optimizeShoppingList(items);
        
        if (response.success) {
            hideLoading();
            showResults(response.data);
        } else {
            throw new Error(response.error || 'Errore durante ottimizzazione');
        }
        
    } catch (error) {
        hideLoading();
        showError(`Errore: ${error.message}`);
        console.error('Errore ottimizzazione:', error);
    }
}

function handleClear() {
    elements.shoppingListInput.value = '';
    elements.resultsSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
    currentResults = null;
}

// ==========================================
// Event Listeners
// ==========================================

elements.optimizeBtn.addEventListener('click', handleOptimize);
elements.clearBtn.addEventListener('click', handleClear);
elements.closeErrorBtn.addEventListener('click', hideError);
elements.exportBtn.addEventListener('click', exportResults);

// Enter key in textarea to optimize
elements.shoppingListInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        handleOptimize();
    }
});

// ==========================================
// Initialization
// ==========================================

async function init() {
    console.log('🚀 Inizializzazione frontend...');
    
    // Check API health
    const isOnline = await checkAPIHealth();
    
    if (isOnline) {
        console.log('✅ API online');
        await fetchDatabaseStats();
    } else {
        console.warn('⚠️ API offline - verifica che il backend sia avviato');
        showError('Backend API non disponibile. Assicurati che il server sia avviato (python backend/api.py)');
    }
    
    console.log('✨ Frontend pronto!');
}

// Start on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
