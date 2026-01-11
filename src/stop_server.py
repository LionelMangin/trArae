"""
Script to stop the FastAPI server running on port 8000
Usage: python src/stop_server.py
"""
import sys
import psutil
import time

PORT = 8000

def find_pids_on_port(port):
    """Find all PIDs using the specified port."""
    pids = set()
    # Method 1: Global net_connections (fastest, might need privileges)
    try:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                if conn.pid:
                    pids.add(conn.pid)
    except (psutil.AccessDenied, Exception):
        pass
        
    # Method 2: Iterate processes (slower, but works per-process permissions)
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
        
        # Check if this process has a parent that is also python (likely uvicorn reloader)
        # If so, we want to kill the parent to stop the reload loop
        try:
            parent = proc.parent()
            if parent and 'python' in parent.name().lower():
                print(f"🔄 Parent process detected (PID {parent.pid}), stopping entire tree...")
                proc = parent
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        # Get all children recursively
        try:
            children = proc.children(recursive=True)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            children = []
            
        # Add the main process to the list
        children.append(proc)
        
        print(f"🛑 Stopping {len(children)} processes (PID {proc.pid} and children)...")
        
        for p in children:
            try:
                p.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Wait for them to die
        gone, alive = psutil.wait_procs(children, timeout=3)
        
        for p in alive:
            print(f"⚠️ Forcing stop for PID {p.pid}...")
            try:
                p.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return True
    except psutil.NoSuchProcess:
        return True
    except Exception as e:
        print(f"❌ Error during stop: {e}")
        return False

def main():
    print(f"🔍 Searching for server on port {PORT}...")
    
    pids = find_pids_on_port(PORT)
    
    if not pids:
        print(f"❌ No server found on port {PORT}")
        # Double check with netstat just to inform user if it's a permission issue
        # (Optional, but helpful since user mentioned netstat works)
        sys.exit(1)
    
    print(f"📍 Processes found: {pids}")
    
    success = True
    for pid in pids:
        if not kill_process_tree(pid):
            success = False
            
    if success:
        print(f"✅ Server stopped successfully")
        sys.exit(0)
    else:
        print(f"⚠️ Some processes may not have been stopped")
        sys.exit(1)

if __name__ == "__main__":
    main()
