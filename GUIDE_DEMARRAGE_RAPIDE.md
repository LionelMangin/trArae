# Guide de Démarrage Rapide - Système de Prix ETF

## 🚀 Démarrage en 5 minutes

### Étape 1 : Installer les dépendances
```bash
pip install requests
```

### Étape 2 : Initialiser la table (déjà fait ✓)
```bash
python src/init_etf_prices_table.py
```
**Résultat attendu :** `OK - Table etf_prices created successfully`

### Étape 3 : Vérifier l'installation
```bash
python test_etf_prices.py
```
**Résultat attendu :** `Total: 5/5 tests passed`

### Étape 4 : Récupérer les prix actuels
```bash
<python src/fetch_etf_prices.py>
```
**Résultat attendu :** 
```
Starting ETF price update...
Found X unique ISINs to update
OK - Fetched price for XXX: YY.YY
...
=== Update Complete ===
Success: X
Failed: Y
Total: Z
```

⚠️ **Note importante** : Certains ISINs peuvent échouer si la conversion ISIN → symbole Yahoo n'est pas correcte. C'est normal pour la première exécution.

### Étape 5 : Lancer le serveur
```bash
python src/server.py
```

### Étape 6 : Tester dans le navigateur
1. Ouvrir http://127.0.0.1:8000
2. Chercher le toggle switch dans le header : `[Prix pivot] ⚫── [Prix actuel]`
3. Cliquer pour basculer entre les modes
4. Observer les changements dans les valeurs affichées

## 🔧 Configuration personnalisée

### Si certains ISINs échouent

Créez un fichier de mapping ISIN → Ticker :

**`config/isin_to_ticker.csv`**
```csv
ISIN,Ticker,Exchange
IE00B4L5Y983,IWDA.AS,Amsterdam
LU1681043599,EUNL.DE,XETRA
IE00B3RBWM25,VWRL.AS,Amsterdam
IE00BK5BQT80,VWCE.DE,XETRA
```

Puis modifiez `src/fetch_etf_prices.py` pour utiliser ce fichier (voir `examples/custom_price_fetcher.py` pour des exemples).

### Automatiser la mise à jour quotidienne

#### Windows (Task Scheduler)
1. Ouvrir le Planificateur de tâches
2. Créer une tâche de base
3. Déclencheur : Quotidien à 18h00
4. Action : Démarrer un programme
   - Programme : `python`
   - Arguments : `src/fetch_etf_prices.py`
   - Dossier de départ : `F:\devPython\trArae`

#### Linux/Mac (Cron)
```bash
# Éditer crontab
crontab -e

# Ajouter cette ligne (exécution à 18h chaque jour)
0 18 * * * cd /path/to/trArae && python src/fetch_etf_prices.py >> log/price_fetch.log 2>&1
```

## 📊 Comprendre les différences entre les modes

### Mode Pivot (par défaut)
- **Avantage** : Reflète votre coût d'acquisition réel
- **Inconvénient** : Ne reflète pas la valeur de marché actuelle
- **Utilisation** : Pour voir votre performance depuis le dernier achat

### Mode Actuel
- **Avantage** : Reflète la valeur de marché en temps réel
- **Inconvénient** : Nécessite une mise à jour quotidienne des prix
- **Utilisation** : Pour voir la valeur réelle de votre portefeuille

### Exemple concret

Imaginons un ETF acheté plusieurs fois :
- Achat 1 (01/01/2024) : 10 parts à 100€ = 1000€
- Achat 2 (01/06/2024) : 10 parts à 110€ = 1100€
- Total : 20 parts, investi = 2100€

**Mode Pivot (dernier achat = 110€)**
- Valeur actuelle = 20 × 110€ = 2200€
- Plus-value = 2200€ - 2100€ = +100€ (+4.8%)

**Mode Actuel (prix du jour = 120€)**
- Valeur actuelle = 20 × 120€ = 2400€
- Plus-value = 2400€ - 2100€ = +300€ (+14.3%)

➡️ Le mode actuel montre la vraie plus-value !

## 🐛 Dépannage rapide

### Problème : Le toggle ne change rien
**Solution :**
```bash
# Vérifier qu'il y a des prix dans la base
python test_etf_prices.py

# Si "0 price records", récupérer les prix
python src/fetch_etf_prices.py
```

### Problème : Tous les ISINs échouent
**Causes possibles :**
1. Pas de connexion internet
2. Yahoo Finance bloque les requêtes
3. Conversion ISIN → Ticker incorrecte

**Solutions :**
1. Vérifier la connexion
2. Ajouter un délai entre les requêtes (déjà fait : 1 seconde)
3. Créer un fichier de mapping manuel (voir ci-dessus)

### Problème : Le serveur ne démarre pas
**Solution :**
```bash
# Vérifier que FastAPI est installé
pip install fastapi uvicorn

# Vérifier qu'aucun autre processus n'utilise le port 8000
# Windows :
netstat -ano | findstr :8000

# Linux/Mac :
lsof -i :8000
```

### Problème : Erreur "Table etf_prices does not exist"
**Solution :**
```bash
python src/init_etf_prices_table.py
```

## 📚 Documentation complète

Pour plus de détails, consultez :

- **Architecture** : `docs/architecture_prix_etf.md`
- **Documentation complète** : `docs/etf_prices_system.md`
- **Résumé des changements** : `CHANGEMENTS_PRIX_ETF.md`
- **Exemples de personnalisation** : `examples/custom_price_fetcher.py`

## ✅ Checklist de vérification

- [ ] Dépendances installées (`pip install requests`)
- [ ] Table créée (`python src/init_etf_prices_table.py`)
- [ ] Tests passent (`python test_etf_prices.py`)
- [ ] Prix récupérés (`python src/fetch_etf_prices.py`)
- [ ] Serveur fonctionne (`python src/server.py`)
- [ ] Toggle visible dans l'interface
- [ ] Toggle change les valeurs affichées
- [ ] Mise à jour quotidienne configurée (optionnel)

## 🎯 Prochaines étapes recommandées

1. **Tester le système** avec le toggle dans l'interface
2. **Vérifier les prix récupérés** pour vos ETF spécifiques
3. **Ajuster la conversion ISIN → Ticker** si nécessaire
4. **Configurer l'automatisation** pour les mises à jour quotidiennes
5. **Personnaliser** selon vos besoins (voir `examples/`)

## 💡 Astuces

- Le choix du mode est sauvegardé dans le navigateur (localStorage)
- Les prix sont mis en cache (1 par jour max)
- Vous pouvez forcer une mise à jour en supprimant les entrées de la table
- Le script `fetch_etf_prices.py` peut être exécuté plusieurs fois sans problème

## 🆘 Besoin d'aide ?

1. Consultez les logs : `python src/fetch_etf_prices.py`
2. Exécutez les tests : `python test_etf_prices.py`
3. Vérifiez la console du navigateur (F12)
4. Consultez la documentation complète

Bon trading ! 📈
