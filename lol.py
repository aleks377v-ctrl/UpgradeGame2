import requests
import time
import random
import sys
import threading
from queue import Queue

print("="*60)
print("NIMBUS")
print("="*60)

TOKENS = [
    "MTUyNDAyMDEyNjI5NzM1ODQ3Nw.Gfejug.YySWHoI9_RgR2OK7fIdZvQwpFoTmYp24BzpKaA",
    "MTUyNDAyMDE1MzI1ODQ3NTcwNQ.GrtO1u.PWMpGp3ytelQkPpd0wC2KPduNX-llB_SIVrvPE",
    "MTUyNDAxOTkxNDg1ODQzMDU3OA.GvJuhw.qqKE_BRQFF23SiapvXL5q1ZOW1NowW02j4J-BU",
    "MTUyNDAyMDA2NTI5NTQwNTExNg.Gyqbx1.QjhEiiguZd0cKYACBqNUyosZZMKEiM6Fu3VWOQ",
    "MTUyNDAyMDEzMDE4NTYxMzQzMw.G_d6fr._QrCV_G3EWBuiISXQO4v8ErNAxJihxpeg35lC8",
    "MTUyNDAxOTc1ODA4MzczNTU1NA.GI7I3Y.8XgUQXwa2ARIzMQQ1RpYUAQ5VUn3W_IKrdk9qI",
    "MTUyNDAyMDE0MTMyMTM1OTQ4NA.GWsm0f.JGKi-O_lZh7eyHH1p76x93-xqB9rQKc-dhdi08",
    "MTUyNDAyMDE3MzUyMTI5MzM2Mg.GWlH44.zp21ozm7IWYurb_XT4hAIdsB0ggVq45AMak0d4"
]

SERVER_ID = "1433362426388156438"
NIMBUS_LINK = ""
RAID_DURATION = 600


SPAM_MESSAGES = [
    f"@everyone ",
    f"@everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2",
    f"@everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2",
    f"@everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2",
    f"@everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2 @everyone Цум 2 открылся залетайте - https://www.roblox.com/games/94414273154974/TSUM-2",
]


MANUAL_CHANNELS = [
    {"id": "1518345680970842343"},
    {"id": "1518348765004824636"},
]


def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = response.headers.get('retry-after')
        if retry_after:
            wait_time = float(retry_after) + 0.5  # Добавляем 0.5с запаса
            print(f"[!] Rate Limit. Sleeping {wait_time:.1f}s")
            time.sleep(wait_time)
            return True  
    return False


class UltraFastSpammer:

    def __init__(self):
        self.total_messages = 0
        self.start_time = time.time()
        self.running = True

    def worker(self, token, channel):
        session = requests.Session()
        session.headers.update({"Authorization": token})
        local_count = 0

        while self.running and time.time() - self.start_time < RAID_DURATION:
            time.sleep(random.uniform(0.2, 0.5))

            url = f"https://discord.com/api/v9/channels/{channel['id']}/messages"
            message = random.choice(SPAM_MESSAGES)
            data = {"content": message, "tts": False}

            try:
                response = session.post(url, json=data, timeout=3)  

                if handle_rate_limit(response):
                    continue  

                if response.status_code == 200:
                    local_count += 1
                    self.total_messages += 1

                    if self.total_messages % 50 == 0:
                        elapsed = time.time() - self.start_time
                        speed = self.total_messages / max(elapsed, 0.1)
                        print(f"{self.total_messages} | {speed:.1f}/сек (от всех 12 аккаунтов)", end='\r')

                elif response.status_code >= 400:
                    time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                time.sleep(1)  
                continue

        print(f"   Аккаунт {token[:10]}... завершил в канале {channel['id']}: ~{local_count}")

    def start(self):
        print(f"\nЗАПУСК ")


        threads = []
        for token in TOKENS:
            for channel in MANUAL_CHANNELS:
                t = threading.Thread(target=self.worker, args=(token, channel))
                t.daemon = True
                t.start()
                threads.append(t)

        while time.time() - self.start_time < RAID_DURATION:
            time.sleep(0.1)
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed = self.total_messages / elapsed
                print(f"{self.total_messages} сообщений | {speed:.1f}/сек | {RAID_DURATION - elapsed:.0f}с осталось", end='\r')

        self.running = False
        time.sleep(1)

        return self.total_messages


def main():
    print("Быстрая проверка первого аккаунта...")
    try:
        r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": TOKENS[0]}, timeout=3)
        if r.status_code == 200:
            print(f"Аккаунт готов: {r.json()['username']}")
        else:
            print("Первый токен мёртв, но продолжаем...")
    except:
        print("Пропускаю проверку")

    print(f"📊 Использую 5 ручных каналов — все 12 аккаунты будут спамить в каждый")


    input("\nEnter")

    start_time = time.time()
    spammer = UltraFastSpammer()
    total_messages = spammer.start()


    # Финальная статистика
    total_time = time.time() - start_time


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nОтменено")
    except Exception as e:
        print(f"\nОшибка: {e}")