#!/usr/bin/env python3
"""
Kargadan Cloud CLI Tool
Manage Kargadan VPS, check balances, perform power actions, and inspect machines.
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from client import KargadanClient

def main():
    parser = argparse.ArgumentParser(description="Kargadan Cloud CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: me
    subparsers.add_parser("me", help="Display user profile and balance")

    # Command: list
    subparsers.add_parser("list", help="List all cloud machines")

    # Command: info
    parser_info = subparsers.add_parser("info", help="Get details of a specific machine")
    parser_info.add_argument("machine_id", help="Machine ID (e.g. vm-abc12)")

    # Command: power
    parser_power = subparsers.add_parser("power", help="Perform power action on machine")
    parser_power.add_argument("machine_id", help="Machine ID")
    parser_power.add_argument("--action", required=True, choices=["resume", "poweroff", "poweroff_hard", "reboot", "reboot_hard"], help="Action to execute")

    # Command: reset-pass
    parser_reset = subparsers.add_parser("reset-password", help="Reset root password")
    parser_reset.add_argument("machine_id", help="Machine ID")

    # Command: invoices
    subparsers.add_parser("invoices", help="List invoices")

    # Command: tickets
    subparsers.add_parser("tickets", help="List support tickets")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    client = KargadanClient()

    if args.command == "me":
        res = client.get_me()
        user = res.get("GetMe", {})
        print(f"User: {user.get('fullname')} ({user.get('cellphone')})")
        print(f"National Code: {user.get('national_code')}")
        print(f"Wallet Balance: {user.get('wallet', {}).get('credit', 0):,} Tomans")
        print(f"Club Level: {user.get('level', {}).get('title')}")
        print(f"Referral Link: {user.get('referral_link')}")

    elif args.command == "list":
        machines = client.list_machines()
        print(f"Found {len(machines)} machines:\n")
        print(f"{'ID':<8} | {'Title':<15} | {'Status':<8} | {'State':<10} | {'IP':<16} | {'CPU/RAM/Disk'}")
        print("-" * 75)
        for m in machines:
            ips = m.get("ip", [])
            ip_str = ips[0].get("ip") if ips else "N/A"
            res_str = f"{m.get('cpu')}C / {m.get('memory')}GB / {m.get('disk')}GB"
            print(f"{m.get('id'):<8} | {m.get('title'):<15} | {m.get('status_human', ''):<8} | {m.get('state', ''):<10} | {ip_str:<16} | {res_str}")

    elif args.command == "info":
        m = client.get_machine(args.machine_id)
        print(json.dumps(m, ensure_ascii=False, indent=2))

    elif args.command == "power":
        action = args.action.upper()
        print(f"Executing {action} on machine {args.machine_id}...")
        res = client.machine_action(args.machine_id, action)
        print("Result:", json.dumps(res, ensure_ascii=False))

    elif args.command == "reset-password":
        print(f"Resetting password for {args.machine_id}...")
        res = client.reset_machine_password(args.machine_id)
        print("Result:", json.dumps(res, ensure_ascii=False))

    elif args.command == "invoices":
        invs = client.list_invoices()
        print(json.dumps(invs, ensure_ascii=False, indent=2))

    elif args.command == "tickets":
        tix = client.list_tickets()
        print(json.dumps(tix, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
