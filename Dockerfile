# === File: Dockerfile ===
FROM python:3.13-slim

WORKDIR /app

# Kopiera requirements och installera
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera resten av appen
COPY . .

# Kopiera Streamlit config till rätt plats i containern
COPY .streamlit /app/.streamlit

# Exponera port
EXPOSE 8080

# Kör Streamlit med rätt port och inga extra adresser, den läses från config istället
CMD ["streamlit", "run", "streamlit_ui.py", "--server.port=8080"]

