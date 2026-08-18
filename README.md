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

## Desafios técnicos e decisões de arquitetura

### 1. Segfault do Uvicorn ao usar `parse_dates` do pandas

**Problema:** `uvicorn main:app` morria silenciosamente ao subir — sem traceback, sem log, o processo simplesmente sumia do Gerenciador de Tarefas e o terminal voltava ao prompt.

**Diagnóstico:** rodei o comando com `timeout` e capturei o exit code, que veio `139` (segmentation fault — crash em código nativo, não uma exceção Python). Isolei por eliminação, comentando cada `pd.read_csv` do módulo um de cada vez, até restringir o gatilho especificamente ao uso do parâmetro `parse_dates`.

**Causa raiz:** incompatibilidade binária entre `pandas==2.2.2` (fixado no `requirements.txt`) e `numpy 2.5.2` (puxado como dependência transitiva, sem versão fixada). A ABI C do parser de datetime do pandas 2.2.2 não é compatível com a série numpy 2.5.x, causando corrupção de memória nesse caminho de código específico.

**Solução:** fixei `pandas==2.3.3` no `requirements.txt` — versão compatível com numpy 2.x — eliminando a ambiguidade de versão transitiva.

### 2. Valores nulos aparecendo como string `"NaT"` em vez de `null` no JSON

**Problema:** campos de data vazios (ex: pedidos sem `order_delivered_carrier_date` registrado) retornavam a string literal `"NaT"` na resposta da API, em vez de `null`.

**Diagnóstico:** reproduzi o caso isoladamente em uma DataFrame de teste, comparando o resultado de `.where(pd.notnull(df), None)` direto contra o mesmo `.where()` precedido de `.astype(object)`.

**Causa raiz:** pandas preserva o dtype `datetime64` da coluna mesmo quando se tenta substituir valores nulos por `None` via `.where()` — o dtype da coluna força a reconversão do `None` de volta para `NaT`.

**Solução:** converti a fatia para dtype `object` antes do `.where()`, o que permite que o `None` seja preservado de fato e corretamente serializado como `null` pelo FastAPI.

### 3. Processo Uvicorn "fantasma" mascarando correções de código

**Problema:** depois de corrigir o bug do `NaT`, a API continuava retornando a versão antiga do comportamento mesmo após editar e salvar o código e subir o servidor de novo.

**Causa raiz:** um processo `uvicorn` anterior ainda estava vivo, ocupando a porta 8000. O processo novo falhava ao tentar bindar nessa porta e encerrava, mas esse erro ficava mascarado porque o processo antigo continuava no ar e respondendo às requisições normalmente.

**Solução:** adotei como prática padrão verificar `netstat -ano | findstr :8000` (ou o Gerenciador de Tarefas) antes de subir o servidor, garantindo que não há processo residual ocupando a porta.

### 4. Paginação incompatível com a Pagination Rule do Azure Data Factory

**Problema:** o consumo da API via Azure Data Factory usa uma Pagination Rule do tipo `AbsoluteUrl` com origem `Body`, que extrai a URL da próxima página direto da resposta via JSONPath (ex: `$.next_page_url`). Esse mecanismo do ADF não suporta expressões condicionais/computadas — ele só sabe ler um valor que já venha pronto no JSON.

**Causa raiz:** a API só retornava `page`, `total_pages` e `has_next`, deixando o cálculo da URL da próxima página a cargo do cliente. Isso funciona para um cliente que sabe montar URLs, mas não para o ADF, que só sabe copiar um campo.

**Solução:** o servidor agora calcula e retorna a URL completa da próxima página. `paginate()` passou a receber um `request_path` (o path de cada endpoint, ex: `/orders`) e monta `next_page_url` como `https://olist-fake-api.onrender.com{request_path}?page={page+1}` quando há próxima página, ou `null` na última página — pronto para o ADF consumir via `$.next_page_url` sem precisar de nenhuma lógica adicional.
