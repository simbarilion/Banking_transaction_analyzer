import json
import os

import requests
from dotenv import load_dotenv

from config import ROOT_DIR
from src.logging_config import setup_logger

load_dotenv()


def get_currency_rates() -> list[dict]:
    """Получает данные о курсе заданных валют к рублю."""
    file_name = os.path.join(ROOT_DIR, "user_settings.json")
    url = "https://api.twelvedata.com/exchange_rate"
    cur_to = "RUB"
    currency_rates = []

    try:
        setup_logger().info(f"Чтение json-файла {file_name}.")
        with open(file_name) as f:
            data = json.load(f)
        valid_for_conversion = data["user_currencies"]

        setup_logger().info("Запрос к API https://api.twelvedata.com/exchange_rate")
        for cur in valid_for_conversion:
            params = {
                "symbol": f"{cur}/{cur_to}",
                "apikey": os.getenv("API_KEY_TWELVEDATA")
            }

            response = requests.get(url, params=params)
            if response.status_code != 200: raise requests.exceptions.RequestException("Подключение не удалось")

            data = response.json()
            result = round(float(data["rate"]), 2)

            currency_rate = dict()
            currency_rate["currency"] = cur
            currency_rate["rate"] = result
            currency_rates.append(currency_rate)

        setup_logger().info("Получены данные через API https://api.twelvedata.com/exchange_rate")
        return currency_rates

    except FileNotFoundError:
        setup_logger().error(f"Json-файл {file_name} не найден.")
        return []

    except requests.exceptions.RequestException as e:
        setup_logger().warning(f"Ошибка запроса к API https://api.twelvedata.com/exchange_rate: {e}.")
        return []

    except Exception as e:
        setup_logger().error(f"Ошибка при получении курса валют: {e}")
        return []


def get_stock_prices() -> list[dict]:
    """Получает данные о cтоимости заданных акций из S&P500 в рублях."""
    file_name = os.path.join(ROOT_DIR, "user_settings.json")
    url = "https://api.twelvedata.com/price"
    stock_prices = []

    try:
        setup_logger().info(f"Чтение json-файла {file_name}.")
        with open(file_name) as f:
            data = json.load(f)
        valid_stocks = data["user_stocks"]

        setup_logger().info("Запрос к API https://api.twelvedata.com/price")
        for stock in valid_stocks:
            params = {
                "symbol": stock,
                "apikey": os.getenv("API_KEY_TWELVEDATA")
            }

            response = requests.get(url, params=params)
            if response.status_code != 200: raise requests.exceptions.RequestException("Подключение не удалось")

            data = response.json()

            stock_price = dict()
            stock_price["stock"] = stock
            stock_price.update(data)
            stock_price["price"] = round(float(stock_price["price"]), 2)
            stock_prices.append(stock_price)

        setup_logger().info("Получены данные через API https://api.twelvedata.com/price")
        return stock_prices

    except FileNotFoundError:
        setup_logger().error(f"Json-файл {file_name} не найден.")
        return []

    except requests.exceptions.RequestException as e:
        setup_logger().warning(f"Ошибка запроса к API https://api.twelvedata.com/price: {e}.")
        print("Ошибка запроса к API:", e)
        return []

    except Exception as e:
        setup_logger().error(f"Ошибка при получении стоимости акций: {e}")
        return []
