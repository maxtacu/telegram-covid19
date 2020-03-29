
with open('text/helpmessageEN.txt', 'r') as file:
    helpmessageEN = file.read()

with open('text/helpmessageRU.txt', 'r') as file:
    helpmessageRU = file.read()

with open('text/helpmessagePT.txt', 'r') as file:
    helpmessagePT = file.read()

helpmessage = {
    "lang-en": helpmessageEN,
    "lang-ru": helpmessageRU,
    "lang-pt": helpmessagePT
}