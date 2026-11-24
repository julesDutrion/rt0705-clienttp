FROM python:3.12-slim

WORKDIR /client

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du client
COPY . .

# Dans le conteneur, le serveur doit écouter sur toutes les interfaces
ENV CLIENT_HOST=0.0.0.0

EXPOSE 5001

CMD ["python", "app.py"]