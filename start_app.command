#!/bin/bash
echo "=================================================="
echo "⛳ Starting DNS Golf Outlet Facebook Post Assistant"
echo "=================================================="
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "📍 Working Directory: $DIR"
echo "🌐 Opening http://localhost:5050 in your browser..."
open "http://localhost:5050"

/usr/bin/python3 app.py
