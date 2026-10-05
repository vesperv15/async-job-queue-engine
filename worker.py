import json
import time
import redis

#redis baglantısı
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True, protocol=2)

QUEUE_NAME = "task_queue"
MAX_RETRIES = 3

def process_job(payload: dict):
    """ iş mantıgının calıstırıldı alan"""
    print(f"(worker) işleniyor : {payload ['job_id']}")
    
    #simule edilmiş hata kontrolü
    
    if payload.get ("should_fail") and payload["attempts"] < 3:
        raise ValueError("simule edilmiş sistem hatası")
    
    time.sleep(2) #ağır işlem
    print(f"(worker) basarıyla tamamlandı {payload['job_id']}")

def start_worker():
    print("worker : dinleme baslatıldı iş bekleniyor")
    while True:
        #brpop:kuyruk bossa blokla ve bekle cpu yormamak için
        _, raw_data = r.brpop(QUEUE_NAME)
        job = json.loads(raw_data)
        
        job_id = job["job_id"]
        job["attempts"] += 1
        #durumu güncelle ın progress
        
        r.hset(f"job:{job_id}", mapping={"status": "IN_PROGRESS", "attempts": job["attempts"]})
        
        try:
            process_job(job)
            #basarılı durumda
            r.hset(f"job:{job_id}", mapping={"status": "COMPLETED"})
        except Exception as e:
            print(f"(error) iş basarısız (deneme {job["attempts"]} / {MAX_RETRIES}): {str(e)} ")
            
            if job["attempts"] < MAX_RETRIES:
                #exponential backoff hesaplaması : 2^attemps saniye bekle
                backoff_delay = 2 ** job["attempts"]
                print(f"(retry) {backoff_delay} sn sonra tekrar denenecek ")
                
                r.hset(f"job:{job_id}", mapping={
                    "status": "RETRYING",
                    "error": str(e)
                })
                
                time.sleep(backoff_delay)
                #işi tekrar kuyruga at
                r.lpush(QUEUE_NAME, json.dumps(job))
            else:
                #dead letter queue v failed durumu
                print(f"(failed) maksimum deneme sayısına ulasıldı : {job_id}")
                r.hset(f"job:{job_id}", mapping={
                    "status": "FAILED",
                    "error": "Maksimum retry limitine ulaşıldı."
                })
if __name__ == "__main__":
    start_worker()