#!/usr/bin/env python3
import os, sys, subprocess, shutil, re, time, threading, signal
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
    print(f"\033[36m[*] Checking Environment (PairIP Engine)...\033[0m")
    
    # 1. Check Java
    if not shutil.which("java"):
        print("\033[31m[!] ERROR: Java not found!\033[0m")
        print("Please install Java in Termux:")
        print("  pkg install openjdk-17")
        return False
    
    # 2. Check APKEditor (Engine Utama)
    if not os.path.exists("APKEditor-1.4.3.jar"):
        print("\033[31m[!] ERROR: APKEditor-1.4.3.jar not found!\033[0m")
        print("Download: wget https://github.com/ReAndroid/APKEditor/releases/download/v1.4.3/APKEditor-1.4.3.jar -O APKEditor-1.4.3.jar")
        return False

    # 3. Check Uber APK Signer (Engine Signing)
    if not os.path.exists("uber-apk-signer.jar"):
        print("\033[31m[!] ERROR: uber-apk-signer.jar not found!\033[0m")
        print("Download: wget https://github.com/patrickfav/uber-apk-signer/releases/download/v1.3.0/uber-apk-signer-1.3.0.jar -O uber-apk-signer.jar")
        return False

    print("\033[32m[+] Environment OK. Engine: APKEditor & UberSigner\033[0m")
    return True

# --- COLOR PALETTE ---
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    BLACK   = "\033[30m"
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
    
    # MODE 9: OMEGA DEEP SCAN
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

    # MODE 7: MASTER NUKE
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
        ("1", "VIP Bypass",      "Unlock Premium/Vip status"),
        ("2", "Signature Kill",  "Bypass Signature Check"),
        ("3", "SSL Unpinning",   "Disable SSL Pinning"),
        ("4", "Logic Flipper",   "Reverse Boolean Logic"),
        ("5", "Auth Force",      "Force Auth Success"),
        ("6", "Localizer",       "Translate Strings to ID"),
        ("7", "Master Nuke",     "Remove Ads & Dialogs"),
        ("8", "Flutter Mod",     "Patch Flutter Engine"),
        ("9", "OMEGA SCAN",      "Omega Deep 20-Lang Scanner"),
    ]

    lines = []
    for num, name, desc in menu_items:
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
        if not choice.isdigit() or int(choice) not in range(1, 10):
            print(f"\n{C.ERROR}[!] Invalid Option{C.RESET}")
            time.sleep(1)
            continue

        target_apk = select_file()
        if not target_apk:
            print_error("No file selected or invalid.")
            time.sleep(1)
            continue

        idx = int(choice)
        work = "nexus_temp"; unsig = "unsig.apk"; final = f"MOD_{target_apk}"

        # Bersihkan folder lama
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
