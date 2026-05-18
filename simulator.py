import time
import random
import requests

FREQUENCY = 3

PAYMENT_URL = "http://localhost:8003/pay"

CARDS = ["1234-5678-9012-3456", "9876-5432-1098-7654"]
ACCOUNTS = ["1111222233334444", "5555666677778888"]

while True:
    source_card = random.choice(CARDS)
    target_account = random.choice(ACCOUNTS)
    amount = random.randint(1000, 15000) 

    payload = {
        "source_card": source_card,
        "target_account": target_account,
        "amount": amount
    }

    try:
        print(f"Indítás: {amount} Ft terhelése a {source_card} kártyáról a {target_account} számlára...")
        response = requests.post(PAYMENT_URL, json=payload)
        
        if response.status_code == 200:
            print(f"SIKER: {response.json().get('message')}")
        else:
            print(f"SIKERTELEN: {response.json().get('detail')}")
            
    except requests.exceptions.ConnectionError:
        print("Hálózati hiba: A Payment szolgáltatás nem elérhető.")

    print("-" * 50)
    time.sleep(FREQUENCY)