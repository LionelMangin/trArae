"""
Script to start the FastAPI server
Usage: python src/start_server.py
"""
import subprocess
import sys
import os
import psutil
import time

# Add the project root to sys.path if running from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

PORT = 8000

def find_pids_on_port(port):
    """Find all PIDs using the specified port."""
    pids = set()
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                if conn.pid:
                    pids.add(conn.pid)
    except (psutil.AccessDenied, Exception):
        pass
        
    if not pids:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.net_connections(kind='inet')
                for conn in connections:
                    if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                        pids.add(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    return list(pids)

def kill_process_tree(pid):
    """Kill the process and its children/parent reloader."""
    try:
        proc = psutil.Process(pid)
        try:
            parent = proc.parent()
            if parent and 'python' in parent.name().lower():
                proc = parent
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        try:
            children = proc.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            children = []
        children.append(proc)
        
        for p in children:
            try:
                p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        psutil.wait_procs(children, timeout=3)
        
        for p in children:
            try:
                if p.is_running():
                    p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return True
    except psutil.NoSuchProcess:
        return True
    except Exception:
        return False

def stop_existing_server():
    """Stop the existing server if running."""
    pids = find_pids_on_port(PORT)
    
    if pids:
        print(f"Warning: A server is already running on port {PORT} (PIDs: {pids})")
        response = input("Do you want to stop it and restart? (y/n) ").strip().lower()
        
        if response in ['y', 'yes']:
            print(f"Stopping server...")
            for pid in pids:
                kill_process_tree(pid)
            print(f"Server stopped")
            time.sleep(1)
            return True
        else:
            print("Cancelled")
            return False
    
    return True

def start_server():
    """Start the FastAPI server."""
    print("Starting uvicorn...")
    print(f"The server will be accessible at http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Start uvicorn
        # We run from project root context
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'src.server:app',
            '--host', '127.0.0.1',
            '--port', str(PORT),
            '--reload'
        ], cwd=project_root, check=True)
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)

def main():
    print("Starting server...")
    
    # Check if server is already running
    if not stop_existing_server():
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
