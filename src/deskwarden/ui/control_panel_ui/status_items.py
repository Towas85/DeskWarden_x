"""
DeskWarden - ui/control_panel_ui/status_items.py

"""

import os
import datetime

import psutil

from ...core.security import load_security_log
from ...core.updater import CURRENT_VERSION, get_cached_update_snapshot
from .theme import _TEAL, _RED, _GREEN, _MUTE, _ACC2


def _sidebar_status_items():

    items = []
    _SKY_BLUE = "#38bdf8"
    try:
        proc = psutil.Process(os.getpid())
        cpu_pct = proc.cpu_percent(interval=None)
        mem_mb = proc.memory_info().rss / (1024 * 1024)
        items.append((f"CPU {cpu_pct:.0f}%  ·  RAM {mem_mb:.0f}MB", _TEAL))
    except Exception:
        pass
    try:
        entries = load_security_log()
        lbl_map = {
            "wrong_password":           "Wrong password",
            "lockout_start":            "Locked out",
            "lockout_end":              "Lockout ended",
            "success":                  "Unlocked",
            "password_changed":         "Password changed",
            "password_reset":           "Password reset",
            "otp_sent":                 "OTP sent",
            "otp_verified":             "OTP verified",
            "wrong_otp":                "Invalid OTP",
            "recovery_key_verified":    "Recovery key verified",
            "wrong_recovery_key":       "Invalid recovery key",
            "recovery_key_regenerated": "Recovery key renewed",
            "recovery_email_updated":   "Recovery email updated",
            "recovery_key_toggled":     "Recovery key updated",
            "recovery_email_toggled":   "Recovery email updated",
            "backup_exported":          "Backup exported",
            "backup_imported":          "Backup imported",
        }
        color_map = {
            "wrong_password":           "#f59e0b",
            "lockout_start":            _RED,
            "lockout_end":              _GREEN,
            "success":                  _GREEN,
            "otp_verified":             _GREEN,
            "recovery_key_verified":    _GREEN,
            "wrong_otp":                "#f59e0b",
            "wrong_recovery_key":       "#f59e0b",
            "otp_sent":                 _SKY_BLUE,
            "password_changed":         _SKY_BLUE,
            "password_reset":           _SKY_BLUE,
            "recovery_key_regenerated": _SKY_BLUE,
            "recovery_email_updated":   _SKY_BLUE,
            "recovery_key_toggled":     _SKY_BLUE,
            "recovery_email_toggled":   _SKY_BLUE,
            "backup_exported":          _SKY_BLUE,
            "backup_imported":          _SKY_BLUE,
        }

        last = None
        for e in reversed(entries):
            if e.get("where") == "Quit":
                continue
            if e.get("where") == "Control Panel" and e.get("type") == "success":
                continue
            last = e
            break
        if last:
            et = last.get("type", "")
            where = last.get("where", "")
            if where.startswith("App:"):
                where = where[4:]
            if where.lower().endswith(".exe"):
                where = where[:-4]
            event_name = lbl_map.get(et, et.replace("_", " ").title() if et else "—")
            txt = f"Last: {event_name} — {where}" if where else f"Last: {event_name}"
            items.append((txt[:46], color_map.get(et, _SKY_BLUE)))
        else:
            items.append(("No security events yet", _MUTE))
    except Exception:
        pass
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        entries = load_security_log()
        unlocks_today = sum(1 for e in entries
                             if e.get("type") == "success" and e.get("time", "").startswith(today))
        items.append((f"{unlocks_today} unlock{'s' if unlocks_today != 1 else ''} today", _GREEN))
    except Exception:
        pass
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        entries = load_security_log()
        failed_today = sum(1 for e in entries
                            if e.get("type") == "wrong_password" and e.get("time", "").startswith(today))
        items.append((f"{failed_today} failed attempt{'s' if failed_today != 1 else ''} today",
                      _RED if failed_today else _MUTE))
    except Exception:
        pass
    try:
        items.append((f"DeskWarden {CURRENT_VERSION}", _ACC2))
    except Exception:
        pass
    try:
        snap = get_cached_update_snapshot()
        if snap.get("update_available"):
            items.append((f"Update available: {snap.get('latest')}", "#fbbf24"))
    except Exception:
        pass
    if not items:
        items = [("Active · monitoring", _GREEN)]
    return items

