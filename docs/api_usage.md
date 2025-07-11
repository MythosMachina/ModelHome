# MyLora REST API

This guide describes all remote API endpoints exposed by MyLora. Replace
`{serverip}` with the address of your running instance.

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `GET`  | `/search` | Query LoRA metadata |
| `GET`  | `/grid_data` | Metadata with categories and a preview image |
| `GET`  | `/categories` | List existing categories |
| `POST` | `/categories` | Create a new category |
| `POST` | `/assign_category` | Assign a LoRA to a category |
| `POST` | `/assign_categories` | Assign multiple LoRAs to a category |
| `POST` | `/unassign_category` | Remove a LoRA from a category |
| `POST` | `/upload` | Upload one or more `.safetensors` files |
| `POST` | `/upload_previews` | Upload preview images or a preview zip |
| `POST` | `/delete_category` | Delete a category |
| `POST` | `/delete` | Delete LoRA or preview files |

Currently only the `GET` and `POST` HTTP verbs are used.

## 1. `/search` (GET)

Search LoRA metadata using an SQLite full text query.

**Parameters**

- `query`: search term or FTS expression
- `limit`: optional maximum number of results
- `offset`: start position for paging

**Example call**

```bash
curl "http://{serverip}:5000/search?query=lora"
```

**Example response**

```json
[
  {
    "filename": "awesome_lora.safetensors",
    "name": "awesome_lora",
    "architecture": "LoRA",
    "tags": "cute,cat",
    "base_model": "sd15"
  }
]
```

## 2. `/grid_data` (GET)

Return search results including category information and a random preview image.

**Parameters**

- `q`: search query (default `*`)
- `category`: optional category ID
- `limit`: items per page (default `50`)
- `offset`: paging offset

**Example call**

```bash
curl "http://{serverip}:5000/grid_data?q=cat&limit=20"
```

**Example response**

```json
[
  {
    "filename": "awesome_lora.safetensors",
    "name": "awesome_lora",
    "architecture": "LoRA",
    "tags": "cute,cat",
    "base_model": "sd15",
    "categories": ["Animals"],
    "preview_url": "/uploads/awesome_lora.png"
  }
]
```

## 3. `/categories` (GET)

List all categories. If uncategorised LoRAs exist, a dynamic "No Category" entry
is added with the ID `0`.

**Example call**

```bash
curl "http://{serverip}:5000/categories"
```

**Example response**

```json
[
  {"id": 1, "name": "Animals"},
  {"id": 2, "name": "Portraits"}
]
```

## 4. `/categories` (POST)

Create a new category by posting its name as form data.

**Parameters**

- `name`: category name

**Example call**

```bash
curl -X POST -F "name=Landscapes" http://{serverip}:5000/categories
```

**Example response**

```json
{"id": 3}
```

## 5. `/assign_category` (POST)

Assign an existing LoRA file to a category.

**Parameters**

- `filename`: LoRA filename
- `category_id`: ID returned from `/categories`

**Example call**

```bash
curl -X POST -F "filename=awesome_lora.safetensors" -F "category_id=1" \
  http://{serverip}:5000/assign_category
```

**Example response**

```json
{"status": "ok"}
```

## 6. `/assign_categories` (POST)

Assign multiple LoRA files to a category.

**Parameters**

- `files`: one or more LoRA filenames
- `category_id`: existing category ID
- `new_category`: optional name to create

**Example call**

```bash
curl -X POST -F "files=a.safetensors" -F "files=b.safetensors" \
  -F "category_id=1" http://{serverip}:5000/assign_categories
```

**Example response**

```json
{"status": "ok"}
```

## 7. `/unassign_category` (POST)

Remove a LoRA file from the given category.

**Parameters**

- `filename`: LoRA filename
- `category_id`: ID of the category to remove

**Example call**

```bash
curl -X POST -F "filename=awesome_lora.safetensors" -F "category_id=1" \
  http://{serverip}:5000/unassign_category
```

**Example response**

```json
{"status": "ok"}
```

## 8. `/upload` (POST)

Upload one or more `.safetensors` files. The request must be a multipart form
with `files` as the field name. If a file with the exact same name already
exists the request fails with HTTP status `409`.

**Example call**

```bash
curl -X POST -F "files=@awesome_lora.safetensors" \
  http://{serverip}:5000/upload
```

**Example response**

```json
[
  {
    "filename": "awesome_lora.safetensors",
    "name": "awesome_lora",
    "architecture": "LoRA",
    "tags": "cute,cat",
    "base_model": "sd15"
  }
]
```

## 9. `/upload_previews` (POST)

Upload preview images. Send the images as the multipart `files` field. You can
also upload a ZIP archive containing previews.

**Example call**

```bash
curl -X POST -F "files=@previews.zip" http://{serverip}:5000/upload_previews
```

**Example response**

```json
{"status": "ok"}
```

## 10. `/delete_category` (POST)

Delete a category by its ID.

**Parameters**

- `category_id`: ID of the category

**Example call**

```bash
curl -X POST -F "category_id=3" http://{serverip}:5000/delete_category
```

**Example response**

```json
{"status": "ok"}
```

## 11. `/delete` (POST)

Delete LoRA or preview files. Provide one or more `files` values as form data.

**Example call**

```bash
curl -X POST -F "files=awesome_lora.safetensors" \
  http://{serverip}:5000/delete
```

**Example response**

```json
{"deleted": ["awesome_lora.safetensors"]}
```

---

All endpoints run on port `5000` and return JSON unless noted otherwise.
