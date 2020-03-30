import os
import yaml

telegram = {
    "token": os.getenv(
        "TOKEN", "test-token"
    )
}
database = {
    "filename": "covid19.db"
}

with open('translations.yaml', 'r') as file:
    translations = yaml.safe_load(file)