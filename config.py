import os
import yaml

TELEGRAM = {
    "token": os.getenv(
        "TOKEN", "test-token"
    )
}
DATABASE = {
    "filename": "covid19.db"
}

with open('translations.yaml', 'r') as file:
    TRANSLATIONS = yaml.safe_load(file)
