# Guide Visuel - Toggle Switch Prix ETF

## Localisation du Toggle

Le toggle switch se trouve dans le **header** de l'interface, à droite du titre "My Portfolio".

```
┌─────────────────────────────────────────────────────────────────┐
│  My Portfolio          [Prix pivot] ⚫── [Prix actuel]  Last... │
│                                                                  │
│  ┌──────────────────┐  ┌────────────────────────────────────┐  │
│  │  Statistiques    │  │  Répartition des Plus-Values       │  │
│  │                  │  │                                     │  │
│  │  Transactions    │  │         [Graphique]                │  │
│  │  Investissement  │  │                                     │  │
│  └──────────────────┘  └────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Positions                                                │  │
│  │  [Table des positions]                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## États du Toggle

### Mode Pivot (par défaut - OFF)
```
[Prix pivot] ⚫── [Prix actuel]
     ↑                ↑
   ACTIF          INACTIF
   (vert)         (gris)
```

**Calcul utilisé** : Prix du dernier achat de chaque ETF

**Exemple** :
- Dernier achat de EWLD.PA : 34.50 €
- Valeur utilisée : 34.50 €

### Mode Actuel (ON)
```
[Prix pivot] ──⚫ [Prix actuel]
     ↑                ↑
  INACTIF          ACTIF
   (gris)          (vert)
```

**Calcul utilisé** : Prix actuel récupéré depuis Yahoo Finance

**Exemple** :
- Prix actuel de EWLD.PA : 35.852 €
- Valeur utilisée : 35.852 €

## Comment utiliser

### 1. Cliquer sur le toggle
```
Avant :  [Prix pivot] ⚫── [Prix actuel]
                      ↑
                   Cliquer ici

Après :  [Prix pivot] ──⚫ [Prix actuel]
```

### 2. Observer les changements

Les valeurs suivantes vont changer automatiquement :

#### Dans les statistiques
- ✓ Valeur actuelle (total)
- ✓ Plus-value totale

#### Dans le graphique
- ✓ Répartition des plus-values
- ✓ Pourcentages affichés

#### Dans le tableau des positions
- ✓ Valeur (colonne 2)
- ✓ Plus value (colonne 3)
- ✓ Prix (colonne 5)

### 3. Comparer les modes

**Astuce** : Basculez plusieurs fois entre les deux modes pour voir les différences !

## Exemple concret avec vos données

### Amundi MSCI World (FR0011871078)

Supposons que votre dernier achat était à **34.50 €** et le prix actuel est **35.852 €**.

#### Mode Pivot
```
Parts : 10
Prix : 34.50 € (dernier achat)
Valeur : 10 × 34.50 = 345.00 €
Investi : 340.00 €
Plus-value : 345.00 - 340.00 = +5.00 € (+1.5%)
```

#### Mode Actuel
```
Parts : 10
Prix : 35.852 € (prix actuel)
Valeur : 10 × 35.852 = 358.52 €
Investi : 340.00 €
Plus-value : 358.52 - 340.00 = +18.52 € (+5.4%)
```

**Différence** : +13.52 € de plus-value réelle !

## Indicateurs visuels

### Couleurs du toggle
- **Vert** : Mode actif
- **Gris** : Mode inactif
- **Fond du slider** : Gris (inactif) ou Vert (actif)

### Texte
- **Gras + Vert** : Mode sélectionné
- **Normal + Gris** : Mode non sélectionné

### Animation
- Transition fluide de 0.4 secondes
- Le bouton glisse de gauche à droite (ou vice-versa)

## Sauvegarde de la préférence

Votre choix est **automatiquement sauvegardé** dans le navigateur.

```
Vous choisissez : Mode Actuel
    ↓
Sauvegarde dans localStorage
    ↓
La prochaine fois que vous ouvrez la page :
Mode Actuel est automatiquement sélectionné
```

**Note** : La préférence est sauvegardée par navigateur. Si vous changez de navigateur, vous devrez re-sélectionner votre mode préféré.

## Dépannage visuel

### Le toggle ne s'affiche pas
1. Vérifiez que le serveur est lancé
2. Rafraîchissez la page (F5)
3. Videz le cache (Ctrl + F5)

### Le toggle ne change rien
1. Vérifiez la console du navigateur (F12)
2. Vérifiez qu'il y a des prix dans la base :
   ```bash
   python test_etf_prices.py
   ```
3. Si "0 price records", exécutez :
   ```bash
   python src/fetch_etf_prices.py
   ```

### Les valeurs sont identiques dans les deux modes
**C'est normal si** :
- Vous venez d'acheter (prix actuel ≈ prix d'achat)
- Le marché n'a pas bougé
- Tous vos achats sont récents

**Vérifiez** :
```bash
# Voir les prix actuels
python test_etf_prices.py
```

## Raccourcis clavier

Malheureusement, il n'y a pas de raccourci clavier pour le toggle. Vous devez cliquer dessus.

**Suggestion** : Vous pouvez ajouter un raccourci en modifiant `app.js` si vous le souhaitez.

## Responsive Design

Le toggle s'adapte à toutes les tailles d'écran :
- **Desktop** : Affiché à droite du titre
- **Tablet** : Affiché sur la même ligne
- **Mobile** : Peut passer sur une nouvelle ligne si nécessaire

## Accessibilité

- ✓ Contraste suffisant pour la lisibilité
- ✓ Taille de clic suffisante (50px × 26px)
- ✓ Animation fluide mais pas trop rapide
- ✓ Texte descriptif clair

---

**Astuce finale** : Essayez de basculer le toggle pendant que vous regardez le graphique de répartition. C'est très satisfaisant de voir les barres changer en temps réel ! 📊✨
