import pytest
import requests
import random


BASE_URL_V1 = "https://qa-internship.avito.com/api/1"
BASE_URL_V2 = "https://qa-internship.avito.com/api/2"


def create_item(payload: dict):
    response = requests.post(BASE_URL_V1 + "/item", json=payload)
    return response


# 1 версия API

# 1. Создание объявления(POST /api/1/item)
# Позитивные проверки
def test_create_item_valid_all_fields():
    payload = {
        "name": "Юбка",
        "price": 5000,
        "sellerId": 234567,
        "statistics": {
            "contacts": 5,
            "likes": 100,
            "viewCount": 1000
        }
    }
    response = requests.post(f"{BASE_URL_V1}/item", json=payload)
    assert response.status_code == 200
    print("Тело ответа:", response.text)
    assert 'Сохранили объявление' in response.json()['status']


# 2) Создание объявления только с обязательными полями (без statistics)
def test_create_item_required_fields_only():
    payload = {
        "name": "Юбка",
        "price": 1200,
        "sellerId": 345678
    }
    response = create_item(payload)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    print("Ответ теста 'required_fields_only':", data)
    assert "Сохранили объявление" in data.get("status", ""), "Статус ответа не соответствует ожидаемому"


# 3) Создание объявления с максимальным sellerId (999999)
def test_create_item_max_sellerId():
    payload = {
        "name": "Юбка",
        "price": 1500,
        "sellerId": 999999,
        "statistics": {
            "contacts": 3,
            "likes": 80,
            "viewCount": 500
        }
    }
    response = create_item(payload)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    print("Ответ теста 'max_sellerId':", data)
    assert "Сохранили объявление" in data.get("status", ""), "Статус ответа не соответствует ожидаемому"


# 4) Создание объявления с минимальным sellerId (111111)
def test_create_item_min_sellerId():
    payload = {
        "name": "Юбка",
        "price": 1500,
        "sellerId": 111111,
        "statistics": {
            "contacts": 3,
            "likes": 80,
            "viewCount": 500
        }
    }
    response = create_item(payload)
    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    data = response.json()
    print("Ответ теста 'min_sellerId':", data)
    assert "Сохранили объявление" in data.get("status", ""), "Статус ответа не соответствует ожидаемому"


# 5) Cоздание повторного объявления у существующего продавца
def test_create_duplicate_item_for_same_seller():
    seller_id = 111111
    payload = {
        "name": "Юбка",
        "price": 1500,
        "sellerId": seller_id,
        "statistics": {
            "contacts": 3,
            "likes": 80,
            "viewCount": 500
        }
    }
    response1 = create_item(payload)
    assert response1.status_code == 200, f"Первый запрос вернул статус: {response1.status_code}"
    data1 = response1.json()
    print("Ответ первого запроса 'duplicate_item':", data1)
    assert "Сохранили объявление" in data1.get("status", ""), "Статус первого ответа не соответствует ожидаемому"


