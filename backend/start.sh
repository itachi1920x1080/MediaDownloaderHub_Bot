#!/bin/bash
# Start the background worker (bot)
python bot.py &

# Start the web server (flask API)
gunicorn app:app -b 0.0.0.0:$PORT
