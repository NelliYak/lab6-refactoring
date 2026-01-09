# Константы для улучшения читаемости и легкого изменения
DEFAULT_CURRENCY = "USD"
DEFAULT_TAX_RATE = 0.21
MIN_TOTAL_AFTER_DISCOUNT = 0

# Константы для кодов купонов
COUPON_CODES = {
    "SAVE10": 0.10,
    "SAVE20_REGULAR": 0.05,
    "SAVE20_PREMIUM": 0.20,
    "VIP_SMALL": 10,
    "VIP_LARGE": 50
}

# Пороговые значения для бизнес-логики
SAVE20_THRESHOLD = 200
VIP_THRESHOLD = 100


class OrderRequest:
    """DTO (Data Transfer Object) для данных запроса заказа"""
    def __init__(self, request: dict):
        self.user_id = request.get("user_id")
        self.items = request.get("items")
        self.coupon = request.get("coupon")
        self.currency = request.get("currency") or DEFAULT_CURRENCY


def validate_request(order_request: OrderRequest) -> None:
    """Валидация входящих данных заказа"""
    
    if order_request.user_id is None:
        raise ValueError("user_id is required")
    
    if order_request.items is None:
        raise ValueError("items is required")
    
    if not isinstance(order_request.items, list):
        raise ValueError("items must be a list")
    
    if len(order_request.items) == 0:
        raise ValueError("items must not be empty")
    
    _validate_items(order_request.items)


def _validate_items(items: list) -> None:
    """Валидация каждого элемента в заказе"""
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")


def calculate_subtotal(items: list) -> int:
    """Вычисление общей стоимости товаров без скидок и налогов"""
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(coupon: str, subtotal: int) -> int:
    """Вычисление размера скидки на основе купона и суммы заказа"""
    
    if not coupon:  # None или пустая строка
        return 0
    
    coupon = coupon.strip()
    
    if coupon == "SAVE10":
        return int(subtotal * COUPON_CODES["SAVE10"])
    
    elif coupon == "SAVE20":
        return _calculate_save20_discount(subtotal)
    
    elif coupon == "VIP":
        return _calculate_vip_discount(subtotal)
    
    else:
        raise ValueError("unknown coupon")


def _calculate_save20_discount(subtotal: int) -> int:
    """Расчет скидки для купона SAVE20"""
    if subtotal >= SAVE20_THRESHOLD:
        return int(subtotal * COUPON_CODES["SAVE20_PREMIUM"])
    else:
        return int(subtotal * COUPON_CODES["SAVE20_REGULAR"])


def _calculate_vip_discount(subtotal: int) -> int:
    """Расчет скидки для VIP купона"""
    if subtotal < VIP_THRESHOLD:
        return COUPON_CODES["VIP_SMALL"]
    else:
        return COUPON_CODES["VIP_LARGE"]


def calculate_tax(total_after_discount: int) -> int:
    """Вычисление налога на сумму после скидки"""
    return int(total_after_discount * DEFAULT_TAX_RATE)


def generate_order_id(user_id: int, items_count: int) -> str:
    """Генерация уникального ID заказа"""
    return f"{user_id}-{items_count}-X"


def process_checkout(request: dict) -> dict:
    """
    Основная функция обработки заказа.
    Читается как сценарий: валидация -> расчеты -> формирование результата.
    """
    # 1. Разбор запроса
    order_request = OrderRequest(request)
    
    # 2. Валидация
    validate_request(order_request)
    
    # 3. Расчет подытога
    subtotal = calculate_subtotal(order_request.items)
    
    # 4. Расчет скидки
    discount = calculate_discount(order_request.coupon, subtotal)
    
    # 5. Расчет суммы после скидки
    total_after_discount = subtotal - discount
    if total_after_discount < MIN_TOTAL_AFTER_DISCOUNT:
        total_after_discount = MIN_TOTAL_AFTER_DISCOUNT
    
    # 6. Расчет налога
    tax = calculate_tax(total_after_discount)
    
    # 7. Расчет итоговой суммы
    total = total_after_discount + tax
    
    # 8. Генерация ID заказа
    order_id = generate_order_id(order_request.user_id, len(order_request.items))
    
    # 9. Формирование результата
    return {
        "order_id": order_id,
        "user_id": order_request.user_id,
        "currency": order_request.currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(order_request.items),
    }