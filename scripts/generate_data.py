import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # fixed seed = same result every run

# ---------- 1. PRODUCTS (40 items) ----------
categories = {
    "Electronics": ["Earphones", "Power Bank", "Wireless Mouse", "Keyboard", "Webcam", "Mini Speaker", "Charger", "Smartwatch"],
    "Fashion": ["Plain T-Shirt", "Dress Shirt", "Jacket", "Jeans", "Sneakers", "Backpack", "Cap", "Scarf"],
    "Home & Living": ["Rice Cooker", "Blender", "LED Lamp", "Cookware Set", "Water Dispenser", "Robot Vacuum", "Electric Fan", "Electric Kettle"],
    "Beauty": ["Face Serum", "Sunscreen", "Lipstick", "Moisturizer", "Face Wash", "Perfume", "Face Mask", "Shampoo"],
    "Sports": ["Yoga Mat", "Dumbbell", "Water Bottle", "Running Shoes", "Badminton Racket", "Gym Gloves", "Jump Rope", "Jersey"],
}
rows = []
pid = 1
for cat, items in categories.items():
    for name in items:
        price = int(rng.integers(30, 1500)) * 1000  # IDR 30k - 1.5M
        rows.append([f"P{pid:03d}", name, cat, price])
        pid += 1
products = pd.DataFrame(rows, columns=["product_id", "product_name", "category", "price"])

# ---------- 2. CUSTOMERS (500) ----------
cities = ["Jakarta", "Surabaya", "Bandung", "Medan", "Pekanbaru", "Makassar", "Semarang", "Yogyakarta", "Palembang", "Denpasar"]
city_weights = [0.25, 0.14, 0.12, 0.09, 0.07, 0.07, 0.08, 0.06, 0.07, 0.05]
n_cust = 500
customers = pd.DataFrame({
    "customer_id": [f"C{i:04d}" for i in range(1, n_cust + 1)],
    "city": rng.choice(cities, n_cust, p=city_weights),
    "gender": rng.choice(["Male", "Female"], n_cust, p=[0.45, 0.55]),
    "age": np.clip(rng.normal(30, 8, n_cust).round(), 17, 60).astype(int),
    "signup_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 730, n_cust), unit="D"),
})

# ---------- 3. ORDERS ----------
n_ord = 5000
dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 731, n_ord), unit="D")
# seasonality: more sales in Nov-Dec (hidden pattern to discover)
season = pd.Series(dates.month).map(lambda m: 1.8 if m in (11, 12) else 1.0).values
keep = rng.random(n_ord) < (season / 1.8)
dates = dates[keep]
n_ord = len(dates)

orders = pd.DataFrame({
    "order_id": [f"ORD{i:05d}" for i in range(1, n_ord + 1)],
    "order_date": dates,
    "customer_id": rng.choice(customers["customer_id"], n_ord),
    "product_id": rng.choice(products["product_id"], n_ord),
    "quantity": rng.choice([1, 2, 3, 4, 5], n_ord, p=[0.55, 0.25, 0.1, 0.06, 0.04]),
    "discount_pct": rng.choice([0, 5, 10, 15, 20], n_ord, p=[0.5, 0.15, 0.15, 0.1, 0.1]),
    "payment_method": rng.choice(["Bank Transfer", "E-Wallet", "COD", "Credit Card"], n_ord, p=[0.3, 0.4, 0.2, 0.1]),
    "status": rng.choice(["Completed", "Cancelled", "Returned"], n_ord, p=[0.88, 0.08, 0.04]),
}).sort_values("order_date").reset_index(drop=True)
orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")

# ---------- 4. INTENTIONALLY MESSY (cleaning practice) ----------
# a) missing values in city
idx = rng.choice(customers.index, 25, replace=False)
customers.loc[idx, "city"] = np.nan
# b) inconsistent text casing
idx = rng.choice(customers.index, 30, replace=False)
customers.loc[idx, "city"] = customers.loc[idx, "city"].str.upper()
idx = rng.choice(orders.index, 80, replace=False)
orders.loc[idx, "payment_method"] = orders.loc[idx, "payment_method"].str.lower()
# c) duplicate rows
orders = pd.concat([orders, orders.sample(40, random_state=1)]).sort_values("order_id").reset_index(drop=True)
# d) outliers (unrealistic quantity)
idx = rng.choice(orders.index, 5, replace=False)
orders.loc[idx, "quantity"] = 99
# e) missing values in status
idx = rng.choice(orders.index, 30, replace=False)
orders.loc[idx, "status"] = np.nan

customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")

# ---------- 5. SAVE ----------
products.to_csv("products.csv", index=False)
customers.to_csv("customers.csv", index=False)
orders.to_csv("orders.csv", index=False)
print(len(products), len(customers), len(orders))
