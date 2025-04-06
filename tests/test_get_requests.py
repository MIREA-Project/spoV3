import requests

host_name = "http://localhost:53474"  # Укажите ваш хост и порт


def test_health_check():
    response = requests.get(f"{host_name}/health")
    assert response.status_code == 200


def test_get_today_statistic_not_found():
    user_id = 9999  # Несуществующий пользователь
    response = requests.get(f"{host_name}/statistic", params={"user_id": user_id})
    assert response.status_code == 404


def test_get_products():
    response = requests.get(f"{host_name}/products")
    assert response.status_code == 200


def test_get_eating():
    response = requests.get(f"{host_name}/eating", params={"user_id": 1})
    assert response.status_code == 200


def test_get_steps():
    response = requests.get(f"{host_name}/steps", params={"user_id": 1})
    assert response.status_code == 200


def test_get_water():
    response = requests.get(f"{host_name}/water", params={"user_id": 1})
    assert response.status_code == 200


def test_get_eating_types():
    response = requests.get(f"{host_name}/eating-types")
    assert response.status_code == 200


def test_search_products():
    response = requests.get(f"{host_name}/products/search", params={"name": "apple"})
    assert response.status_code == 200


def test_get_products_with_pfc():
    response = requests.get(f"{host_name}/products/with-pfc")
    assert response.status_code == 200


def test_get_user_eating_history():
    response = requests.get(f"{host_name}/eating/history/1")
    assert response.status_code == 200


def test_get_user_steps_history():
    response = requests.get(f"{host_name}/steps/history/1")
    assert response.status_code == 200


def test_get_user_water_history():
    response = requests.get(f"{host_name}/water/history/1")
    assert response.status_code == 200


def test_get_user_goals_success():
    response = requests.get(f"{host_name}/goals/123")
    assert response.status_code == 200


def test_get_user_goals_not_found():
    response = requests.get(f"{host_name}/goals/9999")  # Несуществующий пользователь
    assert response.status_code == 404


def test_add_product_success():
    payload = {
        "name": "Banana",
        "proteins": 1.3,
        "fats": 0.3,
        "carbs": 27.0,
        "calories": 105.0
    }
    response = requests.post(f"{host_name}/products", params=payload)
    assert response.status_code == 200


def test_add_steps_success():
    payload = {
        "user_id": 1,
        "count": 5000
    }
    response = requests.post(f"{host_name}/steps", params=payload)
    assert response.status_code == 200


def test_delete_steps_success():
    payload = {
        "user_id": 1,
        "count": 2000
    }
    response = requests.delete(f"{host_name}/steps", params=payload)
    assert response.status_code == 200


def test_add_water_success():
    payload = {
        "user_id": 1,
        "volume": 500
    }
    response = requests.post(f"{host_name}/water", params=payload)
    assert response.status_code == 200


def test_delete_water_success():
    payload = {
        "user_id": 1,
        "volume": 200
    }
    response = requests.delete(f"{host_name}/water", params=payload)
    assert response.status_code == 200


def test_update_goals_success():
    payload = {
        "daily_calories": 2000,
        "daily_proteins": 100,
        "daily_fats": 70,
        "daily_carbs": 250,
        "daily_water": 2000,
        "daily_steps": 8000
    }
    response = requests.patch(f"{host_name}/goals/123", params=payload)
    assert response.status_code == 200


def test_get_weekly_quality():
    response = requests.get(f"{host_name}/weekly-quality/123")
    assert response.status_code == 200


def test_add_eating_batch_success():
    payload = {
        "user_id": 123,
        "eating_type_id": 1
    }
    response = requests.post(f"{host_name}/eating/batch", params=payload, json=[1, 2, 3])
    assert response.status_code == 200


def test_delete_eating_success():
    payload = {
        "user_id": 123,
        "eating_type_id": 1
    }
    response = requests.delete(f"{host_name}/eating", params=payload)
    assert response.status_code == 200
