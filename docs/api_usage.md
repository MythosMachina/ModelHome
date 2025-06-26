# MyLora REST API

This page provides a short overview of the available GET endpoints.
Replace `{serverip}` with the actual IP address of your MyLora instance.

## 1. `/search`
Search LoRA metadata using an SQLite FTS query.

**Parameters**
- `query`: search term or FTS expression
- `limit`: optional maximum number of results
- `offset`: start position for paging

**Example**
```bash
curl "http://{serverip}:5000/search?query=*"
```
Returns a JSON list with fields `filename`, `name`, `architecture`, `tags` and `base_model`.

## 2. `/grid_data`
Similar to `/search` but includes categories and a random preview image.

**Parameters**
- `q`: search query (default `*`)
- `category`: optional category ID
- `limit`: results per page (default 50)
- `offset`: paging offset

**Example**
```bash
curl "http://{serverip}:5000/grid_data?q=dog&category=2"
```
Each list entry contains the `/search` fields plus `categories` and `preview_url`.

## 3. `/categories`
List all categories. If uncategorised LoRAs exist, a dynamic "No Category" entry is included.

**Example**
```bash
curl "http://{serverip}:5000/categories"
```
Returns a JSON list of objects with `id` and `name`.

---
All endpoints are served by FastAPI on port `5000`.
