#!/bin/bash
echo "⛳ Starting DNS Golf Outlet Facebook Post Assistant..."
cd "$(dirname "$0")"
/usr/bin/python3 -m pip install -q -r requirements.txt
/usr/bin/python3 app.py
