import unittest

from ai_helpers import (
    detect_sales_intent_local,
    find_matching_products,
    process_sales_query,
    extract_search_filters,
)


SAMPLE_PRODUCTS = [
    {
        "id": 1,
        "name": "iPhone 15 Pro",
        "price": 129999,
        "image": "",
        "category": "mobiles",
        "description": "Latest Apple flagship smartphone",
        "rating": 4.8,
    },
    {
        "id": 2,
        "name": "Samsung Galaxy S24 Ultra",
        "price": 119999,
        "image": "",
        "category": "mobiles",
        "description": "Samsung premium AI smartphone",
        "rating": 4.7,
    },
    {
        "id": 3,
        "name": "MacBook Air M3",
        "price": 134999,
        "image": "",
        "category": "laptops",
        "description": "Apple M3 ultra fast laptop",
        "rating": 4.9,
    },
    {
        "id": 4,
        "name": "ASUS ROG Gaming Laptop",
        "price": 149999,
        "image": "",
        "category": "laptops",
        "description": "RTX gaming laptop",
        "rating": 4.6,
    },
    {
        "id": 5,
        "name": "Sony WH1000XM5",
        "price": 24999,
        "image": "",
        "category": "electronics",
        "description": "Noise cancellation headphones",
        "rating": 4.8,
    },
    {
        "id": 6,
        "name": "Nike Air Max",
        "price": 8999,
        "image": "",
        "category": "fashion",
        "description": "Premium sneakers",
        "rating": 4.5,
    },
    {
        "id": 7,
        "name": "Nykaa Face Serum",
        "price": 999,
        "image": "",
        "category": "beauty",
        "description": "Vitamin C glowing serum",
        "rating": 4.4,
    },
    {
        "id": 8,
        "name": "PlayStation 5",
        "price": 54999,
        "image": "",
        "category": "gaming",
        "description": "Next generation console",
        "rating": 4.9,
    },
]


class BrandSearchTests(unittest.TestCase):
    def test_extract_search_filters_samsung(self):
        brand, category, clean_q = extract_search_filters("List Samsung Products")
        self.assertEqual(brand, "samsung")
        self.assertIsNone(category)
        self.assertEqual(clean_q, "")

    def test_show_samsung_products(self):
        intent = detect_sales_intent_local("Show Samsung Products")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = [p["name"] for p in matched]
        self.assertEqual(names, ["Samsung Galaxy S24 Ultra"])

    def test_list_samsung_products(self):
        intent = detect_sales_intent_local("List Samsung Products")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = [p["name"] for p in matched]
        self.assertEqual(names, ["Samsung Galaxy S24 Ultra"])

    def test_list_apple_products(self):
        intent = detect_sales_intent_local("List Apple Products")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = {p["name"] for p in matched}
        self.assertEqual(names, {"iPhone 15 Pro", "MacBook Air M3"})

    def test_display_nykaa_products(self):
        intent = detect_sales_intent_local("Display Nykaa Products")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = [p["name"] for p in matched]
        self.assertEqual(names, ["Nykaa Face Serum"])

    def test_find_samsung_mobiles(self):
        intent = detect_sales_intent_local("Find Samsung Mobiles")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = [p["name"] for p in matched]
        self.assertEqual(names, ["Samsung Galaxy S24 Ultra"])

    def test_suggest_samsung_phones(self):
        intent = detect_sales_intent_local("Suggest Samsung Phones")
        matched = find_matching_products(
            intent["product_query"],
            intent["category"],
            SAMPLE_PRODUCTS,
            intent.get("brand"),
        )
        names = [p["name"] for p in matched]
        self.assertEqual(names, ["Samsung Galaxy S24 Ultra"])

    def test_process_sales_query_list_samsung_without_gemini(self):
        result = process_sales_query(None, "List Samsung Products", SAMPLE_PRODUCTS)
        names = [p["name"] for p in result["products"]]
        self.assertEqual(names, ["Samsung Galaxy S24 Ultra"])
        self.assertNotIn("iPhone 15 Pro", names)

    def test_unknown_brand_returns_empty(self):
        result = process_sales_query(None, "List Google Products", SAMPLE_PRODUCTS)
        self.assertEqual(result["products"], [])
        self.assertIn("No products found", result["reply"])


if __name__ == "__main__":
    unittest.main()
