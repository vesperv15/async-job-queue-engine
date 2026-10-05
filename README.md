# async-job-queue-engine
# Async Job Queue & Exponential Backoff Retry Engine
Python (FastAPI) ve Redis kullanılarak geliştirilmiş, yüksek ölçeklenebilir ve hataya dayanıklı (*fault-tolerant*) asenkron iş kuyruğu ve arka plan işlem motoru.

---

## Mimari ve Öne Çıkan Özellikler

- **Non-blocking API (`202 Accepted`):** Uzun süren iş yükleri senkron HTTP döngüsünden çıkarılarak arka plana devredilir.
- **Redis Queue & State Store:** İş transferi için Redis `LPUSH` / `BRPOP` komutları, iş durum takibi için Redis `Hash` yapıları kullanılır.
- **Exponential Backoff Retry Engine:** Başarısız olan işler, sistem yükünü hafifletmek adına katlanarak artan bekleme süreleriyle ($2^{\text{deneme\_sayısı}}$ saniye) yeniden denenir.
- **Decoupled Architecture:** API katmanı (`main.py`) ve Tüketici İş Parçacıkları (`worker.py`) tamamen bağımsız süreçler (*processes*) olarak çalışır.

---
## Kullanılan araçlar

- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **In-Memory Store & Queue:** Redis (RESP2/RESP3)
- **Data Validation:** Pydantic

---
## Kurulum ve Çalıştırma

1. **Depoyu Klonlayın ve Bağımlılıkları Yükleyin:**
   ```bash
   git clone [https://github.com/KULLANICI_ADINIZ/async-job-queue-engine.git](https://github.com/KULLANICI_ADINIZ/async-job-queue-engine.git)
2. **Redis Servisini Başlatın:** redis-server
3. **Worker Sürecini Çalıştırın:** python worker.py
4. **API Sunucusunu Başlatın:** uvicorn main:app --reload --port 8000
   cd async-job-queue-engine
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
