"""Chaos Monkey for Logs - Generates high-entropy, corrupted, and drifting log streams."""

import time
import random
import json
import logging
from datetime import datetime
from faker import Faker

fake = Faker()

# Setup logging to file for the bot to monitor
LOG_FILE = "chaos.log"
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',
    format='%(message)s',
    level=logging.INFO
)

def log(msg):
    print(f"🐒 [CHAOS] {msg}")
    logging.info(msg)

class ChaosMonkey:
    def __init__(self):
        self.formats = ["syslog", "json", "csv", "raw"]
        self.current_format = "syslog"
        self.iteration = 0
        self.delimiter = " "
        
    def generate_line(self):
        self.iteration += 1
        
        # 1. Switch format every 50 lines (Drift)
        if self.iteration % 50 == 0:
            self.current_format = random.choice(self.formats)
            self.delimiter = random.choice([" ", " | ", ",", "\t"])
            log(f"--- FORMAT SWAP: {self.current_format} (Delimiter: '{self.delimiter}') ---")

        # 2. Add corruption probability
        corrupt = random.random() < 0.1
        
        # 3. Generate base content
        if self.current_format == "json":
            data = {
                "timestamp": datetime.now().isoformat(),
                "level": random.choice(["INFO", "DEBUG", "TRACE"]),
                "msg": fake.sentence(),
                "trace_id": fake.uuid4()
            }
            line = json.dumps(data)
        elif self.current_format == "syslog":
            ts = datetime.now().strftime("%b %d %H:%M:%S")
            host = fake.hostname()
            level = random.choice(["INFO", "WARN", "DEBUG"])
            line = f"{ts} {host} proc[{random.randint(100, 999)}]: {level}: {fake.sentence()}"
        elif self.current_format == "csv":
            ts = str(time.time())
            line = self.delimiter.join([ts, "PROC", "OK", fake.word(), fake.sentence()])
        else:
            line = f"{fake.hexify(text='^^^^^^^^')} {fake.sentence()} {fake.hexify(text='########')}"

        # 4. Inject Chaos (Corruption)
        if corrupt:
            chaos_type = random.choice(["truncate", "garbage", "strip_ts"])
            if chaos_type == "truncate":
                line = line[:len(line)//2]
            elif chaos_type == "garbage":
                line = "".join(random.choice("!@#$%^&*()_+") for _ in range(10)) + line
            elif chaos_type == "strip_ts":
                line = " ".join(line.split()[2:]) # Remove first two words
                
        return line

    def inject_critical(self):
        """Hidden critical error in the chaos."""
        errors = [
            "CRITICAL: Segmentation fault at 0x0000FF",
            "FATAL: Database connectivity lost (Auth Failure)",
            "ERROR: OutOfMemoryError: Java heap space",
            "PANIC: Kernel thread panic in 'worker_0'"
        ]
        return random.choice(errors)

def run_chaos(duration_secs=300):
    monkey = ChaosMonkey()
    start_time = time.time()
    
    log("Starting Chaos Gauntlet...")
    
    while time.time() - start_time < duration_secs:
        # 90% normal chaos, 10% hidden critical
        if random.random() < 0.05:
            line = monkey.inject_critical()
            log(f"🔥 INJECTING CRITICAL: {line}")
        else:
            line = monkey.generate_line()
            
        logging.info(line)
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    run_chaos()
