import re

INTENT_PRODUCT_SEARCH = "PRODUCT_SEARCH"
INTENT_PRODUCT_DETAILS = "PRODUCT_DETAILS"
INTENT_ADD_TO_CART = "ADD_TO_CART"
INTENT_ADD_ALL_TO_CART = "ADD_ALL_TO_CART"
INTENT_ADD_TO_WISHLIST = "ADD_TO_WISHLIST"
INTENT_BUY_NOW = "BUY_NOW"
INTENT_GENERAL = "GENERAL"

CATALOG_LIST_KEYWORDS = [
    "all products", "full catalog", "everything you sell", "what do you sell",
    "what do you have", "entire catalog", "complete list",
]
CATALOG_LIST_SHORT = ["all", "list", "catalog", "everything"]

SEARCH_KEYWORDS = [
    "show", "find", "search", "look for", "recommend", "suggest", "available",
    "have any", "do you have", "do you sell", "price", "cost", "cheap", "best",
    "top rated", "under", "below", "budget",
]

STOP_WORDS = {
    "show", "me", "the", "a", "an", "this", "that", "please", "want", "need",
    "some", "any", "for", "my", "your", "our", "can", "you", "what", "which",
    "how", "much", "is", "are", "do", "does", "have", "get", "give", "tell",
    "about", "product", "products", "item", "items", "buy", "shop", "store",
}

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


def row_to_product_dict(row):
    """Row: id, name, price, image, category, description, rating"""
    return {
        "id": row[0],
        "name": row[1],
        "price": float(row[2]),
        "image": row[3],
        "category": row[4],
        "description": row[5],
        "rating": float(row[6]) if len(row) > 6 and row[6] is not None else 4.5,
    }


def _format_products(products, limit=10):
    lines = []
    for row in products[:limit]:
        name, price, category, description = row[1], row[2], row[4], row[5]
        rating = float(row[6]) if len(row) > 6 and row[6] is not None else 4.5
        lines.append(f"- {name} — ₹{float(price):,.0f} ({category}, ★{rating:.1f})\n  {description}")
    return "\n".join(lines)


def detect_sales_intent(message):
    msg = message.lower().strip()

    if re.search(
        r"add\s+(?:all|them\s+all|all\s+of\s+(?:them|these|those)|everything)\s+(?:to\s+)?(?:my\s+)?cart",
        msg,
    ):
        return INTENT_ADD_ALL_TO_CART

    if re.search(r"add\s+(?:to|into)\s+(?:my\s+)?wishlist", msg) or re.search(
        r"add\s+.+\s+to\s+(?:my\s+)?wishlist", msg
    ):
        return INTENT_ADD_TO_WISHLIST

    if re.search(r"\bbuy\s+now\b", msg) or re.search(r"\bbuy\s+this\b", msg):
        return INTENT_BUY_NOW

    if re.search(r"add\s+(?:to|into)\s+(?:my\s+)?cart\b", msg) or re.search(
        r"add\s+.+\s+to\s+(?:my\s+)?cart", msg
    ):
        return INTENT_ADD_TO_CART

    if re.search(r"(details|info|about|tell me about|describe|specifications?|specs)", msg):
        return INTENT_PRODUCT_DETAILS

    if _is_product_query(msg):
        return INTENT_PRODUCT_SEARCH

    return INTENT_GENERAL


def _is_product_query(msg):
    if _extract_price_limit(msg) is not None:
        return True
    if any(k in msg for k in SEARCH_KEYWORDS):
        return True
    if any(k in msg for k in CATALOG_LIST_KEYWORDS):
        return True
    if any(k in msg for k in CATALOG_LIST_SHORT) and "cart" not in msg and "wishlist" not in msg:
        return True
    if any(alias in msg for alias in PRODUCT_ALIASES):
        return True
    if any(kw in msg for cats in CATEGORY_KEYWORDS.values() for kw in cats):
        return True
    tokens = [t for t in re.findall(r"[a-z0-9]+", msg) if len(t) > 2 and t not in STOP_WORDS]
    return bool(tokens)


def _wants_full_catalog(msg):
    if any(k in msg for k in CATALOG_LIST_KEYWORDS):
        return True
    if any(k in msg for k in CATALOG_LIST_SHORT) and "cart" not in msg and "wishlist" not in msg:
        return True
    return False


