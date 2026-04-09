"""
Configuration and constants for the project
"""

PROJECT_NAME = "Urban Copilot AI"
PROJECT_VERSION = "0.1.0"

# Database
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10

# Redis
REDIS_DB = 0
REDIS_EXPIRATION = 3600  # 1 hour

# Kafka
KAFKA_BATCH_SIZE = 100
KAFKA_BATCH_TIMEOUT_MS = 5000

# ML Models
MODEL_PATH = "models/artifacts"
SCALER_PATH = "models/scalers"

# API
API_TIMEOUT = 30
MAX_RETRIES = 3

# Geographic boundaries for CDMX
CDMX_BOUNDS = {
    "north": 19.5861,
    "south": 19.0296,
    "east": -98.9829,
    "west": -99.3607
}
