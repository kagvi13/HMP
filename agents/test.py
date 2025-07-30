# agents/test.py
import json
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from tools.storage import Storage

if __name__ == "__main__":
    print("[*] Инициализация БД через Storage...")
    storage = Storage()
    print("[+] Готово.")
