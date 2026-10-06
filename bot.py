"""Windows Telegram yönetim botu: kapat, yeniden başlat, oturumu kapat, ekranı kilitle.

Gerekli ortam değişkenleri: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
Sadece standart kütüphane kullanır.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

COMMANDS = {
    "kapat": ("Bilgisayarı kapat", ["shutdown", "/s", "/t", "5"]),
    "yenidenbaslat": ("Bilgisayarı yeniden başlat", ["shutdown", "/r", "/t", "5"]),
    "oturumukapat": ("Oturumu kapat", ["shutdown", "/l"]),
    "kilitle": ("Ekranı kilitle", ["rundll32.exe", "user32.dll,LockWorkStation"]),
    "iptal": ("Bekleyen kapatma/yeniden başlatmayı iptal et", ["shutdown", "/a"]),
}


def load_config(env=None):
    env = os.environ if env is None else env
    token = env.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = env.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID ortam değişkenleri zorunludur."
        )
    return token, chat_id


class Bot:
    def __init__(self, token, chat_id):
        self.base = f"https://api.telegram.org/bot{token}/"
        self.chat_id = str(chat_id)

    def api(self, method, **params):
        data = urllib.parse.urlencode(
            {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in params.items()}
        ).encode()
        with urllib.request.urlopen(self.base + method, data, timeout=70) as r:
            return json.load(r)["result"]

    def setup_commands(self):
        cmds = [{"command": "start", "description": "Menüyü göster"}]
        cmds += [{"command": k, "description": v[0]} for k, v in COMMANDS.items()]
        self.api("setMyCommands", commands=cmds)

    def send_menu(self):
        keyboard = [[{"text": v[0], "callback_data": k}] for k, v in COMMANDS.items()]
        self.api("sendMessage", chat_id=self.chat_id, text="Bir işlem seçin:",
                 reply_markup={"inline_keyboard": keyboard})

    def run_action(self, name):
        label, cmd = COMMANDS[name]
        if sys.platform != "win32":
            self.say(f"{label}: Bu bot yalnızca Windows'ta çalışır.")
            return
        self.say(f"{label} işlemi gerçekleştiriliyor...")
        subprocess.run(cmd, check=False)

    def say(self, text):
        self.api("sendMessage", chat_id=self.chat_id, text=text)

    def handle(self, update):
        cb = update.get("callback_query")
        msg = update.get("message")
        if cb:
            chat = str(cb["message"]["chat"]["id"]) if cb.get("message") else ""
            if chat != self.chat_id:
                return
            self.api("answerCallbackQuery", callback_query_id=cb["id"])
            name = cb.get("data")
        elif msg:
            if str(msg["chat"]["id"]) != self.chat_id:
                return
            text = (msg.get("text") or "").strip()
            if not text.startswith("/"):
                return
            name = text[1:].split()[0].split("@")[0].lower()
            if name in ("start", "menu"):
                self.send_menu()
                return
        else:
            return
        if name in COMMANDS:
            self.run_action(name)

    def run(self):
        self.setup_commands()
        self.send_menu()
        offset = None
        while True:
            try:
                params = {"timeout": 50}
                if offset is not None:
                    params["offset"] = offset
                for upd in self.api("getUpdates", **params):
                    offset = upd["update_id"] + 1
                    self.handle(upd)
            except (urllib.error.URLError, OSError, ValueError):
                time.sleep(5)


if __name__ == "__main__":
    Bot(*load_config()).run()
