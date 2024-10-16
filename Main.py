import random
import requests
from woocommerce import API

# تنظیمات ووکامرس
print("Initializing WooCommerce API connection...")
wcapi = API(
    url="https://yourstore.com",  # URL فروشگاه ووکامرس خود را جایگزین کنید
    consumer_key="your_consumer_key",  # کلید مصرف‌کننده خود را جایگزین کنید
    consumer_secret="your_consumer_secret",  # رمز مصرف‌کننده خود را جایگزین کنید
    version="wc/v3"
)
print("WooCommerce API connection initialized.")

# بارگذاری فایل‌های متنی
print("Loading names from names.txt...")
with open('names.txt', 'r', encoding='utf-8') as f:
    names = [line.strip() for line in f]
print(f"Loaded {len(names)} names from names.txt.")

print("Loading comments from comments.txt...")
with open('comments.txt', 'r', encoding='utf-8') as f:
    comments = [line.strip() for line in f]
print(f"Loaded {len(comments)} comments from comments.txt.")

# دریافت لیست محصولات
print("Fetching list of all products...")
all_products = []
page = 1
while True:
    response = wcapi.get("products", params={"per_page": 100, "page": page})
    if response.status_code == 200:
        products = response.json()
        if not products:
            break
        all_products.extend(products)
        page += 1
    else:
        print("خطا در دریافت لیست محصولات")
        print(f"Status Code: {response.status_code}, Response: {response.text}")
        exit()
print(f"Fetched {len(all_products)} products.")

# افزودن نظرات به محصولات
i = 0
print(f'All Product are {len(all_products)}')
for product in all_products:
    i += 1

    product_id = product['id']
    reviewer_name = random.choice(names)
    review_content = random.choice(comments)
    rating = 5

    print(f"{i} --> Adding review to product ID {product_id}...")
    data = {
        "product_id": product_id,
        "review": review_content,
        "reviewer": reviewer_name,
        "reviewer_email": f"{reviewer_name.lower().replace(' ', '')}@Gmail.com",
        "rating": rating,
        "status": "approved"  # تایید نظر به صورت خودکار
    }

    review_response = wcapi.post("products/reviews", data)
    if review_response.status_code == 201:
        print(f"Review successfully added to product ID {product_id}.")
    else:
        print(f"خطا در افزودن نظر به محصول {product_id}")
        print(f"Status Code: {review_response.status_code}, Response: {review_response.text}")