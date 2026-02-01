#!/usr/bin/env python3
"""
Backend API Flask per sistema ottimizzazione lista spesa
Espone endpoint REST per frontend web
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Aggiungi path src per import
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from gemini_optimizer import HybridShoppingOptimizer
from db import PriceDatabase

app = Flask(__name__)
CORS(app)  # Abilita CORS per chiamate frontend

# Inizializza optimizer
optimizer = HybridShoppingOptimizer()
db = PriceDatabase()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Supermarket Price Optimizer API',
        'version': '1.0'
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Statistiche database prodotti"""
    try:
        stats = db.get_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize', methods=['POST'])
def optimize_shopping_list():
    """
    Ottimizza lista della spesa
    Body: {"items": ["pasta", "latte", "uova"]}
    """
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "items" obbligatorio'
            }), 400
        
        items = data['items']
        
        # Valida items
        if not isinstance(items, list):
            return jsonify({
                'success': False,
                'error': 'Il campo "items" deve essere una lista'
            }), 400
        
        if not items:
            return jsonify({
                'success': False,
                'error': 'La lista non può essere vuota'
            }), 400
        
        # Pulisci items (rimuovi vuoti)
        items = [item.strip() for item in items if item.strip()]
        
        if not items:
            return jsonify({
                'success': False,
                'error': 'Nessun prodotto valido nella lista'
            }), 400
        
        # Esegui ottimizzazione
        print(f"🔍 Ottimizzazione richiesta per {len(items)} prodotti...")
        gemini_result = optimizer.optimize_shopping_list(items)
        
        # Converti formato Gemini → formato API
        # gemini_result['selections'] ha formato:
        # [{"requested": "Pasta", "options": [{"nome": ..., "prezzo": ..., "supermercato": ..., "reasoning": ...}]}]
        #
        # API frontend si aspetta:
        # [{"original_query": "Pasta", "alternatives": [{"nome": ..., "prezzo": ..., "supermercato": ..., "reasoning": ...}]}]
        
        formatted_results = []
        for selection in gemini_result.get('selections', []):
            formatted_results.append({
                'original_query': selection['requested'],
                'alternatives': selection.get('options', []),
                'total_found': len(selection.get('options', []))
            })
        
        total_products = len(formatted_results)
        total_matches = sum(len(r['alternatives']) for r in formatted_results)
        
        return jsonify({
            'success': True,
            'data': {
                'results': formatted_results,
                'summary': {
                    'total_products': total_products,
                    'total_matches': total_matches,
                    'avg_matches_per_product': round(total_matches / total_products, 1) if total_products > 0 else 0,
                    'best_store': gemini_result.get('best_store', 'N/A'),
                    'total_price': gemini_result.get('total_price', 0),
                    'coverage': gemini_result.get('coverage', 'N/A')
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Errore durante ottimizzazione: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Errore server: {str(e)}'
        }), 500


@app.route('/api/search', methods=['POST'])
def search_products():
    """
    Cerca prodotti nel database
    Body: {"query": "pasta"}
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo "query" obbligatorio'
            }), 400
        
        query = data['query'].strip()
        limit = data.get('limit', 20)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query non può essere vuota'
            }), 400
        
        # Cerca nel database
        products = db.search_product(query, limit=limit)
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'total_found': len(products),
                'products': products
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Avvio server API...")
    print("📊 Statistiche database:")
    try:
        stats = db.get_stats()
        print(f"   • Prodotti: {stats.get('totale_prodotti', 0)}")
        print(f"   • Supermercati: {stats.get('totale_supermercati', 0)}")
    except:
        print("   ⚠️  Impossibile recuperare statistiche")
    
    print("\n🌐 Server in ascolto su http://localhost:5000")
    print("📡 Endpoint disponibili:")
    print("   • GET  /api/health  - Health check")
    print("   • GET  /api/stats   - Statistiche database")
    print("   • POST /api/optimize - Ottimizza lista spesa")
    print("   • POST /api/search  - Cerca prodotti")
    print("\n💡 Premi CTRL+C per fermare il server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
