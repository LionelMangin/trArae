# Résumé des modifications - Système de Prix ETF

## Objectif
Ajouter un sélecteur on/off pour basculer entre deux modes de calcul de la valeur des positions :
- **Mode Pivot** : Utilise le prix au moment du dernier achat (comportement actuel)
- **Mode Actuel** : Utilise le prix actuel récupéré depuis le web

## Fichiers créés

### 1. Scripts Python
- **`src/init_etf_prices_table.py`** : Initialise la table `etf_prices` dans la base de données
- **`src/fetch_etf_prices.py`** : Récupère les prix actuels des ETF depuis Yahoo Finance
- **`test_etf_prices.py`** : Tests pour vérifier que le système fonctionne

### 2. Documentation
- **`docs/etf_prices_system.md`** : Documentation complète du système

## Fichiers modifiés

### 1. Backend (`src/server.py`)
- Ajout du paramètre `use_current_price` aux endpoints `/api/summary` et `/api/positions`
- Logique pour récupérer les prix depuis la table `etf_prices` quand le mode actuel est activé

### 2. Frontend
- **`src/static/index.html`** : Ajout du toggle switch dans le header
- **`src/static/style.css`** : Styles pour le toggle switch
- **`src/static/app.js`** : 
  - Gestion du toggle switch
  - Sauvegarde de la préférence dans localStorage
  - Passage du paramètre `use_current_price` aux appels API

### 3. Dépendances
- **`requirements.txt`** : Ajout de `requests` pour la récupération des prix

## Base de données

Nouvelle table créée :
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

## Utilisation

### Première utilisation

1. **Installer les dépendances** (si nécessaire) :
   ```bash
   pip install requests
   ```

2. **Initialiser la table** (déjà fait ✓) :
   ```bash
   python src/init_etf_prices_table.py
   ```

3. **Récupérer les prix actuels** :
   ```bash
   python src/fetch_etf_prices.py
   ```
   
   ⚠️ **Note importante** : Le script utilise Yahoo Finance. La conversion ISIN → symbole Yahoo 
   peut nécessiter des ajustements selon vos ETF. Par défaut, il essaie `{ISIN}.SW`.

4. **Lancer le serveur** :
   ```bash
   python src/server.py
   ```

5. **Utiliser le toggle** dans l'interface web pour basculer entre les modes

### Utilisation quotidienne

Pour mettre à jour les prix chaque jour, exécutez :
```bash
python src/fetch_etf_prices.py
```

Vous pouvez automatiser cela avec :
- **Windows** : Planificateur de tâches
- **Linux/Mac** : Cron job

## Fonctionnalités

### Toggle Switch
- Situé dans le header de l'interface
- Deux positions :
  - **Prix pivot** (gauche, par défaut) : Prix du dernier achat
  - **Prix actuel** (droite) : Prix récupéré depuis le web
- La préférence est sauvegardée dans le navigateur

### Récupération des prix
- Source : Yahoo Finance (configurable)
- Fréquence : Une fois par jour maximum (contrainte UNIQUE)
- Cache automatique : Si le prix du jour existe déjà, il n'est pas re-téléchargé

### Calculs affectés
Quand le mode "Prix actuel" est activé, les valeurs suivantes changent :
- Valeur actuelle de chaque position
- Plus-value de chaque position
- Valeur totale du portefeuille
- Plus-value totale
- Graphique de répartition des plus-values

## Tests

Pour vérifier que tout fonctionne :
```bash
python test_etf_prices.py
```

Tous les tests doivent passer (5/5).

## Prochaines étapes recommandées

1. **Tester la récupération des prix** :
   ```bash
   python src/fetch_etf_prices.py
   ```
   
2. **Vérifier les résultats** :
   - Regarder les logs pour voir si les prix ont été récupérés
   - Si certains ISINs échouent, vous devrez peut-être ajuster la logique de conversion ISIN → symbole

3. **Configurer l'automatisation** :
   - Planifier l'exécution quotidienne de `fetch_etf_prices.py`
   - Recommandé : après la fermeture des marchés (18h ou plus tard)

4. **Personnaliser si nécessaire** :
   - Modifier `fetch_etf_prices.py` pour utiliser une autre source de prix
   - Ajuster la logique de conversion ISIN → symbole selon vos ETF

## Dépannage

### Le toggle ne change rien
- Vérifiez que vous avez des prix dans la base de données
- Exécutez `python test_etf_prices.py` pour voir combien de prix sont stockés
- Si aucun prix, exécutez `python src/fetch_etf_prices.py`

### Les prix ne se récupèrent pas
- Vérifiez votre connexion internet
- Vérifiez les logs du script `fetch_etf_prices.py`
- La conversion ISIN → symbole Yahoo peut nécessiter des ajustements
- Consultez `docs/etf_prices_system.md` pour plus de détails

### Différences importantes entre les modes
C'est normal ! Le prix du dernier achat peut être très différent du prix actuel, 
surtout si :
- Il y a eu beaucoup de volatilité
- Le dernier achat date de longtemps
- Les marchés ont beaucoup évolué

## Support

Pour plus de détails, consultez :
- **Documentation complète** : `docs/etf_prices_system.md`
- **Code source** : Tous les fichiers sont commentés
- **Tests** : `test_etf_prices.py` pour des exemples d'utilisation
