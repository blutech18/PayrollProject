from __future__ import annotations

import types

import pytest

import services.user_service as user_service


class DummyWidget:
    """Minimal stand-in for a QWidget to satisfy QMessageBox parent argument in tests."""

    def __init__(self):
        self.messages = []


def test_create_user_validation_errors(monkeypatch):
    parent = DummyWidget()

    # Patch QMessageBox methods to avoid GUI popups
    def _fake_msgbox(*args, **kwargs):
        return None

    monkeypatch.setattr(user_service.QMessageBox, "warning", _fake_msgbox)
    monkeypatch.setattr(user_service.QMessageBox, "information", _fake_msgbox)
    monkeypatch.setattr(user_service.QMessageBox, "critical", _fake_msgbox)

    # Empty username
    assert user_service.create_user("", "pass123", "Employee", parent_widget=parent) is False

    # Empty password
    assert user_service.create_user("user1", "", "Employee", parent_widget=parent) is False

    # Short password
    assert user_service.create_user("user1", "123", "Employee", parent_widget=parent) is False


