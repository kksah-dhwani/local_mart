import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_whatsapp(message: str) -> bool:
    """
    CallMeBot se admin ke WhatsApp pe message bhejo.
    Free service — pehle callmebot.com pe register karo.
    """
    if not settings.CALLMEBOT_API_KEY or not settings.ADMIN_WHATSAPP_NUMBER:
        logger.warning("WhatsApp config missing. Skipping notification.")
        return False

    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            "phone": settings.ADMIN_WHATSAPP_NUMBER,
            "text": message,
            "apikey": settings.CALLMEBOT_API_KEY,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(url, params=params)
            if res.status_code == 200:
                logger.info("WhatsApp notification sent successfully.")
                return True
            else:
                logger.error(f"WhatsApp notification failed: {res.text}")
                return False
    except Exception as e:
        logger.error(f"WhatsApp notification error: {e}")
        return False


async def notify_new_order(order_id: int, customer_name: str, total: float,
                            block: str, zone: str, item_count: int, payment_method: str):
    payment_label = "💳 Online (Paid)" if payment_method == "online" else "💵 Cash on Delivery"
    message = (
        f"🛒 *New Order Alert!*\n"
        f"━━━━━━━━━━━━━━\n"
        f"Order ID: *#{order_id}*\n"
        f"Customer: {customer_name}\n"
        f"Items: {item_count}\n"
        f"Total: *₹{total:.2f}*\n"
        f"Payment: {payment_label}\n"
        f"Area: {block}\n"
        f"Zone: {zone}\n"
        f"━━━━━━━━━━━━━━\n"
        f"👉 Open admin panel to confirm."
    )
    return await send_whatsapp(message)


async def notify_order_status(customer_phone: str, order_id: int, status: str):
    """
    Customer ke WhatsApp pe status update bhejo.
    Iske liye customer ka number CallMeBot mein registered hona chahiye.
    (Optional feature — abhi sirf admin notification implement karte hain)
    """
    status_messages = {
        "confirmed":        "✅ Your order #{id} has been confirmed! We are preparing it.",
        "out_for_delivery": "🚴 Your order #{id} is out for delivery! Be ready.",
        "delivered":        "🎉 Your order #{id} has been delivered! Thank you for shopping.",
        "cancelled":        "❌ Your order #{id} has been cancelled. Contact us for help.",
    }
    msg_template = status_messages.get(status)
    if not msg_template:
        return False
    message = msg_template.replace("{id}", str(order_id))
    return await send_whatsapp(message)
