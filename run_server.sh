#!/bin/bash

# Script per avviare il backend Flask API
# Porta 5000

echo "🚀 Avvio backend Flask API..."
echo ""

# Controlla se virtual env è attivo
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment non attivo"
    echo "   Attivalo con: source .venv/bin/activate"
    echo ""
fi

# Controlla se le dipendenze sono installate
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask non installato"
    echo "   Installa con: pip install -r requirements.txt"
    exit 1
fi

if ! python -c "import flask_cors" 2>/dev/null; then
    echo "❌ Flask-CORS non installato"
    echo "   Installa con: pip install -r requirements.txt"
    exit 1
fi

# Controlla se .env esiste
if [[ ! -f .env ]]; then
    echo "⚠️  File .env non trovato"
    echo "   Crea il file con:"
    echo "   GEMINI_API_KEY=your-api-key"
    echo ""
fi

# Controlla se database esiste
if [[ ! -f src/prezzi.db ]]; then
    echo "⚠️  Database non trovato"
    echo "   Esegui prima lo scraping: ./run_scraping.sh"
    echo ""
fi

echo "🌐 Server API in avvio su http://localhost:5000"
echo "📡 Endpoint disponibili:"
echo "   • GET  /api/health    - Health check"
echo "   • GET  /api/stats     - Statistiche database"
echo "   • POST /api/optimize  - Ottimizza lista spesa"
echo "   • POST /api/search    - Cerca prodotti"
echo ""
echo "💡 Per testare il frontend:"
echo "   Apri frontend/index.html nel browser"
echo ""
echo "🛑 Per fermare: premi CTRL+C"
echo ""
echo "─────────────────────────────────────────────────"
echo ""

# Avvia server
cd "$(dirname "$0")"
python backend/api.py
