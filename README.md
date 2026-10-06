# windows-telegram-yonetim-script
windows bilgisayarınızı uzaktan kapatma, oturumu kapatma, ekranı kilitleme işlemlerini yapar. komutlar, telegram bot üzerinden verilir. scripte telegram bot tokenini ve chat id'nizi eklemeyi unutmayınız. python tabanlıdır.

## Kullanım
1. BotFather'dan bot tokeni alın, chat id'nizi öğrenin.
2. Windows'ta ortam değişkenlerini ayarlayın:
   `set TELEGRAM_BOT_TOKEN=...` ve `set TELEGRAM_CHAT_ID=...`
3. `python bot.py` çalıştırın. (Ek bağımlılık gerekmez, Python 3.8+.)

Botta komut menüsü görünür (`/kapat`, `/yenidenbaslat`, `/oturumukapat`, `/kilitle`, `/iptal`); `/start` ile butonlu menü açılır. Yalnızca belirtilen chat id'den gelen komutlar işlenir.
