import pytest
from order_processing import process_checkout as old_process
from refactored_order_processing import process_checkout as new_process


def test_both_versions_return_same():
    """Проверяем, что обе версии работают одинаково"""
    test_cases = [
        {"user_id": 1, "items": [{"price": 50, "qty": 2}], "coupon": None, "currency": "USD"},
        {"user_id": 2, "items": [{"price": 30, "qty": 3}], "coupon": "SAVE10", "currency": "USD"},
        {"user_id": 3, "items": [{"price": 100, "qty": 2}], "coupon": "SAVE20", "currency": "USD"},
        {"user_id": 4, "items": [{"price": 50, "qty": 1}], "coupon": "VIP", "currency": "USD"},
    ]
    
    for test_case in test_cases:
        result_old = old_process(test_case)
        result_new = new_process(test_case)
        
        # Проверяем, что результаты идентичны
        assert result_old == result_new, f"Results differ for test case: {test_case}"


def test_ok_no_coupon():
    r = new_process({"user_id": 1, "items": [{"price": 50, "qty": 2}], "coupon": None, "currency": "USD"})
    assert r["subtotal"] == 100
    assert r["discount"] == 0
    assert r["tax"] == 21
    assert r["total"] == 121


def test_ok_save10():
    r = new_process({"user_id": 2, "items": [{"price": 30, "qty": 3}], "coupon": "SAVE10", "currency": "USD"})
    assert r["discount"] == 9


def test_ok_save20():
    r = new_process({"user_id": 3, "items": [{"price": 100, "qty": 2}], "coupon": "SAVE20", "currency": "USD"})
    assert r["discount"] == 40


def test_unknown_coupon():
    with pytest.raises(ValueError):
        new_process({"user_id": 1, "items": [{"price": 10, "qty": 1}], "coupon": "???", "currency": "USD"})


def test_empty_coupon():
    r = new_process({"user_id": 1, "items": [{"price": 50, "qty": 1}], "coupon": "", "currency": "USD"})
    assert r["discount"] == 0


def test_vip_coupon_small_order():
    r = new_process({"user_id": 1, "items": [{"price": 50, "qty": 1}], "coupon": "VIP", "currency": "USD"})
    assert r["discount"] == 10


def test_vip_coupon_large_order():
    r = new_process({"user_id": 1, "items": [{"price": 100, "qty": 2}], "coupon": "VIP", "currency": "USD"})
    assert r["discount"] == 50


def test_missing_user_id():
    with pytest.raises(ValueError, match="user_id is required"):
        new_process({"items": [{"price": 10, "qty": 1}]})


def test_missing_items():
    with pytest.raises(ValueError, match="items is required"):
        new_process({"user_id": 1})


def test_empty_items():
    with pytest.raises(ValueError, match="items must not be empty"):
        new_process({"user_id": 1, "items": []})


def test_invalid_items_type():
    with pytest.raises(ValueError, match="items must be a list"):
        new_process({"user_id": 1, "items": "not a list"})


def test_item_missing_price():
    with pytest.raises(ValueError, match="item must have price and qty"):
        new_process({"user_id": 1, "items": [{"qty": 1}]})


def test_item_negative_price():
    with pytest.raises(ValueError, match="price must be positive"):
        new_process({"user_id": 1, "items": [{"price": -10, "qty": 1}]})