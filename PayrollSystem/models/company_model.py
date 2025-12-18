"""
Model functions for company settings.
"""

from __future__ import annotations

from typing import Dict, Optional

from .database import get_connection


def get_company_settings() -> Optional[Dict]:
    """Get company settings for payslip header."""
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT * FROM company_settings LIMIT 1")
            return cur.fetchone()

