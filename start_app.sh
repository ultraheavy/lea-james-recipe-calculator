#!/bin/bash
echo "Starting Restaurant Calculator App..."
echo "Killing any existing processes..."
pkill -f "python3 app.py" 2>/dev/null || true
sleep 2

echo "Activating virtual environment and starting Flask app on port 8888..."
source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &
sleep 3

echo "App started! Access it at: http://localhost:8888"
echo "Log file: app.log"
echo ""
echo "To stop the app, run: pkill -f 'python3 app.py'"
echo ""
echo "Testing connection..."
if curl -s "http://localhost:8888" > /dev/null; then
    echo "✅ App is running successfully!"
else
    echo "❌ App failed to start. Check app.log for errors."
fi
