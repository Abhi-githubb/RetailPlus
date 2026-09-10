"""
Synthetic Data Generator for RetailPulse E-Commerce Analytics Platform.
Generates 100,000+ orders, 20,000+ customers, 500+ products across 2+ years
with realistic business distributions, seasonality, and controlled anomalies
for the ETL data-quality pipeline to audit and clean.
"""

import os
import random
from datetime import datetime, timedelta
from typing import Dict, Tuple
import numpy as np
import pandas as pd
from src.utils.logger import logger
from src.utils.config import RAW_DATA_DIR

# Seed for reproducibility
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

CATEGORIES_CONFIG = {
    "Electronics": {
        "subcategories": ["Smartphones", "Laptops", "Audio & Headphones", "Wearables", "Accessories"],
        "price_range": (35.0, 1499.0),
        "cost_ratio": 0.65,
        "return_rate": 0.07,
    },
    "Apparel": {
        "subcategories": ["Men's Clothing", "Women's Clothing", "Footwear", "Activewear", "Outerwear"],
        "price_range": (19.99, 299.99),
        "cost_ratio": 0.40,
        "return_rate": 0.16,
    },
    "Home & Kitchen": {
        "subcategories": ["Cookware", "Small Appliances", "Bedding", "Furniture", "Home Decor"],
        "price_range": (15.0, 650.0),
        "cost_ratio": 0.50,
        "return_rate": 0.08,
    },
    "Beauty & Personal Care": {
        "subcategories": ["Skincare", "Haircare", "Fragrances", "Cosmetics", "Bath & Body"],
        "price_range": (12.0, 180.0),
        "cost_ratio": 0.35,
        "return_rate": 0.04,
    },
    "Sports & Outdoors": {
        "subcategories": ["Fitness Equipment", "Outdoor Recreation", "Cycling", "Team Sports", "Water Sports"],
        "price_range": (25.0, 850.0),
        "cost_ratio": 0.55,
        "return_rate": 0.06,
    },
    "Books & Media": {
        "subcategories": ["Fiction", "Non-Fiction", "Technical & Business", "Audiobooks", "Children's Books"],
        "price_range": (9.99, 65.0),
        "cost_ratio": 0.45,
        "return_rate": 0.02,
    },
}

REGIONS_CONFIG = {
    "North America": ["United States", "Canada"],
    "Europe": ["United Kingdom", "Germany", "France", "Netherlands", "Sweden"],
    "Asia-Pacific": ["Japan", "Australia", "Singapore", "South Korea", "India"],
    "Latin America": ["Brazil", "Mexico", "Chile", "Colombia"],
    "Middle East": ["United Arab Emirates", "Saudi Arabia", "Qatar"],
}

ACQUISITION_CHANNELS = ["Organic Search", "Paid Search", "Social Media", "Email Marketing", "Referral", "Direct"]
CHANNEL_WEIGHTS = [0.28, 0.24, 0.20, 0.14, 0.08, 0.06]

PAYMENT_METHODS = ["Credit Card", "PayPal", "Apple Pay", "Buy Now Pay Later", "Bank Transfer"]
PAYMENT_WEIGHTS = [0.48, 0.24, 0.14, 0.10, 0.04]

