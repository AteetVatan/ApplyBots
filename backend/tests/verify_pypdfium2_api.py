"""Test script to verify pypdfium2 API before implementation.

Run this script to verify the exact API signatures match our plan.
This prevents implementation failures due to API mismatches.

Usage:
    python -m pytest backend/tests/verify_pypdfium2_api.py -v
    # OR
    python backend/tests/verify_pypdfium2_api.py
"""

import io
import sys
from typing import Any

# Create a minimal test PDF for testing
TEST_PDF_CONTENT = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Hello World) Tj ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
0000000301 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
380
%%EOF
"""


def test_pypdfium2_import() -> bool:
    """Test that pypdfium2 can be imported."""
    try:
        import pypdfium2 as pdfium
        print("✓ pypdfium2 imported successfully")
        return True
    except ImportError as e:
        print(f"✗ pypdfium2 import failed: {e}")
        print("  Install with: pip install pypdfium2")
        return False


def test_document_opening() -> tuple[bool, Any]:
    """Test opening a PDF document."""
    try:
        import pypdfium2 as pdfium
        
        # Test 1: Open from bytes
        doc = pdfium.PdfDocument(TEST_PDF_CONTENT)
        print("✓ PdfDocument(bytes) works")
        
        # Test 2: Get page count
        try:
            page_count = len(doc)
            print(f"✓ len(doc) = {page_count}")
        except TypeError:
            # Try alternative
            page_count = doc.get_page_count()
            print(f"✓ doc.get_page_count() = {page_count}")
        
        return True, doc
    except Exception as e:
        print(f"✗ Document opening failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False, None


def test_page_access(doc: Any) -> tuple[bool, Any]:
    """Test accessing pages."""
    try:
        import pypdfium2 as pdfium
        
        # Test 1: Get first page
        try:
            page = doc.get_page(0)
            print("✓ doc.get_page(0) works")
        except AttributeError:
            try:
                page = doc[0]
                print("✓ doc[0] works")
            except Exception as e:
                print(f"✗ Page access failed: {e}")
                return False, None
        
        # Test 2: Check page type
        print(f"  Page type: {type(page).__name__}")
        
        return True, page
    except Exception as e:
        print(f"✗ Page access failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False, None


def test_text_extraction(page: Any) -> bool:
    """Test text extraction from page."""
    try:
        import pypdfium2 as pdfium
        
        # Test 1: Get textpage
        try:
            textpage = page.get_textpage()
            print("✓ page.get_textpage() works")
        except AttributeError:
            try:
                textpage = page.textpage
                print("✓ page.textpage works")
            except Exception as e:
                print(f"✗ Textpage access failed: {e}")
                return False
        
        # Test 2: Extract text
        try:
            text = textpage.get_text_range()
            print(f"✓ textpage.get_text_range() = '{text}'")
        except AttributeError:
            try:
                text = textpage.get_text()
                print(f"✓ textpage.get_text() = '{text}'")
            except AttributeError:
                try:
                    text = str(textpage)
                    print(f"✓ str(textpage) = '{text}'")
                except Exception as e:
                    print(f"✗ Text extraction failed: {e}")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ Text extraction failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        return False


def test_page_rendering(page: Any) -> bool:
    """Test rendering page to image."""
    try:
        import pypdfium2 as pdfium
        from PIL import Image
        
        # Test 1: Render to bitmap
        try:
            bitmap = page.render(scale=2.0)
            print("✓ page.render(scale=2.0) works")
        except AttributeError:
            try:
                bitmap = page.render_to_bitmap(scale=2.0)
                print("✓ page.render_to_bitmap(scale=2.0) works")
            except Exception as e:
                print(f"✗ Page rendering failed: {e}")
                return False
        
        print(f"  Bitmap type: {type(bitmap).__name__}")
        
        # Test 2: Convert to PIL Image
        try:
            image = bitmap.to_pil()
            print("✓ bitmap.to_pil() works")
            print(f"  Image size: {image.size}")
        except AttributeError:
            try:
                image = bitmap.to_pil_image()
                print("✓ bitmap.to_pil_image() works")
            except AttributeError:
                try:
                    # Manual conversion
                    import numpy as np
                    array = bitmap.to_numpy()
                    image = Image.fromarray(array)
                    print("✓ bitmap.to_numpy() + Image.fromarray() works")
                except Exception as e:
                    print(f"✗ PIL conversion failed: {e}")
                    return False
        
        # Test 3: Cleanup
        try:
            if hasattr(bitmap, 'close'):
                bitmap.close()
                print("✓ bitmap.close() works")
            elif hasattr(bitmap, '__del__'):
                del bitmap
                print("✓ del bitmap works")
            else:
                print("⚠ No explicit cleanup method found")
        except Exception as e:
            print(f"⚠ Cleanup warning: {e}")
        
        # Test 4: Context manager (if supported)
        try:
            with page.render(scale=1.0) as bm:
                img = bm.to_pil()
            print("✓ Context manager (with page.render()) works")
        except (AttributeError, TypeError):
            print("⚠ Context manager not supported (use explicit cleanup)")
        
        # Cleanup image
        if 'image' in locals():
            image.close()
        
        return True
    except Exception as e:
        print(f"✗ Page rendering failed: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def test_encrypted_pdf_detection() -> bool:
    """Test detecting encrypted PDFs."""
    try:
        import pypdfium2 as pdfium
        
        # Create a simple encrypted PDF (or use test data)
        # For now, just test that we can check metadata
        doc = pdfium.PdfDocument(TEST_PDF_CONTENT)
        
        try:
            meta = doc.get_meta_dict()
            print(f"✓ doc.get_meta_dict() works: {meta}")
            
            # Check for encryption
            if '/Encrypt' in meta:
                print("  PDF is encrypted")
            else:
                print("  PDF is not encrypted")
        except AttributeError:
            try:
                # Alternative metadata access
                meta = doc.metadata
                print(f"✓ doc.metadata works: {meta}")
            except Exception as e:
                print(f"⚠ Metadata access: {e}")
        
        return True
    except Exception as e:
        print(f"✗ Encrypted PDF detection test failed: {e}")
        return False


def test_document_cleanup(doc: Any) -> bool:
    """Test document cleanup."""
    try:
        import pypdfium2 as pdfium
        
        # Test cleanup methods
        if hasattr(doc, 'close'):
            doc.close()
            print("✓ doc.close() works")
        elif hasattr(doc, '__del__'):
            del doc
            print("✓ del doc works")
        else:
            print("⚠ No explicit cleanup method found")
        
        return True
    except Exception as e:
        print(f"⚠ Cleanup warning: {e}")
        return True  # Not critical


def main() -> int:
    """Run all API verification tests."""
    print("=" * 60)
    print("pypdfium2 API Verification Test")
    print("=" * 60)
    print()
    
    # Test 1: Import
    if not test_pypdfium2_import():
        print("\n❌ Cannot proceed without pypdfium2")
        return 1
    
    print()
    
    # Test 2: Document opening
    success, doc = test_document_opening()
    if not success:
        print("\n❌ Cannot proceed without document opening")
        return 1
    
    print()
    
    # Test 3: Page access
    success, page = test_page_access(doc)
    if not success:
        print("\n❌ Cannot proceed without page access")
        return 1
    
    print()
    
    # Test 4: Text extraction
    if not test_text_extraction(page):
        print("\n⚠ Text extraction failed - may need OCR fallback")
    
    print()
    
    # Test 5: Page rendering
    if not test_page_rendering(page):
        print("\n❌ Page rendering failed - OCR fallback will not work")
        return 1
    
    print()
    
    # Test 6: Encrypted PDF detection
    test_encrypted_pdf_detection()
    
    print()
    
    # Test 7: Cleanup
    test_document_cleanup(doc)
    
    print()
    print("=" * 60)
    print("✓ All critical API tests passed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Update plan with verified API calls")
    print("2. Implement using the verified method signatures")
    print("3. Test with real PDF files")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
