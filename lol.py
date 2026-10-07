import requests
import time
import random
import sys
import threading
from queue import Queue

print("="*60)
print("TEST HARNESS")
print("="*60)

# Тестовые учётные данные (замени на свои)
AUTH_KEYS = [
    "TEST_KEY_01",
    "TEST_KEY_02",
    "TEST_KEY_03",
    "TEST_KEY_04",
    "TEST_KEY_05",
    "TEST_KEY_06",
    "TEST_KEY_07",
    "TEST_KEY_08"
]

TARGET_ID = "000000000000000000"
TEST_LINK = ""
TEST_DURATION = 600

# Тестовые payload'ы для проверки нагрузки
TEST_PAYLOADS = [
    "test_message_1",
    "test_message_2",
    "test_message_3",
    "test_message_4",
    "test_message_5",
]

# Целевые эндпоинты (тестовые)
TARGET_ENDPOINTS = [
    {"id": "0000000000000000001"},
    {"id": "0000000000000000002"},
]


def handle_backoff(response):
    if response.status_code == 429:
        retry_after = response.headers.get('retry-after')
        if retry_after:
            wait_time = float(retry_after) + 0.5
            print(f"[!] Backoff. Sleeping {wait_time:.1f}s")
            time.sleep(wait_time)
            return True
    return False


class LoadTester:

    def __init__(self):
        self.total_requests = 0
        self.start_time = time.time()
        self.running = True

    def worker(self, auth_key, endpoint):
        session = requests.Session()
        session.headers.update({"Authorization": auth_key})
        local_count = 0

        while self.running and time.time() - self.start_time < TEST_DURATION:
            time.sleep(random.uniform(0.2, 0.5))

            url = f"https://example.com/api/v1/endpoints/{endpoint['id']}/items"
            payload = random.choice(TEST_PAYLOADS)
            data = {"content": payload, "tts": False}

            try:
                response = session.post(url, json=data, timeout=3)

                if handle_backoff(response):
                    continue

                if response.status_code == 200:
                    local_count += 1
                    self.total_requests += 1

                    if self.total_requests % 50 == 0:
                        elapsed = time.time() - self.start_time
                        speed = self.total_requests / max(elapsed, 0.1)
                        print(f"{self.total_requests} | {speed:.1f}/sec", end='\r')

                elif response.status_code >= 400:
                    time.sleep(0.5)

            except requests.exceptions.RequestException:
                time.sleep(1)
                continue

        print(f"   Worker {auth_key[:10]}... done on {endpoint['id']}: ~{local_count}")

    def start(self):
        print(f"\nSTART")

        threads = []
        for auth_key in AUTH_KEYS:
            for endpoint in TARGET_ENDPOINTS:
                t = threading.Thread(target=self.worker, args=(auth_key, endpoint))
                t.daemon = True
                t.start()
                threads.append(t)

        while time.time() - self.start_time < TEST_DURATION:
            time.sleep(0.1)
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed = self.total_requests / elapsed
                print(f"{self.total_requests} requests | {speed:.1f}/sec | {TEST_DURATION - elapsed:.0f}s left", end='\r')

        self.running = False
        time.sleep(1)

        return self.total_requests


def main():
    print("Checking first auth key...")
    try:
        r = requests.get("https://example.com/api/v1/users/@me",
                         headers={"Authorization": AUTH_KEYS[0]}, timeout=3)
        if r.status_code == 200:
            print(f"Auth OK: {r.json().get('username', 'unknown')}")
        else:
            print("First key invalid, continuing...")
    except:
        print("Skipping check")

    print(f"Using {len(TARGET_ENDPOINTS)} manual endpoints")

    input("\nEnter")

    start_time = time.time()
    tester = LoadTester()
    total_requests = tester.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled")
    except Exception as e:
        print(f"\nError: {e}")
