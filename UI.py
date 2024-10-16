import random
import requests
from woocommerce import API
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import threading

# تابع برای افزودن نظرات به محصولات
def add_reviews(wcapi, names, comments, min_rating, max_rating, selected_products, num_reviews):
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

    i = 0
    total_reviews = len(all_products) * num_reviews if selected_products is None else len(selected_products) * num_reviews
    progress_var.set(0)
    progress_bar['maximum'] = total_reviews

    for product in all_products:
        if selected_products and product['id'] not in selected_products:
            continue

        for _ in range(num_reviews):
            i += 1

            product_id = product['id']
            reviewer_name = random.choice(names)
            review_content = random.choice(comments)
            rating = random.randint(min_rating, max_rating)  # امتیاز بین min_rating و max_rating

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
            
            progress_var.set(i)
            progress_bar.update()

# تابع برای شروع فرآیند افزودن نظرات به صورت همزمان
def start_add_reviews():
    url = url_entry.get()
    consumer_key = consumer_key_entry.get()
    consumer_secret = consumer_secret_entry.get()
    min_rating = int(min_rating_entry.get())
    max_rating = int(max_rating_entry.get())
    num_reviews = int(num_reviews_entry.get())
    
    if not url or not consumer_key or not consumer_secret:
        messagebox.showerror("خطا", "لطفاً تمامی اطلاعات مورد نیاز را وارد کنید.")
        return

    wcapi = API(
        url=url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        version="wc/v3"
    )

    try:
        with open(names_file_path.get(), 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f]

        with open(comments_file_path.get(), 'r', encoding='utf-8') as f:
            comments = [line.strip() for line in f]

        selected_products = product_selection.get() if product_selection.get() != "همه محصولات" else None
        if selected_products:
            selected_products = [int(pid) for pid in selected_products.split(',')]

        # اجرای تابع افزودن نظرات در یک رشته جدید برای جلوگیری از بلاک شدن رابط کاربری
        threading.Thread(target=add_reviews, args=(wcapi, names, comments, min_rating, max_rating, selected_products, num_reviews)).start()
    except Exception as e:
        messagebox.showerror("خطا", f"خطایی رخ داد: {str(e)}")

# تابع برای انتخاب فایل
def select_file(entry):
    file_path = filedialog.askopenfilename()
    entry.set(file_path)

# تابع برای ذخیره تنظیمات
def save_settings():
    settings = {
        "url": url_entry.get(),
        "consumer_key": consumer_key_entry.get(),
        "consumer_secret": consumer_secret_entry.get(),
        "names_file": names_file_path.get(),
        "comments_file": comments_file_path.get(),
        "min_rating": min_rating_entry.get(),
        "max_rating": max_rating_entry.get(),
        "num_reviews": num_reviews_entry.get()
    }
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f)
    messagebox.showinfo("ذخیره تنظیمات", "تنظیمات ذخیره شدند.")

# تابع برای بارگذاری تنظیمات
def load_settings():
    if os.path.exists("settings.json"):
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            url_entry.insert(0, settings.get("url", ""))
            consumer_key_entry.insert(0, settings.get("consumer_key", ""))
            consumer_secret_entry.insert(0, settings.get("consumer_secret", ""))
            names_file_path.set(settings.get("names_file", ""))
            comments_file_path.set(settings.get("comments_file", ""))
            min_rating_entry.insert(0, settings.get("min_rating", "1"))
            max_rating_entry.insert(0, settings.get("max_rating", "5"))
            num_reviews_entry.insert(0, settings.get("num_reviews", "1"))

# رابط کاربری گرافیکی با استفاده از tkinter
root = tk.Tk()
root.title("WooCommerce Random Reviews Generator")
root.state('zoomed')  # Fullscreen window
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#ccc")
style.configure("TLabel", padding=6, background="#f0f0f0", font=("Segoe UI", 12))
style.configure("TEntry", padding=6, font=("Segoe UI", 12))

# تنظیمات ووکامرس
main_frame = ttk.Frame(root, padding=(20, 10, 20, 10))
main_frame.pack(expand=True, fill="both")

