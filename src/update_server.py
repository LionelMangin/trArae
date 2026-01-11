"""
Script to update the server data (run the importer)
Usage: python src/update_server.py
"""
import subprocess
import sys
import os

# Add the project root to sys.path if running from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    print("🚀 Mise à jour du serveur (import des données)...")
    
    try:
        # Run src.main module
        subprocess.run([
            sys.executable, '-m', 'src.main'
        ], cwd=project_root, check=True)
        
        print("✅ Mise à jour terminée")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
