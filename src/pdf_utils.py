"""Module for utility functions."""

import base64
import streamlit as st
import re


def display_pdf(file_path):
    """Display PDF file.

    Args:
        file_path (str):

    Returns:
        str: pdf display in html format
    """

    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = (
        f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    )
    return pdf_display


def pdf_to_text(doc_path):
    """Load PDF file and convert to text.

    Args:
        doc_path (str): path to PDF file

    Returns:
        str: text from PDF file
    """
    try:
        import fitz
    except ImportError as e:
        raise ImportError("PyMuPDF package not found, please install it with " "`pip install pymupdf`") from e

    with fitz.open(doc_path) as doc_file:
        text: str = "".join(page.get_text() for page in doc_file)

    
    return text
