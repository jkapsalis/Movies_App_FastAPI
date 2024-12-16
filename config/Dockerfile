# Χρησιμοποιούμε την εικόνα Python 3.10-slim
FROM python:3.10-slim

# Ορίζουμε το working directory στο /app
WORKDIR /app

# Αντιγράφουμε το requirements.txt πρώτα για να εγκαταστήσουμε τις εξαρτήσεις
COPY requirements.txt /app/

# Εγκαθιστούμε τις απαιτούμενες βιβλιοθήκες
RUN pip install --no-cache-dir -r requirements.txt

# Αντιγράφουμε το υπόλοιπο της εφαρμογής
COPY . /app/

# Εκθέτουμε την πόρτα του FastAPI
EXPOSE 80

# Ορίζουμε την εντολή εκκίνησης
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
