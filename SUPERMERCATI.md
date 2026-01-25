# 🛒 Supermercati Italiani - Riferimento per Parsing

Questo documento elenca i principali supermercati italiani con informazioni utili per sviluppare parser dedicati.

---

## 📋 Indice
1. [Supermercati Implementati](#supermercati-implementati)
2. [Supermercati Prioritari](#supermercati-prioritari)
3. [Supermercati Secondari](#supermercati-secondari)
4. [Note Tecniche](#note-tecniche)

---

## ✅ Supermercati Implementati

### 1. **Eurospin**
- **Sito**: https://laspesaonline.eurospin.it
- **Status**: ✅ Parser implementato (`EurospinParser`)
- **Tecnologia**: Vue.js, Salesforce Commerce Cloud, Shadow DOM
- **Note**: Richiede login OTP via email. Cookie persistence implementata.
- **Copertura**: Nazionale

---

## 🎯 Supermercati Prioritari

### 2. **Lidl Italia**
- **Sito**: https://www.lidl.it
- **Spesa online**: https://shop.lidl.it (limitato ad alcune zone)
- **Status**: ⏳ Da implementare
- **Tecnologia**: React, API REST
- **Note**: Volantino online sempre disponibile, spesa online solo in alcune città
- **Copertura**: Nazionale (700+ punti vendita)

### 3. **Conad**
- **Sito**: https://www.conad.it
- **Spesa online**: https://spesaonline.conad.it
- **Status**: ⏳ Da implementare
- **Tecnologia**: Custom, possibile API
- **Note**: Diverse insegne (Conad, Conad City, Spazio Conad, ecc.)
- **Copertura**: Nazionale (3.000+ punti vendita)

### 4. **Esselunga**
- **Sito**: https://www.esselunga.it
- **Spesa online**: https://www.esselungaacasa.it
- **Status**: ⏳ Da implementare
- **Tecnologia**: Custom web app, API proprietaria
- **Copertura**: Nord e Centro Italia

### 5. **Carrefour Italia**
- **Sito**: https://www.carrefour.it
- **Spesa online**: https://www.carrefour.it/spesa-online
- **Status**: ⏳ Da implementare
- **Tecnologia**: Vtex Commerce Platform
- **Copertura**: Nazionale (1.100+ punti vendita)

### 6. **Coop**
- **Sito**: https://www.e-coop.it
- **Spesa online**: https://www.cooponline.it
- **Status**: ⏳ Da implementare
- **Tecnologia**: Multi-piattaforma (diverse cooperative)
- **Copertura**: Nazionale (oltre 1.100 punti vendita)

---

## 🔵 Supermercati Secondari

### 7. **MD Discount**
- **Sito**: https://www.mdspa.it
- **Spesa online**: ❌ Non disponibile
- **Status**: ⏳ Da implementare (solo volantini)
- **Copertura**: Nazionale (800+ punti vendita)

### 8. **Penny Market**
- **Sito**: https://www.pennymarket.it
- **Spesa online**: ❌ Non disponibile
- **Status**: ⏳ Da implementare (solo volantini)
- **Copertura**: Nord e Centro Italia (400+ punti vendita)

### 9. **Iper La Grande i**
- **Sito**: https://www.ipergrandei.it
- **Spesa online**: https://www.spesadigitale.ipergrandei.it
- **Status**: ⏳ Da implementare
- **Copertura**: Nord Italia

### 10. **Pam Panorama**
- **Sito**: https://www.pampanorama.it
- **Spesa online**: https://www.pampanorama.it/spesa-online
- **Status**: ⏳ Da implementare
- **Copertura**: Nord e Centro Italia

### 11. **Bennet**
- **Sito**: https://www.bennet.com
- **Spesa online**: https://www.bennetdrive.it
- **Status**: ⏳ Da implementare
- **Copertura**: Nord Italia

### 12. **Tigros**
- **Sito**: https://www.tigros.it
- **Spesa online**: https://spesa.tigros.it
- **Status**: ⏳ Da implementare
- **Copertura**: Lombardia

### 13. **Aldi**
- **Sito**: https://www.aldi.it
- **Spesa online**: ❌ Non disponibile
- **Status**: ⏳ Da implementare (solo volantini)
- **Copertura**: Nord Italia (in espansione)

### 14. **Todis**
- **Sito**: https://www.todis.it
- **Spesa online**: ❌ Limitata
- **Status**: ⏳ Da implementare
- **Copertura**: Centro-Sud Italia

### 15. **Unes / U2**
- **Sito**: https://www.unesupermercati.it
- **Spesa online**: https://www.unesupermercati.it/spesa-online
- **Status**: ⏳ Da implementare
- **Copertura**: Lombardia

---

## 📊 Statistiche di Mercato

| Catena | Quote Mercato | Punti Vendita | Regioni |
|--------|---------------|---------------|---------|
| Conad | ~13.5% | 3.000+ | Tutte |
| Coop | ~12.5% | 1.100+ | Tutte |
| Esselunga | ~8% | 180+ | Nord/Centro |
| Carrefour | ~7% | 1.100+ | Tutte |
| Lidl | ~6% | 700+ | Tutte |
| Eurospin | ~5% | 1.200+ | Tutte |

---

## 🛠️ Note Tecniche per Parsing

### Tecnologie Comuni
- **Frontend**: React, Vue.js, Angular
- **E-commerce**: Salesforce Commerce Cloud, Vtex, Magento, Custom
- **Anti-bot**: Cloudflare, reCAPTCHA, rate limiting
- **Auth**: OAuth, JWT, Session cookies, OTP

### Sfide Comuni
1. **Login obbligatorio**: Molti richiedono account per vedere i prezzi
2. **Geolocalizzazione**: Prezzi/disponibilità variano per punto vendita
3. **Lazy loading**: Prodotti caricati dinamicamente con scroll
4. **Shadow DOM**: Web components complessi (es. Salesforce)
5. **API protection**: Header custom, token dinamici
6. **Rate limiting**: Necessità di pause tra richieste

### Best Practices
- ✅ User-Agent realistico
- ✅ Cookie persistence per evitare login ripetuti
- ✅ Pause random tra richieste (2-5 secondi)
- ✅ Rispettare robots.txt
- ✅ Limitare frequenza scraping (max 1x/giorno per supermercato)
- ✅ Gestione errori e retry intelligente

---

## 📝 Template Parser

Ogni parser dovrebbe:
1. Ereditare da `BaseParser` (classe astratta)
2. Implementare metodi:
    - `login()` - Gestione autenticazione
    - `get_categories()` - Recupero categorie
    - `scrape_category(url)` - Scraping prodotti
    - `extract_product_info(element)` - Parsing card prodotto
3. Utilizzare `PriceDatabase` per storage unificato
4. Gestire cookie e sessioni
5. Implementare retry e error handling

---

## 🔗 Risorse Utili

- **Volantino Facile**: https://www.volantinofacile.it (aggregatore volantini)
- **DoveConviene**: https://www.doveconviene.it (volantini e offerte)
- **PromoQui**: https://www.promoqui.it (cataloghi e promozioni)

---

## ⚖️ Note Legali

- ⚠️ Rispettare sempre i Termini di Servizio dei siti
- ⚠️ Non sovraccaricare i server con troppe richieste
- ⚠️ Uso personale/educativo consigliato
- ⚠️ Per uso commerciale, valutare API ufficiali se disponibili

---

**Ultimo aggiornamento**: Gennaio 2026
