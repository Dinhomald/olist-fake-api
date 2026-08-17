# Olist Fake API

API FastAPI que expõe os datasets públicos da Olist (e-commerce brasileiro) paginados via HTTP, para uso em testes e prototipagem sem precisar de banco de dados.

## Endpoints

`GET /orders`, `/order_items`, `/customers`, `/products`, `/sellers`, `/payments`, `/reviews`, `/geolocation`, `/category_translation` — todos aceitam `?page=N` (padrão 1, 100 registros por página).

## Rodando localmente

```
pip install -r requirements.txt
uvicorn main:app --reload
```
