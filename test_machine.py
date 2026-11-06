#!/usr/bin/env python3
import json
import sys
from client import KargadanClient

def main():
    client = KargadanClient()
    machine_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not machine_id:
        machines = client.list_machines()
        if not machines:
            print("No machines found in account.")
            return
        machine_id = machines[0].get("id")

    print(f"Fetching machine '{machine_id}'...")
    machine = client.get_machine(machine_id)
    print("Machine Title:", machine.get("title"))
    print("Power State:", machine.get("state_title"), f"({machine.get('state')})")
    print("CPU / RAM / Disk:", f"{machine.get('cpu')} Core, {machine.get('memory')} GB, {machine.get('disk')} GB")
    print("Hourly Price:", machine.get("price"), "Rials")

if __name__ == "__main__":
    main()
