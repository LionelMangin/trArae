# Scripts de gestion du serveur (Git Bash)

## 📁 Fichiers

- **`start_server.sh`** - Démarre le serveur
- **`stop_server.sh`** - Arrête le serveur

## 🚀 Utilisation

### Première utilisation

Rendez les scripts exécutables :
```bash
chmod +x start_server.sh stop_server.sh
```

### Démarrer le serveur

```bash
./start_server.sh
```

Le script :
- ✅ Vérifie si un serveur tourne déjà
- ✅ Propose de l'arrêter si nécessaire
- ✅ Démarre le serveur sur http://127.0.0.1:8000

### Arrêter le serveur

**Méthode 1 : Dans le terminal du serveur**
```
Ctrl + C
```

**Méthode 2 : Depuis un autre terminal**
```bash
./stop_server.sh
```

Le script :
- ✅ Trouve le processus sur le port 8000
- ✅ L'arrête proprement
- ✅ Affiche un message de confirmation

## 📋 Exemples

### Démarrage simple
```bash
$ ./start_server.sh
🚀 Démarrage du serveur...
▶️  Lancement de uvicorn...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Arrêt simple
```bash
$ ./stop_server.sh
🛑 Arrêt du serveur sur le port 8000...
📍 Processus trouvé : PID 12345
✅ Serveur arrêté avec succès (PID: 12345)
```

### Redémarrage
```bash
$ ./start_server.sh
🚀 Démarrage du serveur...
⚠️  Un serveur tourne déjà sur le port 8000 (PID: 12345)
Voulez-vous l'arrêter et redémarrer ? (o/n) o
🛑 Arrêt du serveur sur le port 8000...
✅ Serveur arrêté avec succès (PID: 12345)
▶️  Lancement de uvicorn...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

## 🔧 Dépannage

### "Permission denied"
Rendez le script exécutable :
```bash
chmod +x stop_server.sh
```

### "Aucun serveur trouvé"
Le serveur n'est pas en cours d'exécution sur le port 8000.

### Le script ne trouve pas le processus
Vérifiez manuellement :
```bash
netstat -ano | grep :8000
```

## 💡 Astuces

### Créer des alias (optionnel)
Ajoutez dans votre `~/.bashrc` :
```bash
alias start='cd /f/devPython/trArae && ./start_server.sh'
alias stop='cd /f/devPython/trArae && ./stop_server.sh'
```

Puis rechargez :
```bash
source ~/.bashrc
```

Maintenant vous pouvez simplement taper :
```bash
start  # Démarre le serveur
stop   # Arrête le serveur
```

### Vérifier le statut
```bash
# Voir si le serveur tourne
netstat -ano | grep :8000

# Voir tous les processus Python
tasklist | grep python
```

## 📚 Commandes utiles

```bash
# Démarrer le serveur
./start_server.sh

# Arrêter le serveur
./stop_server.sh

# Ou simplement Ctrl+C dans le terminal du serveur

# Vérifier si le serveur tourne
curl http://127.0.0.1:8000/api/summary

# Voir les logs en temps réel (si lancé en arrière-plan)
tail -f nohup.out
```

## ⚙️ Configuration

Les scripts utilisent :
- **Port** : 8000 (modifiable dans les scripts)
- **Host** : 127.0.0.1 (localhost uniquement)
- **Mode** : --reload (redémarre automatiquement si le code change)

Pour changer le port, éditez les scripts et remplacez `8000` par votre port.

## 🎯 Workflow recommandé

1. **Démarrer** : `./start_server.sh`
2. **Développer** : Le serveur se recharge automatiquement
3. **Tester** : Ouvrir http://127.0.0.1:8000
4. **Arrêter** : `Ctrl+C` ou `./stop_server.sh`

---

**Note** : Ces scripts sont conçus pour Git Bash sur Windows 11. Pour PowerShell ou CMD, utilisez les fichiers `.bat` à la place.
