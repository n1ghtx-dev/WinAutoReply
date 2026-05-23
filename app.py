import sys, os, subprocess, threading, asyncio, json, time
import tkinter as tk
from tkinter import ttk

                                                                                
TG_API_ID   = 2496
TG_API_HASH = "8da85b0d5bfe62527e5b244c209159c3"

                                                                               
def _user_data_dir() -> str:
    """Возвращает путь к папке Documents текущего пользователя."""
    if sys.platform == "win32":
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 0, buf)
        base = buf.value or os.path.expanduser("~/Documents")
    else:
                                                     
        for candidate in ("Документы", "Documents"):
            p = os.path.join(os.path.expanduser("~"), candidate)
            if os.path.isdir(p):
                base = p
                break
        else:
            base = os.path.expanduser("~")
    folder = os.path.join(base, "AutoReply")
    os.makedirs(folder, exist_ok=True)
    return folder

DATA_DIR    = _user_data_dir()
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
SESSION     = os.path.join(DATA_DIR, "session")

                                                                                
C = {
    "bg":      "#0D0D0D",
    "surface": "#161616",
    "card":    "#1E1E1E",
    "border":  "#2A2A2A",
    "accent":  "#FFFFFF",
    "dim":     "#555555",
    "text":    "#EEEEEE",
    "sub":     "#666666",
    "ok":      "#4CAF50",
    "err":     "#F44336",
    "entry":   "#111111",
}

PACKAGES = [("telethon", "telethon")]

                                                                                
def load_cfg():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_cfg(d):
    with open(CONFIG_FILE, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def pkg_ok(name):
    try:
        __import__(name)
        return True
    except ImportError:
        return False

def install_pkg(pip_name, cb=None):
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name,
             "--break-system-packages", "-q"],
            capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0
        if cb: cb(ok, pip_name + (" ✓" if ok else " ✗"))
    except Exception as e:
        if cb: cb(False, f"{pip_name} ✗ {e}")

                                                                                
                   
                                                                                
