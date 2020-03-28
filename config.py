import os

with open('helpmessage.txt', 'r') as file:
    helpmessage = file.read()

telegram = {
    "token": os.getenv(
        "TOKEN", "test-token"
    ),
    "helptext": helpmessage,
}
database = {
    "filename": "covid19.db"
}