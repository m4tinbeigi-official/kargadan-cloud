#!/usr/bin/env python3
import json
from client import KargadanClient

def main():
    print("Testing KargadanClient with live session...")
    client = KargadanClient()
    
    print("\n1. Testing get_me()...")
    me = client.get_me()
    print("GetMe:", json.dumps(me, ensure_ascii=False, indent=2))
    
    print("\n2. Testing list_machines()...")
    machines = client.list_machines()
    print(f"Total machines: {len(machines)}")
    for m in machines:
        print(f"  - [{m.get('id')}] {m.get('title')} | Status: {m.get('status_human')} | State: {m.get('state')} | IP: {m.get('ip', [{}])[0].get('ip')}")

if __name__ == "__main__":
    main()
