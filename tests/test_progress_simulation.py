#!/usr/bin/env python3
"""Test script to simulate a process with progress logging."""

import time
import sys

def simulate_process():
    """Simulate a long-running process with progress indicators."""
    total_items = 100
    
    print("Starting Data Processing Job...")
    print(f"Total items to process: {total_items}")
    print()
    
    for i in range(1, total_items + 1):
        # Simulate work
        time.sleep(0.5)  # 0.5 seconds per item = ~50 seconds total
        
        # Print progress indicators
        if i % 5 == 0:  # Every 5 items
            percentage = (i / total_items) * 100
            print(f"Progress: {percentage:.0f}% | Processed {i}/{total_items} items")
        
        # Simulate occasional errors for testing
        if i == 30:
            print("WARNING: Temporary connection issue, retrying...")
        
        if i == 75:
            print("INFO: Approaching completion, finalizing batch...")
    
    print()
    print("✓ Process completed successfully!")
    print(f"Total items processed: {total_items}")

if __name__ == "__main__":
    try:
        simulate_process()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(1)