RETURN_REASONS = [
    "Defective or Damaged Item",
    "Size or Fit Issue",
    "Item Not as Described",
    "Changed Mind",
    "Late Delivery",
    "Received Wrong Item",
]
RETURN_REASON_WEIGHTS = [0.28, 0.32, 0.18, 0.12, 0.06, 0.04]

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth",
    "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
    "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra",
    "Donald", "Ashley", "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah",
    "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia",
    "Alexander", "Kathleen", "Gary", "Amy", "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen",
    "Stephen", "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Frank", "Debra", "Alexander", "Rachel",
    "Raymond", "Catherine", "Patrick", "Carolyn", "Jack", "Janet", "Dennis", "Ruth", "Jerry", "Maria",
    "Tyler", "Heather", "Aaron", "Diane", "Jose", "Virginia", "Adam", "Julie", "Henry", "Joyce",
    "Nathan", "Victoria", "Douglas", "Olivia", "Zachary", "Kelly", "Peter", "Christina", "Kyle", "Lauren",
    "Walter", "Joan", "Ethan", "Evelyn", "Jeremy", "Judith", "Harold", "Megan", "Keith", "Cheryl",
    "Christian", "Andrea", "Roger", "Hannah", "Noah", "Martha", "Gerald", "Jacqueline", "Carl", "Frances",
    "Terry", "Gloria", "Sean", "Ann", "Austin", "Teresa", "Arthur", "Kathryn", "Lawrence", "Sara",
    "Jesse", "Janice", "Dylan", "Jean", "Bryan", "Alice", "Joe", "Madison", "Jordan", "Doris",
    "Billy", "Abigail", "Albert", "Julia", "Bruce", "Judy", "Willie", "Grace", "Gabriel", "Denise",
    "Logan", "Amber", "Alan", "Marilyn", "Juan", "Beverly", "Wayne", "Danielle", "Roy", "Theresa",
    "Ralph", "Sophia", "Randy", "Marie", "Eugene", "Diana", "Vincent", "Brittany", "Russell", "Natalie",
    "Louis", "Isabella", "Philip", "Charlotte", "Bobby", "Rose", "Johnny", "Alexis", "Bradley", "Kayla"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long", "Ross", "Foster", "Jimenez",
    "Powell", "Jenkins", "Perry", "Russell", "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes",
    "Gonzales", "Fisher", "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant", "Herrera", "Gibson",
    "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray", "Ford", "Castro", "Marshall", "Owens",
    "Harrison", "Fernandez", "McDonald", "Woods", "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen"
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "hotmail.com", "proton.me", "workmail.com"]


