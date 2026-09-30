from pathlib import Path
def ocr_image(path:str|Path,language="por"):
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e: raise RuntimeError("Para OCR local opcional, instale pytesseract e Tesseract.") from e
    return pytesseract.image_to_string(Image.open(path),lang=language)
