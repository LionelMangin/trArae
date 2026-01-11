# Architecture du Système de Prix ETF

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERFACE WEB                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Header                                                   │   │
│  │  ┌────────────┐  ┌──────────────────┐                   │   │
│  │  │ My Portfolio│  │ [Prix pivot] ⚫──│ [Prix actuel]    │   │
│  │  └────────────┘  └──────────────────┘                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Toggle Switch (ON/OFF)                                          │
│    │                                                              │
│    ├─ OFF (défaut) : Mode Pivot                                 │
│    │   └─> Utilise le prix du dernier achat                     │
│    │                                                              │
│    └─ ON : Mode Actuel                                           │
│        └─> Utilise les prix de la table etf_prices              │
│                                                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP Request
                            │ GET /api/positions?use_current_price=true/false
                            │ GET /api/summary?use_current_price=true/false
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  server.py                                                │   │
│  │                                                            │   │
│  │  @app.get("/api/positions")                              │   │
│  │  def get_positions(use_current_price: bool = False):     │   │
│  │      if use_current_price:                               │   │
│  │          ├─> Récupère prix depuis etf_prices             │   │
│  │      else:                                                │   │
│  │          └─> Calcule prix depuis dernier achat           │   │
│  │                                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ SQL Query
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BASE DE DONNÉES (SQLite)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Table: transactions                                      │   │
│  │  ├─ id, date, isin, name, type, value, shares           │   │
│  │  └─ Contient l'historique des achats/ventes             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Table: etf_prices (NOUVELLE)                            │   │
│  │  ├─ id, isin, date, price, created_at                   │   │
│  │  ├─ UNIQUE(isin, date) ← Une seule valeur par jour      │   │
│  │  └─ Contient les prix actuels récupérés du web          │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────▲─────────────────────────────────────┘
                            │
                            │ INSERT/SELECT
                            │
┌─────────────────────────────────────────────────────────────────┐
│              SCRIPT DE RÉCUPÉRATION DES PRIX                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  fetch_etf_prices.py                                      │   │
│  │                                                            │   │
│  │  1. Récupère tous les ISINs depuis transactions          │   │
│  │  2. Pour chaque ISIN:                                     │   │
│  │     ├─> Vérifie si prix du jour existe déjà             │   │
│  │     ├─> Si non, récupère depuis Yahoo Finance            │   │
│  │     └─> Stocke dans etf_prices                           │   │
│  │                                                            │   │
│  │  Exécution: Manuelle ou automatisée (cron/scheduler)     │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────▲─────────────────────────────────────┘
                            │
                            │ HTTP Request
                            │
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE DE DONNÉES WEB                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Yahoo Finance API                                        │   │
│  │  https://query1.finance.yahoo.com/v8/finance/chart/...   │   │
│  │                                                            │   │
│  │  Alternatives possibles:                                  │   │
│  │  ├─ Alpha Vantage                                        │   │
│  │  ├─ Finnhub                                              │   │
│  │  ├─ IEX Cloud                                            │   │
│  │  └─ API du courtier                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Flux de données

### Mode Pivot (par défaut)
```
User clique sur toggle (OFF)
    │
    ├─> localStorage.setItem('priceMode', 'pivot')
    │
    ├─> fetch('/api/positions?use_current_price=false')
    │
    └─> Backend:
        ├─> Récupère transactions
        ├─> Pour chaque ISIN:
        │   ├─> Trouve le dernier achat
        │   └─> Prix = value / shares du dernier achat
        │
        └─> Retourne positions avec prix pivot
```

### Mode Actuel
```
User clique sur toggle (ON)
    │
    ├─> localStorage.setItem('priceMode', 'current')
    │
    ├─> fetch('/api/positions?use_current_price=true')
    │
    └─> Backend:
        ├─> Récupère transactions
        ├─> Récupère prix actuels depuis etf_prices
        ├─> Pour chaque ISIN:
        │   ├─> Si prix actuel existe: utilise ce prix
        │   └─> Sinon: fallback sur prix pivot
        │
        └─> Retourne positions avec prix actuels
```

### Mise à jour des prix
```
Exécution quotidienne (manuelle ou automatisée)
    │
    ├─> python src/fetch_etf_prices.py
    │
    └─> Pour chaque ISIN:
        ├─> Vérifie si prix du jour existe
        │   ├─> Oui: Skip (UNIQUE constraint)
        │   └─> Non: Continue
        │
        ├─> Récupère prix depuis Yahoo Finance
        │   ├─> Succès: INSERT INTO etf_prices
        │   └─> Échec: Log erreur, continue
        │
        └─> Résumé: X succès, Y échecs
```

## Fichiers créés/modifiés

### Nouveaux fichiers
```
src/
├── init_etf_prices_table.py    # Initialisation de la table
└── fetch_etf_prices.py          # Récupération des prix

test_etf_prices.py               # Tests du système

docs/
└── etf_prices_system.md         # Documentation complète

examples/
└── custom_price_fetcher.py      # Exemples de personnalisation

CHANGEMENTS_PRIX_ETF.md          # Ce fichier - résumé
```

### Fichiers modifiés
```
src/
├── server.py                    # Ajout paramètre use_current_price
└── static/
    ├── index.html               # Ajout toggle switch
    ├── style.css                # Styles du toggle
    └── app.js                   # Logique du toggle

requirements.txt                 # Ajout de 'requests'
```

## Calculs affectés par le mode

| Métrique                  | Mode Pivot                    | Mode Actuel                |
|---------------------------|-------------------------------|----------------------------|
| Prix unitaire             | Prix du dernier achat         | Prix de etf_prices         |
| Valeur actuelle           | shares × prix_pivot           | shares × prix_actuel       |
| Plus-value                | valeur_actuelle - investi     | valeur_actuelle - investi  |
| Valeur totale portfolio   | Σ valeurs_actuelles           | Σ valeurs_actuelles        |
| Plus-value totale         | Σ plus-values                 | Σ plus-values              |
| Graphique répartition     | Basé sur plus-values pivot    | Basé sur plus-values actuelles |

## Sécurité et robustesse

### Contraintes de la base de données
- `UNIQUE(isin, date)` : Empêche les doublons
- Index sur `(isin, date DESC)` : Optimise les requêtes

### Gestion des erreurs
- Fallback automatique sur prix pivot si prix actuel indisponible
- Logs détaillés dans fetch_etf_prices.py
- Tests automatisés (test_etf_prices.py)

### Performance
- Cache automatique (1 prix par jour max)
- Requêtes SQL optimisées avec index
- Pas de re-téléchargement si prix existe déjà

## Maintenance

### Quotidienne
```bash
# Automatiser avec cron ou Task Scheduler
python src/fetch_etf_prices.py
```

### Hebdomadaire
```bash
# Vérifier les logs
python test_etf_prices.py
```

### Mensuelle
```bash
# Nettoyer les vieux prix (optionnel)
sqlite3 data/trade_republic.db "DELETE FROM etf_prices WHERE date < date('now', '-90 days')"
```
