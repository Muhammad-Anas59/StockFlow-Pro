# barcode_gen.py
import barcode
from barcode.writer import ImageWriter
import os

BARCODE_FOLDER = "barcodes"

def ensure_folder():
    if not os.path.exists(BARCODE_FOLDER):
        os.makedirs(BARCODE_FOLDER)

def generate_barcode(value, filename_prefix):
    """
    Generates a Code128 barcode image for the given value.
    Returns the full file path of the saved PNG.
    """
    ensure_folder()
    code128 = barcode.get_barcode_class('code128')
    barcode_obj = code128(value, writer=ImageWriter())
    filepath = os.path.join(BARCODE_FOLDER, filename_prefix)
    saved_path = barcode_obj.save(filepath)
    return saved_path
def generate_sku_barcode(product_id, sku_name):
    """
    Generates a barcode for a product SKU, tied permanently to product_id.
    Filename is ID-only, so re-generating always overwrites the same file
    instead of creating duplicates when the name changes.
    """
    barcode_value = f"SKU-{product_id:05d}"
    filename = f"sku_{product_id}"
    filepath = generate_barcode(barcode_value, filename)
    return barcode_value, filepath

def generate_carton_barcode(carton_id, sku_name):
    """
    Generates a barcode for a specific carton.
    Example: generate_carton_barcode(12, "HC2") -> barcode value "CTN-HC2-12"
    """
    barcode_value = f"CTN-{sku_name}-{carton_id}"
    filename = f"carton_{carton_id}_{sku_name}"
    filepath = generate_barcode(barcode_value, filename)
    return barcode_value, filepath
if __name__ == "__main__":
    val, path = generate_sku_barcode(1, "HC2")
    print(f"Generated: {val} -> saved at {path}")