# Stage 20: Deployment & Containerization (Docker Architecture)

> **Kategoriya:** DevOps, MLOps & Production Containerization  
> **Status:** Muvaffaqiyatli yakunlandi ✅  
> **Fayllar:** `Dockerfile`, `docker-compose.yml`, `.dockerignore`  
> **Test moduli:** `tests/test_dashboard_and_deployment.py` (Passed)

---

## 1. Nima Uchun Docker va Konteynerizatsiya Kerak?

Dasturlashda "Mening kompyuterimda ishlayotgan edi" degan holat sanoat standartlarida mutlaqo qabul qilinmaydi. Python versiyalari, operatsion tizim kutubxonalari va portlar turli xil serverlarda har xil bo'lishi mumkin.

Biz butun loyiha (Data ombori, modellar, vizualizatsiyalar va Streamlit boshqaruv paneli)ni **Docker konteyneri** ichiga qadoqladik. Bu loyihani Amazon AWS, Google Cloud, DigitalOcean yoki mahalliy serverda bitta buyruq (`docker compose up`) bilan bir xil ishga tushirish imkonini beradi.

---

## 2. Docker Arxitekturasi va Xavfsizlik Tamoyillari

1. **Lightweight Base Image:**
   - Xotirani tejash va tez yuklanish uchun rasmiy `python:3.11-slim` imijidan foydalanildi.
2. **Xavfsizlik (Non-root user):**
   - Konteyner ichida `root` huquqlarida ishlash xavfsizlikka zid. Shuning uchun `appuser (UID 1000)` yaratilib, barcha jarayonlar cheklangan huquqlarda ishga tushirildi.
3. **Healthcheck mexanizmi:**
   - Konteynerning holatini muntazam tekshirib turuvchi `curl http://localhost:8501/_stcore/health` ssenariysi kiritildi.
4. **Volume Mounting:**
   - Ma'lumotlar bazasi (`data/`) va hisobotlar (`reports/`) konteyner tashqarisida saqlanib, konteyner o'chirilganda ham ma'lumotlar yo'qolmaydi (Persistent Storage).

---

## 3. Ishga Tushirish Yo'riqnomasi (1 Buyruq)

```bash
# Konteynerni qurish va fonda ishga tushirish:
docker compose up -d --build

# Boshqaruv panelini brauzerda ochish:
# http://localhost:8501
```

---

## 4. Web Sayt / Portfolio Showcase uchun Xulosalar

- **Pitch:** "Loyiha ishlab chiqarish standartlariga muvofiq Docker va Docker Compose yordamida to'liq konteynerlashtirildi, healthcheck va non-root xavfsizlik talablariga moslashtirildi."
- **Key Metrics:** 1 ta buyruq bilan ishga tushish (`docker compose up`), 8501 port izolyatsiyasi, 100% qayta takrorlanuvchanlik.
