import os

telegram = {
    "token": os.getenv(
        "TOKEN", "test-token"
    )
}
database = {
    "filename": "covid19.db"
}