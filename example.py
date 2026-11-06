#!/usr/bin/env python3
"""
Example usage of Kargadan Cloud Python SDK.
"""

import json
from client import KargadanClient

def main():
    # 1. Initialize client (auto-connects to open Chrome tab on macOS or uses HTTP)
    client = KargadanClient()

    # 2. Get user profile and wallet balance
    print("=== 1. Profile & Balance ===")
    me_resp = client.get_me()
    user = me_resp.get("GetMe", {})
    print(f"User: {user.get('fullname')}")
    print(f"Phone: {user.get('cellphone')}")
    print(f"Balance: {user.get('wallet', {}).get('credit', 0):,} Tomans")
    print(f"Club Level: {user.get('level', {}).get('title')}")

    # 3. List all machines
    print("\n=== 2. Virtual Machines ===")
    machines = client.list_machines()
    print(f"Total machines: {len(machines)}")
    for m in machines:
        ip = m.get("ip", [{}])[0].get("ip", "N/A")
        print(f"  - ID: {m.get('id')} | Name: {m.get('title')} | Status: {m.get('status_human')} | IP: {ip} | Power: {m.get('state')}")

    # 4. Get detailed specs of the first machine (if available)
    if machines:
        first_id = machines[0].get("id")
        print(f"\n=== 3. Details for Machine [{first_id}] ===")
        details = client.get_machine(first_id)
        print(f"Title: {details.get('title')}")
        print(f"OpenNebula VM ID: {details.get('one_vm_id')}")
        print(f"State: {details.get('state_title')} ({details.get('state')})")
        print(f"Specs: {details.get('cpu')} CPU Cores, {details.get('memory')} GB RAM, {details.get('disk')} GB Disk")
        print(f"Price: {details.get('price')} Rials/Hour ({details.get('price_month'):,} Rials/Month)")

if __name__ == "__main__":
    main()