def _extract_product_query(message, intent):
    msg = message.lower().strip()

    if intent == INTENT_ADD_ALL_TO_CART:
        return ""

    match = re.search(r"add\s+(.+?)\s+to\s+(?:my\s+)?(?:cart|wishlist)", msg)
    if match:
        return match.group(1).strip()

    match = re.search(r"(?:buy\s+now|buy)\s+(.+)", msg)
    if match:
        return match.group(1).strip()

    for pattern in [
        r"add\s+(?:to|into)\s+(?:my\s+)?cart",
        r"add\s+(?:to|into)\s+(?:my\s+)?wishlist",
        r"add\s+(?:this|that)\s+(?:product\s+)?(?:to\s+)?(?:cart|wishlist)",
        r"\bbuy\s+now\b",
        r"\bbuy\s+this\b",
    ]:
        msg = re.sub(pattern, " ", msg)

    return " ".join(msg.split()).strip()


def _meaningful_tokens(message):
    return [
        t for t in re.findall(r"[a-z0-9]+", message.lower())
        if len(t) > 2 and t not in STOP_WORDS
    ]


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

    if _wants_full_catalog(msg):
        matched = list(products)
    else:
        matched = []
        tokens = _meaningful_tokens(msg)

        for alias, product_name in PRODUCT_ALIASES.items():
            if alias in msg:
                alias_matches = [p for p in products if p[1] == product_name]
                if alias_matches:
                    matched = alias_matches
                    break

        if not matched and tokens:
            name_matches = [
                p for p in products
                if any(token in p[1].lower() for token in tokens)
            ]
            if name_matches:
                matched = name_matches

        if not matched:
            for category, keywords in CATEGORY_KEYWORDS.items():
                if any(keyword in msg for keyword in keywords):
                    category_matches = [p for p in products if p[4] == category]
                    if category_matches:
                        matched = category_matches
                    break

        if not matched and tokens:
            desc_matches = [
                p for p in products
                if any(token in (p[5] or "").lower() for token in tokens)
            ]
            if desc_matches:
                matched = desc_matches

    price_limit = _extract_price_limit(message)
    if price_limit is not None:
        matched = [p for p in matched if float(p[2]) <= price_limit]

    if any(k in msg for k in ["cheapest", "lowest price", "affordable", "budget"]):
        matched = sorted(matched, key=lambda p: float(p[2]))

    if any(k in msg for k in ["best", "top rated", "recommend", "popular"]):
        matched = sorted(
            matched,
            key=lambda p: float(p[6]) if len(p) > 6 and p[6] is not None else 4.5,
            reverse=True,
        )

    return matched


def _suggest_similar_products(message, products, limit=3):
    tokens = _meaningful_tokens(message)
    if not tokens:
        return sorted(
            products,
            key=lambda p: float(p[6]) if len(p) > 6 and p[6] is not None else 4.5,
            reverse=True,
        )[:limit]

    scored = []
    for product in products:
        haystack = f"{product[1]} {product[4]} {product[5] or ''}".lower()
        score = sum(1 for token in tokens if token in haystack)
        if score:
            scored.append((score, product))

    if not scored:
        return sorted(
            products,
            key=lambda p: float(p[6]) if len(p) > 6 and p[6] is not None else 4.5,
            reverse=True,
        )[:limit]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [product for _, product in scored[:limit]]


def _format_product_details(row):
    rating = float(row[6]) if len(row) > 6 and row[6] is not None else 4.5
    return (
        f"**{row[1]}**\n"
        f"Price: ₹{float(row[2]):,.0f}\n"
        f"Category: {row[4]}\n"
        f"Rating: ★{rating:.1f}\n"
        f"Details: {row[5]}\n\n"
        "Say 'add to cart', 'add to wishlist', or 'buy now' to act on this product."
    )


def _no_products_reply(message, products):
    suggestions = _suggest_similar_products(message, products)
    reply = "No products found for your request."
    if suggestions:
        reply += "\n\nYou might like these items from our store:\n\n" + _format_products(suggestions)
        reply += "\n\nTry searching for another item, e.g. 'show mobiles' or 'gaming products'."
    else:
        reply += "\n\nTry searching for another item or browse our categories on the Shop page."
    return reply


def _resolve_action_targets(intent, message, products, last_products):
    if intent == INTENT_ADD_ALL_TO_CART:
        if not last_products:
            return []
        return [_normalize_product(item) for item in last_products]

    query = _extract_product_query(message, intent)
    if query:
        matched = _filter_products(query, products)
        if matched:
            return [row_to_product_dict(row) for row in matched]

    if len(last_products) == 1:
        return [_normalize_product(last_products[0])]

    if last_products and intent in (INTENT_ADD_TO_CART, INTENT_ADD_TO_WISHLIST, INTENT_BUY_NOW):
        if re.search(r"\b(this|that|it)\b", message.lower()):
            return [_normalize_product(last_products[0])]

    return []


def _normalize_product(item):
    if isinstance(item, dict):
        return item
    return row_to_product_dict(item)


