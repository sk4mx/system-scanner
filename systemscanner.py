import os
import platform
import subprocess
import threading
import hashlib
import shutil
import psutil
from datetime import datetime
from collections import defaultdict

# ─── COLORS ─────────────────────────────────────
R = "\033[91m"  # Red
G = "\033[92m"  # Green
Y = "\033[93m"  # Yellow
B = "\033[94m"  # Blue
C = "\033[96m"  # Cyan
W = "\033[97m"  # White
X = "\033[0m"   # Reset

# ─── BANNER ─────────────────────────────────────
def banner():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"""{C}
╔══════════════════════════════════════════╗
║        🖥️  SYS TOOL PRO  🖥️             ║
║     All-in-One System Utility Tool       ║
╚══════════════════════════════════════════╝{X}
    """)

# ─── MENU ────────────────────────────────────────
def menu():
    print(f"{Y}  [1]{W} 📊 System Info Dashboard")
    print(f"{Y}  [2]{W} ⚙️  Process Monitor")
    print(f"{Y}  [3]{W} 📁 Directory Size Analyzer")
    print(f"{Y}  [4]{W} 🔍 File Duplicate Finder")
    print(f"{Y}  [0]{W} 🚪 Exit")
    print()

# ════════════════════════════════════════════════
# 1. SYSTEM INFO DASHBOARD
# ════════════════════════════════════════════════
def system_info():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"\n{C}{'='*45}")
    print(f"   📊 SYSTEM INFO DASHBOARD")
    print(f"{'='*45}{X}\n")

    # OS Info
    print(f"{Y}🖥️  OS Info{X}")
    print(f"  OS       : {platform.system()} {platform.release()}")
    print(f"  Version  : {platform.version()}")
    print(f"  Machine  : {platform.machine()}")
    print(f"  Hostname : {platform.node()}")
    print(f"  Time     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count   = psutil.cpu_count()
    cpu_freq    = psutil.cpu_freq()
    print(f"{Y}⚡ CPU{X}")
    print(f"  Cores    : {cpu_count}")
    print(f"  Freq     : {cpu_freq.current:.0f} MHz")
    bar = "█" * int(cpu_percent // 5) + "░" * (20 - int(cpu_percent // 5))
    color = G if cpu_percent < 50 else Y if cpu_percent < 80 else R
    print(f"  Usage    : {color}[{bar}] {cpu_percent}%{X}\n")

    # RAM
    ram = psutil.virtual_memory()
    ram_used = ram.used / (1024**3)
    ram_total = ram.total / (1024**3)
    ram_pct = ram.percent
    print(f"{Y}🧠 RAM{X}")
    bar = "█" * int(ram_pct // 5) + "░" * (20 - int(ram_pct // 5))
    color = G if ram_pct < 50 else Y if ram_pct < 80 else R
    print(f"  Used     : {ram_used:.2f} GB / {ram_total:.2f} GB")
    print(f"  Usage    : {color}[{bar}] {ram_pct}%{X}\n")

    # Disk
    print(f"{Y}💾 Disk{X}")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            pct   = usage.percent
            bar   = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
            color = G if pct < 50 else Y if pct < 80 else R
            print(f"  {part.mountpoint:<10} {color}[{bar}] {pct}%{X}  "
                  f"({usage.used/(1024**3):.1f}GB / {usage.total/(1024**3):.1f}GB)")
        except:
            pass

    # Network
    print(f"\n{Y}🌐 Network{X}")
    net = psutil.net_io_counters()
    print(f"  Sent     : {net.bytes_sent / (1024**2):.2f} MB")
    print(f"  Received : {net.bytes_recv / (1024**2):.2f} MB")

    print(f"\n{G}✅ Done!{X}")
    input(f"\n{W}Press Enter to return to menu...{X}")

# ════════════════════════════════════════════════
# 2. PROCESS MONITOR
# ════════════════════════════════════════════════
def process_monitor():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"\n{C}{'='*55}")
    print(f"   ⚙️  PROCESS MONITOR")
    print(f"{'='*55}{X}\n")

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
        try:
            info = proc.info
            mem_mb = info['memory_info'].rss / (1024**2)
            processes.append((info['pid'], info['name'], info['cpu_percent'], mem_mb, info['status']))
        except:
            pass

    # Sort by memory usage
    processes.sort(key=lambda x: x[3], reverse=True)

    print(f"{Y}{'PID':<8} {'NAME':<25} {'CPU%':<8} {'MEM(MB)':<10} {'STATUS'}{X}")
    print("-" * 60)
    for pid, name, cpu, mem, status in processes[:20]:
        color = R if mem > 500 else Y if mem > 100 else G
        print(f"{color}{pid:<8} {name[:24]:<25} {cpu:<8.1f} {mem:<10.1f} {status}{X}")

    print(f"\n{W}Showing top 20 processes by memory usage.{X}")

    # Kill option
    print(f"\n{Y}🔫 Kill a process?{X}")
    choice = input("Enter PID to kill (or press Enter to skip): ").strip()
    if choice.isdigit():
        try:
            p = psutil.Process(int(choice))
            p.terminate()
            print(f"{G}✅ Process {choice} terminated.{X}")
        except Exception as e:
            print(f"{R}❌ Error: {e}{X}")

    input(f"\n{W}Press Enter to return to menu...{X}")

# ════════════════════════════════════════════════
# 3. DIRECTORY SIZE ANALYZER
# ════════════════════════════════════════════════
def dir_size(path):
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += dir_size(entry.path)
    except PermissionError:
        pass
    return total

def directory_analyzer():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"\n{C}{'='*45}")
    print(f"   📁 DIRECTORY SIZE ANALYZER")
    print(f"{'='*45}{X}\n")

    path = input(f"{W}Enter directory path (e.g. /home or C:\\Users): {X}").strip()

    if not os.path.isdir(path):
        print(f"{R}❌ Invalid path!{X}")
        input(f"\n{W}Press Enter to return to menu...{X}")
        return

    print(f"\n{Y}⏳ Scanning... please wait{X}\n")

    folders = []
    try:
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                size = dir_size(entry.path)
                folders.append((entry.name, size))
    except PermissionError:
        print(f"{R}❌ Permission denied!{X}")

    folders.sort(key=lambda x: x[1], reverse=True)

    total = sum(s for _, s in folders)

    print(f"{Y}{'FOLDER':<35} {'SIZE':>10} {'BAR'}{X}")
    print("-" * 65)
    for name, size in folders[:15]:
        mb   = size / (1024**2)
        pct  = (size / total * 100) if total > 0 else 0
        bar  = "█" * int(pct // 3)
        color = R if mb > 1000 else Y if mb > 100 else G
        print(f"{color}{name[:34]:<35} {mb:>8.1f}MB  {bar}{X}")

    print(f"\n{W}Total size: {total/(1024**3):.2f} GB across {len(folders)} folders{X}")
    print(f"{G}✅ Done!{X}")
    input(f"\n{W}Press Enter to return to menu...{X}")

# ════════════════════════════════════════════════
# 4. FILE DUPLICATE FINDER
# ════════════════════════════════════════════════
def hash_file(path):
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except:
        return None

def duplicate_finder():
    os.system("cls" if platform.system() == "Windows" else "clear")
    print(f"\n{C}{'='*45}")
    print(f"   🔍 FILE DUPLICATE FINDER")
    print(f"{'='*45}{X}\n")

    path = input(f"{W}Enter directory to scan: {X}").strip()

    if not os.path.isdir(path):
        print(f"{R}❌ Invalid path!{X}")
        input(f"\n{W}Press Enter to return to menu...{X}")
        return

    print(f"\n{Y}⏳ Hashing files... please wait{X}\n")

    hashes = defaultdict(list)
    total_files = 0

    for root, dirs, files in os.walk(path):
        for fname in files:
            fpath = os.path.join(root, fname)
            fhash = hash_file(fpath)
            if fhash:
                hashes[fhash].append(fpath)
                total_files += 1

    duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}

    print(f"{Y}📊 Scan Summary{X}")
    print(f"  Total files scanned : {total_files}")
    print(f"  Duplicate groups    : {len(duplicates)}\n")

    if duplicates:
        wasted = 0
        for i, (fhash, paths) in enumerate(duplicates.items(), 1):
            size = os.path.getsize(paths[0]) / (1024**2)
            wasted += size * (len(paths) - 1)
            print(f"{R}🔁 Duplicate Group {i} — {size:.2f} MB each{X}")
            for p in paths:
                print(f"   {W}→ {p}{X}")
            print()
        print(f"{Y}💾 Total wasted space: {wasted:.2f} MB{X}")
    else:
        print(f"{G}✅ No duplicates found!{X}")

    input(f"\n{W}Press Enter to return to menu...{X}")

# ─── MAIN LOOP ───────────────────────────────────
def main():
    while True:
        banner()
        menu()
        choice = input(f"{C}Select option: {X}").strip()

        if choice == "1":
            system_info()
        elif choice == "2":
            process_monitor()
        elif choice == "3":
            directory_analyzer()
        elif choice == "4":
            duplicate_finder()
        elif choice == "0":
            print(f"\n{G}👋 Goodbye!{X}\n")
            break
        else:
            print(f"{R}❌ Invalid option!{X}")

if __name__ == "__main__":
    main()