"""
Cart — Redis asosida.

Har bir kassir uchun alohida cart: key = "cart:{user_id}"
Cart ma'lumoti JSON formatda Redis da saqlanadi.

Struktura:
{
  "items": {
    "<product_id>": {
      "product_id":   1,
      "name":         "Coca-Cola",
      "barcode":      "5901234567890",
      "sell_price":   "5000.00",
      "quantity":     "2.00",
      "unit_short":   "d",
      "subtotal":     "10000.00"
    },
    ...
  }
}
"""
import json
from decimal import Decimal, ROUND_HALF_UP

from django.core.cache import cache

from core.exceptions import BusinessLogicError, InsufficientStockError

CART_TTL     = 60 * 60 * 8   # 8 soat (ish kuni)
CART_KEY_TPL = "cart:{user_id}"


def _key(user_id: int) -> str:
    return CART_KEY_TPL.format(user_id=user_id)


def _load(user_id: int) -> dict:
    raw = cache.get(_key(user_id))
    if raw is None:
        return {"items": {}}
    return json.loads(raw) if isinstance(raw, str) else raw


def _save(user_id: int, cart: dict) -> None:
    cache.set(_key(user_id), json.dumps(cart, default=str), timeout=CART_TTL)


def _recalc_subtotal(item: dict) -> dict:
    qty   = Decimal(str(item["quantity"])).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    price = Decimal(str(item["sell_price"]))
    item["quantity"] = str(qty)
    item["subtotal"] = str(
        (qty * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )
    return item


class CartService:
    """
    Redis cart.
    Barcha metod user_id qabul qiladi — har kassir o'z cartiga ega.
    """

    # ── Get ───────────────────────────────────────────────────────────────

    @staticmethod
    def get_cart(user_id: int) -> dict:
        """Cart ma'lumotlari + jami summa."""
        cart  = _load(user_id)
        items = list(cart["items"].values())
        total = sum((Decimal(str(i["subtotal"])) for i in items), Decimal("0"))
        return {
            "items":        items,
            "item_count":   len(items),
            "total_amount": str(total.quantize(Decimal("0.01"))),
        }

    # ── Add ───────────────────────────────────────────────────────────────

    @staticmethod
    def add_item(user_id: int, product_id: int, quantity: Decimal = Decimal("1")) -> dict:
        """
        Cartga mahsulot qo'shish.
        Agar mahsulot allaqachon cartda bo'lsa — miqdor qo'shiladi.
        """
        from products.models import Product
        from inventory.services import StockService

        if quantity <= 0:
            raise BusinessLogicError("Miqdor musbat bo'lishi kerak.", "invalid_quantity")

        # Mahsulot mavjudligini tekshirish
        try:
            product = (
                Product.objects
                .select_related("unit", "category")
                .get(pk=product_id, deleted_at__isnull=True, is_active=True)
            )
        except Product.DoesNotExist:
            raise BusinessLogicError("Mahsulot topilmadi.", "product_not_found")

        cart  = _load(user_id)
        key   = str(product_id)
        items = cart["items"]

        if key in items:
            new_qty = Decimal(str(items[key]["quantity"])) + quantity
        else:
            new_qty = quantity

        # Stock tekshirish
        stock_qty = StockService.get_current_quantity(product)
        if new_qty > stock_qty:
            raise InsufficientStockError(
                f"'{product.name}' dan faqat {stock_qty} dona mavjud."
            )

        items[key] = _recalc_subtotal({
            "product_id": product.pk,
            "name":       product.name,
            "barcode":    product.barcode or "",
            "sell_price": str(product.sell_price),
            "quantity":   str(new_qty),
            "unit_short": product.unit.short_name if product.unit else "",
        })

        _save(user_id, cart)
        return CartService.get_cart(user_id)

    # ── Update ────────────────────────────────────────────────────────────

    @staticmethod
    def update_item(user_id: int, product_id: int, quantity: Decimal) -> dict:
        """Miqdorni yangilash. quantity=0 bo'lsa — o'chiriladi."""
        from products.models import Product
        from inventory.services import StockService

        cart  = _load(user_id)
        key   = str(product_id)

        if key not in cart["items"]:
            raise BusinessLogicError("Bu mahsulot cartda yo'q.", "not_in_cart")

        if quantity <= 0:
            return CartService.remove_item(user_id, product_id)

        # Stock tekshirish
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise BusinessLogicError("Mahsulot topilmadi.", "product_not_found")

        stock_qty = StockService.get_current_quantity(product)
        if quantity > stock_qty:
            raise InsufficientStockError(
                f"'{product.name}' dan faqat {stock_qty} dona mavjud."
            )

        cart["items"][key]["quantity"] = str(quantity)
        _recalc_subtotal(cart["items"][key])
        _save(user_id, cart)
        return CartService.get_cart(user_id)

    # ── Remove ────────────────────────────────────────────────────────────

    @staticmethod
    def remove_item(user_id: int, product_id: int) -> dict:
        """Cartdan mahsulotni olib tashlash."""
        cart = _load(user_id)
        key  = str(product_id)
        if key not in cart["items"]:
            raise BusinessLogicError("Bu mahsulot cartda yo'q.", "not_in_cart")
        del cart["items"][key]
        _save(user_id, cart)
        return CartService.get_cart(user_id)

    # ── Clear ─────────────────────────────────────────────────────────────

    @staticmethod
    def clear(user_id: int) -> None:
        """Cartni to'liq tozalash."""
        cache.delete(_key(user_id))

    # ── Scan ─────────────────────────────────────────────────────────────

    @staticmethod
    def add_by_barcode(user_id: int, barcode: str, quantity: Decimal = Decimal("1")) -> dict:
        """
        Barcode / QR kod bilan scan qilib cartga qo'shish.
        POS sahifasining asosiy funksiyasi.
        """
        from products.services import ProductService
        product = ProductService.get_by_barcode(barcode)
        return CartService.add_item(user_id, product.pk, quantity)