def _build_action(intent, products):
    action_type = {
        INTENT_ADD_TO_CART: "ADD_TO_CART",
        INTENT_ADD_ALL_TO_CART: "ADD_ALL_TO_CART",
        INTENT_ADD_TO_WISHLIST: "ADD_TO_WISHLIST",
        INTENT_BUY_NOW: "BUY_NOW",
    }[intent]
    product_dicts = [_normalize_product(product) for product in products]
    return {"type": action_type, "products": product_dicts}


def _action_confirmation(intent, products):
    count = len(products)
    names = ", ".join(p["name"] for p in products[:3])
    if count > 3:
        names += f", and {count - 3} more"

    if intent == INTENT_ADD_ALL_TO_CART:
        return f"Added {count} product(s) to your cart: {names}."
    if intent == INTENT_ADD_TO_CART:
        return f"Added {names} to your cart." if count == 1 else f"Added {count} products to your cart: {names}."
    if intent == INTENT_ADD_TO_WISHLIST:
        return f"Added {names} to your wishlist." if count == 1 else f"Added {count} products to your wishlist: {names}."
    if intent == INTENT_BUY_NOW:
        return f"Ready to checkout with {names}. Opening your cart now."
    return ""


def process_sales_message(message, products, last_products=None):
    last_products = last_products or []

    if not products:
        return {
            "reply": "Our catalog is being updated. Please check the Shop page shortly.",
            "intent": INTENT_GENERAL,
            "actions": [],
            "matched_products": [],
        }

    intent = detect_sales_intent(message)

    if intent in (INTENT_ADD_TO_CART, INTENT_ADD_ALL_TO_CART, INTENT_ADD_TO_WISHLIST, INTENT_BUY_NOW):
        targets = _resolve_action_targets(intent, message, products, last_products)
        if not targets:
            if intent == INTENT_ADD_ALL_TO_CART:
                reply = (
                    "I don't have a recent product list to add. "
                    "Search for products first (e.g. 'show laptops'), then say 'add all to cart'."
                )
            else:
                reply = (
                    "I couldn't identify which product to use. "
                    "Search for a product first or specify it, e.g. 'add iPhone to cart'."
                )
            return {"reply": reply, "intent": intent, "actions": [], "matched_products": []}

        action = _build_action(intent, targets)
        return {
            "reply": _action_confirmation(intent, targets),
            "intent": intent,
            "actions": [action],
            "matched_products": targets,
        }

    search_message = message
    if intent in (INTENT_PRODUCT_SEARCH, INTENT_PRODUCT_DETAILS):
        search_message = _extract_product_query(message, intent) or message

    matched = _filter_products(search_message, products)

    if not matched and intent in (INTENT_PRODUCT_SEARCH, INTENT_PRODUCT_DETAILS):
        return {
            "reply": _no_products_reply(search_message, products),
            "intent": intent,
            "actions": [],
            "matched_products": [],
        }

    if intent == INTENT_PRODUCT_DETAILS and matched:
        if len(matched) == 1:
            return {
                "reply": _format_product_details(matched[0]),
                "intent": INTENT_PRODUCT_DETAILS,
                "actions": [],
                "matched_products": [row_to_product_dict(matched[0])],
            }
        return {
            "reply": (
                f"I found {len(matched)} matching products:\n\n"
                + _format_products(matched)
                + "\n\nAsk about a specific product for full details."
            ),
            "intent": INTENT_PRODUCT_SEARCH,
            "actions": [],
            "matched_products": [row_to_product_dict(row) for row in matched],
        }

    if matched:
        if len(matched) == 1:
            return {
                "reply": _format_product_details(matched[0]),
                "intent": INTENT_PRODUCT_DETAILS,
                "actions": [],
                "matched_products": [row_to_product_dict(matched[0])],
            }

        heading = f"I found {len(matched)} matching product(s) in our store:"
        if _wants_full_catalog(message.lower()):
            heading = "Here is our full STYLE catalog:"
        return {
            "reply": (
                f"{heading}\n\n"
                + _format_products(matched)
                + "\n\nSay 'add all to cart', 'add [product] to cart', or 'buy now' to purchase."
            ),
            "intent": INTENT_PRODUCT_SEARCH,
            "actions": [],
            "matched_products": [row_to_product_dict(row) for row in matched],
        }

    return {
        "reply": (
            "Hi! I'm your STYLE shopping assistant. "
            "Ask me to search products, e.g. 'show mobiles', 'iPhone price', or 'laptops under ₹150000'."
        ),
        "intent": INTENT_GENERAL,
        "actions": [],
        "matched_products": [],
    }


def local_sales_reply(message, products, last_products=None):
    return process_sales_message(message, products, last_products)["reply"]


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
