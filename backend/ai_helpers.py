import re
import json

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

SEARCH_INTENT_KEYWORDS = [
    "show", "list", "display", "find", "search", "suggest", "recommend",
    "browse", "see", "get", "give", "what do you have", "what do you sell",
]

SEARCH_STOPWORDS = [
    "show", "list", "display", "find", "search", "suggest", "recommend",
    "browse", "see", "get", "give", "me", "the", "a", "an", "for", "buy",
    "about", "details", "specs", "price", "cost", "wishlist", "cart",
    "products", "product", "items", "item", "all", "any", "some", "please",
    "mobile", "mobiles", "phone", "phones", "smartphone", "smartphones",
]

BRAND_KEYWORDS = {
    "samsung": ["samsung", "galaxy"],
    "apple": ["apple", "iphone", "macbook"],
    "nykaa": ["nykaa"],
    "nike": ["nike"],
    "sony": ["sony"],
    "asus": ["asus", "rog"],
    "lakme": ["lakme"],
    "playstation": ["playstation", "ps5"],
}

PRODUCT_ALIASES = {
    "iphone": "iPhone 15 Pro",
    "samsung": "Samsung Galaxy S24 Ultra",
    "galaxy": "Samsung Galaxy S24 Ultra",
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

CATEGORY_KEYWORDS = {
    "mobiles": ["mobile", "phone", "smartphone"],
    "laptops": ["laptop", "notebook", "computer"],
    "electronics": ["headphone", "earphone", "speaker", "electronic"],
    "fashion": ["shoe", "sneaker", "handbag", "bag", "fashion", "wear"],
    "beauty": ["makeup", "beauty", "serum", "skincare", "cosmetic"],
    "gaming": ["gaming", "console", "game"],
}


def infer_product_brand(product):
    explicit_brand = product.get("brand")
    if explicit_brand:
        return explicit_brand

    text = f"{product.get('name', '')} {product.get('description', '')}".lower()
    for brand_name, keywords in BRAND_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return brand_name
    return ""


def extract_brand_from_text(text):
    msg = text.lower().strip()
    for brand_name, keywords in BRAND_KEYWORDS.items():
        if any(keyword in msg for keyword in keywords):
            return brand_name
    return None


def extract_category_from_text(text):
    msg = text.lower().strip()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in msg for keyword in keywords):
            return category
    return None


def clean_search_query(text):
    msg = text.lower().strip()
    stopword_pattern = r"\b(" + "|".join(re.escape(word) for word in SEARCH_STOPWORDS) + r")\b"
    clean_q = re.sub(stopword_pattern, " ", msg)
    clean_q = re.sub(r"\s+", " ", clean_q).strip()
    return clean_q


def extract_search_filters(message):
    msg = message.lower().strip()
    brand = extract_brand_from_text(msg)
    category = extract_category_from_text(msg)
    clean_q = clean_search_query(msg)

    if brand and clean_q == brand:
        clean_q = ""
    if category and clean_q == category:
        clean_q = ""

    return brand, category, clean_q


def product_matches_brand(product, brand):
    if not brand:
        return True

    product_brand = infer_product_brand(product).lower()
    if product_brand and brand.lower() in product_brand:
        return True

    searchable = f"{product.get('name', '')} {product.get('description', '')}".lower()
    keywords = BRAND_KEYWORDS.get(brand.lower(), [brand.lower()])
    return any(keyword in searchable for keyword in keywords)


def is_product_search_message(message):
    msg = message.lower().strip()
    if any(keyword in msg for keyword in SEARCH_INTENT_KEYWORDS):
        return True
    if extract_brand_from_text(msg) or extract_category_from_text(msg):
        return True
    return any(keyword in msg for cats in CATEGORY_KEYWORDS.values() for keyword in cats)


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
    matched = list(products)
    brand, category, clean_q = extract_search_filters(message)

    if brand:
        matched = [
            p for p in matched
            if product_matches_brand({"name": p[0], "description": p[3]}, brand)
        ]
    elif category:
        matched = [p for p in products if p[2] == category]
    elif clean_q:
        matched = [
            p for p in products
            if clean_q in p[0].lower() or any(word in p[0].lower() for word in clean_q.split() if len(word) > 2)
        ]

    for alias, product_name in PRODUCT_ALIASES.items():
        if alias in message.lower():
            alias_matches = [p for p in products if p[0] == product_name]
            if alias_matches:
                matched = alias_matches
                break

    price_limit = _extract_price_limit(message)
    if price_limit is not None:
        matched = [p for p in matched if float(p[1]) <= price_limit]

    msg = message.lower()
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
        if any(k in msg for k in ["all", "catalog", "everything", "what do you sell"]) and not extract_brand_from_text(msg):
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


