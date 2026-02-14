
import time
import random
import sys
from datetime import datetime
from faker import Faker

fake = Faker()

def main():
    log_file = "process.log"
    total_steps = 300  
    process_id = random.randint(10000, 99999)
    worker_node = fake.hostname(levels=1)
    
    with open(log_file, "w") as f:
        f.write(f"🚀 [INIT] Starting high-fidelity simulation on node: {worker_node}\n")
        f.write(f"Process ID: {process_id}\n")
        f.write(f"Task: Full ETL pipeline for {fake.company()}\n")
        f.write("-" * 50 + "\n")
        f.flush()
        
        print(f"Simulation started. Writing to {log_file}...")

        for i in range(1, total_steps + 1):
            # Progress Tracking (Batch processing simulation)
            progress = (i / total_steps) * 100
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Periodic Heartbeat (TESTS CACHE)
            # Every 10 seconds, print an identical status line
            if i % 10 == 0:
                f.write(f"[{timestamp}] INFO: Heartbeat signal active. System status: HEALTHY. Node: {worker_node}\n")
                f.flush()

            # 2. Progress Updates (TESTS PROGRESS TRACKING)
            if i % 5 == 0:
                batch_id = fake.uuid4()[:8]
                f.write(f"[{timestamp}] INFO: Processed batch {batch_id} - Progress: {progress:.1f}%\n")
                f.flush()

            # 3. Pattern Matching (TESTS SEVERITY MATCHER)
            if i == 50:
                f.write(f"[{timestamp}] INFO: Database connection stabilized. Pool size: {random.randint(5, 20)}\n")
                f.flush()
            
            # 4. LLM Analysis (TESTS UNIQUE ERRORS)
            # Randomly generate varied errors with Faker
            if i % 15 == 0:
                # REPEATED ERROR to test CACHE
                f.write(f"[{timestamp}] ERROR: Database connection pool exhausted (max_size=20)\n")
                f.flush()
            elif i % 67 == 0:
                error_type = random.choice(["RuntimeError", "IOError", "DatabaseError", "APIConnectionError"])
                err_msg = fake.sentence(nb_words=10)
                ip_addr = fake.ipv4()
                f.write(f"[{timestamp}] ERROR: {error_type}: {err_msg} (source: {ip_addr})\n")
                f.flush()

            # 5. Stall Detection (TESTS STALL ALERT)
            # Intentionally hang at 40%
            if i == 120:
                f.write(f"[{timestamp}] WARNING: Network latency detected. Pausing data ingestion...\n")
                f.flush()
                time.sleep(35) # Longer than 1 loop to trigger stall logic if threshold is low
                f.write(f"[{timestamp}] INFO: Connection resumed. Continuing...\n")
                f.flush()

            # 6. Critical Failure (TESTS LLM ANALYSIS)
            if i == 250:
                file_path = f"/var/data/{fake.file_name(category='text')}"
                f.write(f"[{timestamp}] CRITICAL: Invalid checksum for {file_path}. Data corruption suspected!\n")
                f.flush()

            time.sleep(1)

        f.write("-" * 50 + "\n")
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Simulation complete. Result: SUCCESS\n")
        f.flush()

if __name__ == "__main__":
    main()
