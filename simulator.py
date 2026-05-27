import requests

PAYMENT_URL = "http://localhost:8003/pay"
ACCOUNTS_URL = "http://localhost:8001/accounts"
CARDS_URL = "http://localhost:8002/cards"
PAYMENTS_URL = "http://localhost:8003/payments"

VALID_CARD = "1234-5678-9012-3456"
SECOND_CARD = "9876-5432-1098-7654"
VALID_ACCOUNT = "5555666677778888"
OTHER_ACCOUNT = "1111222233334444"
INVALID_CARD = "0000-0000-0000-0000"
INVALID_ACCOUNT = "0000000000000000"


def print_section(title: str):
    print("\n" + "#" * 8 + f" {title} " + "#" * 8)


def fetch_json(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def show_accounts():
    accounts = fetch_json(ACCOUNTS_URL)
    print("Számlaegyenlegek:")
    for account in accounts:
        print(f"  {account['account_number']}: {account['balance']} Ft")


def show_payment_log():
    payments = fetch_json(PAYMENTS_URL)
    print("Payment tranzakciók:")
    for payment in payments:
        print(f"  id={payment['id']} status={payment['status']} source={payment['source_card']} target={payment['target_account']} amount={payment['amount']}")


def do_payment(source_card: str, target_account: str, amount: int, description: str):
    print_section(description)
    print(f"Kísérlet: {source_card} -> {target_account}, összeg = {amount} Ft")
    payload = {"source_card": source_card, "target_account": target_account, "amount": amount}

    try:
        response = requests.post(PAYMENT_URL, json=payload)
    except requests.exceptions.ConnectionError:
        print("  Hiba: A payment szolgáltatás nem elérhető.")
        return None

    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
    else:
        data = {"detail": response.text}

    if response.status_code == 200:
        print(f"  Siker: {data.get('message')}")
    else:
        print(f"  Sikertelen ({response.status_code}): {data.get('detail')}")
    return data


def main():
    print_section("Kezdő állapot")
    show_accounts()

    do_payment(VALID_CARD, VALID_ACCOUNT, 5000, "Sikeres fizetés")
    show_accounts()

    do_payment(INVALID_CARD, VALID_ACCOUNT, 1000, "Sikertelen fizetés: érvénytelen kártya")
    show_accounts()

    do_payment(VALID_CARD, INVALID_ACCOUNT, 2000, "Sikertelen fizetés: érvénytelen cél számla, de terhelés után visszatérítés")
    show_accounts()

    do_payment(SECOND_CARD, OTHER_ACCOUNT, 25000, "Sikertelen fizetés: nincs fedezet")
    show_accounts()

    do_payment(SECOND_CARD, OTHER_ACCOUNT, 5000, "Sikeres fizetés a második kártyáról")
    show_accounts()

    print_section("Összegző tranzakciók")
    show_payment_log()

    print("\nA bemutatóban látható, hogy a sikeres műveletek változtatják az egyenlegeket, míg a hibás fizetések nem hagynak elvészett pénzt a rendszerben.")


if __name__ == "__main__":
    main()
