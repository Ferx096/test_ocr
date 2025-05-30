import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
import a_ocr_extractor

def test_extract_text_from_pdf_azure_exists():
    assert hasattr(a_ocr_extractor, 'extract_text_from_pdf_azure')

def test_concat_text_exists():
    assert hasattr(a_ocr_extractor, 'concat_text')
