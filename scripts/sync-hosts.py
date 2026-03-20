#!/usr/bin/env python3
"""
Sync ansible_host IPs from act/inventory.yml into autovpn/inventory.yml.
Run this after rebuilding the ACT lab and updating act/inventory.yml.
"""

import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ACT_INVENTORY = REPO_ROOT / "act/inventory.yml"
WAN_INVENTORY = REPO_ROOT / "autovpn/inventory.yml"


def get_hosts(groups):
    """Flatten a nested inventory into {hostname: ip}."""
    hosts = {}
    for group in groups.values():
        if "hosts" in group and group["hosts"]:
            for host, vars in group["hosts"].items():
                if vars and "ansible_host" in vars:
                    hosts[host] = vars["ansible_host"]
        if "children" in group:
            hosts.update(get_hosts(group["children"]))
    return hosts


def update_hosts(groups, act_hosts):
    """Walk inventory groups and update ansible_host where hostnames match."""
    updated = []
    for group in groups.values():
        if "hosts" in group and group["hosts"]:
            for host, vars in group["hosts"].items():
                if host in act_hosts and vars:
                    old_ip = vars.get("ansible_host")
                    new_ip = act_hosts[host]
                    if old_ip != new_ip:
                        vars["ansible_host"] = new_ip
                        updated.append(f"  {host}: {old_ip} -> {new_ip}")
        if "children" in group:
            updated.extend(update_hosts(group["children"], act_hosts))
    return updated


def main():
    with open(ACT_INVENTORY) as f:
        act = yaml.safe_load(f)

    with open(WAN_INVENTORY) as f:
        wan = yaml.safe_load(f)

    act_hosts = get_hosts(act["all"]["children"])
    changes = update_hosts(wan["all"]["children"], act_hosts)

    if changes:
        with open(WAN_INVENTORY, "w") as f:
            yaml.dump(wan, f, default_flow_style=False, sort_keys=False)
        print(f"Updated {len(changes)} host(s) in {WAN_INVENTORY}:")
        for change in changes:
            print(change)
    else:
        print("No IP changes detected.")


if __name__ == "__main__":
    main()
