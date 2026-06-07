import re

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-flash-latest",
]

STORE_POLICIES = """
- 30-day return policy for unused items in original packaging
- Refunds processed within 5-7 business days
- Free shipping on orders above ₹5,000; standard delivery in 3-5 business days
- Payment: credit/debit cards, UPI, Google Pay, PhonePe, and Cash on Delivery
- Support email: support@styletech.com | Phone: +91 98765 43210
"""

CATEGORY_KEYWORDS = {
    "mobiles": ["iphone", "samsung", "mobile", "phone", "smartphone", "galaxy"],
    "laptops": ["laptop", "macbook", "notebook", "computer", "rog", "gaming laptop", "asus", "air m3"],
    "fashion": ["nike", "sneaker", "shoe", "handbag", "fashion", "bag", "air max"],
    "electronics": ["headphone", "sony", "wh1000", "electronic", "noise"],
    "beauty": ["makeup", "serum", "lakme", "nykaa", "beauty", "skincare"],
    "gaming": ["playstation", "ps5", "console", "gaming"],
}

PRODUCT_ALIASES = {
    "iphone": "iPhone 15 Pro",
    "samsung": "Samsung Galaxy S24 Ultra",
    "macbook": "MacBook Air M3",
    "rog": "ASUS ROG Gaming Laptop",
    "asus": "ASUS ROG Gaming Laptop",
    "sony": "Sony WH1000XM5",
    "headphone": "Sony WH1000XM5",
    "nike": "Nike Air Max",
    "handbag": "Luxury Handbag",
    "lakme": "Lakme Makeup Kit",
    "makeup": "Lakme Makeup Kit",
    "nykaa": "Nykaa Face Serum",
    "serum": "Nykaa Face Serum",
    "playstation": "PlayStation 5",
    "ps5": "PlayStation 5",
}


def generate_with_gemini(client, prompt):
    if not client:
        return None

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as exc:
            print(f"Model {model_name} failed: {exc}")

    return None


def classify_route(message):
    msg = message.lower().strip()

    if re.search(r"order\s*#?\s*\d+", msg):
        return "ORDER"
    if any(k in msg for k in [
        "my order", "order status", "track", "tracking", "where is my",
        "delivery status", "shipped", "delivered", "order history", "past order",
    ]):
        return "ORDER"

    if any(k in msg for k in [
        "return", "refund", "policy", "policies", "help", "support",
        "complaint", "cancel order", "payment method", "how to pay",
        "upi", "cod", "cash on delivery", "contact", "email support",
    ]):
        return "SUPPORT"

    return "SALES"


def _format_products(products, limit=10):
    lines = []
    for row in products[:limit]:
        name, price, category, description = row[0], row[1], row[2], row[3]
        rating = float(row[4]) if len(row) > 4 and row[4] is not None else 4.5
        lines.append(f"- {name} — ₹{float(price):,.0f} ({category}, ★{rating:.1f})\n  {description}")
    return "\n".join(lines)


def _extract_price_limit(message):
    msg = message.lower()
    patterns = [
        r"(?:under|below|less than|max|upto|up to|within)\s*₹?\s*([\d,]+)",
        r"₹\s*([\d,]+)\s*(?:or less|and below|max)",
        r"budget\s*₹?\s*([\d,]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, msg)
        if match:
            return int(re.sub(r"[^\d]", "", match.group(1)))
    return None


def _filter_products(message, products):
    msg = message.lower()
    matched = list(products)

    for alias, product_name in PRODUCT_ALIASES.items():
        if alias in msg:
            alias_matches = [p for p in products if p[0] == product_name]
            if alias_matches:
                return alias_matches

    name_matches = [
        p for p in products
        if any(part in p[0].lower() for part in msg.split() if len(part) > 2)
    ]
    if name_matches:
        matched = name_matches

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in msg for keyword in keywords):
            category_matches = [p for p in products if p[2] == category]
            if category_matches:
                matched = category_matches
            break

    price_limit = _extract_price_limit(message)
    if price_limit is not None:
        matched = [p for p in matched if float(p[1]) <= price_limit]

    if any(k in msg for k in ["cheapest", "lowest price", "affordable", "budget"]):
        matched = sorted(matched, key=lambda p: float(p[1]))

    if any(k in msg for k in ["best", "top rated", "recommend", "popular"]):
        matched = sorted(
            matched,
            key=lambda p: float(p[4]) if len(p) > 4 and p[4] is not None else 4.5,
            reverse=True,
        )

    return matched


