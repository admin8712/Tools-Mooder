#!/usr/bin/env python3
import os, sys, subprocess, shutil, re, time, threading, signal, textwrap, concurrent.futures, multiprocessing
from shutil import get_terminal_size

# --- INSTALL MODULE ---
try:
    os.system("sudo apt install binutils -y ")
    #os.system("apt install android-tools ")
    #os.system("sudo apt install zipalign -y ")
    #os.system("sudo apt install wget ")
    #os.system("wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool ")
    #os.system("wget -O apktool.jar https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar ")
    #os.system("sudo apt install openjdk-17-jdk -y")
    #os.system("pip install rich")
    #os.system("sudo apt-get install -y nodejs")
    #os.system("npm install -g apk-mitm")
    #os.system("sudo install aapt2 -y")
    #os.system("apt install aapt -y")
    from deep_translator import GoogleTranslator
except ImportError:
    print("\033[33m[!] Installing modules...\033[0m")
    os.system('pip3 install deep-translator --quiet')
    try:
        os.system("clear")
        from deep_translator import GoogleTranslator
    except:
        pass

# Cek & Install library rich untuk menu 2 dan 3 yang baru
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.prompt import IntPrompt
    from rich import box
    from rich.align import Align
except ImportError:
    print("\033[33m[!] Installing 'rich' module for new tools...\033[0m")
    os.system('pip3 install rich --quiet')
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
        from rich.prompt import IntPrompt
        from rich import box
        from rich.align import Align
    except ImportError:
        print("\033[31m[!] Gagal install rich. Menu 2 & 3 mungkin error.\033[0m")
        
# --- CHECK REQUIREMENTS (PAKAI APKEDITOR & UBER SIGNER) ---
def check_requirements():
    print(f"{C.CYAN}[*] Checking Environment (Nexus Engine)...\033[0m")
    
    if not shutil.which("java"):
        print(f"{C.ERROR}[!] ERROR: Java not found!{C.RESET}")
        print("Please install Java in Termux:")
        os.system("clear")
        print(" \napt install openjdk-17")
        return False
    
    if not os.path.exists("APKEditor-1.4.7.jar"):
        print(f"{C.ERROR}[!] ERROR: APKEditor-1.4.7.jar not found!{C.RESET}")
        print("Download: https://github.com/ReAndroid/APKEditor/releases/download/V1.4.7/APKEditor-1.4.7.jar -O APKEditor-1.4.7.jar")
        print("menginstall otomatis")
        time.sleep(3)
        os.system("wget https://github.com/ReAndroid/APKEditor/releases/download/V1.4.7/APKEditor-1.4.7.jar -O APKEditor-1.4.7.jar")
        
        os.system("wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O uber-apk-signer.jar")
        print("tunggu...")
        time.sleep(3)
        
        return False

    if not os.path.exists("uber-apk-signer.jar"):
        print(f"{C.ERROR}[!] ERROR: uber-apk-signer.jar not found!{C.RESET}")
        print("Download: wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O uber-apk-signer.jar")
        os.system("wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O uber-apk-signer.jar")
        return False

    print(f"{C.SUCCESS}[+] Environment OK. Engine: APKEditor & UberSigner{C.RESET}")
    return True

# --- COLOR PALETTE ---
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    HEAD    = "\033[38;5;39m"
    ACCENT  = "\033[38;5;226m"
    SUCCESS = "\033[38;5;82m"
    ERROR   = "\033[38;5;196m"
    WARN    = "\033[38;5;208m"
    TEXT    = "\033[38;5;250m"
    GRAY    = "\033[38;5;242m"
    MENU    = "\033[38;5;45m"
    
# --- TERMINAL UTILITIES ---
def get_width():
    return get_terminal_size((40, 20)).columns

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_str_len(text):
    ansi_escape = re.compile(r'\033\[[0-9;]*m')
    return len(ansi_escape.sub('', text))

def truncate(text, max_len):
    clean_len = get_str_len(text)
    if clean_len <= max_len:
        return text
    return text[:max_len-3] + C.RESET + "..."

# --- GRAPHICS ENGINE ---
def draw_box(title, content_lines, color=C.HEAD, double_border=True):
    term_w = get_width()
    min_width = 35
    if term_w < min_width: term_w = min_width

    max_content_w = 0
    clean_title = re.sub(r'\033\[[0-9;]*m', '', title) if title else ""
    max_content_w = len(clean_title) if title else 0

    processed_lines = []
    for line in content_lines:
        clean_line = re.sub(r'\033\[[0-9;]*m', '', line)
        if len(clean_line) > max_content_w:
            max_content_w = len(clean_line)
        processed_lines.append(line)

    box_w = max_content_w + 4
    if box_w > term_w - 2: box_w = term_w - 2

    if double_border:
        tl, tr, bl, br, h, v = "╔", "╗", "╚", "╝", "═", "║"
        hl, lr, rl = "╠", "╣", "╣"
    else:
        tl, tr, bl, br, h, v = "┌", "┐", "└", "┘", "─", "│"
        hl, lr, rl = "├", "┤", "┤"

    print(f"{C.TEXT}{tl}{h * box_w}{tr}{C.RESET}")

    if title:
        title_len = len(clean_title)
        left_pad = (box_w - title_len) // 2
        right_pad = box_w - title_len - left_pad
        print(f"{C.TEXT}{v}{C.RESET}{' ' * left_pad}{color}{C.BOLD}{title}{C.RESET}{' ' * right_pad}{C.TEXT}{v}{C.RESET}")
        print(f"{C.TEXT}{hl}{h * box_w}{rl}{C.RESET}")

    for line in processed_lines:
        clean_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
        padding_right = box_w - (clean_len + 1)
        if padding_right < 0: padding_right = 0
        display_line = line
        if clean_len > box_w - 2:
             display_line = truncate(line, box_w - 5)
             clean_len = len(re.sub(r'\033\[[0-9;]*m', '', display_line))
             padding_right = box_w - (clean_len + 1)
        print(f"{C.TEXT}{v}{C.RESET} {display_line}{' ' * padding_right}{C.TEXT}{v}{C.RESET}")

    print(f"{C.TEXT}{bl}{h * box_w}{br}{C.RESET}")

def center_text(text):
    w = get_width()
    clean_len = get_str_len(text)
    pad = (w - clean_len) // 2
    if pad < 0: pad = 0
    return " " * pad + text
    
# --- ANIMATED SPINNER ---
class Spinner:
    def __init__(self, text):
        self.text = text
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin)
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _spin(self):
        while not self._stop_event.is_set():
            for char in self.spinner_chars:
                if self._stop_event.is_set(): break
                sys.stdout.write(f"\r{C.HEAD}{char} {C.TEXT}{self.text}...{C.RESET}")
                sys.stdout.flush()
                time.sleep(0.1)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()
        sys.stdout.write(f"\r{C.SUCCESS}✔ {C.TEXT}{self.text} Done.{C.RESET}\n")
        sys.stdout.flush()

# --- LOGGING FUNCTIONS ---
def print_success(text): print(f"{C.SUCCESS}[+] {C.TEXT}{text}{C.RESET}")
def print_error(text): print(f"{C.ERROR}[!] {C.TEXT}{text}{C.RESET}")
def print_info(text): print(f"{C.DIM}[*] {C.TEXT}{text}{C.RESET}")

def run_command_anim(cmd, label):
    spinner = Spinner(label)
    spinner.start()
    ret = os.system(f'{cmd} > /dev/null 2>&1')
    spinner.stop()
    return ret
    
