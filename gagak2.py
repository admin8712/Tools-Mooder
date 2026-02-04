#!/usr/bin/env python3
import os, sys, subprocess, shutil, re, time, threading, signal, textwrap
from shutil import get_terminal_size

# --- INSTALL MODULE ---
try:
    from deep_translator import GoogleTranslator
except ImportError:
    print("\033[33m[!] Installing modules...\033[0m")
    os.system('pip3 install deep-translator --quiet')
    try:
        from deep_translator import GoogleTranslator
    except:
        pass

# --- CHECK REQUIREMENTS (PAKAI APKEDITOR & UBER SIGNER) ---
def check_requirements():
    print(f"{C.CYAN}[*] Checking Environment (Nexus Engine)...\033[0m")
    
    if not shutil.which("java"):
        print(f"{C.ERROR}[!] ERROR: Java not found!{C.RESET}")
        print("Please install Java in Termux:")
        print("  pkg install openjdk-17")
        return False
    
    if not os.path.exists("APKEditor-1.4.3.jar"):
        print(f"{C.ERROR}[!] ERROR: APKEditor-1.4.3.jar not found!{C.RESET}")
        print("Download: wget https://github.com/ReAndroid/APKEditor/releases/download/v1.4.3/APKEditor-1.4.3.jar -O APKEditor-1.4.3.jar")
        return False

    if not os.path.exists("uber-apk-signer.jar"):
        print(f"{C.ERROR}[!] ERROR: uber-apk-signer.jar not found!{C.RESET}")
        print("Download: wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O uber-apk-signer.jar")
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