def generate_synthetic_data(
    num_customers: int = 22000,
    num_products: int = 550,
    num_orders: int = 105000,
    start_date: str = "2023-01-01",
    end_date: str = "2025-06-30",
    inject_anomalies: bool = True,
) -> Dict[str, pd.DataFrame]:
    """
    Generates realistic e-commerce datasets:
    - customers
    - products
    - orders
    - order_items
    - payments
    - returns
    """
    logger.info(f"Starting synthetic data generation: {num_customers} customers, {num_products} products, {num_orders} orders.")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days

    # ==========================================
    # 1. CUSTOMERS
    # ==========================================
    logger.info("Generating customers...")
    customer_ids = [f"CUST-{100000 + i}" for i in range(num_customers)]
    first_choice = np.random.choice(FIRST_NAMES, size=num_customers)
    last_choice = np.random.choice(LAST_NAMES, size=num_customers)
    names = [f"{f} {l}" for f, l in zip(first_choice, last_choice)]

    # Signup dates spread over the timeframe (slightly front-loaded)
    signup_day_offsets = np.random.exponential(scale=total_days * 0.45, size=num_customers)
    signup_day_offsets = np.clip(signup_day_offsets, 0, total_days - 30).astype(int)
    signup_dates = [start_dt + timedelta(days=int(d), hours=random.randint(6, 22), minutes=random.randint(0, 59)) for d in signup_day_offsets]

    regions = list(REGIONS_CONFIG.keys())
    region_weights = [0.42, 0.28, 0.16, 0.08, 0.06]
    cust_regions = np.random.choice(regions, size=num_customers, p=region_weights)
    cust_countries = [random.choice(REGIONS_CONFIG[r]) for r in cust_regions]
    cust_channels = np.random.choice(ACQUISITION_CHANNELS, size=num_customers, p=CHANNEL_WEIGHTS)

    emails = []
    for i, (fn, ln) in enumerate(zip(first_choice, last_choice)):
        domain = random.choice(EMAIL_DOMAINS)
        clean_fn = fn.lower().replace("'", "").replace(" ", "")
        clean_ln = ln.lower().replace("'", "").replace(" ", "")
        email = f"{clean_fn}.{clean_ln}{random.randint(10, 999)}@{domain}"
        emails.append(email)

    customers_df = pd.DataFrame({
        "customer_id": customer_ids,
        "name": names,
        "email": emails,
        "signup_date": [d.strftime("%Y-%m-%d %H:%M:%S") for d in signup_dates],
        "country": cust_countries,
        "region": cust_regions,
        "acquisition_channel": cust_channels,
    })

    # ==========================================
    # 2. PRODUCTS
    # ==========================================
    logger.info("Generating products...")
    product_records = []
    prod_id_counter = 1001

    category_list = list(CATEGORIES_CONFIG.keys())
    prods_per_category = num_products // len(category_list)

    adjectives = ["Ultra", "Pro", "Classic", "Premium", "Essential", "Eco", "Smart", "Studio", "Wireless", "Apex"]
    nouns = ["Max", "Plus", "Edition", "Prime", "Series", "Glide", "Wave", "Flow", "Core", "Vibe"]

    for cat_name, cfg in CATEGORIES_CONFIG.items():
        subcats = cfg["subcategories"]
        low_p, high_p = cfg["price_range"]
        cost_ratio = cfg["cost_ratio"]

        for _ in range(prods_per_category):
            subcat = random.choice(subcats)
            adj = random.choice(adjectives)
            noun = random.choice(nouns)
            prod_name = f"{adj} {subcat.rstrip('s')} {noun}"

            # Log-normal distribution for prices within category bounds
            price = round(float(np.random.uniform(low_p, high_p)), 2)
            cost = round(price * float(np.random.uniform(cost_ratio * 0.85, cost_ratio * 1.15)), 2)
            cost = min(cost, round(price * 0.92, 2))  # Ensure cost is below price

            launch_offset = random.randint(0, int(total_days * 0.7))
            launch_date = (start_dt + timedelta(days=launch_offset)).strftime("%Y-%m-%d")

            product_records.append({
                "product_id": f"PROD-{prod_id_counter}",
                "product_name": prod_name,
                "category": cat_name,
                "subcategory": subcat,
                "price": price,
                "cost": cost,
                "launch_date": launch_date,
            })
            prod_id_counter += 1

    # Fill remainder if integer division left some out
    while len(product_records) < num_products:
        cat_name = random.choice(category_list)
        cfg = CATEGORIES_CONFIG[cat_name]
        subcat = random.choice(cfg["subcategories"])
        price = round(float(np.random.uniform(cfg["price_range"][0], cfg["price_range"][1])), 2)
        cost = round(price * cfg["cost_ratio"], 2)
        product_records.append({
            "product_id": f"PROD-{prod_id_counter}",
            "product_name": f"RetailPulse {subcat} Edition",
            "category": cat_name,
            "subcategory": subcat,
            "price": price,
            "cost": cost,
            "launch_date": start_dt.strftime("%Y-%m-%d"),
        })
        prod_id_counter += 1

    products_df = pd.DataFrame(product_records)

    # ==========================================
    # 3. ORDERS & CUSTOMER ACTIVITY
    # ==========================================
    logger.info("Generating orders with realistic purchasing patterns...")
    # Power-law / Pareto customer activity:
    # 20% of customers make 70% of repeat orders; some customers order 1x, some 2-10x
    cust_weights = np.random.pareto(a=1.8, size=num_customers) + 0.1
    cust_weights = cust_weights / cust_weights.sum()

    order_customer_indices = np.random.choice(np.arange(num_customers), size=num_orders, p=cust_weights)

    # Order dates with seasonality (Holiday spike in Nov-Dec, summer spike in July)
    order_dates = []
    logger.info("Simulating seasonal order timestamps...")
    all_dates = [start_dt + timedelta(days=i) for i in range(total_days)]
    seasonal_multipliers = []
    for d in all_dates:
        mult = 1.0
        # Nov & Dec holiday shopping boost
        if d.month in [11, 12]:
            mult *= 1.75
            # Black Friday / Cyber Monday extra boost
            if d.month == 11 and d.day >= 22:
                mult *= 1.4
        elif d.month == 7:  # Mid-year sale
            mult *= 1.25
        # Weekend boost (Saturday/Sunday)
        if d.weekday() in [5, 6]:
            mult *= 1.20
        seasonal_multipliers.append(mult)

    seasonal_probs = np.array(seasonal_multipliers) / sum(seasonal_multipliers)
    selected_day_indices = np.random.choice(np.arange(total_days), size=num_orders, p=seasonal_probs)

    customer_signup_dt_map = {i: signup_dates[i] for i in range(num_customers)}
    customer_region_map = {i: cust_regions[i] for i in range(num_customers)}

    order_records = []
    order_items_records = []
    payment_records = []
    return_records = []

    order_statuses = ["Completed", "Shipped", "Processing", "Cancelled", "Refunded"]
    order_status_weights = [0.81, 0.08, 0.04, 0.04, 0.03]

    prod_ids = products_df["product_id"].values
    prod_prices = dict(zip(products_df["product_id"], products_df["price"]))
    prod_categories = dict(zip(products_df["product_id"], products_df["category"]))

    order_item_id_counter = 1
    payment_id_counter = 1
    return_id_counter = 1

    logger.info("Generating order line items, payments, and return records...")
    for order_idx in range(num_orders):
        order_id = f"ORD-{1000000 + order_idx}"
        c_idx = order_customer_indices[order_idx]
        c_id = customer_ids[c_idx]
        signup_time = customer_signup_dt_map[c_idx]
        order_day = start_dt + timedelta(days=int(selected_day_indices[order_idx]))

        # Ensure order date is on or after signup date
        if order_day < signup_time:
            order_day = signup_time + timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
        else:
            order_day = order_day.replace(hour=random.randint(0, 23), minute=random.randint(0, 59), second=random.randint(0, 59))

        status = np.random.choice(order_statuses, p=order_status_weights)
        shipping_region = customer_region_map[c_idx]
        payment_method = np.random.choice(PAYMENT_METHODS, p=PAYMENT_WEIGHTS)

        # 1 to 4 line items per order
        num_items = np.random.choice([1, 2, 3, 4], p=[0.60, 0.25, 0.10, 0.05])
        chosen_prods = np.random.choice(prod_ids, size=num_items, replace=False)

        order_gross = 0.0
        order_discount = 0.0
        order_has_return = False
        returned_items = []

        for p_id in chosen_prods:
            qty = int(np.random.choice([1, 2, 3], p=[0.78, 0.17, 0.05]))
            unit_price = prod_prices[p_id]
            # Occasional discount between 0% and 20%
            disc_rate = float(np.random.choice([0.0, 0.05, 0.10, 0.15, 0.20], p=[0.65, 0.12, 0.10, 0.08, 0.05]))
            item_disc = round(unit_price * qty * disc_rate, 2)
            item_total = round(unit_price * qty - item_disc, 2)

            order_gross += unit_price * qty
            order_discount += item_disc

            order_items_records.append({
                "order_item_id": f"ITEM-{order_item_id_counter}",
                "order_id": order_id,
                "product_id": p_id,
                "quantity": qty,
                "unit_price": unit_price,
                "discount": item_disc,
            })
            order_item_id_counter += 1

            # Check if this item is returned (only for completed/refunded orders)
            if status in ["Completed", "Refunded"]:
                cat = prod_categories[p_id]
                cat_return_rate = CATEGORIES_CONFIG[cat]["return_rate"]
                if status == "Refunded" or random.random() < cat_return_rate:
                    returned_items.append((p_id, item_total))
                    order_has_return = True

        order_total = round(order_gross - order_discount, 2)
        order_total = max(0.0, order_total)

        order_records.append({
            "order_id": order_id,
            "customer_id": c_id,
            "order_date": order_day.strftime("%Y-%m-%d %H:%M:%S"),
            "order_status": status,
            "shipping_region": shipping_region,
            "payment_method": payment_method,
            "discount": round(order_discount, 2),
            "total_amount": order_total,
        })

        # Payment record
        pay_status = "Success"
        if status == "Cancelled":
            pay_status = np.random.choice(["Failed", "Refunded"], p=[0.7, 0.3])
        elif status == "Refunded":
            pay_status = "Refunded"

        payment_records.append({
            "payment_id": f"PAY-{payment_id_counter}",
            "order_id": order_id,
            "payment_date": (order_day + timedelta(minutes=random.randint(1, 15))).strftime("%Y-%m-%d %H:%M:%S"),
            "payment_method": payment_method,
            "payment_status": pay_status,
            "payment_amount": order_total,
        })
        payment_id_counter += 1

        # Return records
        if order_has_return:
            for p_id, item_amount in returned_items:
                ret_date = order_day + timedelta(days=random.randint(2, 28), hours=random.randint(1, 12))
                reason = np.random.choice(RETURN_REASONS, p=RETURN_REASON_WEIGHTS)
                return_records.append({
                    "return_id": f"RET-{return_id_counter}",
                    "order_id": order_id,
                    "product_id": p_id,
                    "return_date": ret_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "return_reason": reason,
                    "refund_amount": item_amount,
                })
                return_id_counter += 1

    orders_df = pd.DataFrame(order_records)
    order_items_df = pd.DataFrame(order_items_records)
    payments_df = pd.DataFrame(payment_records)
    returns_df = pd.DataFrame(return_records)

    # ==========================================
    # 4. CONTROLLED DIRTY DATA INJECTION
    # ==========================================
    if inject_anomalies:
        logger.info("Injecting controlled data quality anomalies for ETL pipeline to detect...")
        # 1. Missing customer emails (~0.4%)
        null_email_idx = np.random.choice(customers_df.index, size=int(num_customers * 0.004), replace=False)
        customers_df.loc[null_email_idx, "email"] = None

        # 2. Duplicate customer records (~0.2%)
        dup_cust_idx = np.random.choice(customers_df.index, size=int(num_customers * 0.002), replace=False)
        dup_cust = customers_df.loc[dup_cust_idx].copy()
        customers_df = pd.concat([customers_df, dup_cust], ignore_index=True)

        # 3. Duplicate order items (~0.15%)
        dup_item_idx = np.random.choice(order_items_df.index, size=int(len(order_items_df) * 0.0015), replace=False)
        dup_items = order_items_df.loc[dup_item_idx].copy()
        order_items_df = pd.concat([order_items_df, dup_items], ignore_index=True)

        # 4. Whitespace in names
        ws_idx = np.random.choice(customers_df.index, size=50, replace=False)
        customers_df.loc[ws_idx, "name"] = "  " + customers_df.loc[ws_idx, "name"] + "  "

        # 5. A few negative or 0 unit prices in order items to test data quarantine (~0.05%)
        neg_item_idx = np.random.choice(order_items_df.index, size=25, replace=False)
        order_items_df.loc[neg_item_idx, "unit_price"] = -9.99

    logger.info(f"Dataset generation complete:")
    logger.info(f"  Customers:   {len(customers_df):,}")
    logger.info(f"  Products:    {len(products_df):,}")
    logger.info(f"  Orders:      {len(orders_df):,}")
    logger.info(f"  Order Items: {len(order_items_df):,}")
    logger.info(f"  Payments:    {len(payments_df):,}")
    logger.info(f"  Returns:     {len(returns_df):,}")

    return {
        "customers": customers_df,
        "products": products_df,
        "orders": orders_df,
        "order_items": order_items_df,
        "payments": payments_df,
        "returns": returns_df,
    }


def save_raw_datasets(datasets: Dict[str, pd.DataFrame], output_dir: str = None) -> None:
    """Saves raw datasets to CSV files."""
    target_dir = output_dir or str(RAW_DATA_DIR)
    os.makedirs(target_dir, exist_ok=True)
    for table_name, df in datasets.items():
        filepath = os.path.join(target_dir, f"{table_name}_raw.csv")
        df.to_csv(filepath, index=False)
        logger.info(f"Saved raw table to {filepath} ({len(df):,} rows)")


if __name__ == "__main__":
    data = generate_synthetic_data()
    save_raw_datasets(data)