# =============================================================================
# --- TOOL ANALYSIS (10-17) - LOGIC PRESERVED, STYLE ADAPTED ---
# =============================================================================

def print_header(text):
    width = get_width()
    print(f"{C.TEXT}{'─' * width}{C.RESET}")
    print(center_text(f"{C.HEAD}{text}{C.RESET}"))
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

def ai_desc(msg):
    width = get_width()
    wrapper = textwrap.TextWrapper(width=width-6)
    print(f"\n{C.WARN}[ ANALISIS AI ]:{C.RESET}")
    for line in wrapper.wrap(msg):
        print(f"    {C.TEXT}{line}{C.RESET}")

def print_kv(key, value):
    print(f"  {C.SUCCESS}├─ {C.TEXT}{key.ljust(15)} : {C.WARN}{value}{C.RESET}")

def get_reg(line):
    match = re.search(r'[vp](\d+)', line)
    if match:
        return match.group(0)
    return "v0"
    
# 10. API SNIPER
def run_p10(apk):
    width = get_width()
    print_header("HADI-API-SNIPER v2.0")
    ai_desc("Mencari API Key di libapp.so (Flutter) & classes.dex (Java/Kotlin).")
    keys = "qonv|api_key|project_id|client_key|authorization|sdk_key|access_token"
    
    print(f"{C.CYAN}[*] TARGET 1: NATIVE (libapp.so){C.RESET}")
    find_lib = f"unzip -l '{apk}' | grep 'libapp.so' | awk '{{print $4}}' | head -n 1"
    lib_path = subprocess.run(find_lib, shell=True, capture_output=True, text=True).stdout.strip()
    
    if not lib_path:
        print(f"  {C.ERROR}[!] libapp.so tidak ditemukan.{C.RESET}")
    else:
        print(f"  {C.SUCCESS}[+] Scanning: {C.TEXT}{lib_path}{C.RESET}")
        cmd = f"unzip -p '{apk}' '{lib_path}' | strings | grep -iE '{keys}' | sort -u | head -n 15"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        if res:
            print(f"  {C.SUCCESS}┌── TEMUAN NATIVE ───────────────────────{C.RESET}")
            for line in res.strip().split('\n'):
                print(f"  {C.SUCCESS}│ {C.TEXT}{line.strip()[:width-15]}{C.RESET}")
            print(f"  {C.SUCCESS}└──────────────────────────────────────────{C.RESET}")

    print(f"\n{C.CYAN}[*] TARGET 2: JAVA/DEX (classes.dex){C.RESET}")
    find_dex = f"unzip -l '{apk}' | grep '.dex' | awk '{{print $4}}'"
    dex_files = subprocess.run(find_dex, shell=True, capture_output=True, text=True).stdout.strip().split('\n')
    
    found_dex = False
    for dex in dex_files:
        if not dex: continue
        cmd_dex = f"unzip -p '{apk}' '{dex}' | strings | grep -iE '{keys}' | sort -u | head -n 10"
        res_dex = subprocess.run(cmd_dex, shell=True, capture_output=True, text=True).stdout
        if res_dex.strip():
            found_dex = True
            print(f"  {C.CYAN}┌── TEMUAN DI {dex.upper()} ──────────{C.RESET}")
            for line in res_dex.strip().split('\n'):
                print(f"  {C.CYAN}│ {C.WARN}{line.strip()[:width-15]}{C.RESET}")
            print(f"  {C.CYAN}└──────────────────────────────────────────{C.RESET}")
    if not found_dex: print(f"  {C.DIM}    Tidak ditemukan API Key di file Dex.{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

# 11. TECH HUNTER
def run_p11(apk):
    width = get_width()
    print_header("HADI ULTIMATE TECH HUNTER v30.3")
    ai_desc("Analisis Struktur, Deteksi Engine, dan Real Smali Patching.")
    
    file_list = subprocess.run(f"unzip -l '{apk}'", shell=True, capture_output=True, text=True).stdout
    is_flutter = "libflutter.so" in file_list or "libapp.so" in file_list
    
    print(f"{C.CYAN}[*] INFO APLIKASI & REKOMENDASI:{C.RESET}")
    if is_flutter:
        print_kv("Engine", "FLUTTER")
        print_kv("Status", f"{C.ERROR}HARD TO MOD (Native Logic){C.RESET}")
        print(f"  {C.WARN}[!] Saran: Keyword di bawah mungkin tidak efektif. Gunakan Menu [13].{C.RESET}")
    else:
        print_kv("Engine", "NATIVE (Java/Kotlin)")
        print_kv("Status", f"{C.SUCCESS}EASY TO MOD (Dex Editing){C.RESET}")
        print(f"  {C.SUCCESS}[+] Saran: Fokus pada patching Smali melalui MT Manager.{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")
    
    keywords = ["isVipUser", "isPremium", "JWTUserData", "BillingClient", "isPro", "isSubscribed"]
    dex_files = sorted([f for f in file_list.split() if f.endswith(".dex")])
    for dex in dex_files:
        print(f"\n{C.TEXT}● SCANNING: {C.SUCCESS}{dex.upper()}{C.RESET}")
        all_strings = subprocess.run(f"unzip -p '{apk}' {dex} 2>/dev/null | strings", shell=True, capture_output=True, text=True).stdout
        for k in keywords:
            found = [line for line in all_strings.split('\n') if k.lower() in line.lower()]
            if found:
                print(f"{C.WARN}▼ KEYWORD: {C.TEXT}{k}{C.RESET}")
                seen = set(); count = 0
                for item in found:
                    clean_item = item.strip()
                    if clean_item and clean_item not in seen:
                        real_reg = get_reg(clean_item)
                        print(f"  {C.MAGENTA}┌──[ MT MANAGER GUIDE ]──┐{C.RESET}")
                        print(f"  {C.MAGENTA}│ {C.TEXT}Cari: {C.CYAN}move-result {real_reg}{C.RESET}")
                        print(f"  {C.MAGENTA}│ {C.TEXT}Add : {C.SUCCESS}const/4 {real_reg}, 0x1{C.RESET}")
                        print(f"  {C.MAGENTA}└───────────────────────┘{C.RESET}")
                        wrapper = textwrap.TextWrapper(width=width-8, initial_indent=f"  {C.SUCCESS}└─> {C.TEXT}", subsequent_indent="      ")
                        print(wrapper.fill(clean_item))
                        seen.add(clean_item); count += 1
                    if count >= 3: break
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

# 12. V-SNIPER (Added missing function)
def run_p12(apk):
    width = get_width()
    print_header("HADI ULTIMATE VIP DETECTOR v5.0")
    ai_desc("Mendeteksi keberadaan Class/Method VIP/Premium biasa.")
    
    check_list = [
        "Lcom/google/android/gms/ads/...",
        "Lcom/ironsource/...",
        "Lcom/startapp/...",
        "isPremium", "isVip", "checkLicense"
    ]
    
    find_dex = f"unzip -l '{apk}' | grep '.dex' | awk '{{print $4}}'"
    dex_files = subprocess.run(find_dex, shell=True, capture_output=True, text=True).stdout.strip().split('\n')
    
    total_hits = 0
    for dex in dex_files:
        if not dex: continue
        cmd = f"unzip -p '{apk}' '{dex}' | strings"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        found_in_dex = False
        for check in check_list:
            if check in res:
                if not found_in_dex:
                    print(f"\n  {C.SUCCESS}📂 FILE: {C.TEXT}{dex}{C.RESET}")
                    found_in_dex = True
                print(f"  {C.CYAN}[-] DETECTED: {C.WARN}{check}{C.RESET}")
                total_hits += 1
                
    if total_hits == 0:
        print(f"  {C.DIM}    Tidak ada struktur VIP/Ads yang terdeteksi.{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

# 13. FLUTTER EXT (Added missing function)
def run_p13(apk):
    width = get_width()
    print_header("HADI-FLUTTER-V1.0")
    ai_desc("Ekstrak dan Analisa libflutter.so atau libapp.so.")
    
    find_lib = f"unzip -l '{apk}' | grep -E '(libflutter|libapp).so' | awk '{{print $4}}' | head -n 1"
    lib_path = subprocess.run(find_lib, shell=True, capture_output=True, text=True).stdout.strip()
    
    if not lib_path:
        print(f"  {C.ERROR}[!] Tidak ditemukan file .so Flutter.{C.RESET}")
    else:
        print(f"  {C.SUCCESS}[+] Found: {C.TEXT}{lib_path}{C.RESET}")
        print(f"  {C.CYAN}[*] Menghitung CRC32/MD5...{C.RESET}")
        # Simulasi info file
        cmd = f"unzip -p '{apk}' '{lib_path}' | md5sum"
        md5 = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip().split()[0]
        print(f"  {C.TEXT}MD5: {C.WARN}{md5}{C.RESET}")
        print(f"  {C.YELLOW}[!] Saran: Gunakan Menu 16 (Hex Patcher) untuk patch manual.{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")
    
# 14. ULTRA CONTEXT SNIPER
def run_p14(apk):
    width = get_width()
    print_header("ULTRA-SNIPER v5.0 (DEEP SEARCH)")
    ai_desc("Scan keyword dengan melihat baris sebelum dan sesudah (Context).")
    key = input(f"\n{C.CYAN}  >> INPUT KEYWORD: {C.TEXT}").strip()
    if not key: return
    find_dex = f"unzip -l '{apk}' | grep '.dex' | awk '{{print $4}}'"
    dex_files = subprocess.run(find_dex, shell=True, capture_output=True, text=True).stdout.strip().split('\n')
    for dex in dex_files:
        if not dex: continue
        cmd = f"unzip -p '{apk}' '{dex}' | strings -a | grep -i -C 1 '{key}' | head -n 15"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        if res.strip():
            print(f"\n  {C.SUCCESS}📂 FILE: {C.TEXT}{dex}{C.RESET}")
            for line in res.strip().split('\n'):
                is_target = key.lower() in line.lower()
                prefix = f"{C.SUCCESS}  ▶ {C.TEXT}" if is_target else f"{C.DIM}    {C.RESET}"
                print(f"{prefix}{line.strip()[:width-10]}{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

# 15. SMALI PATCHER GUIDE
def run_p15():
    print_header("SMALI PATCHER ULTIMATE GUIDE")
    ai_desc("Gunakan kode ini untuk modifikasi di Smali Editor MT Manager.")
    print(f"\n {C.SUCCESS}1. Boolean (True/False){C.RESET}")
    print(f"    {C.WARN}const/4 v0, 0x1\n    return v0{C.RESET}")
    print(f"\n {C.SUCCESS}2. Integer (Vip Level/Coins){C.RESET}")
    print(f"    {C.WARN}const/16 v0, 0x3e7\n    return v0{C.RESET}")
    print(f"\n {C.SUCCESS}3. String (Status/User){C.RESET}")
    print(f"    {C.WARN}const-string v0, \"Premium\"\n    return-object v0{C.RESET}")
    print(f"{C.TEXT}{'─' * get_width()}{C.RESET}")

# 16. HEX PATCHER
def run_p16():
    print_header("HADI-HEX-PATCHER v1.0")
    ai_desc("Ubah kode mesin (Hex) file .so secara permanen (Binary Mod).")
    so_file = input(f"{C.SUCCESS}[?] Nama File .so: {C.WARN}").strip()
    if not os.path.exists(so_file): print(f"{C.ERROR}[!] File tidak ditemukan!{C.RESET}"); return
    old_hex = input(f"{C.SUCCESS}[?] Hex Lama: {C.WARN}").strip()
    new_hex = input(f"{C.SUCCESS}[?] Hex Baru: {C.WARN}").strip()
    try:
        with open(so_file, 'rb') as f: content = f.read()
        old_bytes = bytes.fromhex(old_hex); new_bytes = bytes.fromhex(new_hex)
        if old_bytes in content:
            updated = content.replace(old_bytes, new_bytes)
            with open(so_file, 'wb') as f: f.write(updated)
            print(f"\n{C.SUCCESS}[+] BERHASIL: File dipatch secara permanen!{C.RESET}")
        else: print(f"\n{C.ERROR}[!] GAGAL: Hex lama tidak ditemukan.{C.RESET}")
    except Exception as e: print(f"{C.ERROR}[!] Error: {e}{C.RESET}")
    print(f"{C.TEXT}{'─' * get_width()}{C.RESET}")

# 17. HEX SUGGESTER
def run_p17():
    print_header("HADI-HEX-SUGGESTER (ARM64)")
    ai_desc("Rekomendasi kode hex untuk bypass fungsi pada file .so (ARM64).")
    print(f" {C.TEXT}Pilih target modifikasi:{C.RESET}")
    print(f" {C.SUCCESS}1. Return True (Bypass Boolean/VIP){C.RESET}")
    print(f" {C.SUCCESS}2. Return False (Disable Checks){C.RESET}")
    print(f" {C.SUCCESS}3. NOP (No Operation / Disable Function){C.RESET}")
    opt = input(f"\n{C.CYAN}Pilih Opsi: {C.TEXT}")
    print(f"{C.TEXT}{'─' * get_width()}{C.RESET}")
    if opt == '1':
        print(f" {C.WARN}[!] REKOMENDASI PATCH (HEX):{C.RESET}")
        print(f" {C.TEXT}Code   : {C.SUCCESS}MOV X0, #1; RET{C.RESET}")
        print(f" {C.TEXT}Hex    : {C.CYAN}200080D2C0035FD6{C.RESET}")
    elif opt == '2':
        print(f" {C.WARN}[!] REKOMENDASI PATCH (HEX):{C.RESET}")
        print(f" {C.TEXT}Code   : {C.SUCCESS}MOV X0, #0; RET{C.RESET}")
        print(f" {C.TEXT}Hex    : {C.CYAN}000080D2C0035FD6{C.RESET}")
    elif opt == '3':
        print(f" {C.WARN}[!] REKOMENDASI PATCH (HEX):{C.RESET}")
        print(f" {C.TEXT}Code   : {C.SUCCESS}NOP{C.RESET}")
        print(f" {C.TEXT}Hex    : {C.CYAN}1F2003D5{C.RESET}")
    print(f"{C.TEXT}{'─' * get_width()}{C.RESET}")
    
# =============================================================================
# --- REPLACEMENT ENGINE (MENU 2 HELPER) ---
# =============================================================================

PTN_HOOK = re.compile(r"(\.method public onTransact\(ILandroid/os/Parcel;Landroid/os/Parcel;I\)Z.*?\.end annotation)", re.DOTALL)
HOOK_CODE = "\n    const/4 v0, 0x0\n    return v0"

def process_smali_file(path):
    """Worker Thread: Tugas kecil untuk setiap core CPU"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Cek super cepat string biasa sebelum regex berat
        if "onTransact" in content:
            if PTN_HOOK.search(content):
                if HOOK_CODE not in content:
                    new_content = PTN_HOOK.sub(r"\1" + HOOK_CODE, content)
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    return 1 
    except:
        pass
    return 0 
    
# =============================================================================
# --- REPLACEMENT ENGINE (MENU 2) ---
# =============================================================================

class CyberBypassV8:
    def __init__(self):
        self.jar_editor = "APKEditor-1.4.7.jar"
        self.jar_signer = "uber-apk-signer.jar"
        self.work_dir = "work_folder"
        
        # --- PERBAIKAN SPEED: JVM TUNING ---
        self.java_cmd = "java -Xms512m -Xmx2048m -XX:TieredStopAtLevel=1 -jar" 
        
        # Hitung jumlah Core CPU HP untuk Threading
        self.cpu_cores = os.cpu_count() + 2
        
        self.console = Console()
        self.refresh_apk_list()

    def refresh_apk_list(self):
        self.apks = [f for f in os.listdir('.') if f.endswith('.apk') 
                     and not f.startswith('Mod_') 
                     and not f.startswith('unsigned_')
                     and not f.endswith('-aligned-debugSigned.apk')]

    def banner(self):
        os.system('clear')
        art = """
 [bold green]██████╗ ██╗   ██╗██████╗ [/bold green]
 [bold green]██╔═══╝ ╚██╗ ██╔╝██╔══██╗[/bold green]
 [bold green]██║      ╚████╔╝ ██████╔╝[/bold green]
 [bold green]██║       ╚██╔╝  ██╔══██╗[/bold green]
 [bold green]╚██████╗   ██║   ██████╔╝[/bold green]
 [bold green] ╚═════╝   ╚═╝   ╚═════╝ [/bold green]
 [bold cyan] BYPASS ENGINE V8 - MAX [/bold cyan]
        """
        panel = Panel(
            Align.center(art),
            title="[bold red]SYSTEM READY[/bold red]",
            subtitle=f"[bold yellow]CPU Cores Detected: {os.cpu_count()}[/bold yellow]",
            border_style="bright_blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        self.console.print(panel)

    def show_menu(self):
        self.banner()
        if not self.apks:
            self.console.print(Panel("[bold red]❌ TIDAK ADA FILE APK![/bold red]", border_style="red"))
            input("\n[Enter to Back]")
            return None

        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD, expand=True)
        table.add_column("No", style="dim", width=4, justify="center")
        table.add_column("Nama File APK", style="cyan")
        table.add_column("Size", style="green", justify="right")

        for i, apk in enumerate(self.apks, 1):
            size_mb = os.path.getsize(apk) / (1024 * 1024)
            table.add_row(str(i), apk, f"{size_mb:.2f} MB")
        
        table.add_row(" ", "", "")
        table.add_row("[bold red]0[/bold red]", "[bold red]KEMBALI (BACK)[/bold red]", "")

        self.console.print(table)
        self.console.print("[dim]─" * self.console.width + "[/dim]")
        
        try:
            valid_choices = [str(i) for i in range(0, len(self.apks)+1)]
            prompt_style = "[bold green]nexus㉿termux[/bold green][white]~$[/white]"
            choice = IntPrompt.ask(prompt_style, choices=valid_choices, show_choices=False)
            
            if choice == 0:
                return None
            return self.apks[choice - 1]
        except KeyboardInterrupt:
            return None

    def run_cmd_silent(self, cmd):
        process = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return process.returncode == 0

    def clean_manifest(self):
        m_path = os.path.join(self.work_dir, "AndroidManifest.xml")
        if os.path.exists(m_path):
            with open(m_path, 'r', encoding='utf-8') as f: content = f.read()
            patterns = [
                (re.compile(r'<activity\s+android:name="com\.pairip\.licensecheck\.LicenseActivity".*?/>', re.DOTALL), ""),
                (re.compile(r'<provider\s+android:name="com\.pairip\.licensecheck\.LicenseContentProvider".*?/>', re.DOTALL), ""),
                (re.compile(r'<uses-permission\s+android:name="com\.android\.vending\.CHECK_LICENSE"\s*/>'), "")
            ]
            for ptrn, repl in patterns:
                content = ptrn.sub(repl, content)
            with open(m_path, 'w', encoding='utf-8') as f: f.write(content)
            return True
        return False
        
    def multithreaded_patching(self, progress_obj, task_id):
        all_smali_files = []
        progress_obj.update(task_id, description="[bold blue]Scanning Smali...[/bold blue]")
        
        for root, dirs, files in os.walk(self.work_dir, topdown=True):
            dirs[:] = [d for d in dirs if "smali" in d]
            
            for d in list(dirs):
                if "pairip" in d or "licensecheck" in d:
                    try: 
                        shutil.rmtree(os.path.join(root, d))
                        dirs.remove(d)
                    except: pass
            
            for file in files:
                if file.endswith(".smali"):
                    all_smali_files.append(os.path.join(root, file))

        total_files = len(all_smali_files)
        if total_files == 0: return

        progress_obj.update(task_id, description=f"[bold blue]Injecting {total_files} files...[/bold blue]")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.cpu_cores) as executor:
            results = list(executor.map(process_smali_file, all_smali_files))
            patched_count = sum(results)

        if patched_count > 0:
            progress_obj.print(f"  [green]✔ Injected hooks into {patched_count} files[/green]")

    def execute(self, target):
        os.system('clear')
        final_apk_name = f"Mod_{target}"
        self.console.print(Panel(f"[bold white]Target:[/bold white] [cyan]{target}[/cyan]", border_style="green"))
        
        with Progress(
            SpinnerColumn("dots", style="bold blue"),
            TextColumn("{task.description}"),
            BarColumn(bar_width=None, style="blue", complete_style="green", finished_style="green"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task1 = progress.add_task("[bold blue]Decompiling APK...[/bold blue]", total=100)
            if not self.run_cmd_silent(f"{self.java_cmd} {self.jar_editor} d -i \"{target}\" -o {self.work_dir}"):
                progress.stop()
                self.console.print("[bold red]❌ Gagal Decompile![/bold red]")
                input("[Enter]")
                return
            progress.update(task1, completed=100, description="[bold green]✔ Decompile Selesai[/bold green]")
            progress.print("  [green]✔ Source code extracted[/green]")

            task2 = progress.add_task("[bold blue]Scanning & Injecting...[/bold blue]", total=100)
            if self.clean_manifest(): progress.print("  [green]✔ Manifest Cleaned[/green]")
            self.multithreaded_patching(progress, task2)
            progress.update(task2, completed=100, description="[bold green]✔ Patching Selesai[/bold green]")

            task3 = progress.add_task("[bold blue]Rebuilding APK...[/bold blue]", total=100)
            if not self.run_cmd_silent(f"{self.java_cmd} {self.jar_editor} b -i {self.work_dir} -o \"{final_apk_name}\""):
                progress.stop()
                self.console.print("[bold red]❌ Gagal Rebuild![/bold red]")
                input("[Enter]")
                return
            progress.update(task3, completed=100, description="[bold green]✔ Rebuild Selesai[/bold green]")
            progress.print("  [green]✔ APK Built Successfully[/green]")

            task4 = progress.add_task("[bold blue]Signing APK...[/bold blue]", total=100)
            if self.run_cmd_silent(f"{self.java_cmd} {self.jar_signer} -a \"{final_apk_name}\" --overwrite"):
                progress.update(task4, completed=100, description="[bold green]✔ Signing Selesai[/bold green]")
                progress.print("  [green]✔ Signature Applied[/green]")
            else:
                self.console.print("[bold red]⚠ Signing Failed.[/bold red]")

            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)

        self.console.print("\n")
        final_panel = Panel(
            f"[bold green]Proses Selesai![/bold green]\nOutput File: [cyan]{final_apk_name}[/cyan]\n[dim](Signed & Ready to Install)[/dim]",
            title="[bold white]SUCCESS[/bold white]",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(final_panel)
        input("\n[Tekan Enter untuk kembali ke menu]")
        
        
# =============================================================================
# --- REPLACEMENT ENGINE (MENU 3) ---
# =============================================================================

class MitmEngineV8:
    def __init__(self):
        self.console = Console()
        self.refresh_apk_list()

    def refresh_apk_list(self):
        self.apks = [f for f in os.listdir('.') if f.endswith('.apk') 
                     and not f.endswith('-patched.apk')]

    def banner(self):
        os.system('clear')
        art = """
 [bold green]██████╗ ██╗   ██╗██████╗ [/bold green]
 [bold green]██╔═══╝ ╚██╗ ██╔╝██╔══██╗[/bold green]
 [bold green]██║      ╚████╔╝ ██████╔╝[/bold green]
 [bold green]██║       ╚██╔╝  ██╔══██╗[/bold green]
 [bold green]╚██████╗   ██║   ██████╔╝[/bold green]
 [bold green] ╚═════╝   ╚═╝   ╚═════╝ [/bold green]
 [bold cyan]  APK-MITM UNPIN ENGINE  [/bold cyan]
        """
        panel = Panel(
            Align.center(art),
            title="[bold red]MITM READY[/bold red]",
            subtitle="[bold yellow]SSL Pinning Bypass Mode[/bold yellow]",
            border_style="bright_blue",
            box=box.ROUNDED,
            padding=(0, 1)
        )
        self.console.print(panel)
        
    def show_menu(self):
        self.banner()
        if not self.apks:
            self.console.print(Panel("[bold red]❌ TIDAK ADA FILE APK DI DIREKTORI INI![/bold red]", border_style="red"))
            input("\n[Enter to Back]")
            return None

        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE_HEAD, expand=True)
        table.add_column("No", style="dim", width=4, justify="center")
        table.add_column("Nama File APK", style="cyan")
        table.add_column("Size", style="green", justify="right")

        for i, apk in enumerate(self.apks, 1):
            size_bytes = os.path.getsize(apk)
            size_mb = size_bytes / (1024 * 1024)
            table.add_row(str(i), apk, f"{size_mb:.2f} MB")
        
        table.add_row(" ", "", "")
        table.add_row("[bold red]0[/bold red]", "[bold red]KEMBALI (BACK)[/bold red]", "")

        self.console.print(table)
        self.console.print("[dim]─" * self.console.width + "[/dim]")
        
        try:
            valid_choices = [str(i) for i in range(0, len(self.apks)+1)]
            prompt_style = "[bold green]nexus㉿termux[/bold green][white]~$[/white]"
            choice = IntPrompt.ask(prompt_style, choices=valid_choices, show_choices=False)
            
            if choice == 0:
                return None
            return self.apks[choice - 1]
        except KeyboardInterrupt:
            return None

    def smart_wrapper(self, command):
        try:
            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True
            )
            for line in process.stdout:
                if line.strip():
                    self.console.print(f"  [dim]>[/dim] [white]{line.strip()}[/white]")
            process.wait()
            return process.returncode == 0
        except Exception as e:
            self.console.print(f"[bold red][!] ERROR: {str(e)}[/bold red]")
            return False

    def execute(self, target):
        os.system('clear')
        self.console.print(Panel(f"[bold white]Target APK:[/bold white] [cyan]{target}[/cyan]", border_style="green"))
        
        self.console.print("[bold yellow][*] Memulai proses patch SSL Pinning...[/bold yellow]")
        
        success = self.smart_wrapper(f"apk-mitm {target} --unpin")
        
        if success:
            self.console.print("\n")
            final_panel = Panel(
                f"[bold green]Patching Selesai![/bold green]\nCek file dengan akhiran [cyan]-patched.apk[/cyan]",
                title="[bold white]SUCCESS[/bold white]",
                border_style="bright_green",
                box=box.DOUBLE
            )
            self.console.print(final_panel)
        else:
            self.console.print(Panel("[bold red]Proses gagal atau dihentikan.[/bold red]", border_style="red"))
            
        input("\n[Tekan Enter untuk kembali ke menu]")
        
        
# =============================================================================
# --- NEW AD KILLER ENGINE (MENU 1) ---
# =============================================================================

class AdKillerV9_Nexus:
    def __init__(self):
        self.jar_editor = "APKEditor-1.4.7.jar"
        self.signer = "uber-apk-signer.jar"
        self.work_dir = "ad_cleaner_work"
        self.ad_domains = [
            "googleads", "doubleclick", "googlesyndication", "startapp",
            "unity3d.ads", "applovin", "ironsrc", "vungle", "inmobi",
            "adcolony", "mopub", "chartboost"
        ]
        self.banner_keywords = [
            "adView", "ad_view", "banner_ad", "banner_container",
            "ad_container", "mopub_banner", "startapp_banner"
        ]
        self.console = Console() # Menggunakan instance sendiri
        self.refresh_apk_list()

    def banner(self):
        os.system("clear")
        art = """
 [bold red] █████╗ ██████╗ ██╗  ██╗██╗██╗     ██╗     ███████╗██████╗ [/bold red]
 [bold red]██╔══██╗██╔══██╗██║ ██╔╝██║██║     ██║     ██╔════╝██╔══██╗[/bold red]
 [bold red]███████║██║  ██║█████╔╝ ██║██║     ██║     █████╗  ██████╔╝[/bold red]
 [bold red]██╔══██║██║  ██║██╔═██╗ ██║██║     ██║     ██╔══╝  ██╔══██╗[/bold red]
 [bold red]██║  ██║██████╔╝██║  ██╗██║███████╗███████╗███████╗██║  ██║[/bold red]
 [bold red]╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝[/bold red]
 [bold yellow]   NEXUS AD-KILLER V9.0 | SMALI & MB-TRACKER   [/bold yellow]
        """
        self.console.print(Panel(Align.center(art), title="[bold green]SYSTEM READY[/bold green]", border_style="bright_red", box=box.ROUNDED))

    def get_file_size(self, file_path):
        """Menghitung ukuran file dalam Megabytes"""
        size_bytes = os.path.getsize(file_path)
        return f"{size_bytes / (1024 * 1024):.2f} MB"

    def refresh_apk_list(self):
        """Mendapatkan daftar APK beserta ukurannya"""
        self.apks = []
        for f in os.listdir('.'):
            if f.lower().endswith('.apk') and not f.startswith('AdFree_'):
                self.apks.append({
                    "name": f,
                    "size": self.get_file_size(f)
                })

    def patch_layout_banners(self):
        patched_layouts = 0
        res_path = os.path.join(self.work_dir, "res")
        if not os.path.exists(res_path): return 0

        for root, _, files in os.walk(res_path):
            if "layout" in root:
                for file in files:
                    if file.endswith(".xml"):
                        path = os.path.join(root, file)
                        try:
                            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            if any(kw in content for kw in self.banner_keywords):
                                content = re.sub(r'android:layout_width="[^"]*"', 'android:layout_width="0dp"', content)
                                content = re.sub(r'android:layout_height="[^"]*"', 'android:layout_height="0dp"', content)
                                if 'android:visibility' not in content:
                                    content = content.replace('android:layout_height="0dp"', 'android:layout_height="0dp" android:visibility="gone"')
                                with open(path, 'w', encoding='utf-8') as f:
                                    f.write(content)
                                patched_layouts += 1
                        except: pass
        return patched_layouts

    def patch_smali_aggressive(self):
        """Injeksi Smali Cerdas (Fixing .locals injection order)"""
        patched_smali = 0
        for root, _, files in os.walk(self.work_dir):
            for file in files:
                if file.endswith(".smali"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()

                        new_lines = []
                        modified = False
                        i = 0
                        while i < len(lines):
                            line = lines[i]
                            # Domain Redirect
                            for domain in self.ad_domains:
                                if domain in line:
                                    line = re.sub(domain, "127.0.0.1", line, flags=re.IGNORECASE)
                                    modified = True

                            new_lines.append(line)

                            # Smart Method Killer
                            if ".method" in line and ("loadAd" in line or "showAd" in line):
                                for j in range(1, 6):
                                    if i + j < len(lines):
                                        next_line = lines[i+j]
                                        if ".locals" in next_line or ".registers" in next_line:
                                            new_lines.append(next_line)
                                            new_lines.append("    return-void\n")
                                            i += j
                                            modified = True
                                            patched_smali += 1
                                            break
                            i += 1

                        if modified:
                            with open(path, 'w', encoding='utf-8') as f:
                                f.writelines(new_lines)
                    except: pass
        return patched_smali

    def execute(self, target_name):
        if not os.path.exists(self.jar_editor):
            self.console.print(f"[bold red] ❌ ERROR: {self.jar_editor} MISSING![/bold red]")
            return

        output_apk = f"AdFree_{target_name}"
        self.console.print(f"\n[bold yellow][*] TARGET: {target_name} ({self.get_file_size(target_name)})[/bold yellow]")

        # 1. DECOMPILE
        cmd_d = f"java -jar {self.jar_editor} d -i \"{target_name}\" -o {self.work_dir}"
        if subprocess.run(cmd_d, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE).returncode == 0:

            nav_path = os.path.join(self.work_dir, "res", "navigation")
            if os.path.exists(nav_path): shutil.rmtree(nav_path)

            self.console.print("[bold cyan][*] INJECTING EXPLOITS...[/bold cyan]")
            l_count = self.patch_layout_banners()
            s_count = self.patch_smali_aggressive()
            self.console.print(f"[bold green][+] STATUS: {l_count} Layouts & {s_count} Smali units patched.[/bold green]")

            # 2. BUILD
            self.console.print("[bold yellow][*] REBUILDING BINARY...[/bold yellow]")
            cmd_b = f"java -jar {self.jar_editor} b -i {self.work_dir} -o \"{output_apk}\" -t xml"
            res_b = subprocess.run(cmd_b, shell=True, capture_output=True, text=True)

            if res_b.returncode == 0:
                # 3. SIGNING
                if os.path.exists(self.signer):
                    self.console.print("[bold magenta][*] SIGNING APK...[/bold magenta]")
                    subprocess.run(f"java -jar {self.signer} -a \"{output_apk}\" --overwrite", shell=True, stdout=subprocess.DEVNULL)
                    self.console.print(f"[bold green]✔ MISSION SUCCESS: {output_apk} ({self.get_file_size(output_apk)})[/bold green]")
                else:
                    self.console.print("[bold red]⚠ SIGNER MISSING![/bold red]")
            else:
                self.console.print(Panel(res_b.stderr, title="[bold red]BUILD FAILED[/bold red]", border_style="red"))

            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
        else:
            self.console.print("[bold red]❌ DECOMPILE FAILED![/bold red]")

    def main_loop(self):
        while True:
            self.refresh_apk_list()
            self.banner()
            if not self.apks:
                self.console.print(Panel("[bold red]NO APK FILES FOUND IN DIRECTORY![/bold red]", border_style="red"))
                input("\n[Enter] Re-scan...")
                continue

            table = Table(box=box.HORIZONTALS, expand=True, header_style="bold magenta")
            table.add_column("ID", style="dim", width=4)
            table.add_column("APK FILENAME", style="cyan")
            table.add_column("SIZE (MB)", style="green", justify="right")

            for i, apk in enumerate(self.apks, 1):
                table.add_row(str(i), apk['name'], apk['size'])

            table.add_row("0", "EXIT SYSTEM", "-", style="bold red")
            self.console.print(table)

            try:
                choice = IntPrompt.ask("[bold red]nexus㉿root[/bold red]", choices=[str(i) for i in range(len(self.apks)+1)], show_choices=False)
                if choice == 0: break
                self.execute(self.apks[choice-1]['name'])
                input("\n[Enter] Back to Terminal...")
            except Exception as e:
                print_error(str(e))
                break
                
                
# =============================================================================
# --- PATCHING LOGIC (4-9) --- Mode 1 Removed, 2 & 3 Moved to Classes
# =============================================================================

translation_cache = {}

def is_safe_to_translate(text):
    t = text.strip()
    return len(t) >= 1 and not t.isnumeric() and not any(x in t for x in ["%", "{", "}", "Landroid", "http", "@string", "0x", ".com", "true", "false"])

def safe_translate(text, target_lang, mode="xml"):
    text_s = text.strip()
    if not is_safe_to_translate(text): return text
    if text_s in translation_cache: return translation_cache[text_s]
    try:
        trans = GoogleTranslator(source='auto', target=target_lang).translate(text_s)
        if mode == "xml": trans = trans.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        else: trans = trans.replace('"', '\\"')
        translation_cache[text_s] = trans; return trans
    except: return text

def apply_patch(work_dir, mode, target_lang='id'):
    hits = 0
    
    if mode == 9:
        print_info(f"OMEGA DEEP SCAN: Target Lang -> {target_lang.upper()}")
        
        for root, _, files in os.walk(work_dir):
            if any(x in root for x in ["original", "kotlin", "androidx", "com/google", "META-INF", "build"]): continue
            
            for f in files:
                if f.endswith(('.xml', '.smali', '.lua', '.json', '.txt', '.properties')):
                    p = os.path.join(root, f)
                    try:
                        sys.stdout.write(f"\r{C.DIM} > Scanning: {f[:20]:<20} {C.RESET}")
                        sys.stdout.flush()
                        
                        with open(p, "r", encoding="utf-8", errors="ignore") as file: 
                            content = file.read()
                        
                        changed = False
                        matches = re.findall(r'[\u4e00-\u9fff]+', content)
                        
                        if matches:
                            for m in set(matches):
                                trans = safe_translate(m, target_lang, "xml" if f.endswith(".xml") else "smali")
                                if trans != m:
                                    content = content.replace(m, trans)
                                    hits += 1; changed = True
                                    
                        if changed:
                            with open(p, "w", encoding="utf-8") as file: file.write(content)
                    except: continue
        print()
        return hits
        
    heavy_targets = [
        "Landroid/app/AlertDialog;->show()V",
    "Landroid/app/Dialog;->show()V",
    "Landroidx/appcompat/app/AlertDialog;->show()V",
    "Landroid/app/ProgressDialog;->show()V",
    "Lcom/google/android/material/snackbar/Snackbar;->show()V",
    "Landroid/widget/Toast;->show()V",
    "Landroid/widget/PopupWindow;->showAtLocation(Landroid/view/View;III)V",
    "Landroid/widget/PopupWindow;->showAsDropDown(Landroid/view/View;III)V",
    "Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;",
    "Lmt/modder/hub/Main;->init",
    "Lmt/modder/hub/Check;->Verify",
    "Lmt/modder/hub/Update;->check",
    "FloatWindow;->show",
    "Config;->isActivated()Z",
    "Lmt/modder/hub/MTMain;->main",
    "Lmt/modder/hub/Check;->Verify",
    "invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext",
    "Landroid/widget/PopupWindow;->showAtLocation(Landroid/view/View;III)V",
    "Landroid/widget/PopupWindow;->showAsDropDown(Landroid/view/View;III)V",
    "Landroid/widget/Toast;->show()V",
    "mt/modder/",
    "Lmt/modder/hub/",
    "np/",
    "Landroid/app/AlertDialog;->show()V",
    "Landroid/app/Dialog;->show()V",
    "Landroidx/appcompat/app/AlertDialog;->show()V",
    "Landroid/app/ProgressDialog;->show()V",
    "Lcom/google/android/material/snackbar/Snackbar;->show()V",
    "Landroid/widget/Toast;->show()V",
    "Landroid/widget/PopupWindow;->showAtLocation(Landroid/view/View;III)V",
    "Landroid/widget/PopupWindow;->showAsDropDown(Landroid/view/View;III)V",
    "Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;",
    "Lmt/modder/hub/Main;->init",
    "Lmt/modder/hub/Check;->Verify",
    "Lmt/modder/hub/Update;->check",
    "FloatWindow;->show",
    "Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;",
    "Landroid/app/AlertDialog;->show()V", "Landroid/app/Dialog;->show()V",
    "Landroidx/appcompat/app/AlertDialog;->show()V", "Landroid/app/ProgressDialog;->show()V",
    "Landroid/app/AlertDialog$Builder;->create()", "Landroid/app/AlertDialog$Builder;->show()",
    "Landroidx/appcompat/app/AlertDialog$Builder;->create()", "Landroidx/appcompat/app/AlertDialog$Builder;->show()",
    "Lcom/google/android/material/dialog/MaterialAlertDialogBuilder;->create()",
    "Lcom/google/android/material/dialog/MaterialAlertDialogBuilder;->show()",
    "Lcom/google/android/material/snackbar/Snackbar;->show()V", "Landroid/widget/Toast;->show()V",
    "Landroid/widget/PopupWindow;->showAtLocation", "Landroid/widget/PopupWindow;->showAsDropDown",
    "Lmt/modder/hub/"

    ]

    if mode == 7:
        print_info("Remove Dialog/Ads/Toas ...")
        for s_dir in [d for d in os.listdir(work_dir) if d.startswith("smali")]:
            for folder in ["mt/modder/hub", "mt/modder", "com/google/android/gms/ads"]:
                p = os.path.join(work_dir, s_dir, folder)
                if os.path.exists(p): shutil.rmtree(p, ignore_errors=True)

    print_info("Patching Smali files...")
    for root, _, files in os.walk(work_dir):
        if any(x in root for x in ["androidx", "com/google", "mt/modder"]): continue
        for file in files:
            if file.endswith(".smali"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding="utf-8", errors='ignore') as f: lines = f.readlines()
                    new_l, changed = [], False
                    for i, line in enumerate(lines):
                        if mode == 7 and any(t in line for t in heavy_targets):
                            changed = True; hits += 1
                            new_l.append("    nop\n")
                            if i+1 < len(lines) and "move-result" in lines[i+1]:
                                try:
                                    reg = lines[i+1].split()[-1]
                                    new_l.append(f"    const/4 {reg}, 0x0\n")
                                    lines[i+1] = ""
                                except: pass
                            continue
                        
                        if line == "":
                            continue
                            
                        c = line
                        # Mode 1 (VIP Bypass) DIHAPUS - Digantikan Menu AdKiller
                        # Mode 2 (Signature Kill) Dihapus
                        # Mode 3 (SSL Unpinning) Dihapus
                        
                        # FIX: Ubah elif menjadi if agar sintaks benar
                        if mode == 4: 
                            c = c.replace("if-eqz v0,", "if-nez v0,")
                        elif mode == 5: 
                            c = c.replace("onAuthFailed", "onAuthSuccess")
                        
                        if c != line: changed = True; hits += 1
                        new_l.append(c)
                    
                    if changed:
                        with open(path, "w", encoding="utf-8") as f: f.writelines(new_l)
                except: continue
    return hits

def select_file():
    files = [f for f in os.listdir('.') if f.endswith('.apk') and not f.startswith('MOD_')]
    if not files: return None

    lines = []
    for i, f in enumerate(files, 1):
        size_str = "N/A"
        try:
            size_mb = os.path.getsize(f) / (1024*1024)
            size_str = f"{size_mb:.1f}MB"
        except: pass

        line = f"{C.MENU}[{i}]{C.RESET} {C.TEXT}{f}{C.RESET}"
        lines.append(line)

    draw_box("SELECT TARGET APK", lines, color=C.ACCENT)

    try:
        print(f"\n{C.TEXT}Select file:{C.RESET} ", end="")
        ch = input().strip()
        idx = int(ch) - 1
        if 0 <= idx < len(files):
            return files[idx]
    except: pass
    return None

def show_summary(title, apk_name, stats):
    status_icon = lambda x: f"{C.SUCCESS}✔{C.RESET}" if x else f"{C.ERROR}✘{C.RESET}"

    content = [
        f"{C.TEXT}Target File     :{C.RESET} {C.WARN}{apk_name}{C.RESET}",
        f"{C.TEXT}{'─' * 35}{C.RESET}",
        f"{C.TEXT}Decompile       :{C.RESET} {status_icon(stats['decompile'])}",
        f"{C.TEXT}Patches Injected:{C.RESET} {C.ACCENT}{stats['patches']} Hits{C.RESET}",
        f"{C.TEXT}Rebuild APK     :{C.RESET} {status_icon(stats['build'])}",
        f"{C.TEXT}Signing Key     :{C.RESET} {status_icon(stats['sign'])}",
        f"{C.TEXT}{'─' * 35}{C.RESET}",
        f"{C.SUCCESS}Output saved to: MOD_{apk_name}{C.RESET}"
    ]

    draw_box(title, content, color=C.SUCCESS, double_border=True)
    
    
def main_menu():
    clear()

    logo = [
        f"{C.HEAD}{C.BOLD}  NEXUS APK TOOLS{C.RESET}",
        f"{C.GRAY}  Advanced Android Modder{C.RESET}"
    ]
    print(center_text("\n".join(logo)))
    print()

    apks = [f for f in os.listdir('.') if f.endswith('.apk') and not f.startswith('MOD_')]
    apk_count = len(apks)
    apk_status = f"{C.SUCCESS}{apk_count} Ready{C.RESET}" if apk_count > 0 else f"{C.ERROR}No APK{C.RESET}"

    menu_items = [
        # MODDING TOOLS
        ("1", "Ad Killer V9", "Remove Ads & Banners"), # Diubah dari VIP Bypass
        ("2", "Cyber Bypass V8", "Auto Hook & Pairip Nuke"), # Baru
        ("3", "MITM Unpin",      "SSL Pinning Bypass"),     # Baru
        ("4", "Logic Flipper",   "Reverse Boolean Logic"),
        ("5", "Auth Force",      "Force Auth Success"),
        ("6", "Localizer",       "Translate Strings to ID"),
        ("7", "Master Nuke",     "Remove Dialogs & Toast"),
        ("8", "Flutter Mod",     "Patch Flutter Engine"),
        ("9", "OMEGA SCAN",      "Omega Deep 20-Lang Scanner"),
        # ANALYSIS TOOLS
        ("10", "API Sniper",     "Find API Keys in .dex/.so"),
        ("11", "Tech Hunter",    "Deep VIP Structure Scan"),
        ("12", "V-Sniper v5.3",  "Real Engine VIP Detect"),
        ("13", "Flutter Ext",    "Extract & View Hex Offset"),
        ("14", "Ultra Context",  "Context Deep Search"),
        ("15", "Smali Guide",    "MT Manager Patch Codes"),
        ("16", "Hex Patcher",    "Manual .so Hex Editor"),
        ("17", "Hex Suggester",  "ARM64 Bypass Hex Codes"),
    ]

    lines = []
    for num, name, desc in menu_items:
        if num == "10":
            lines.append("")
            lines.append(f"{C.HEAD}── [ ANALYSIS TOOLS ] ──{C.RESET}")
        
        line = f"{C.MENU}[{num}]{C.RESET} {C.BOLD}{name}{C.RESET}"
        lines.append(line)
        lines.append(f"{C.GRAY}   └─ {desc}{C.RESET}")

    lines.append("")
    lines.append(f"{C.ERROR}[0] EXIT{C.RESET}")

    title = f"MAIN MENU  •  APK: {apk_status}"
    draw_box(title, lines, color=C.HEAD)

    print(f"{C.DIM}nexus{C.TEXT}㉿{C.SUCCESS}termux{C.TEXT}~{C.RESET}$ ", end="", flush=True)

def main():
    if not check_requirements(): sys.exit(1)
    while True:
        main_menu()
        choice = input().strip()

        if choice == '0':
            print(f"\n{C.TEXT}Exiting Nexus.{C.RESET}")
            break
        
        # Handle Menu 1 (AdKillerV9_Nexus)
        if choice == '1':
            try:
                app = AdKillerV9_Nexus()
                app.main_loop()
            except Exception as e:
                print_error(f"Error: {e}")
                input("Enter...")
            continue

        # Handle Menu 2 (CyberBypassV8)
        if choice == '2':
            try:
                app = CyberBypassV8()
                target = app.show_menu()
                if target:
                    app.execute(target)
            except Exception as e:
                print_error(f"Error: {e}")
                input("Enter...")
            continue

        # Handle Menu 3 (MitmEngineV8)
        if choice == '3':
            try:
                app = MitmEngineV8()
                while True:
                    app.refresh_apk_list()
                    target = app.show_menu()
                    if target:
                        app.execute(target)
                    else:
                        break
            except Exception as e:
                print_error(f"Error: {e}")
                input("Enter...")
            continue

        is_mod = choice.isdigit() and (4 <= int(choice) <= 9) # 1, 2, 3 sudah dihandle di atas
        is_analysis = choice.isdigit() and 10 <= int(choice) <= 17

        if not (is_mod or is_analysis):
            print(f"\n{C.ERROR}[!] Invalid Option{C.RESET}")
            time.sleep(1)
            continue

        target_apk = select_file()
        if not target_apk:
            print_error("No file selected or invalid.")
            time.sleep(1)
            continue

        # --- HANDLE ANALYSIS TOOLS (10-17) ---
        if is_analysis:
            clear()
            try:
                if choice == '10': run_p10(target_apk)
                elif choice == '11': run_p11(target_apk)
                elif choice == '12': run_p12(target_apk)
                elif choice == '13': run_p13(target_apk)
                elif choice == '14': run_p14(target_apk)
                elif choice == '15': run_p15()
                elif choice == '16': run_p16()
                elif choice == '17': run_p17()
            except Exception as e:
                print_error(f"Analysis error: {e}")
            input(f"\n{C.GRAY}[ Press Enter to continue ]{C.RESET}")
            continue

        # --- HANDLE MODDING TOOLS (4-9) ---
        idx = int(choice)
        work = "nexus_temp"; unsig = "unsig.apk"; final = f"MOD_{target_apk}"

        for f in [work, unsig, "aligned.apk"]:
            if os.path.exists(f):
                if os.path.isdir(f): shutil.rmtree(f)
                else: os.remove(f)

        stats = {'decompile': False, 'patches': 0, 'build': False, 'sign': False}

        # 1. DECOMPILE
        print()
        print_info("Decompiling APK (Using APKEditor Engine)...")
        cmd = f'java -jar APKEditor-1.4.7.jar d -i "{target_apk}" -o "{work}"'
        
        if os.system(f'{cmd} > /dev/null 2>&1') == 0:
            stats['decompile'] = True
            print_success("Decompile Successful!")
        else:
            print_error("Decompile Failed!")
            input(f"\n{C.GRAY}[ Press Enter ]{C.RESET}")
            continue

        # 2. PATCHING
        t_lang = 'id'
        
        if idx == 9:
            langs = [
                ("1","Indonesia","id"), ("2","Arabia","ar"), ("3","Inggris","en"), ("4","Rusia","ru"), ("5","Tailand","th")
            ]
            
            lang_lines = []
            for i in range(0, len(langs), 2):
                chunk = langs[i:i+2]
                row_str = "".join([f"{C.MENU}[{item[0]}]{C.RESET} {item[1][:12]:<12} " for item in chunk])
                lang_lines.append(row_str)
            
            draw_box("OMEGA TARGET LANGUAGE", lang_lines, color=C.MAGENTA)
            print()
            l_sel = input(f"{C.TEXT}Select lang_id:{C.RESET} ").strip()
            
            selected = next((x for x in langs if x[0] == l_sel), None)
            if selected:
                t_lang = selected[2]
            else:
                print_error("Invalid selection, using Default (ID).")
                t_lang = 'id'

        start_time = time.time()
        stats['patches'] = apply_patch(work, idx, t_lang)
        elapsed = time.time() - start_time
        print_success(f"Patch Complete: {stats['patches']} changes in {elapsed:.2f}s")

        # 3. BUILD
        print()
        print_info("Building APK (Using APKEditor Engine)...")
        cmd = f'java -jar APKEditor-1.4.7.jar b -i "{work}" -o "{unsig}"'
        
        if os.system(f'{cmd} > /dev/null 2>&1') == 0:
            stats['build'] = True
            print_success("Build Successful!")
        else:
            print_error("Build Failed!")
            input(f"\n{C.GRAY}[ Press Enter ]{C.RESET}")
            continue

        # 4. SIGNING
        if stats['build']:
            print_info("Signing APK (Using Uber APK Signer)...")
            ret = os.system(f'java -jar uber-apk-signer.jar -a {unsig} --out . > /dev/null 2>&1')
            
            if ret == 0:
                for f in os.listdir('.'):
                    if "aligned-debugSigned" in f and f.endswith('.apk'):
                        os.rename(f, final)
                        stats['sign'] = True
                        print_success("Signing Successful!")
                        break
                if not stats['sign']:
                    print_error("Uber Signer ran but output not found.")
            else:
                print_error("Signing Failed.")

        show_summary("SESSION SUMMARY", target_apk, stats)
        input(f"\n{C.GRAY}[ Press Enter to continue ]{C.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()       