def local_sales_reply(message, products):
    if not products:
        return "Our catalog is being updated. Please check the Shop page shortly."

    matched = _filter_products(message, products)
    msg = message.lower()

    if matched:
        if len(matched) == 1:
            p = matched[0]
            rating = float(p[4]) if len(p) > 4 and p[4] is not None else 4.5
            return (
                f"**{p[0]}**\n"
                f"Price: ₹{float(p[1]):,.0f}\n"
                f"Category: {p[2]}\n"
                f"Rating: ★{rating:.1f}\n"
                f"Details: {p[3]}\n\n"
                "Add it to cart from the Shop page!"
            )

        heading = f"I found {len(matched)} matching product(s) in our store:"
        if any(k in msg for k in ["all", "list", "catalog", "everything", "what do you sell"]):
            heading = "Here is our full STYLE catalog:"
        return (
            f"{heading}\n\n"
            + _format_products(matched)
            + "\n\nOpen the Shop page to buy, or ask e.g. 'iPhone price' or 'laptops under ₹150000'."
        )

    return (
        "I couldn't find an exact match. Here are all products we currently sell:\n\n"
        + _format_products(products)
        + "\n\nTry: 'show mobiles', 'gaming products', 'cheapest item', or 'laptops under ₹150000'."
    )


def local_support_reply(message):
    msg = message.lower()

    if any(k in msg for k in ["payment", "pay", "upi", "cod", "card", "debit", "credit"]):
        return (
            "Payment options at STYLE:\n"
            "- Credit / Debit cards\n"
            "- UPI (Google Pay, PhonePe, etc.)\n"
            "- Cash on Delivery at checkout\n\n"
            "No real payment is processed in this demo store."
        )

    if any(k in msg for k in ["return", "refund"]):
        return (
            "Returns & refunds:\n"
            "- 30-day return policy for unused items in original packaging\n"
            "- Refunds processed within 5-7 business days\n"
            "- Contact support@styletech.com for return requests"
        )

    if any(k in msg for k in ["ship", "delivery", "deliver"]):
        return (
            "Shipping info:\n"
            "- Free shipping on orders above ₹5,000\n"
            "- Standard delivery in 3-5 business days\n"
            "- Tracking number is shown after you place an order"
        )

    if any(k in msg for k in ["contact", "email", "phone", "call"]):
        return (
            "Contact STYLE support:\n"
            "- Email: support@styletech.com\n"
            "- Phone: +91 98765 43210\n"
            "- Address: 123 Fashion Street, Tech Park, Bangalore"
        )

    return f"STYLE store policies:\n{STORE_POLICIES.strip()}"


def _format_order(order):
    order_id, status, total, created_at, tracking, customer, address = order
    lines = [
        f"Order #{order_id}",
        f"  Status: {status}",
        f"  Amount: ₹{float(total):,.0f}",
        f"  Date: {created_at}",
    ]
    if tracking:
        lines.append(f"  Tracking: {tracking}")
    if customer:
        lines.append(f"  Customer: {customer}")
    if address:
        lines.append(f"  Address: {address}")
    return "\n".join(lines)


def local_order_reply(message, orders, user_email):
    if not user_email:
        return (
            "Please log in first (top-right Login button) so I can look up your orders securely.\n"
            "After login, ask: 'where is my order?' or 'show my orders'."
        )

    if not orders:
        return "You don't have any orders yet. Add items from the Shop and complete checkout to place your first order!"

    msg = message.lower()
    order_match = re.search(r"order\s*#?\s*(\d+)", msg)
    if order_match:
        order_id = int(order_match.group(1))
        for order in orders:
            if order[0] == order_id:
                return f"Here are the details for your request:\n\n{_format_order(order)}"
        return f"I couldn't find Order #{order_id} on your account. Here are your recent orders:\n\n" + "\n\n".join(_format_order(o) for o in orders)

    if any(k in msg for k in ["track", "tracking", "status", "where", "latest", "recent"]):
        latest = orders[0]
        reply = f"Your most recent order:\n\n{_format_order(latest)}"
        if len(orders) > 1:
            reply += f"\n\nYou have {len(orders)} recent order(s). Ask 'show all my orders' for the full list."
        return reply

    lines = [f"You have {len(orders)} recent order(s):\n"]
    for order in orders:
        lines.append(_format_order(order))
        lines.append("")
    lines.append("Ask about a specific order, e.g. 'Order #3 status'.")
    return "\n".join(lines)


def build_sales_prompt(message, products):
    product_list = _format_products(products, limit=20)
    return f"""You are the Sales Expert Agent for STYLE store.
Here are our available products:
{product_list}

User: {message}

Respond as a helpful, premium sales assistant. Recommend products from the catalog only, format nicely, and mention prices in INR (₹)."""


def build_support_prompt(message):
    return f"""You are the Customer Support Agent for STYLE store.
Store Policies:
{STORE_POLICIES}

User: {message}

Respond politely and helpfully using the store policies."""


def build_order_prompt(message, user_email, order_summary):
    return f"""You are the Order Tracking Assistant for STYLE store.
The user ({user_email}) is asking about their orders.

Here is their order history:
{order_summary}

User: {message}

Provide a helpful response about their order status. Be concise and friendly."""


def build_router_prompt(message):
    return f"""Classify this customer message into exactly one category: SALES, ORDER, or SUPPORT.

SALES = product recommendations, catalog, prices, what to buy
ORDER = order status, tracking, delivery, past purchases
SUPPORT = returns, refunds, policies, payments, general help

Message: "{message}"

Reply with exactly one word: SALES, ORDER, or SUPPORT."""