# Негативные проверки
# 1) Создание без обязательного поля sellerId
def test_create_item_missing_sellerId():
    payload = {
        "name": "Юбка",
        "price": 1000
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за отсутствия обязательного поля sellerId"
    print("Ответ теста 'missing_sellerId':", response.json())


# 2) Неверный тип price (строка вместо числа)
def test_create_item_invalid_price_type():
    payload = {
        "name": "Юбка",
        "price": "сто тысяч",
        "sellerId": 123456
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за неверного типа цены"
    print("Ответ теста 'invalid_price_type':", response.json())


# 3) sellerId ниже допустимого диапазона (<111111)
def test_create_item_sellerId_below_min():
    payload = {
        "name": "Юбка",
        "price": 1000,
        "sellerId": 111110
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за sellerId ниже минимального"
    print("Ответ теста 'sellerId_below_min':", response.json())


# 4) sellerId выше допустимого диапазона (>999999)
def test_create_item_sellerId_above_max():
    payload = {
        "name": "Юбка",
        "price": 1000,
        "sellerId": 1000000
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за sellerId выше максимального"
    print("Ответ теста 'sellerId_above_max':", response.json())


# 5) Пустое поле name
def test_create_item_empty_name():
    payload = {
        "name": "",
        "price": 1000,
        "sellerId": 123456
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за пустого имени"
    print("Ответ теста 'empty_name':", response.json())


# 6) Отрицательное значение price
def test_create_item_negative_price():
    payload = {
        "name": "Юбка",
        "price": -1000,
        "sellerId": 123456
    }
    response = create_item(payload)
    assert response.status_code == 400, "Ожидалась ошибка из-за отрицательной цены"
    print("Ответ теста 'negative_price':", response.json())


# 2. Получение объявления по ID (GET /api/1/item/{id})
# Позитивные проверки
# 1) Получение объявления по существующему ID
def test_get_item_positive():
    item_id = '06a70754-120c-40b0-b901-02de8abf5f60'
    response = requests.get(f"{BASE_URL_V1}/item/{item_id}")
    print("Тело ответа:", response.text)
    assert response.status_code == 200
    item_data = response.json()
    assert isinstance(item_data, list)
    assert len(item_data) > 0


# Негативные проверки
# 1) Запрос несуществующего ID
def test_get_item_by_nonexistent_id():
    nonexistent_id = "15e8400-e29b-41d4-a716-1234540000"
    response = requests.get(f"{BASE_URL_V1}/item/{nonexistent_id}")
    assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    print("Ответ теста 'nonexistent_id':", response.json())
    assert "error" in response.json(), "Ожидалось сообщение об ошибке"


# 2) Некорректный формат ID (не UUID)
def test_get_item_by_invalid_id_format():
    invalid_id = "123-не-UUID-формат"
    response = requests.get(f"{BASE_URL_V1}/item/{invalid_id}")
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    print("Ответ теста 'invalid_id_format':", response.json())
    assert "error" in response.json(), "Ожидалось сообщение об ошибке"


# 3) Пустой ID
def test_get_item_by_empty_id():
    empty_id = ""
    response = requests.get(f"{BASE_URL_V1}/item/{empty_id}")
    assert response.status_code == 404, f"Ожидался статус 400, получен {response.status_code}"
    print("Ответ теста 'empty_id':", response.json())
    assert "error" in response.json(), "Ожидалось сообщение об ошибке"


# 3. Получение всех объявлений продавца (GET /api/1/{sellerId}/item)
# Позитивные проверки
# 1) Получение объявлений по существующему sellerId
def test_get_items_by_seller_id_positive():
    response = requests.get(f"{BASE_URL_V1}/{111111}/item")
    print("Тело ответа:", response.text)
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)

# 2) Запрос для продавца без объявлений
def test_get_items_by_existing_seller_without_ads():
    seller_id = 411718
    response = requests.get(f"{BASE_URL_V1}/{seller_id}/item")
    assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
    data = response.json()
    print(f"Ответ теста 'existing_seller_without_ads': {data}")
    assert data == [], "Ожидался пустой список объявлений"


# Негативные проверки
# 1) Запрос несуществующего ID
def test_get_items_by_nonexistent_seller():
    nonexistent_seller_id = 417649
    response = requests.get(f"{BASE_URL_V1}/{nonexistent_seller_id}/item")
    assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    print(f"Ответ теста 'nonexistent_seller': {response.json()}")
    assert "error" in response.json(), "Ожидалось сообщение об ошибке"


# 2) Некорректный формат ID (не UUID)
def test_get_items_by_invalid_seller_id_format():
    invalid_seller_id = "not-a-number"
    response = requests.get(f"{BASE_URL_V1}/{invalid_seller_id}/item")
    assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    print(f"Ответ теста 'invalid_seller_id_format': {response.json()}")
    assert "error" in response.json(), "Ожидалось сообщение об ошибке"


# 3) Пустой ID
def test_get_items_with_empty_seller_id():
    empty_id = " "
    response = requests.get(f"{BASE_URL_V1}/{empty_id}/item")
    assert  response.status_code == 400, \
        f"Ожидался статус 400, получен {response.status_code}"
    print(f"Ответ теста 'empty_seller_id': {response.json()}")


# 4. Получение статистики по ID товара (GET /api/1/statistic/{id})
# Позитивные проверки
# 1) Получение полной статистики
def test_get_statistic_positive():
    item_id = '5806557a-61ac-4dea-9e1a-afbe0e0df13e'
    response = requests.get(f"{BASE_URL_V1}/statistic/{item_id}")
    print("Тело ответа:", response.text)
    assert response.status_code == 200
    item_data = response.json()
    assert isinstance(item_data, list)
    assert len(item_data) > 0


# Негативные проверки
# 1) Запрос статистики несуществующего товара
def test_get_statistic_nonexistent_item():
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL_V1}/statistic/{fake_id}")
    print("Ответ сервера:", response.text)

    assert response.status_code == 404, "Должен вернуть статус 404"
    assert "error" in response.json(), "Должна быть информация об ошибке"


# 2) Некорректный формат ID
def test_get_statistic_invalid_id():
    invalid_id = "это-некорректный-id"
    response = requests.get(f"{BASE_URL_V1}/statistic/{invalid_id}")
    print("Ответ сервера:", response.text)
    assert response.status_code == 400, "Должен вернуть статус 400"
    assert "error" in response.json(), "Должна быть информация об ошибке"

# 2 версия API

# 1. Получение статистики (GET /api/2/statistic/{id})
# Позитивные проверки
# 1) Получение статистики существующего ID товара
def test_get_statistic_v2_success():
    response = requests.get(f"{BASE_URL_V2}/statistic/06a70754-120c-40b0-b901-02de8abf5f60")
    print("Response:", response.json())
    assert response.status_code == 200
    data = response.json()

# 2) Проверка обработки статуса 100 Continue
def test_get_statistic_v2_100_status():
    headers = {'Expect': '100-continue'}
    response = requests.get(
        f"{BASE_URL_V2}/statistic/06a70754-120c-40b0-b901-02de8abf5f60",
        headers=headers
    )
    print("Response status:", response.status_code)
    print("Headers:", response.headers)


# 2. Удаление объявления (DELETE /api/2/item/{id})
# Позитивные проверки
# 1) Удаление существующего объявления
def test_delete_item_positive():
    response = requests.delete(f"{BASE_URL_V2}/item/e7bf24f4-eae9-43ff-8843-9fb97e4d47a3")
    print(f"DELETE Response: {response.status_code} - {response.text}")
    assert response.status_code == 200, "Ожидался статус 200 после удаления"


# 2) Повторное удаление существующего объявления
def test_delete_item_positive_2():
    response = requests.delete(f"{BASE_URL_V2}/item/e7bf24f4-eae9-43ff-8843-9fb97e4d47a3")
    print(f"DELETE Response: {response.status_code} - {response.text}")
    assert response.status_code == 200, "Ожидался статус 200 после удаления"


# Негативные проверки
# 1) Удаление несуществующего ID
def test_v2_delete_nonexistent_item():
    nonexistent_id = "550e8400-e29b-41d4-a716-446655440000"
    response = requests.delete(f"{BASE_URL_V2}/item/{nonexistent_id}")
    assert response.status_code == 404
    assert "error" in response.json()


# 2) Некорректный формат ID
def test_v2_delete_invalid_id_format():
    invalid_id = "invalid-id-123"
    response = requests.delete(f"{BASE_URL_V2}/item/{invalid_id}")
    assert response.status_code == 400
    assert "error" in response.json()


