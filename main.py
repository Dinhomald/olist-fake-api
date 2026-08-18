from fastapi import FastAPI, Query, HTTPException
import pandas as pd

app = FastAPI(title="Olist Fake API", version="1.0")

orders_df = pd.read_csv("data/olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_approved_at",
    "order_delivered_carrier_date", "order_delivered_customer_date",
    "order_estimated_delivery_date"
])

order_items_df = pd.read_csv("data/olist_order_items_dataset.csv")
customers_df = pd.read_csv("data/olist_customers_dataset.csv")
products_df = pd.read_csv("data/olist_products_dataset.csv")
sellers_df = pd.read_csv("data/olist_sellers_dataset.csv")
payments_df = pd.read_csv("data/olist_order_payments_dataset.csv")
reviews_df = pd.read_csv("data/olist_order_reviews_dataset.csv", parse_dates=[
    "review_creation_date", "review_answer_timestamp"
])
geolocation_df = pd.read_csv("data/olist_geolocation_dataset.csv")
category_translation_df = pd.read_csv("data/product_category_name_translation.csv")

def paginate(df: pd.DataFrame, page: int, request_path: str, page_size: int = 100):
    total_records = len(df)
    total_pages = (total_records + page_size - 1) // page_size

    if page > total_pages and total_pages > 0:
        raise HTTPException(status_code=404, detail=f"page {page} não existe. total_pages={total_pages}")

    start = (page - 1) * page_size
    end = start + page_size
    subset = df.iloc[start:end]
    data = subset.astype(object).where(pd.notnull(subset), None).to_dict(orient="records")

    has_next = page < total_pages
    next_page_url = f"https://olist-fake-api.onrender.com{request_path}?page={page + 1}" if has_next else None

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": total_pages,
        "has_next": has_next,
        "next_page_url": next_page_url,
        "data": data
    }

@app.get("/orders")
def get_orders(page: int = Query(1, ge=1)):
    return paginate(orders_df, page, "/orders")


@app.get("/order_items")
def get_order_items(page: int = Query(1, ge=1)):
    return paginate(order_items_df, page, "/order_items")


@app.get("/customers")
def get_customers(page: int = Query(1, ge=1)):
    return paginate(customers_df, page, "/customers")


@app.get("/products")
def get_products(page: int = Query(1, ge=1)):
    return paginate(products_df, page, "/products")


@app.get("/sellers")
def get_sellers(page: int = Query(1, ge=1)):
    return paginate(sellers_df, page, "/sellers")


@app.get("/payments")
def get_payments(page: int = Query(1, ge=1)):
    return paginate(payments_df, page, "/payments")


@app.get("/reviews")
def get_reviews(page: int = Query(1, ge=1)):
    return paginate(reviews_df, page, "/reviews")


@app.get("/geolocation")
def get_geolocation(page: int = Query(1, ge=1)):
    return paginate(geolocation_df, page, "/geolocation")


@app.get("/category_translation")
def get_category_translation(page: int = Query(1, ge=1)):
    return paginate(category_translation_df, page, "/category_translation")


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Olist Fake API rodando"}