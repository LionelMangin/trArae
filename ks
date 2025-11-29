ps -eaf | grep "uvicorn" | grep -v grep | awk '{print $2}' | xargs kill -9 || echo "No server process found"
