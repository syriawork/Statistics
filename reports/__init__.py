"""Reporting package for biostatistical application."""
from .excel import generate_excel_report
from .pdf import generate_pdf_report

__all__ = ["generate_excel_report", "generate_pdf_report"]
