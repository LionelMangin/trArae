# 🎯 Guide Rapide - Scripts Serveur

## ✅ Scripts créés pour Git Bash

Deux scripts ont été créés pour gérer le serveur facilement :

### 📄 Fichiers
- **`start_server.sh`** - Démarre le serveur
- **`stop_server.sh`** - Arrête le serveur
- **`SCRIPTS_SERVEUR.md`** - Documentation complète

## 🚀 Utilisation dans Git Bash

### Démarrer le serveur
```bash
./start_server.sh
```

### Arrêter le serveur

**Option 1 : Dans le terminal du serveur**
```
Ctrl + C
```

**Option 2 : Depuis un autre terminal Git Bash**
```bash
./stop_server.sh
```

## 📋 Ce que font les scripts

### `start_server.sh`
1. Vérifie si un serveur tourne déjà
2. Propose de l'arrêter si nécessaire
3. Démarre le serveur sur http://127.0.0.1:8000

### `stop_server.sh`
1. Trouve le processus sur le port 8000
2. L'arrête proprement
3. Affiche un message de confirmation

## 💡 Note importante

Les scripts `.sh` sont automatiquement exécutables dans Git Bash sur Windows.
Vous n'avez pas besoin de faire `chmod +x`.

## 🎯 Workflow simple

```bash
# 1. Démarrer
./start_server.sh

# 2. Développer
# Le serveur se recharge automatiquement quand vous modifiez le code

# 3. Tester
# Ouvrir http://127.0.0.1:8000

# 4. Arrêter
Ctrl + C
# ou
./stop_server.sh
```

## 📚 Documentation complète

Consultez `SCRIPTS_SERVEUR.md` pour :
- Exemples détaillés
- Dépannage
- Astuces et alias
- Configuration avancée

---

**Prêt à utiliser !** Ouvrez Git Bash et tapez `./start_server.sh` 🚀
