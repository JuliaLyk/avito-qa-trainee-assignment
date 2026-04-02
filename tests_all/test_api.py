import requests
import pytest
import re
import random
import uuid  # Добавили импорт!

BASE_URL = "https://qa-internship.avito.com/api/1"


# Добавили функцию, которую потеряли
def get_random_seller_id():
    return random.randint(111111, 999999)


def get_id_from_status(status_string):
    if not status_string:
        return None
    # Ищем UUID в строке статуса
    match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', status_string)
    return match.group(1) if match else None


# --- ТЕСТЫ ---

def test_tc01_create_item_success():
    """TC-01: Создание валидного объявления"""
    payload = {
        "sellerID": get_random_seller_id(),
        "name": "Персидский котенок",
        "price": 15000,
        "statistics": {"likes": 2, "viewCount": 2, "contacts": 2}  # Добавили статику
    }
    response = requests.post(f"{BASE_URL}/item", json=payload)
    assert response.status_code == 200
    status_text = response.json().get('status', '')
    assert get_id_from_status(status_text) is not None


def test_tc02_get_item_by_id():
    """TC-02: Получение объявления по ID"""
    # Добавляем statistics, чтобы создание прошло успешно
    payload = {
        "sellerID": get_random_seller_id(),
        "name": "Тест получения",
        "price": 500,
        "statistics": {"likes": 1, "viewCount": 1, "contacts": 1}
    }
    create_res = requests.post(f"{BASE_URL}/item", json=payload)
    item_id = get_id_from_status(create_res.json().get('status'))

    response = requests.get(f"{BASE_URL}/item/{item_id}")
    assert response.status_code == 200
    assert response.json()[0]["name"] == payload["name"]

def test_tc03_get_items_by_seller_id():
    """TC-03: Получение по SellerID"""
    seller_id = get_random_seller_id()
    # Тоже добавляем statistics
    payload = {
        "sellerID": seller_id,
        "name": "Товар продавца",
        "price": 100,
        "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}
    }
    requests.post(f"{BASE_URL}/item", json=payload)

    response = requests.get(f"{BASE_URL}/{seller_id}/item")
    assert response.status_code == 200
    assert len(response.json()) > 0
def test_tc07_get_non_existent_item():
    """TC-07: Поиск несуществующего ID"""
    non_id = str(uuid.uuid4())
    response = requests.get(f"{BASE_URL}/item/{non_id}")
    assert response.status_code == 404


def test_tc10_create_item_negative_price():
    """TC-10: Отрицательная цена"""
    payload = {"sellerID": 999999, "name": "Bug Price", "price": -1}
    response = requests.post(f"{BASE_URL}/item", json=payload)
    # Печатаем ответ сервера, чтобы увидеть правду в логах (pytest -s)
    print(f"\nResponse Body: {response.json()}")
    assert response.status_code == 400, f"Сервер принял цену -1, а не должен был! Статус: {response.status_code}"

def test_tc11_get_empty_seller_items():
    """TC-11: Пустой список"""
    unused_id = 1  # Попробуем совсем короткий ID
    response = requests.get(f"{BASE_URL}/{unused_id}/item")
    print(f"\nResponse Body: {response.json()}")
    assert response.json() == [], "Сервер вернул чужие объявления вместо пустого списка!"