# 12. V-SNIPER
def run_p12(apk):
    width = get_width()
    print_header("HADI-V-SNIPER v5.3 (REAL ENGINE)")
    ai_desc("Deep Scan Method VIP & Status Rekomendasi Modifikasi.")
    
    file_list = subprocess.run(f"unzip -l '{apk}'", shell=True, capture_output=True, text=True).stdout
    is_flutter = "libflutter.so" in file_list or "libapp.so" in file_list
    
    print(f"{C.CYAN}[*] HASIL ANALISIS ENGINE:{C.RESET}")
    if is_flutter:
        print(f"  {C.ERROR}STATUS: [ HARD MOD ] - Terdeteksi Flutter Engine{C.RESET}")
        print(f"  {C.WARN}REKOMENDASI: Gunakan Menu [13] (Flutter Extractor){C.RESET}")
    else:
        print(f"  {C.SUCCESS}STATUS: [ EASY MOD ] - Terdeteksi Pure Java/Dex{C.RESET}")
        print(f"  {C.WARN}REKOMENDASI: Gunakan Menu [11] (Tech Hunter){C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

    keys = "isVip|isPremium|isPro|isSubscribed|setVip|setPremium|BillingClient"
    found_total = False
    for i in range(1, 16):
        dex_name = f"classes{'' if i==1 else i}.dex"
        check = subprocess.run(f"unzip -l '{apk}' {dex_name} 2>/dev/null", shell=True, capture_output=True)
        if check.returncode != 0: continue
        sys.stdout.write(f"\r{C.DIM}    Scanning {dex_name}...{C.RESET}")
        sys.stdout.flush()
        cmd = f"unzip -p '{apk}' {dex_name} 2>/dev/null | strings | grep -iE '{keys}' | head -n 5"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
        if res:
            found_total = True
            print(f"\n  {C.SUCCESS}┌── TEMUAN DI {dex_name.upper()} ──────────{C.RESET}")
            for line in res.strip().split('\n'):
                line_clean = line.strip()
                real_reg = get_reg(line_clean)
                print(f"  {C.MAGENTA}│ [GUIDE]: const/4 {real_reg}, 0x1{C.RESET}")
                print(f"  {C.SUCCESS}│ {C.TEXT}» {line_clean[:width-15]}{C.RESET}")
                print(f"  {C.DIM}│ ------------------------------------{C.RESET}")
            print(f"  {C.SUCCESS}└── [SIAP DIEKSEKUSI DI MT MANAGER] ─────{C.RESET}")
    print("\r" + " " * 30 + "\r", end="")
    if not found_total: print(f"{C.ERROR}[!] NEGATIF. Tidak ditemukan keyword VIP standar.{C.RESET}")
    print(f"{C.TEXT}{'─' * width}{C.RESET}")

# 13. FLUTTER EXTRACTOR
def run_p13(apk):
    width = get_width()
    print_header("HADI FLUTTER EXTRACTOR v1.1")
    ai_desc("Mengekstrak Binary .so untuk melihat Offset Hex.")
    find_libs = f"unzip -l '{apk}' | grep -E 'libapp.so|libflutter.so' | awk '{{print $4}}' | head -n 1"
    target_path = subprocess.run(find_libs, shell=True, capture_output=True, text=True).stdout.strip()
    if not target_path:
        print(f"{C.ERROR}[!] GAGAL: File .so tidak ditemukan.{C.RESET}"); return
    subprocess.run(f"unzip -o '{apk}' '{target_path}'", shell=True, capture_output=True)
    base_name = os.path.basename(target_path)
    if target_path != base_name and os.path.exists(target_path): shutil.copy2(target_path, base_name)
    print(f"\n{C.WARN}   [ HEX OFFSET ]   │   [ STRING VALUE ]{C.RESET}")
    cmd = f"strings -t x '{base_name}' | grep -iE 'premium|vip|subscription' | head -n 20"
    final = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    if final:
        for line in final.strip().split('\n'):
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2: print(f"   {C.WARN}{parts[0]:>10}       {C.DIM}│{C.TEXT}   {parts[1][:width-25]}{C.RESET}")
    if os.path.exists(base_name): os.remove(base_name)
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
# --- PATCHING LOGIC (1-9) ---
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
        print_info("Nuking Ads & Dialogs (15 Targets)...")
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
                        if mode == 1: c = re.sub(r"(isVip|isPremium).*", r"const/4 v0, 0x1\n    return v0", c)
                        elif mode == 2: c = c.replace("verifySignature", "nexusBypass")
                        elif mode == 3 and "checkServerTrusted" in c: c = "    return-void\n"
                        elif mode == 4: c = c.replace("if-eqz v0,", "if-nez v0,")
                        elif mode == 5: c = c.replace("onAuthFailed", "onAuthSuccess")
                        
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
        # MODDING TOOLS (1-9)
        ("1", "VIP Bypass",      "Unlock Premium/Vip status"),
        ("2", "Signature Kill",  "Bypass Signature Check"),
        ("3", "SSL Unpinning",   "Disable SSL Pinning"),
        ("4", "Logic Flipper",   "Reverse Boolean Logic"),
        ("5", "Auth Force",      "Force Auth Success"),
        ("6", "Localizer",       "Translate Strings to ID"),
        ("7", "Master Nuke",     "Remove Ads & Dialogs"),
        ("8", "Flutter Mod",     "Patch Flutter Engine"),
        ("9", "OMEGA SCAN",      "Omega Deep 20-Lang Scanner"),
        # ANALYSIS TOOLS (10-17) - Adapted from Source 1
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
        
        is_mod = choice.isdigit() and 1 <= int(choice) <= 9
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

        # --- HANDLE MODDING TOOLS (1-9) ---
        idx = int(choice)
        work = "nexus_temp"; unsig = "unsig.apk"; final = f"MOD_{target_apk}"

        for f in [work, unsig, "aligned.apk"]:
            if os.path.exists(f):
                if os.path.isdir(f): shutil.rmtree(f)
                else: os.remove(f)

        stats = {'decompile': False, 'patches': 0, 'build': False, 'sign': False}

        # 1. DECOMPILE (PAKAI APKEDITOR)
        print()
        print_info("Decompiling APK (Using APKEditor Engine)...")
        cmd = f'java -jar APKEditor-1.4.3.jar d -i "{target_apk}" -o "{work}"'
        
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

        # 3. BUILD (PAKAI APKEDITOR)
        print()
        print_info("Building APK (Using APKEditor Engine)...")
        cmd = f'java -jar APKEditor-1.4.3.jar b -i "{work}" -o "{unsig}"'
        
        if os.system(f'{cmd} > /dev/null 2>&1') == 0:
            stats['build'] = True
            print_success("Build Successful!")
        else:
            print_error("Build Failed!")
            input(f"\n{C.GRAY}[ Press Enter ]{C.RESET}")
            continue

        # 4. SIGNING (PAKAI UBER SIGNER)
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