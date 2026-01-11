# Mise à jour du comportement de récupération des prix

## Changement effectué

### Avant
- Si un prix existait déjà pour aujourd'hui : **SKIP** (ignoré)
- Le script ne récupérait pas de nouveau prix
- Message : `SKIP - Skipping {isin} - already have today's price`

### Après (actuel)
- Si un prix existe déjà pour aujourd'hui : **UPDATE** (mis à jour)
- Le script récupère toujours le nouveau prix
- Le prix existant est **remplacé** par le nouveau
- Message : `UPDATE - Updated price for {isin} on {date}: {old_price} -> {new_price}`

## Avantages

### 1. Prix toujours à jour
Vous pouvez exécuter le script plusieurs fois par jour pour avoir le prix le plus récent :
- Matin : Prix à l'ouverture
- Midi : Prix en milieu de journée
- Soir : Prix à la clôture

### 2. Correction automatique
Si un prix était incorrect (erreur de récupération), il sera automatiquement corrigé à la prochaine exécution.

### 3. Flexibilité
Vous n'êtes plus limité à une seule mise à jour par jour.

## Comportement technique

### Base de données
```sql
-- Utilise INSERT OR REPLACE au lieu de INSERT OR IGNORE
INSERT OR REPLACE INTO etf_prices (isin, date, price)
VALUES (?, ?, ?)
```

### Logique
1. Vérifier si un prix existe pour (isin, date)
2. Si oui : Afficher l'ancien prix et le remplacer
3. Si non : Insérer le nouveau prix
4. Toujours récupérer depuis Yahoo Finance (pas de skip)

## Exemple de logs

### Première exécution du jour
```
INFO:__main__:OK - Fetched price for FR0011871078 (EWLD.PA): 35.852
INFO:__main__:OK - Stored new price for FR0011871078 on 2025-12-11: 35.852
```

### Exécutions suivantes le même jour
```
INFO:__main__:OK - Fetched price for FR0011871078 (EWLD.PA): 35.900
INFO:__main__:UPDATE - Updated price for FR0011871078 on 2025-12-11: 35.852 -> 35.900
```

Vous voyez clairement :
- ✓ L'ancien prix (35.852)
- ✓ Le nouveau prix (35.900)
- ✓ Que c'est une mise à jour (UPDATE)

## Cas d'usage

### Suivi intra-journalier
```bash
# Matin (9h) - Prix à l'ouverture
python src/fetch_etf_prices.py

# Midi (12h) - Prix en milieu de journée
python src/fetch_etf_prices.py

# Soir (18h) - Prix à la clôture
python src/fetch_etf_prices.py
```

Chaque exécution met à jour les prix avec les valeurs les plus récentes.

### Correction d'erreurs
Si Yahoo Finance a retourné un prix incorrect le matin, la prochaine exécution le corrigera automatiquement.

## Impact sur l'interface

Quand vous utilisez le toggle "Prix actuel" dans l'interface :
- Le prix affiché sera **toujours le plus récent** récupéré pour aujourd'hui
- Si vous exécutez le script plusieurs fois, vous verrez les derniers prix

## Recommandations

### Fréquence d'exécution
- **Minimum** : 1 fois par jour (après la clôture, vers 18h)
- **Recommandé** : 2 fois par jour (ouverture + clôture)
- **Maximum** : Autant que nécessaire (pas de limite)

### Automatisation
Si vous automatisez avec le Planificateur de tâches :
```
Tâche 1 : 09h30 (après ouverture des marchés)
Tâche 2 : 18h00 (après clôture des marchés)
```

### Limite de requêtes
⚠️ **Attention** : Yahoo Finance peut limiter les requêtes si vous exécutez trop souvent.
- Délai entre chaque ISIN : 1 seconde (déjà implémenté)
- Évitez d'exécuter plus de 10 fois par jour

## Historique des prix

### Conservation
La table `etf_prices` conserve **un seul prix par jour** par ISIN :
- Date : 2025-12-11, Prix : Le dernier prix récupéré ce jour
- Date : 2025-12-12, Prix : Le dernier prix récupéré ce jour
- etc.

### Historique
Si vous voulez conserver l'historique intra-journalier, vous devriez :
1. Créer une table séparée `etf_prices_history`
2. Modifier le script pour y stocker tous les prix
3. Utiliser un timestamp au lieu d'une date

Mais pour l'usage actuel (un prix par jour), le système actuel est optimal.

## Vérification

Pour voir les prix actuels dans la base :
```bash
python test_etf_prices.py
```

Ou directement en SQL :
```bash
sqlite3 data/trade_republic.db "SELECT * FROM etf_prices WHERE date = date('now')"
```

## Résumé

| Aspect | Avant | Après |
|--------|-------|-------|
| Comportement | SKIP si existe | UPDATE si existe |
| Exécutions multiples | Ignorées | Mises à jour |
| Prix affiché | Premier du jour | Dernier du jour |
| Flexibilité | Limitée | Maximale |
| Logs | SKIP message | UPDATE avec ancien/nouveau |

---

**Conclusion** : Le système est maintenant plus flexible et vous permet d'avoir toujours les prix les plus récents, même si vous exécutez le script plusieurs fois par jour ! 🎯
