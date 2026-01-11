#!/bin/bash
# Script to stop the FastAPI server running on port 8000
# Usage: ./stop_server.sh

PORT=8000

echo "🛑 Arrêt du serveur sur le port $PORT..."

# Find the PID using the port
PID=$(netstat -ano | grep ":$PORT" | grep "LISTENING" | awk '{print $5}' | head -n 1)

if [ -z "$PID" ]; then
    echo "❌ Aucun serveur trouvé sur le port $PORT"
    exit 1
fi

echo "📍 Processus trouvé : PID $PID"

# Kill the process using Windows taskkill command
# MSYS_NO_PATHCONV=1 prevents Git Bash from converting /F to a path
MSYS_NO_PATHCONV=1 taskkill /F /PID $PID 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Serveur arrêté avec succès (PID: $PID)"
else
    echo "❌ Erreur lors de l'arrêt du serveur"
    echo "💡 Essayez manuellement dans PowerShell : taskkill /F /PID $PID"
    exit 1
fi
