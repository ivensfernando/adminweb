import json
import os
import unittest
from importlib import import_module
import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.conf import settings

from src.db.bot_helpers import get_bot_users_by_email, get_user_exchanges_by_user_ids


if not settings.configured:
    settings.configure(DEFAULT_CHARSET="utf-8")


def import_account_module():
    os.environ.setdefault("DATABASE_URL", "postgres://test:test@localhost:5432/test")
    os.environ.setdefault("BOT_DATABASE_URL", "postgres://test:test@localhost:5432/test")
    if "ninja" not in sys.modules:
        ninja_module = types.ModuleType("ninja")

        class DummyRouter:
            def __init__(self, *args, **kwargs):
                pass

            def get(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

            def post(self, *args, **kwargs):
                def decorator(func):
                    return func

                return decorator

        ninja_module.Router = DummyRouter
        sys.modules["ninja"] = ninja_module

    if "pydantic" not in sys.modules:
        pydantic_module = types.ModuleType("pydantic")
        pydantic_module.BaseModel = object
        sys.modules["pydantic"] = pydantic_module

    if "pydantic.main" not in sys.modules:
        pydantic_main = types.ModuleType("pydantic.main")
        pydantic_main.BaseModel = object
        sys.modules["pydantic.main"] = pydantic_main

    return import_module("src.api.account")


class BotHelpersTests(unittest.TestCase):
    def test_get_bot_users_by_email_returns_rows(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "user@example.com"),
            (2, "user@example.com"),
        ]

        result = get_bot_users_by_email(mock_conn, "user@example.com")

        self.assertEqual(
            result,
            [
                {"id": 1, "email": "user@example.com"},
                {"id": 2, "email": "user@example.com"},
            ],
        )
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_get_user_exchanges_by_user_ids_returns_rows(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (
                1,
                10,
                3,
                False,
                25,
                "1.2",
                "0.3",
                "1.1",
                "1.0",
                "0.9",
                True,
                False,
                "strategy",
                "BTCUSDT",
                "1h",
                "binance",
            ),
        ]

        result = get_user_exchanges_by_user_ids(mock_conn, [10])

        self.assertEqual(
            result,
            [
                {
                    "id": 1,
                    "user_id": 10,
                    "exchange_id": 3,
                    "run_on_server": False,
                    "order_size_percent": 25,
                    "weekend_holiday_multiplier": "1.2",
                    "dead_zone_multiplier": "0.3",
                    "asia_multiplier": "1.1",
                    "london_multiplier": "1.0",
                    "us_multiplier": "0.9",
                    "enable_no_trade_window": True,
                    "no_trade_window_orders_closed": False,
                    "strategy_name": "strategy",
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "exchange_name": "binance",
                    "display": "binance strategy BTCUSDT 1h",
                }
            ],
        )
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


class UserExchangesOptionsTests(unittest.TestCase):
    def test_get_user_bots_options_returns_list(self):
        account = import_account_module()
        with patch.object(account, "getConn") as mock_get_conn, \
                patch.object(account, "get_bot_conn") as mock_get_bot_conn, \
                patch.object(account, "get_user_by_id") as mock_get_user_by_id, \
                patch.object(account, "get_bot_users_by_email") as mock_get_bot_users_by_email, \
                patch.object(account, "get_user_exchanges_by_user_ids") as mock_get_user_exchanges_by_user_ids:
            mock_get_conn.return_value = MagicMock()
            mock_get_bot_conn.return_value = MagicMock()
            mock_get_user_by_id.return_value = {"username": "user@example.com"}
            mock_get_bot_users_by_email.return_value = [{"id": 10, "email": "user@example.com"}]
            mock_get_user_exchanges_by_user_ids.return_value = [
                {
                    "id": 1,
                    "user_id": 10,
                    "exchange_id": 3,
                    "run_on_server": False,
                    "order_size_percent": 25,
                    "weekend_holiday_multiplier": "1.2",
                    "dead_zone_multiplier": "0.3",
                    "asia_multiplier": "1.1",
                    "london_multiplier": "1.0",
                    "us_multiplier": "0.9",
                    "enable_no_trade_window": True,
                    "no_trade_window_orders_closed": False,
                    "strategy_name": "strategy",
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "exchange_name": "binance",
                    "display": "binance strategy BTCUSDT 1h",
                }
            ]

            request = SimpleNamespace(auth={"user_id": 1})
            response = account.get_user_bots_options(request)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), [
                {
                    "id": 1,
                    "user_id": 10,
                    "exchange_id": 3,
                    "run_on_server": False,
                    "order_size_percent": 25,
                    "weekend_holiday_multiplier": "1.2",
                    "dead_zone_multiplier": "0.3",
                    "asia_multiplier": "1.1",
                    "london_multiplier": "1.0",
                    "us_multiplier": "0.9",
                    "enable_no_trade_window": True,
                    "no_trade_window_orders_closed": False,
                    "strategy_name": "strategy",
                    "symbol": "BTCUSDT",
                    "timeframe": "1h",
                    "exchange_name": "binance",
                    "display": "binance strategy BTCUSDT 1h",
                }
            ])

    def test_get_user_bots_options_returns_empty_when_no_bot_users(self):
        account = import_account_module()
        with patch.object(account, "getConn") as mock_get_conn, \
                patch.object(account, "get_bot_conn") as mock_get_bot_conn, \
                patch.object(account, "get_user_by_id") as mock_get_user_by_id, \
                patch.object(account, "get_bot_users_by_email") as mock_get_bot_users_by_email:
            mock_get_conn.return_value = MagicMock()
            mock_get_bot_conn.return_value = MagicMock()
            mock_get_user_by_id.return_value = {"username": "user@example.com"}
            mock_get_bot_users_by_email.return_value = []

            request = SimpleNamespace(auth={"user_id": 1})
            response = account.get_user_bots_options(request)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content), [])
