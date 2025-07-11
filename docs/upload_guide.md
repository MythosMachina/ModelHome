# Uploading LoRA Files

This guide explains the different ways to upload `.safetensors` models and their preview images to a running MyLora instance. All examples assume the server is available at `http://{serverip}:5000`.

## 1. Using the Upload Wizard

1. Open your browser and navigate to `http://{serverip}:5000/upload_wizard`.
2. **Step 1** – Click the drop area or drag a single `.safetensors` file onto the page.
3. Press **Upload** to send the file. A progress bar shows the upload status.
4. After the model file was uploaded you are asked to upload previews.
5. **Step 2** – Drag one or more image files (`.png`, `.jpg`, `.jpeg`, `.gif`) or a ZIP archive containing them.
6. Click **Upload Previews**. Once finished you will be redirected to the detail page of the uploaded LoRA where you can assign categories.

The wizard is the easiest way when you want to upload a new LoRA along with its images in one flow.

## 2. Uploading with the simple forms

Two separate pages are available for small manual uploads:

- `http://{serverip}:5000/upload` – Select one or multiple `.safetensors` files and submit the form. If a file with the same name already exists the upload is rejected with an error.
- `http://{serverip}:5000/upload_previews` – Upload preview images for an existing LoRA or a ZIP archive containing previews. If you pass a `lora` query parameter the form will automatically target that LoRA.

After sending the previews you can go to `/detail/<filename>` to review the images and metadata.

## 3. Uploading from the command line

The same endpoints can be used with tools like `curl`.

```bash
# Upload a LoRA file
curl -X POST -F "files=@awesome_lora.safetensors" \
  http://{serverip}:5000/upload

# Upload previews for that LoRA
curl -X POST -F "files=@preview1.png" -F "files=@preview2.png" \
  -F "lora=awesome_lora" \
  http://{serverip}:5000/upload_previews
```

## 4. After uploading

Uploaded files are stored under `loradb/uploads`. The web interface automatically extracts metadata and indexes the LoRA so it appears in the gallery. You can manage categories from the LoRA's detail page or via the `/category_admin` view.
