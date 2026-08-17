# Olist Fake API

API FastAPI que expõe os datasets públicos da Olist (e-commerce brasileiro) paginados via HTTP, para uso em testes e prototipagem sem precisar de banco de dados.

## Endpoints

`GET /orders`, `/order_items`, `/customers`, `/products`, `/sellers`, `/payments`, `/reviews`, `/geolocation`, `/category_translation` — todos aceitam `?page=N` (padrão 1, 100 registros por página).

## Fonte dos dados

Dataset público "Brazilian E-Commerce Public Dataset by Olist", disponível no Kaggle:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Usado exclusivamente para fins educacionais/portfólio, simulando uma fonte de API real.

## Rodando localmente

```
pip install -r requirements.txt
uvicorn main:app --reload
```