def detect_sales_intent_local(message):
    msg = message.lower().strip()
    
    # Check "Add All to Cart" first
    if any(k in msg for k in ["add all", "add all of them", "add all these", "add everything"]):
        return {
            "intent": "Add All to Cart",
            "product_query": None,
            "category": None
        }
    
    # Check "Add to Cart"
    if "cart" in msg and any(k in msg for k in ["add", "put", "insert"]):
        product_query = None
        for k in ["add", "put"]:
            if k in msg:
                parts = msg.split(k)
                if len(parts) > 1:
                    sub = parts[1].split("to cart")[0].strip()
                    sub = re.sub(r"\b(the|this|my|a|an|products|product|items|item)\b", "", sub).strip()
                    if len(sub) > 1:
                        product_query = sub
        return {
            "intent": "Add to Cart",
            "product_query": product_query,
            "category": None
        }
        
    # Check "Add to Wishlist"
    if "wishlist" in msg:
        product_query = None
        for k in ["add", "put"]:
            if k in msg:
                parts = msg.split(k)
                if len(parts) > 1:
                    sub = parts[1].split("to wishlist")[0].strip()
                    sub = re.sub(r"\b(the|this|my|a|an|products|product|items|item)\b", "", sub).strip()
                    if len(sub) > 1:
                        product_query = sub
        return {
            "intent": "Add to Wishlist",
            "product_query": product_query,
            "category": None
        }
        
    # Check "Buy Now"
    if any(k in msg for k in ["buy now", "purchase now", "checkout now", "buy this", "buy the", "buy it"]):
        product_query = None
        match = re.search(r"\bbuy\s+(?:now\s+)?(?:the|this|it|a|an)?\s*(.*)", msg)
        if match:
            sub = match.group(1).replace("now", "").strip()
            sub = re.sub(r"\b(the|this|my|a|an|products|product|items|item)\b", "", sub).strip()
            if len(sub) > 1:
                product_query = sub
        return {
            "intent": "Buy Now",
            "product_query": product_query,
            "category": None
        }
        
    # Check Product Details
    if any(k in msg for k in ["detail", "spec", "description", "how much", "rating", "review"]) or (
        any(k in msg for k in ["price", "cost"]) and not is_product_search_message(message)
    ):
        product_query = msg
        for k in ["price of", "cost of", "details of", "specs of", "about"]:
            if k in msg:
                product_query = msg.split(k)[1].strip()
                break
        product_query = re.sub(r"\b(price|cost|how much|details|specs|description|rating|reviews|review)\b", "", product_query).strip()
        brand, category, _ = extract_search_filters(product_query or message)
        return {
            "intent": "Product Details",
            "product_query": product_query,
            "category": category,
            "brand": brand,
        }

    brand, category, _ = extract_search_filters(message)
    return {
        "intent": "Product Search",
        "product_query": message,
        "category": category,
        "brand": brand,
    }


def find_matching_products(query_str, category_str, products, brand_str=None):
    """
    products: list of dicts with keys: id, name, price, image, category, description, rating
    """
    source_text = " ".join(
        part for part in [query_str or "", category_str or "", brand_str or ""] if part
    ).strip()
    if not source_text:
        return []

    brand, category, clean_q = extract_search_filters(source_text)
    if brand_str:
        brand = brand_str.lower().strip()
    if category_str:
        category = category_str.lower().strip()

    candidates = list(products)

    if brand:
        candidates = [p for p in candidates if product_matches_brand(p, brand)]
        if not candidates:
            return []

    if category:
        candidates = [p for p in candidates if p["category"].lower() == category]
        if not candidates:
            return []

    if not clean_q:
        return candidates if (brand or category) else []

    for alias, product_name in PRODUCT_ALIASES.items():
        if alias in clean_q:
            matched = [p for p in candidates if p["name"].lower() == product_name.lower()]
            if matched:
                return matched

    matched = [p for p in candidates if clean_q in p["name"].lower()]
    if matched:
        return matched

    q_words = [w for w in clean_q.split() if len(w) > 2]
    if q_words:
        matched = [p for p in candidates if any(w in p["name"].lower() for w in q_words)]
        if matched:
            return matched

        matched = [
            p for p in candidates
            if any(w in f"{p['name']} {p.get('description', '')}".lower() for w in q_words)
        ]
        if matched:
            return matched

    return candidates if (brand or category) else []


