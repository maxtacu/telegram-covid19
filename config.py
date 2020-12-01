import os
import yaml

TELEGRAM = {
    "token": os.getenv(
        "TOKEN", "test-token" # set your token here or as environment variable
    )
}
DATABASE = {
    "filename": "covid19.db"
}
PLOT = {
    "date_format": "%d/%m",
    "fontsize": 9,
    "fontweight": "bold"
}

with open('translations.yaml', 'r') as file:
    TRANSLATIONS = yaml.safe_load(file)
