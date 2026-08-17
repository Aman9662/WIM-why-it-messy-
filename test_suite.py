import requests
import io
import time
from PIL import Image

BASE_URL = "http://127.0.0.1:8000/api"

def create_dummy_image():
    img = Image.new('RGB', (1000, 1000), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def create_dummy_pdf():
    from reportlab.pdfgen import canvas
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    can.drawString(100, 100, "Hello world")
    can.save()
    return packet.getvalue()

def run_tests():
    print("Testing Size Fixer (Compress Image)...")
    img_data = create_dummy_image()
    res = requests.post(
        f"{BASE_URL}/utils/compress-image", 
        files={"file": ("test.jpg", img_data, "image/jpeg")},
        data={"quality": "10"}
    )
    if res.status_code == 200 and len(res.content) < len(img_data):
        print("[SUCCESS] Size Fixer Image Compress passed!")
    else:
        print("[ERROR] Size Fixer Failed:", res.status_code, res.text)

    print("\nTesting Transfer System (Send Anywhere)...")
    res = requests.post(
        f"{BASE_URL}/transfer/upload",
        files={"file": ("transfer_test.txt", b"Hello this is a secret file", "text/plain")}
    )
    if res.status_code == 200:
        code = res.json().get("code")
        print(f"[SUCCESS] Upload passed! Got code: {code}")
        
        # Test download
        dl_res = requests.get(f"{BASE_URL}/transfer/download/{code}")
        if dl_res.status_code == 200 and dl_res.content == b"Hello this is a secret file":
            print("[SUCCESS] Download passed!")
        else:
            print("[ERROR] Download Failed:", dl_res.status_code)
    else:
        print("[ERROR] Upload Failed:", res.status_code, res.text)
        
    print("\nTesting PDF Merge...")
    pdf_data = create_dummy_pdf()
    res = requests.post(
        f"{BASE_URL}/ilovepdf/merge",
        files=[
            ("files", ("test1.pdf", pdf_data, "application/pdf")),
            ("files", ("test2.pdf", pdf_data, "application/pdf"))
        ]
    )
    if res.status_code == 200 and len(res.content) > len(pdf_data):
        print("[SUCCESS] PDF Merge passed!")
    else:
        print("[ERROR] PDF Merge Failed:", res.status_code, res.text)

if __name__ == "__main__":
    try:
        import reportlab
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab", "requests", "pillow"])
    run_tests()
