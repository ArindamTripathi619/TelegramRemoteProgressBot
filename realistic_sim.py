
import time
import random
import sys
from datetime import datetime
from faker import Faker

fake = Faker()

def main():
    total_steps = 300  # 5 minutes at 1 sec/step
    process_id = random.randint(10000, 99999)
    worker_node = fake.hostname(levels=1)
    
    print(f"🚀 [INIT] Starting high-fidelity simulation on node: {worker_node}")
    print(f"Process ID: {process_id}")
    print(f"Task: Full ETL pipeline for {fake.company()}")
    print("-" * 50)

    for i in range(1, total_steps + 1):
        # Progress Tracking (Batch processing simulation)
        progress = (i / total_steps) * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Periodic Heartbeat (TESTS CACHE)
        # Every 10 seconds, print an identical status line
        if i % 10 == 0:
            print(f"[{timestamp}] INFO: Heartbeat signal active. System status: HEALTHY. Node: {worker_node}")
            sys.stdout.flush()

        # 2. Progress Updates (TESTS PROGRESS TRACKING)
        if i % 5 == 0:
            batch_id = fake.uuid4()[:8]
            print(f"[{timestamp}] INFO: Processed batch {batch_id} - Progress: {progress:.1f}%")
            sys.stdout.flush()

        # 3. Pattern Matching (TESTS SEVERITY MATCHER)
        if i == 50:
            print(f"[{timestamp}] INFO: Database connection stabilized. Pool size: {random.randint(5, 20)}")
            sys.stdout.flush()
        
        # 4. LLM Analysis (TESTS UNIQUE ERRORS)
        # Randomly generate varied errors with Faker
        if i % 15 == 0:
            # REPEATED ERROR to test CACHE
            print(f"[{timestamp}] ERROR: Database connection pool exhausted (max_size=20)")
            sys.stdout.flush()
        elif i % 67 == 0:
            error_type = random.choice(["RuntimeError", "IOError", "DatabaseError", "APIConnectionError"])
            err_msg = fake.sentence(nb_words=10)
            ip_addr = fake.ipv4()
            print(f"[{timestamp}] ERROR: {error_type}: {err_msg} (source: {ip_addr})")
            sys.stdout.flush()

        # 5. Stall Detection (TESTS STALL ALERT)
        # Intentionally hang at 40%
        if i == 120:
            print(f"[{timestamp}] WARNING: Network latency detected. Pausing data ingestion...")
            sys.stdout.flush()
            time.sleep(35) # Longer than 1 loop to trigger stall logic if threshold is low
            print(f"[{timestamp}] INFO: Connection resumed. Continuing...")
            sys.stdout.flush()

        # 6. Critical Failure (TESTS LLM ANALYSIS)
        if i == 250:
            file_path = f"/var/data/{fake.file_name(category='text')}"
            print(f"[{timestamp}] CRITICAL: Invalid checksum for {file_path}. Data corruption suspected!")
            sys.stdout.flush()

        time.sleep(1)

    print("-" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ Simulation complete. Result: SUCCESS")

if __name__ == "__main__":
    main()
