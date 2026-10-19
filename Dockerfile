# ==========================================
# Uzum Market BI & Data Science Containerfile
# ==========================================
FROM python:3.11-slim

# Tizim paketlarini yangilash
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Ishchi katalog
WORKDIR /app

# Qaramliklarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodlarini nusxalash
COPY . .

# Xavfsizlik uchun non-root user yaratish
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Streamlit portini ochish
EXPOSE 8501

# Sog'lomlik tekshiruvi (Healthcheck)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Dasturni ishga tushirish buyrug'i
ENTRYPOINT ["streamlit", "run", "src/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
