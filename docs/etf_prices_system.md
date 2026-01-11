# Système de Prix des ETF

## Vue d'ensemble

Le système de prix des ETF permet de basculer entre deux modes de calcul de la valeur des positions :

1. **Mode Pivot** (par défaut) : Utilise le prix du dernier achat comme référence
2. **Mode Actuel** : Utilise le prix actuel récupéré depuis le web

## Architecture

### Base de données

Une nouvelle table `etf_prices` stocke les prix quotidiens des ETF :

```sql
CREATE TABLE etf_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isin TEXT NOT NULL,
    date TEXT NOT NULL,
    price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(isin, date)
);
```

La contrainte `UNIQUE(isin, date)` garantit qu'une seule valeur par jour et par ETF est conservée.

### Scripts

#### 1. Initialisation de la table

```bash
python src/init_etf_prices_table.py
```

Crée la table `etf_prices` si elle n'existe pas déjà.

#### 2. Récupération des prix

```bash
python src/fetch_etf_prices.py
```

Ce script :
- Récupère tous les ISINs uniques depuis la table `transactions`
- Pour chaque ISIN, tente de récupérer le prix actuel depuis Yahoo Finance
- Stocke le prix dans la table `etf_prices` (une seule fois par jour)
- Utilise un cache pour éviter les requêtes multiples le même jour

**Note** : Le script utilise Yahoo Finance comme source. Vous devrez peut-être ajuster la logique de conversion ISIN → symbole Yahoo selon vos ETF.

### API Backend

Deux endpoints ont été modifiés pour supporter le paramètre `use_current_price` :

- `GET /api/summary?use_current_price=true|false`
- `GET /api/positions?use_current_price=true|false`

Lorsque `use_current_price=true`, le système utilise les prix de la table `etf_prices` au lieu du prix du dernier achat.

### Interface utilisateur

Un toggle switch dans le header permet de basculer entre les deux modes :
- **Prix pivot** : Mode par défaut, utilise le prix du dernier achat
- **Prix actuel** : Utilise les prix récupérés depuis le web

Le choix de l'utilisateur est sauvegardé dans le `localStorage` du navigateur.

## Utilisation

### Première utilisation

1. Initialiser la table :
   ```bash
   python src/init_etf_prices_table.py
   ```

2. Récupérer les prix actuels :
   ```bash
   python src/fetch_etf_prices.py
   ```

3. Lancer le serveur :
   ```bash
   python src/server.py
   ```

4. Ouvrir l'interface web et utiliser le toggle pour basculer entre les modes

### Mise à jour quotidienne

Pour mettre à jour les prix quotidiennement, vous pouvez :

1. **Manuellement** :
   ```bash
   python src/fetch_etf_prices.py
   ```

2. **Automatiquement** (Windows Task Scheduler) :
   - Créer une tâche planifiée qui exécute le script chaque jour
   - Exemple : tous les jours à 18h après la fermeture des marchés

3. **Automatiquement** (cron sur Linux/Mac) :
   ```bash
   0 18 * * * cd /path/to/trArae && python src/fetch_etf_prices.py
   ```

## Personnalisation

### Changer la source de prix

Le script `fetch_etf_prices.py` utilise Yahoo Finance par défaut. Pour utiliser une autre source :

1. Modifier la fonction `fetch_etf_price(isin)` dans `src/fetch_etf_prices.py`
2. Implémenter votre propre logique de récupération de prix
3. Retourner le prix sous forme de `float`

Exemples d'alternatives :
- Alpha Vantage
- Finnhub
- IEX Cloud
- API de votre courtier

### Ajuster la fréquence de mise à jour

La contrainte `UNIQUE(isin, date)` permet une seule mise à jour par jour. Pour changer cela :

1. Modifier la table pour utiliser un timestamp au lieu d'une date
2. Ajuster la logique dans `fetch_etf_prices.py` pour gérer plusieurs mises à jour par jour

## Dépannage

### Les prix ne se mettent pas à jour

1. Vérifier que la table existe :
   ```bash
   sqlite3 data/trade_republic.db "SELECT * FROM etf_prices LIMIT 5;"
   ```

2. Vérifier les logs du script :
   ```bash
   python src/fetch_etf_prices.py
   ```

3. Vérifier la connexion internet et l'accès à Yahoo Finance

### Le toggle ne fonctionne pas

1. Vérifier la console du navigateur (F12) pour les erreurs JavaScript
2. Vérifier que le serveur est à jour et redémarré
3. Vider le cache du navigateur (Ctrl+F5)

### Différences importantes entre les modes

C'est normal ! Le mode pivot utilise le prix du dernier achat, qui peut être très différent du prix actuel si :
- Le marché a beaucoup évolué depuis le dernier achat
- Il y a eu une longue période sans achat
- L'ETF a connu une forte volatilité

## Améliorations futures

- [ ] Ajouter un indicateur visuel de la date de dernière mise à jour des prix
- [ ] Permettre de forcer une mise à jour manuelle depuis l'interface
- [ ] Afficher l'historique des prix dans un graphique
- [ ] Ajouter des alertes si les prix n'ont pas été mis à jour depuis X jours
- [ ] Supporter plusieurs sources de prix avec fallback automatique