# تنظیمات ووکامرس
ttk.Label(main_frame, text="آدرس فروشگاه ووکامرس:").grid(row=0, column=0, sticky="W", pady=5, padx=5)
url_entry = ttk.Entry(main_frame, width=50)
url_entry.grid(row=0, column=1, pady=5, padx=5, sticky="EW")

# کلید مصرف‌کننده و رمز مصرف‌کننده
ttk.Label(main_frame, text="کلید مصرف‌کننده (Consumer Key):").grid(row=1, column=0, sticky="W", pady=5, padx=5)
consumer_key_entry = ttk.Entry(main_frame, width=50)
consumer_key_entry.grid(row=1, column=1, pady=5, padx=5, sticky="EW")

ttk.Label(main_frame, text="رمز مصرف‌کننده (Consumer Secret):").grid(row=2, column=0, sticky="W", pady=5, padx=5)
consumer_secret_entry = ttk.Entry(main_frame, width=50)
consumer_secret_entry.grid(row=2, column=1, pady=5, padx=5, sticky="EW")

# فایل‌های متنی
names_file_path = tk.StringVar()
comments_file_path = tk.StringVar()

ttk.Label(main_frame, text="فایل نام‌ها (names.txt):").grid(row=3, column=0, sticky="W", pady=5, padx=5)
ttk.Entry(main_frame, textvariable=names_file_path, width=50).grid(row=3, column=1, pady=5, padx=5, sticky="EW")
ttk.Button(main_frame, text="انتخاب فایل", command=lambda: select_file(names_file_path)).grid(row=3, column=2, pady=5, padx=5)

ttk.Label(main_frame, text="فایل دیدگاه‌ها (comments.txt):").grid(row=4, column=0, sticky="W", pady=5, padx=5)
ttk.Entry(main_frame, textvariable=comments_file_path, width=50).grid(row=4, column=1, pady=5, padx=5, sticky="EW")
ttk.Button(main_frame, text="انتخاب فایل", command=lambda: select_file(comments_file_path)).grid(row=4, column=2, pady=5, padx=5)

# محدوده امتیازها
ttk.Label(main_frame, text="حداقل امتیاز:").grid(row=5, column=0, sticky="W", pady=5, padx=5)
min_rating_entry = ttk.Entry(main_frame, width=10)
min_rating_entry.grid(row=5, column=1, pady=5, padx=5, sticky="W")
min_rating_entry.insert(0, "1")

ttk.Label(main_frame, text="حداکثر امتیاز:").grid(row=6, column=0, sticky="W", pady=5, padx=5)
max_rating_entry = ttk.Entry(main_frame, width=10)
max_rating_entry.grid(row=6, column=1, pady=5, padx=5, sticky="W")
max_rating_entry.insert(0, "5")

# تعداد نظرات برای هر محصول
ttk.Label(main_frame, text="تعداد نظرات برای هر محصول:").grid(row=7, column=0, sticky="W", pady=5, padx=5)
num_reviews_entry = ttk.Entry(main_frame, width=10)
num_reviews_entry.grid(row=7, column=1, pady=5, padx=5, sticky="W")
num_reviews_entry.insert(0, "1")

# انتخاب محصولات
ttk.Label(main_frame, text="انتخاب محصولات (شناسه‌ها را با کاما جدا کنید، یا 'همه محصولات'):").grid(row=8, column=0, sticky="W", pady=5, padx=5)
product_selection = ttk.Entry(main_frame, width=50)
product_selection.grid(row=8, column=1, pady=5, padx=5, sticky="EW")
product_selection.insert(0, "همه محصولات")

# نوار پیشرفت
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
progress_bar.grid(row=9, column=0, columnspan=3, pady=10, padx=5, sticky="EW")

# دکمه‌ها
ttk.Button(main_frame, text="شروع افزودن نظرات", command=start_add_reviews).grid(row=10, column=0, columnspan=2, pady=20, padx=5, sticky="EW")
ttk.Button(main_frame, text="ذخیره تنظیمات", command=save_settings).grid(row=11, column=0, columnspan=2, pady=5, padx=5, sticky="EW")

main_frame.columnconfigure(1, weight=1)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# بارگذاری تنظیمات
load_settings()

root.mainloop()