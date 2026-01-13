"""Configuration settings for C2 server"""

import os

# Server Configuration
SERVER_HOST = os.getenv('C2_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('C2_PORT', 5000))
SECRET_KEY = os.getenv('C2_SECRET', 'change-this-secret-key-in-production')

# Agent Configuration
BEACON_INTERVAL = 30  # seconds
AGENT_TIMEOUT = 300  # seconds

# Database
DATABASE_PATH = 'c2_database.db'

# Encryption
ENCRYPTION_KEY_SIZE = 32  # bytes for AES-256
