import httpx
import io
import os
from PIL import Image

BASE_URL = "http://127.0.0.1:8000/api"

def create_dummy_image():
    img = Image.new('RGB', (1000, 1000), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def create_dummy_pdf():
    try:
        from reportlab.pdfgen import canvas
        packet = io.BytesIO()
        can = canvas.Canvas(packet)
        can.drawString(100, 100, "Hello world")
        can.save()
        return packet.getvalue()
    except ImportError:
        # Fallback to a minimal valid PDF if reportlab is not installed
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 <<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\n>>\n>>\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 55\n>>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000288 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n393\n%%EOF\n"

def run_tests():
    passed = 0
    failed = 0

    def print_result(name, success, error=None):
        nonlocal passed, failed
        if success:
            print(f"[SUCCESS] {name}")
            passed += 1
        else:
            print(f"[FAILED] {name}")
            if error:
                print(f"   -> {error}")
            failed += 1

    print("\n--- Starting Test Suite ---\n")

    # 1. Health Check
    try:
        res = httpx.get(f"{BASE_URL}/health")
        print_result("Health Check", res.status_code == 200)
    except Exception as e:
        print_result("Health Check", False, str(e))
        return

    # 2. Transfer Service
    try:
        res = httpx.post(
            f"{BASE_URL}/transfer/upload",
            files=[("files", ("transfer_test.txt", b"Hello this is a secret file", "text/plain"))]
        )
        if res.status_code == 200:
            code = res.json().get("code")
            print_result("Transfer Upload", True)
            
            dl_res = httpx.get(f"{BASE_URL}/transfer/download/{code}")
            print_result("Transfer Download", dl_res.status_code == 200 and b"Hello" in dl_res.content)
        else:
            print_result("Transfer Upload", False, f"{res.status_code} - {res.text}")
    except Exception as e:
        print_result("Transfer System", False, str(e))

    # 3. PDF Tools
    try:
        pdf_data = create_dummy_pdf()
        
        # Merge
        res = httpx.post(
            f"{BASE_URL}/ilovepdf/merge",
            files=[
                ("files", ("test1.pdf", pdf_data, "application/pdf")),
                ("files", ("test2.pdf", pdf_data, "application/pdf"))
            ]
        )
        print_result("PDF Merge", res.status_code == 200 and len(res.content) > len(pdf_data), res.text if res.status_code != 200 else None)
        
        # Protect & Unlock
        res = httpx.post(
            f"{BASE_URL}/ilovepdf/protect",
            files={"file": ("test.pdf", pdf_data, "application/pdf")},
            data={"password": "testpassword"}
        )
        if res.status_code == 200:
            print_result("PDF Protect", True)
            protected_data = res.content
            
            res_unlock = httpx.post(
                f"{BASE_URL}/ilovepdf/unlock",
                files={"file": ("protected.pdf", protected_data, "application/pdf")},
                data={"password": "testpassword"}
            )
            print_result("PDF Unlock", res_unlock.status_code == 200, res_unlock.text if res_unlock.status_code != 200 else None)
        else:
            print_result("PDF Protect", False, res.text)
            
    except Exception as e:
        print_result("PDF Tools", False, str(e))

    # 4. Utilities (Images and Compress)
    try:
        img_data = create_dummy_image()
        pdf_data = create_dummy_pdf()

        # Compress Image
        res = httpx.post(
            f"{BASE_URL}/utils/compress-image", 
            files={"file": ("test.jpg", img_data, "image/jpeg")},
            data={"quality": "10"}
        )
        print_result("Image Compress", res.status_code == 200 and len(res.content) < len(img_data), res.text if res.status_code != 200 else None)

        # Target Size Image
        res = httpx.post(
            f"{BASE_URL}/utils/target-size-image", 
            files={"file": ("test.jpg", img_data, "image/jpeg")},
            data={"target_kb": "1"} # Extremely small to force heavy compression
        )
        print_result("Image Target Size", res.status_code == 200, res.text if res.status_code != 200 else None)

        # Resize Image
        res = httpx.post(
            f"{BASE_URL}/utils/resize-image", 
            files={"file": ("test.jpg", img_data, "image/jpeg")},
            data={"width": "100", "height": "100"}
        )
        print_result("Image Resize", res.status_code == 200, res.text if res.status_code != 200 else None)

        # Compress PDF
        res = httpx.post(
            f"{BASE_URL}/utils/compress-pdf", 
            files={"file": ("test.pdf", pdf_data, "application/pdf")}
        )
        print_result("PDF Compress (Utils)", res.status_code == 200, res.text if res.status_code != 200 else None)

    except Exception as e:
        print_result("Utilities", False, str(e))

    # Summary
    print("\n--- Test Suite Summary ---")
    print(f"Total passed: {passed}")
    print(f"Total failed: {failed}")
    
    if failed == 0:
        print("[SUCCESS] All tests passed successfully!")
    else:
        print("[WARNING] Some tests failed.")

if __name__ == "__main__":
    run_tests()