def process_sales_query(client, message, products, last_seen_products=None):
    """
    products: list of dicts with keys: id, name, price, image, category, description, rating
    last_seen_products: list of dicts or None
    """
    intent_data = None
    if client:
        try:
            prompt = f"""
Analyze the customer's query and extract their intent, target product name, brand, and target category.
The allowed intents are:
- "Product Search" (searching/filtering/listing products by brand, category, or keywords — includes show, list, display, find, search, suggest)
- "Product Details" (asking for details, price, rating, specs, or description of a specific product)
- "Add to Cart" (adding a specific product or the current/last product to cart)
- "Add All to Cart" (adding all previously listed/shown/mentioned products to cart)
- "Add to Wishlist" (adding a specific product or the current/last product to wishlist)
- "Buy Now" (purchasing/buying a specific product or the current/last product immediately)

Return your response in raw JSON format with these exact keys:
{{
  "intent": "intent_string",
  "product_query": "name of product or keywords if specified, otherwise null",
  "brand": "samsung" or "apple" or "nykaa" or "nike" or "sony" or "asus" or "lakme" or "playstation" or null,
  "category": "mobiles" or "laptops" or "electronics" or "fashion" or "beauty" or "gaming" or null
}}

Do not return any other text, only valid JSON.

Query: "{message}"
"""
            response_text = generate_with_gemini(client, prompt)
            if response_text:
                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    intent_data = json.loads(json_match.group(0))
        except Exception as e:
            print("Gemini intent detection failed, falling back to local:", e)
            
    if not intent_data:
        intent_data = detect_sales_intent_local(message)
        
    intent = intent_data.get("intent", "Product Search")
    product_query = intent_data.get("product_query")
    category = intent_data.get("category")
    brand = intent_data.get("brand")

    if not brand and product_query:
        brand = extract_brand_from_text(product_query)
    if not brand:
        brand = extract_brand_from_text(message)
    if not category:
        category = extract_category_from_text(message)

    print(f"Sales Agent detected intent: {intent} | Query: {product_query} | Brand: {brand} | Category: {category}")

    # 1. Product Search
    if intent == "Product Search":
        matched = find_matching_products(product_query, category, products, brand)
        if not matched:
            return {
                "reply": "No products found for your request.",
                "action": None,
                "products": []
            }
        
        lines = []
        for p in matched:
            lines.append(f"- **{p['name']}** — ₹{p['price']:,.0f} ({p['category']}, ★{p['rating']:.1f})\n  {p['description']}")
        
        reply = "I found matching product(s) in our store:\n\n" + "\n".join(lines)
        return {
            "reply": reply,
            "action": None,
            "products": matched
        }
        
    # 2. Product Details
    elif intent == "Product Details":
        matched = find_matching_products(product_query, category, products, brand)
        if not matched:
            return {
                "reply": "No products found for your request.",
                "action": None,
                "products": []
            }
            
        lines = []
        for p in matched:
            lines.append(
                f"**{p['name']}**\n"
                f"Price: ₹{p['price']:,.0f}\n"
                f"Category: {p['category']}\n"
                f"Rating: ★{p['rating']:.1f}\n"
                f"Details: {p['description']}\n"
            )
        reply = "\n\n".join(lines)
        return {
            "reply": reply,
            "action": None,
            "products": matched
        }
        
    # 3. Add to Cart
    elif intent == "Add to Cart":
        matched = []
        if product_query:
            matched = find_matching_products(product_query, category, products, brand)
        if not matched and last_seen_products:
            matched = [last_seen_products[0]]
            
        if not matched:
            return {
                "reply": "No products found for your request.",
                "action": None,
                "products": []
            }
            
        product_to_add = matched[0]
        reply = f"Added **{product_to_add['name']}** to your cart!"
        return {
            "reply": reply,
            "action": {
                "type": "ADD_TO_CART",
                "products": [product_to_add]
            },
            "products": matched
        }
        
    # 4. Add All to Cart
    elif intent == "Add All to Cart":
        if not last_seen_products:
            return {
                "reply": "No products found from the previous search/listing to add to the cart.",
                "action": None,
                "products": []
            }
            
        count = len(last_seen_products)
        names = ", ".join(f"**{p['name']}**" for p in last_seen_products)
        reply = f"Added {count} product(s) to your cart: {names}!"
        return {
            "reply": reply,
            "action": {
                "type": "ADD_ALL_TO_CART",
                "products": last_seen_products
            },
            "products": last_seen_products
        }
        
    # 5. Add to Wishlist
    elif intent == "Add to Wishlist":
        matched = []
        if product_query:
            matched = find_matching_products(product_query, category, products, brand)
        if not matched and last_seen_products:
            matched = [last_seen_products[0]]
            
        if not matched:
            return {
                "reply": "No products found for your request.",
                "action": None,
                "products": []
            }
            
        product_to_add = matched[0]
        reply = f"Added **{product_to_add['name']}** to your wishlist!"
        return {
            "reply": reply,
            "action": {
                "type": "ADD_TO_WISHLIST",
                "products": [product_to_add]
            },
            "products": matched
        }
        
    # 6. Buy Now
    elif intent == "Buy Now":
        matched = []
        if product_query:
            matched = find_matching_products(product_query, category, products, brand)
        if not matched and last_seen_products:
            matched = [last_seen_products[0]]
            
        if not matched:
            return {
                "reply": "No products found for your request.",
                "action": None,
                "products": []
            }
            
        product_to_buy = matched[0]
        reply = f"Starting checkout for **{product_to_buy['name']}**!"
        return {
            "reply": reply,
            "action": {
                "type": "BUY_NOW",
                "products": [product_to_buy]
            },
            "products": matched
        }
        
    return {
        "reply": "I couldn't process your request. Please try again.",
        "action": None,
        "products": []
    }
