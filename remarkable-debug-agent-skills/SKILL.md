---
name: remarkable-debug-agent-skills
description: Use when troubleshooting reMarkable tablets (SSH setup, Wi-Fi issues, cloud sync failures, or providing internet via USB NAT tethering).
---

# Remarkable Debug Agent Skills

## Overview
Comprehensive runbook for reMarkable 2 (OS 3.27+) to establish persistent SSH access, fix broken Wi-Fi/Sync via Qt workarounds, and provide internet through USB tethering.

## When to Use
- **Trigger when**: Tablet cannot connect to Wi-Fi, sync fails, TLS errors occur (clock drift), or when persistent root SSH access is required.

## 1. SSH Setup & Persistence
Firmware updates wipe `/etc` but preserve `/home`. 
- **Connect**: Find password in **Settings > Help > Copyrights & licenses**. Connect via `ssh root@10.11.99.1`.
- **Persistence**: Copy your Mac's SSH key to `/home/root/.ssh/authorized_keys` to survive updates.
- **Custom Binaries**: Store static binaries (like `curl`) in `/home/root/bin` and add to `.bashrc` PATH.

## 2. Wi-Fi & Sync Recovery
If Wi-Fi fails or cloud sync hangs (often due to Qt network blocking or NTP drift):
- **Mitigation 1 (The Qt Block)**: `xochitl` blocks background SSL if the UI Wi-Fi toggle is OFF. **Always toggle Wi-Fi ON** in the UI to unblock the network stack, even if no network connects.
- **Mitigation 2 (Force Sync)**: Refresh stale tokens by forcing a D-Bus sync over SSH:
  ```bash
  TOKEN=$(grep -E '^(UserToken|devicetoken)=' /home/root/.config/remarkable/xochitl.conf | head -n1 | cut -d'=' -f2-)
  busctl call no.remarkable.sync /Synchronizer no.remarkable.sync.Synchronizer execute "s(asasasb)" "$TOKEN" 0 0 0 true
  ```
- **Mitigation 3 (Curl Override)**: Add `UseCurlHttpBackend=true` under `[General]` in `/home/root/.config/remarkable/xochitl.conf` and restart UI (`systemctl restart xochitl`).

## 3. USB Tethering via macOS (Fallback Internet)
If native Wi-Fi is totally dead, provide internet via Mac USB (`en10`) to Mac Wi-Fi (`en0`) to fix NTP time or force a sync.
- **On macOS (Host)**:
  ```bash
  sudo sysctl -w net.inet.ip.forwarding=1
  echo "nat on en0 from en10:network to any -> (en0)" > /tmp/pf_rm.conf
  sudo pfctl -f /etc/pf.conf -f /tmp/pf_rm.conf -E
  ```
- **On reMarkable (Client)**:
  ```bash
  ip route add default via 10.11.99.4
  echo "nameserver 8.8.8.8" > /etc/resolv.conf
  ```
- **Cleanup (Host)**: `sudo pfctl -f /etc/pf.conf && sudo sysctl -w net.inet.ip.forwarding=0`

## Common Pitfalls & Edge Cases
| Issue | Mitigation |
| :--- | :--- |
| **Connection Refused (SSH)** | Check power. USB Web Interface (port 80) and SSH (port 22) do NOT conflict. |
| **TLS Validation Fails** | Tablet NTP is out of sync. Tether via USB, or set manually: `date -s "YYYY-MM-DD HH:MM:SS"`. |
| **Wrong macOS Interface** | If Mac Wi-Fi isn't `en0` or USB isn't `en10`, adjust `nat on enX` and `enY:network` accordingly. |

## Verification Checklist
- [ ] `ssh root@10.11.99.1` works without password.
- [ ] D-Bus sync command returns successfully.
- [ ] `curl -I https://remarkable.com` on tablet returns 200 OK.