class Page(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=C["bg"])
        self.app = app

    def on_show(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _build(self):
        pass

                                                                               
    def lbl(self, p, text, size=12, color=None, bold=False, **kw):
        return tk.Label(p, text=text, bg=kw.pop("bg", C["bg"]),
                        fg=color or C["text"],
                        font=("Segoe UI", size, "bold" if bold else "normal"), **kw)

    def entry(self, p, show="", size=14):
        e = tk.Entry(p, bg=C["entry"], fg=C["text"],
                     insertbackground=C["accent"],
                     relief="flat", font=("Segoe UI", size),
                     highlightthickness=1,
                     highlightbackground=C["border"],
                     highlightcolor=C["accent"],
                     show=show, bd=0)
        return e

    def btn(self, p, text, cmd, fg=None, bg=None, size=12):
        return tk.Button(p, text=text, command=cmd,
                         bg=bg or C["card"],
                         fg=fg or C["text"],
                         activebackground=C["border"],
                         activeforeground=C["text"],
                         relief="flat", font=("Segoe UI", size),
                         cursor="hand2", bd=0,
                         highlightthickness=1,
                         highlightbackground=C["border"])

    def divider(self, p):
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", pady=12)

    def back_btn(self, p, target):
        tk.Button(p, text="←", command=lambda: self.app.go(target),
                  bg=C["bg"], fg=C["dim"],
                  activebackground=C["bg"], activeforeground=C["text"],
                  relief="flat", font=("Segoe UI", 16),
                  cursor="hand2", bd=0).pack(anchor="w", pady=(0, 8))

                                                                                
                   
                                                                                
class SplashPage(Page):
    def _build(self):
        c = tk.Frame(self, bg=C["bg"])
        c.place(relx=.5, rely=.5, anchor="center")

        tk.Label(c, text="◈", font=("Segoe UI", 56),
                 bg=C["bg"], fg=C["accent"]).pack()
        tk.Label(c, text="AutoReply", font=("Segoe UI", 30, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(4, 2))
        tk.Label(c, text="WinDev Studio  ×  n1ghtxxxxx",
                 font=("Segoe UI", 10),
                 bg=C["bg"], fg=C["sub"]).pack()

        tk.Frame(c, bg=C["border"], height=1, width=280).pack(pady=20)

        msg = (
            "Ваши данные не передаются на сторонние серверы.\n"
            "Всё хранится только на вашем устройстве."
        )
        tk.Label(c, text=msg, font=("Segoe UI", 10),
                 bg=C["bg"], fg=C["sub"], justify="center").pack(pady=(0, 24))

                  
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("W.Horizontal.TProgressbar",
                        troughcolor=C["surface"],
                        background=C["accent"],
                        bordercolor=C["surface"],
                        lightcolor=C["accent"],
                        darkcolor=C["dim"])
        self._pb = ttk.Progressbar(c, style="W.Horizontal.TProgressbar",
                                   length=280, mode="determinate")
        self._pb.pack()
        self._tlbl = tk.Label(c, text="", font=("Segoe UI", 9),
                              bg=C["bg"], fg=C["sub"])
        self._tlbl.pack(pady=(6, 0))

        self._t0 = time.time()
        self._tick()

    def _tick(self):
        e = time.time() - self._t0
        self._pb["value"] = min(e / 6 * 100, 100)
        self._tlbl.configure(text=f"{max(0, 6-e):.1f} с")
        if e < 6:
            self.after(50, self._tick)
        else:
            self.app.go("loader")

                                                                                
            
                                                                                
class LoaderPage(Page):
    def _build(self):
        c = tk.Frame(self, bg=C["bg"])
        c.place(relx=.5, rely=.5, anchor="center")

        tk.Label(c, text="Загрузка компонентов",
                 font=("Segoe UI", 18, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(0, 4))
        tk.Label(c, text="Проверяем зависимости...",
                 font=("Segoe UI", 10),
                 bg=C["bg"], fg=C["sub"]).pack(pady=(0, 18))

             
        wrap = tk.Frame(c, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        wrap.pack(pady=(0, 14))
        self._log = tk.Text(wrap, width=50, height=8,
                            bg=C["entry"], fg=C["text"],
                            font=("Consolas", 10), relief="flat",
                            state="disabled", bd=0)
        self._log.pack(padx=1, pady=1)

        style = ttk.Style()
        style.configure("W.Horizontal.TProgressbar",
                        troughcolor=C["surface"],
                        background=C["accent"],
                        bordercolor=C["surface"],
                        lightcolor=C["accent"],
                        darkcolor=C["dim"])
        self._pb = ttk.Progressbar(c, style="W.Horizontal.TProgressbar",
                                   length=420, mode="determinate")
        self._pb.pack(pady=(0, 8))

        self._st = tk.Label(c, text="", font=("Segoe UI", 10),
                            bg=C["bg"], fg=C["sub"])
        self._st.pack()

        self._cont = tk.Button(c, text="Продолжить →",
                               command=lambda: self.app.go("phone"),
                               bg=C["card"], fg=C["text"],
                               activebackground=C["border"],
                               relief="flat", font=("Segoe UI", 12),
                               cursor="hand2", bd=0,
                               highlightthickness=1,
                               highlightbackground=C["border"],
                               pady=8, padx=20)

                           
        self._nopy = tk.Frame(c, bg=C["bg"])
        tk.Label(self._nopy, text="Python не найден",
                 font=("Segoe UI", 13, "bold"),
                 bg=C["bg"], fg=C["err"]).pack()
        tk.Label(self._nopy, text="Скачай Python 3.12:",
                 font=("Segoe UI", 10),
                 bg=C["bg"], fg=C["sub"]).pack(pady=(4, 2))
        lnk = tk.Label(self._nopy, text="python.org/downloads",
                       font=("Segoe UI", 10, "underline"),
                       bg=C["bg"], fg=C["text"], cursor="hand2")
        lnk.pack()
        lnk.bind("<Button-1>", lambda e: __import__("webbrowser").open(
            "https://www.python.org/downloads/"))
        tk.Label(self._nopy, text="После установки перезапусти приложение.",
                 font=("Segoe UI", 9),
                 bg=C["bg"], fg=C["sub"]).pack(pady=(6, 0))

        if sys.version_info < (3, 8):
            self._addlog("✗ Python 3.8+ не найден")
            self._st.configure(text="Требуется Python 3.8+", fg=C["err"])
            self._nopy.pack(pady=(16, 0))
        else:
            self._addlog(f"✓ Python {sys.version.split()[0]}")
            threading.Thread(target=self._run, daemon=True).start()

    def _addlog(self, msg):
        def _do():
            self._log.configure(state="normal")
            self._log.insert("end", msg + "\n")
            self._log.see("end")
            self._log.configure(state="disabled")
        self.after(0, _do)

    def _run(self):
        all_ok = True
        for i, (imp, pip) in enumerate(PACKAGES):
            self.after(0, lambda p=pip: self._st.configure(
                text=f"Проверяем {p}...", fg=C["sub"]))
            if pkg_ok(imp):
                self._addlog(f"✓ {pip}")
            else:
                self._addlog(f"↓ Устанавливаем {pip}...")
                ev = threading.Event()
                res = [True]
                def cb(ok, msg, _ev=ev, _res=res):
                    _res[0] = ok
                    self._addlog(msg)
                    _ev.set()
                install_pkg(pip, cb)
                ev.wait()
                if not res[0]:
                    all_ok = False
            self.after(0, lambda p=(i+1)/len(PACKAGES)*100:
                       self._pb.configure(value=p))
            time.sleep(0.2)

        if all_ok:
            self._addlog("\n✓ Готово")
            self.after(0, lambda: self._st.configure(text="Готово", fg=C["ok"]))
        else:
            self._addlog("\n⚠ Ошибка установки")
            self.after(0, lambda: self._st.configure(
                text="Ошибка. Запусти от администратора.", fg=C["err"]))
        self.after(0, lambda: self._cont.pack(pady=(14, 0)))

                                                                                
              
                                                                                
class PhonePage(Page):
    def _build(self):
        c = tk.Frame(self, bg=C["bg"])
        c.place(relx=.5, rely=.5, anchor="center")

        tk.Label(c, text="Telegram", font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(0, 4))
        tk.Label(c, text="Введи номер телефона",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["sub"]).pack(pady=(0, 24))

              
        wrap = tk.Frame(c, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        wrap.pack(fill="x", ipadx=24, ipady=20)

        tk.Label(wrap, text="Номер телефона",
                 font=("Segoe UI", 10), bg=C["card"], fg=C["sub"]).pack(
                     anchor="w", padx=20, pady=(16, 4))

        self._ph = tk.Entry(wrap, bg=C["entry"], fg=C["text"],
                            insertbackground=C["accent"],
                            relief="flat", font=("Segoe UI", 18),
                            highlightthickness=1,
                            highlightbackground=C["border"],
                            highlightcolor=C["accent"],
                            bd=0, justify="center")
        self._ph.pack(fill="x", padx=20, ipady=10)

        cfg = load_cfg()
        if cfg.get("phone"):
            self._ph.insert(0, cfg["phone"])

        self._err = tk.Label(wrap, text="", font=("Segoe UI", 9),
                             bg=C["card"], fg=C["err"])
        self._err.pack(pady=(4, 0))

        self._btn = tk.Button(wrap, text="Получить код",
                              command=self._next,
                              bg=C["accent"], fg=C["bg"],
                              activebackground=C["dim"],
                              activeforeground=C["bg"],
                              relief="flat", font=("Segoe UI", 12, "bold"),
                              cursor="hand2", bd=0, pady=10)
        self._btn.pack(fill="x", padx=20, pady=(12, 20))

        self._ph.bind("<Return>", lambda e: self._next())

    def _next(self):
        phone = self._ph.get().strip()
        if not phone.startswith("+") or len(phone) < 8:
            self._err.configure(text="Формат: +7XXXXXXXXXX")
            return
        self._err.configure(text="")
        self._btn.configure(state="disabled", text="Отправляем...")

        cfg = load_cfg()
        cfg["phone"] = phone
        save_cfg(cfg)
        self.app.tg_phone = phone

        threading.Thread(target=self._send, args=(phone,), daemon=True).start()

    def _send(self, phone):
        from telethon import TelegramClient
        loop = self.app.loop

        async def _do():
            try:
                if self.app.client is None:
                    self.app.client = TelegramClient(
                        SESSION, TG_API_ID, TG_API_HASH, loop=loop)
                await self.app.client.connect()
                if await self.app.client.is_user_authorized():
                    self.after(0, lambda: self.app.go("profile"))
                    return
                sent = await self.app.client.send_code_request(phone)
                self.app.tg_phone_hash = sent.phone_code_hash
                self.after(0, lambda: self.app.go("code"))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._err.configure(text=msg[:60]))
                self.after(0, lambda: self._btn.configure(
                    state="normal", text="Получить код"))
        asyncio.run_coroutine_threadsafe(_do(), loop)

                                                                                
            
                                                                                
class CodePage(Page):
    def _build(self):
        c = tk.Frame(self, bg=C["bg"])
        c.place(relx=.5, rely=.5, anchor="center")

        self.back_btn(c, "phone")

        tk.Label(c, text="Код подтверждения",
                 font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(0, 4))
        tk.Label(c, text="Telegram отправил тебе код",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["sub"]).pack(pady=(0, 24))

        wrap = tk.Frame(c, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        wrap.pack(fill="x", ipadx=24, ipady=20)

        tk.Label(wrap, text="Код из Telegram",
                 font=("Segoe UI", 10), bg=C["card"], fg=C["sub"]).pack(
                     anchor="w", padx=20, pady=(16, 4))

        self._code = tk.Entry(wrap, bg=C["entry"], fg=C["text"],
                              insertbackground=C["accent"],
                              relief="flat", font=("Segoe UI", 24),
                              highlightthickness=1,
                              highlightbackground=C["border"],
                              highlightcolor=C["accent"],
                              bd=0, justify="center")
        self._code.pack(fill="x", padx=20, ipady=12)
        self._code.focus_set()

        self._err = tk.Label(wrap, text="", font=("Segoe UI", 9),
                             bg=C["card"], fg=C["err"])
        self._err.pack(pady=(4, 0))

        self._btn = tk.Button(wrap, text="Подтвердить",
                              command=self._confirm,
                              bg=C["accent"], fg=C["bg"],
                              activebackground=C["dim"],
                              activeforeground=C["bg"],
                              relief="flat", font=("Segoe UI", 12, "bold"),
                              cursor="hand2", bd=0, pady=10)
        self._btn.pack(fill="x", padx=20, pady=(12, 20))

        self._code.bind("<Return>", lambda e: self._confirm())

    def _confirm(self):
        code = self._code.get().strip()
        if not code:
            self._err.configure(text="Введи код")
            return
        self._btn.configure(state="disabled", text="Проверяем...")
        threading.Thread(target=self._verify, args=(code,), daemon=True).start()

    def _verify(self, code):
        from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
        loop = self.app.loop

        async def _do():
            try:
                await self.app.client.sign_in(
                    self.app.tg_phone, code,
                    phone_code_hash=getattr(self.app, "tg_phone_hash", None))
                self.after(0, lambda: self.app.go("profile"))
            except SessionPasswordNeededError:
                self.after(0, lambda: self.app.go("twofa"))
            except PhoneCodeInvalidError:
                self.after(0, lambda: self._err.configure(text="Неверный код"))
                self.after(0, lambda: self._btn.configure(
                    state="normal", text="Подтвердить"))
            except Exception as e:
                self.after(0, lambda: self._err.configure(text=str(e)[:60]))
                self.after(0, lambda: self._btn.configure(
                    state="normal", text="Подтвердить"))
        asyncio.run_coroutine_threadsafe(_do(), loop)

                                                                                
      
                                                                                
class TwoFAPage(Page):
    def _build(self):
        c = tk.Frame(self, bg=C["bg"])
        c.place(relx=.5, rely=.5, anchor="center")

        tk.Label(c, text="Двухфакторная защита",
                 font=("Segoe UI", 22, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(pady=(0, 4))
        tk.Label(c, text="Введи пароль 2FA",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["sub"]).pack(pady=(0, 24))

        wrap = tk.Frame(c, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        wrap.pack(fill="x", ipadx=24, ipady=20)

        tk.Label(wrap, text="Пароль",
                 font=("Segoe UI", 10), bg=C["card"], fg=C["sub"]).pack(
                     anchor="w", padx=20, pady=(16, 4))

        self._pw = tk.Entry(wrap, bg=C["entry"], fg=C["text"],
                            insertbackground=C["accent"],
                            relief="flat", font=("Segoe UI", 18),
                            highlightthickness=1,
                            highlightbackground=C["border"],
                            highlightcolor=C["accent"],
                            bd=0, justify="center", show="●")
        self._pw.pack(fill="x", padx=20, ipady=10)
        self._pw.focus_set()

        self._err = tk.Label(wrap, text="", font=("Segoe UI", 9),
                             bg=C["card"], fg=C["err"])
        self._err.pack(pady=(4, 0))

        self._btn = tk.Button(wrap, text="Войти",
                              command=self._login,
                              bg=C["accent"], fg=C["bg"],
                              activebackground=C["dim"],
                              activeforeground=C["bg"],
                              relief="flat", font=("Segoe UI", 12, "bold"),
                              cursor="hand2", bd=0, pady=10)
        self._btn.pack(fill="x", padx=20, pady=(12, 20))

        self._pw.bind("<Return>", lambda e: self._login())

    def _login(self):
        pw = self._pw.get().strip()
        if not pw:
            self._err.configure(text="Введи пароль")
            return
        self._btn.configure(state="disabled", text="Входим...")
        threading.Thread(target=self._do, args=(pw,), daemon=True).start()

    def _do(self, pw):
        async def _run():
            try:
                await self.app.client.sign_in(password=pw)
                self.after(0, lambda: self.app.go("profile"))
            except Exception as e:
                self.after(0, lambda: self._err.configure(text=str(e)[:60]))
                self.after(0, lambda: self._btn.configure(
                    state="normal", text="Войти"))
        asyncio.run_coroutine_threadsafe(_run(), self.app.loop)

                                                                                
                      
                                                                                
class ProfilePage(Page):
    def _build(self):
        self._running = False
        self._replied: set = set()
        self._count = 0
        self._handler_set = False

               
        bar = tk.Frame(self, bg=C["surface"], height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="AutoReply", font=("Segoe UI", 13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left", padx=20)
        self._dot = tk.Label(bar, text="● offline",
                             font=("Segoe UI", 10),
                             bg=C["surface"], fg=C["sub"])
        self._dot.pack(side="right", padx=20)

                 
        main = tk.Frame(self, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=28, pady=20)

                 
        prof = tk.Frame(main, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        prof.pack(fill="x", pady=(0, 20))
        row = tk.Frame(prof, bg=C["card"])
        row.pack(padx=20, pady=16, anchor="w")
        tk.Label(row, text="◉", font=("Segoe UI", 28),
                 bg=C["card"], fg=C["dim"]).pack(side="left", padx=(0, 12))
        info = tk.Frame(row, bg=C["card"])
        info.pack(side="left")
        self._name = tk.Label(info, text="Загрузка...",
                              font=("Segoe UI", 14, "bold"),
                              bg=C["card"], fg=C["text"])
        self._name.pack(anchor="w")
        self._uname = tk.Label(info, text="",
                               font=("Segoe UI", 10),
                               bg=C["card"], fg=C["sub"])
        self._uname.pack(anchor="w")

                          
        tk.Label(main, text="Текст автоответа",
                 font=("Segoe UI", 10), bg=C["bg"], fg=C["sub"]).pack(
                     anchor="w", pady=(0, 6))

        self._txt = tk.Text(main, height=5,
                            bg=C["card"], fg=C["text"],
                            insertbackground=C["accent"],
                            relief="flat", font=("Segoe UI", 12),
                            highlightthickness=1,
                            highlightbackground=C["border"],
                            highlightcolor=C["accent"],
                            wrap="word", bd=0,
                            padx=12, pady=10)
        self._txt.pack(fill="x", pady=(0, 16))

        cfg = load_cfg()
        if cfg.get("reply"):
            self._txt.insert("1.0", cfg["reply"])

                
        row2 = tk.Frame(main, bg=C["bg"])
        row2.pack(fill="x", pady=(0, 12))

        self._start_btn = tk.Button(row2, text="Запустить",
                                    command=self._toggle,
                                    bg=C["accent"], fg=C["bg"],
                                    activebackground=C["dim"],
                                    activeforeground=C["bg"],
                                    relief="flat", font=("Segoe UI", 12, "bold"),
                                    cursor="hand2", bd=0, pady=10)
        self._start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        tk.Button(row2, text="Выйти", command=self._logout,
                  bg=C["card"], fg=C["sub"],
                  activebackground=C["border"],
                  relief="flat", font=("Segoe UI", 11),
                  cursor="hand2", bd=0,
                  highlightthickness=1,
                  highlightbackground=C["border"],
                  pady=10, padx=16).pack(side="right")

        self._cnt = tk.Label(main, text="Ответов: 0",
                             font=("Segoe UI", 10),
                             bg=C["bg"], fg=C["sub"])
        self._cnt.pack(anchor="w")

                           
        threading.Thread(target=self._load_me, daemon=True).start()

    def _load_me(self):
        async def _do():
            try:
                me = await self.app.client.get_me()
                name = f"{me.first_name or ''} {me.last_name or ''}".strip()
                un = f"@{me.username}" if me.username else f"+{me.phone}"
                self.after(0, lambda: self._name.configure(text=name))
                self.after(0, lambda: self._uname.configure(text=un))
                self.after(0, lambda: self._dot.configure(
                    text="● online", fg=C["ok"]))
            except Exception:
                pass
        asyncio.run_coroutine_threadsafe(_do(), self.app.loop)

    def _toggle(self):
        reply = self._txt.get("1.0", "end").strip()
        if not reply:
            return
        cfg = load_cfg()
        cfg["reply"] = reply
        save_cfg(cfg)
        self._reply_text = reply

        if self._running:
            self._running = False
            self._start_btn.configure(text="Запустить", bg=C["accent"], fg=C["bg"])
            self._dot.configure(text="● online", fg=C["ok"])
        else:
            self._running = True
            self._replied.clear()
            self._count = 0
            self._cnt.configure(text="Ответов: 0")
            self._start_btn.configure(text="Остановить", bg=C["err"], fg=C["text"])
            self._dot.configure(text="● автоответ активен", fg=C["accent"])
            if not self._handler_set:
                self._handler_set = True
                asyncio.run_coroutine_threadsafe(
                    self._register(), self.app.loop)

    async def _register(self):
        from telethon import events

        @self.app.client.on(events.NewMessage(incoming=True))
        async def _h(event):
            if not self._running or not event.is_private:
                return
            try:
                sender = await event.get_sender()
            except Exception:
                return
            if getattr(sender, "bot", False):
                return
            uid = sender.id
            if uid not in self._replied:
                self._replied.add(uid)
                try:
                    await event.reply(self._reply_text)
                    self._count += 1
                    n = self._count
                    self.after(0, lambda c=n: self._cnt.configure(
                        text=f"Ответов: {c}"))
                except Exception:
                    pass

                           
        while self.app.client and self.app.client.is_connected():
            await asyncio.sleep(20)

    def _logout(self):
        async def _do():
            try:
                await self.app.client.log_out()
            except Exception:
                pass
            self.app.client = None
        asyncio.run_coroutine_threadsafe(_do(), self.app.loop)
        self.app.go("phone")

                                                                                
             
                                                                                
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoReply")
        self.geometry("480x580")
        self.resizable(False, False)
        self.configure(bg=C["bg"])

        self.client = None
        self.tg_phone = ""
        self.tg_phone_hash = None

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=lambda: (
            asyncio.set_event_loop(self.loop),
            self.loop.run_forever()
        ), daemon=True).start()

        cont = tk.Frame(self, bg=C["bg"])
        cont.place(relwidth=1, relheight=1)

        self._pages: dict[str, Page] = {}
        for key, cls in [
            ("splash",  SplashPage),
            ("loader",  LoaderPage),
            ("phone",   PhonePage),
            ("code",    CodePage),
            ("twofa",   TwoFAPage),
            ("profile", ProfilePage),
        ]:
            p = cls(cont, self)
            p.place(relwidth=1, relheight=1)
            self._pages[key] = p

        self.go("splash")
        self.protocol("WM_DELETE_WINDOW", self._quit)

    def go(self, key: str):
        p = self._pages[key]
        p.tkraise()
        p.on_show()

    def _quit(self):
        if self.client:
            asyncio.run_coroutine_threadsafe(
                self.client.disconnect(), self.loop)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.destroy()

if __name__ == "__main__":
    App().mainloop()
