"""
DeskWarden - ui/control_panel_ui/security_panel.py
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QGraphicsDropShadowEffect, QFileDialog, QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor

from ...core.config import save_config
from ...core.security import (
    hash_pw, generate_recovery_key, hash_recovery_key,
    log_security_event, mask_email,
)
from ...core.logging_utils import suppress_faulthandler

from .theme import _BG, _CARD, _CARD2, _BORD, _ACC, _ACC2, _FG, _MUTE, _RED, _GREEN
from .widgets import _Card, _ToggleSwitch


class _SecurityPanelMixin:

    # ── Build ────────────────────────────────────────────────────────────

    def _build_security_panel(self):
        panel = QWidget(); panel.setStyleSheet(f"background: {_BG};"); panel.hide()
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(0, 0, 0, 0); pl.setSpacing(0)

        card = _Card(panel, bg=_CARD, border=_BORD, radius=16)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 14, 18, 20); cl.setSpacing(10)

        hdr = QHBoxLayout()
        hl = QLabel("MASTER PASSWORD", card)
        hl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        hl.setStyleSheet(f"color: #b794f6; background: transparent;")
        hdr.addWidget(hl); hdr.addStretch()
        has_pw = bool(self._cfg.get("password_hash"))
        bc = _GREEN if has_pw else _RED
        bt = "✓ Set" if has_pw else "✗ Not set"
        badge = QLabel(bt, card)
        badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        badge.setStyleSheet(f"""
            color: white; background: {bc};
            border-radius: 10px; padding: 2px 10px;""")
        hdr.addWidget(badge)
        self._pw_badge = badge
        cl.addLayout(hdr)

        div = QFrame(card); div.setFixedHeight(1)
        div.setStyleSheet(f"background: {_BORD};")
        cl.addWidget(div)

        self._pw_toggle_btn = QPushButton(
            "🔑  Change Password" if has_pw else "🔑  Set Password",
            card
        )
        self._pw_toggle_btn.setFixedHeight(36)
        self._pw_toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._pw_toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._pw_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
                padding: 0 20px; text-align: left;
            }}
            QPushButton:hover {{ background: {_BORD}; }}""")
        self._pw_toggle_btn.clicked.connect(self._toggle_pw_form)

        self._pwtoggle_glow = QGraphicsDropShadowEffect(self._pw_toggle_btn)
        self._pwtoggle_glow.setBlurRadius(0)
        self._pwtoggle_glow.setColor(QColor(_ACC))
        self._pwtoggle_glow.setOffset(0, 0)
        self._pw_toggle_btn.setGraphicsEffect(self._pwtoggle_glow)

        def _pwtoggle_enter(ev):
            self._pwtoggle_glow.setBlurRadius(16)
            QPushButton.enterEvent(self._pw_toggle_btn, ev)
        def _pwtoggle_leave(ev):
            self._pwtoggle_glow.setBlurRadius(0)
            QPushButton.leaveEvent(self._pw_toggle_btn, ev)
        self._pw_toggle_btn.enterEvent = _pwtoggle_enter
        self._pw_toggle_btn.leaveEvent = _pwtoggle_leave

        cl.addWidget(self._pw_toggle_btn)

        self._pw_form = QWidget(card); self._pw_form.setStyleSheet("background: transparent;")
        fl = QVBoxLayout(self._pw_form)
        fl.setContentsMargins(0, 8, 0, 0); fl.setSpacing(8)

        if has_pw:
            ol = QLabel("Current Password", self._pw_form)
            ol.setFont(QFont("Segoe UI", 9))
            ol.setStyleSheet(f"color: {_MUTE}; background: transparent;")
            fl.addWidget(ol)
            self._old_pw = QLineEdit(self._pw_form); self._old_pw.setEchoMode(QLineEdit.EchoMode.Password)
            fl.addWidget(self._old_pw)
        else:
            self._old_pw = None

        nl = QLabel("New Password", self._pw_form)
        nl.setFont(QFont("Segoe UI", 9))
        nl.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        fl.addWidget(nl)
        self._new_pw = QLineEdit(self._pw_form); self._new_pw.setEchoMode(QLineEdit.EchoMode.Password)
        fl.addWidget(self._new_pw)

        cnl = QLabel("Confirm New Password", self._pw_form)
        cnl.setFont(QFont("Segoe UI", 9))
        cnl.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        fl.addWidget(cnl)
        self._con_pw = QLineEdit(self._pw_form); self._con_pw.setEchoMode(QLineEdit.EchoMode.Password)
        fl.addWidget(self._con_pw)

        self._pw_err = QLabel("", self._pw_form)
        self._pw_err.setFont(QFont("Segoe UI", 9))
        self._pw_err.setStyleSheet(f"color: {_RED}; background: transparent;")
        fl.addWidget(self._pw_err)

        save_btn = QPushButton("💾  Save Password", self._pw_form)
        save_btn.setFixedHeight(36)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_ACC}; color: white; border: none;
                border-radius: 8px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {_ACC2}; }}""")
        save_btn.clicked.connect(self._save_pw)
        fl.addWidget(save_btn)

        self._savepw_glow = QGraphicsDropShadowEffect(save_btn)
        self._savepw_glow.setBlurRadius(0)
        self._savepw_glow.setColor(QColor(_ACC))
        self._savepw_glow.setOffset(0, 0)
        save_btn.setGraphicsEffect(self._savepw_glow)

        def _savepw_enter(ev):
            self._savepw_glow.setBlurRadius(22)
            QPushButton.enterEvent(save_btn, ev)

        def _savepw_leave(ev):
            self._savepw_glow.setBlurRadius(0)
            QPushButton.leaveEvent(save_btn, ev)

        save_btn.enterEvent = _savepw_enter
        save_btn.leaveEvent = _savepw_leave

        self._pw_form.setVisible(False)
        cl.addWidget(self._pw_form)

        pl.addWidget(card)
        pl.addSpacing(14)

        # ── Recovery Key Card ─────────────────────────────────────────────────
        rec_card = _Card(panel, bg=_CARD, border=_BORD, radius=16)
        rcl = QVBoxLayout(rec_card)
        rcl.setContentsMargins(18, 14, 18, 20); rcl.setSpacing(10)

        r_hdr = QHBoxLayout()
        r_hl = QLabel("EMERGENCY RECOVERY KEY", rec_card)
        r_hl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        r_hl.setStyleSheet(f"color: #b794f6; background: transparent;")
        r_hdr.addWidget(r_hl)

        self._rec_warn_lbl = QLabel("⚠ Disabled in Recovery", rec_card)
        self._rec_warn_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._rec_warn_lbl.setStyleSheet("color: #f87171; background: #281116; border: 1px solid #551920; border-radius: 6px; padding: 2px 8px;")
        self._rec_warn_lbl.setVisible(False)
        r_hdr.addWidget(self._rec_warn_lbl)
        r_hdr.addStretch()

        has_rec = bool(self._cfg.get("recovery_key_hash"))
        self._rec_badge = QLabel("", rec_card)
        self._rec_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        r_hdr.addWidget(self._rec_badge)

        self._rec_toggle_switch = _ToggleSwitch(rec_card)
        self._rec_toggle_switch.toggled.connect(self._on_rec_key_toggled)
        r_hdr.addWidget(self._rec_toggle_switch)

        rcl.addLayout(r_hdr)

        r_div = QFrame(rec_card); r_div.setFixedHeight(1)
        r_div.setStyleSheet(f"background: {_BORD};")
        rcl.addWidget(r_div)

        desc = QLabel(
            "An offline Emergency Recovery Key allows you to reset your master password "
            "if you ever forget it. Keep your recovery key in a safe place.",
            rec_card
        )
        desc.setFont(QFont("Segoe UI", 9))
        desc.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        desc.setWordWrap(True)
        rcl.addWidget(desc)

        self._rec_toggle_btn = QPushButton(
            "🔑  Regenerate Recovery Key" if has_rec else "🔑  Generate Recovery Key",
            rec_card
        )
        self._rec_toggle_btn.setFixedHeight(36)
        self._rec_toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._rec_toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._rec_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
                padding: 0 20px; text-align: left;
            }}
            QPushButton:hover {{ background: {_BORD}; }}""")
        self._rec_toggle_btn.clicked.connect(self._toggle_rec_form)

        self._rectoggle_glow = QGraphicsDropShadowEffect(self._rec_toggle_btn)
        self._rectoggle_glow.setBlurRadius(0)
        self._rectoggle_glow.setColor(QColor(_ACC))
        self._rectoggle_glow.setOffset(0, 0)
        self._rec_toggle_btn.setGraphicsEffect(self._rectoggle_glow)

        def _rectoggle_enter(ev):
            self._rectoggle_glow.setBlurRadius(16)
            QPushButton.enterEvent(self._rec_toggle_btn, ev)
        def _rectoggle_leave(ev):
            self._rectoggle_glow.setBlurRadius(0)
            QPushButton.leaveEvent(self._rec_toggle_btn, ev)
        self._rec_toggle_btn.enterEvent = _rectoggle_enter
        self._rec_toggle_btn.leaveEvent = _rectoggle_leave

        rcl.addWidget(self._rec_toggle_btn)

        self._rec_form = QWidget(rec_card); self._rec_form.setStyleSheet("background: transparent;")
        rfl = QVBoxLayout(self._rec_form)
        rfl.setContentsMargins(0, 8, 0, 0); rfl.setSpacing(8)

        self._rec_pw_label = QLabel("Confirm Current Master Password", self._rec_form)
        self._rec_pw_label.setFont(QFont("Segoe UI", 9))
        self._rec_pw_label.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        rfl.addWidget(self._rec_pw_label)

        self._rec_pw_in = QLineEdit(self._rec_form)
        self._rec_pw_in.setEchoMode(QLineEdit.EchoMode.Password)
        rfl.addWidget(self._rec_pw_in)

        self._rec_err = QLabel("", self._rec_form)
        self._rec_err.setFont(QFont("Segoe UI", 9))
        self._rec_err.setStyleSheet(f"color: {_RED}; background: transparent;")
        rfl.addWidget(self._rec_err)

        gen_btn = QPushButton("⚡  Generate Key", self._rec_form)
        gen_btn.setFixedHeight(36)
        gen_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        gen_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        gen_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_ACC}; color: white; border: none;
                border-radius: 8px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {_ACC2}; }}""")
        gen_btn.clicked.connect(self._generate_new_recovery_key)
        rfl.addWidget(gen_btn)

        self._rec_result_box = QWidget(self._rec_form)
        self._rec_result_box.setStyleSheet("background: transparent;")
        rbl = QVBoxLayout(self._rec_result_box)
        rbl.setContentsMargins(0, 8, 0, 0); rbl.setSpacing(8)

        key_box = QFrame(self._rec_result_box)
        key_box.setStyleSheet(f"""
            QFrame {{
                background: {_CARD2}; border: 1px solid {_BORD};
                border-radius: 10px; padding: 10px;
            }}""")
        kbl = QVBoxLayout(key_box)
        kbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rec_key_display = QLabel("", key_box)
        self._rec_key_display.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self._rec_key_display.setStyleSheet("color: #c4b5fd; background: transparent; letter-spacing: 1.5px;")
        self._rec_key_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        kbl.addWidget(self._rec_key_display)
        rbl.addWidget(key_box)

        action_row = QHBoxLayout()
        self._rec_copy_btn = QPushButton("📋  Copy Key", self._rec_result_box)
        self._rec_copy_btn.setFixedHeight(34)
        self._rec_copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._rec_copy_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._rec_copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {_BORD}; }}""")
        self._rec_copy_btn.clicked.connect(self._copy_generated_key)
        action_row.addWidget(self._rec_copy_btn)

        self._rec_file_btn = QPushButton("💾  Save to File", self._rec_result_box)
        self._rec_file_btn.setFixedHeight(34)
        self._rec_file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._rec_file_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._rec_file_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {_BORD}; }}""")
        self._rec_file_btn.clicked.connect(self._save_generated_key_file)
        action_row.addWidget(self._rec_file_btn)
        rbl.addLayout(action_row)

        self._rec_result_box.setVisible(False)
        rfl.addWidget(self._rec_result_box)

        self._rec_form.setVisible(False)
        rcl.addWidget(self._rec_form)

        self._update_rec_badge()

        pl.addWidget(rec_card)
        pl.addSpacing(14)

        # ── Recovery Email Card ────────────────────────────────────────────────
        email_card = _Card(panel, bg=_CARD, border=_BORD, radius=16)
        ecl = QVBoxLayout(email_card)
        ecl.setContentsMargins(18, 14, 18, 20); ecl.setSpacing(10)

        e_hdr = QHBoxLayout()
        e_hl = QLabel("RECOVERY EMAIL", email_card)
        e_hl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        e_hl.setStyleSheet(f"color: #b794f6; background: transparent;")
        e_hdr.addWidget(e_hl)

        self._em_warn_lbl = QLabel("⚠ Disabled in Recovery", email_card)
        self._em_warn_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._em_warn_lbl.setStyleSheet("color: #f87171; background: #281116; border: 1px solid #551920; border-radius: 6px; padding: 2px 8px;")
        self._em_warn_lbl.setVisible(False)
        e_hdr.addWidget(self._em_warn_lbl)
        e_hdr.addStretch()

        cur_email = self._cfg.get("recovery_email", "").strip()
        self._em_badge = QLabel("", email_card)
        self._em_badge.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        e_hdr.addWidget(self._em_badge)

        self._em_toggle_switch = _ToggleSwitch(email_card)
        self._em_toggle_switch.toggled.connect(self._on_rec_email_toggled)
        e_hdr.addWidget(self._em_toggle_switch)

        ecl.addLayout(e_hdr)

        e_div = QFrame(email_card); e_div.setFixedHeight(1)
        e_div.setStyleSheet(f"background: {_BORD};")
        ecl.addWidget(e_div)

        e_desc = QLabel(
            "Configure a recovery email address to receive 6-digit OTP codes for "
            "online password recovery via Cloudflare & Brevo.",
            email_card
        )
        e_desc.setFont(QFont("Segoe UI", 9))
        e_desc.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        e_desc.setWordWrap(True)
        ecl.addWidget(e_desc)

        self._em_info_lbl = QLabel(
            f"Registered: {cur_email}" if cur_email else "No recovery email registered.",
            email_card
        )
        self._em_info_lbl.setFont(QFont("Segoe UI", 9))
        self._em_info_lbl.setStyleSheet(f"color: #c4b5fd; background: transparent;")
        ecl.addWidget(self._em_info_lbl)

        self._em_toggle_btn = QPushButton(
            "✉️  Change Recovery Email" if cur_email else "✉️  Set Recovery Email",
            email_card
        )
        self._em_toggle_btn.setFixedHeight(36)
        self._em_toggle_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._em_toggle_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._em_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
                padding: 0 20px; text-align: left;
            }}
            QPushButton:hover {{ background: {_BORD}; }}""")
        self._em_toggle_btn.clicked.connect(self._toggle_em_form)

        self._emtoggle_glow = QGraphicsDropShadowEffect(self._em_toggle_btn)
        self._emtoggle_glow.setBlurRadius(0)
        self._emtoggle_glow.setColor(QColor(_ACC))
        self._emtoggle_glow.setOffset(0, 0)
        self._em_toggle_btn.setGraphicsEffect(self._emtoggle_glow)

        def _emtoggle_enter(ev):
            self._emtoggle_glow.setBlurRadius(16)
            QPushButton.enterEvent(self._em_toggle_btn, ev)
        def _emtoggle_leave(ev):
            self._emtoggle_glow.setBlurRadius(0)
            QPushButton.leaveEvent(self._em_toggle_btn, ev)
        self._em_toggle_btn.enterEvent = _emtoggle_enter
        self._em_toggle_btn.leaveEvent = _emtoggle_leave

        ecl.addWidget(self._em_toggle_btn)

        self._em_form = QWidget(email_card); self._em_form.setStyleSheet("background: transparent;")
        efl = QVBoxLayout(self._em_form)
        efl.setContentsMargins(0, 8, 0, 0); efl.setSpacing(8)

        self._em_pw_label = QLabel("Confirm Current Master Password", self._em_form)
        self._em_pw_label.setFont(QFont("Segoe UI", 9))
        self._em_pw_label.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        efl.addWidget(self._em_pw_label)

        self._em_pw_in = QLineEdit(self._em_form)
        self._em_pw_in.setEchoMode(QLineEdit.EchoMode.Password)
        efl.addWidget(self._em_pw_in)

        em_input_label = QLabel("Recovery Email Address", self._em_form)
        em_input_label.setFont(QFont("Segoe UI", 9))
        em_input_label.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        efl.addWidget(em_input_label)

        self._em_in = QLineEdit(self._em_form)
        self._em_in.setPlaceholderText("user@example.com")
        efl.addWidget(self._em_in)

        self._em_err = QLabel("", self._em_form)
        self._em_err.setFont(QFont("Segoe UI", 9))
        self._em_err.setStyleSheet(f"color: {_RED}; background: transparent;")
        efl.addWidget(self._em_err)

        save_em_btn = QPushButton("💾  Save Recovery Email", self._em_form)
        save_em_btn.setFixedHeight(36)
        save_em_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_em_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        save_em_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_ACC}; color: white; border: none;
                border-radius: 8px; padding: 0 20px;
            }}
            QPushButton:hover {{ background: {_ACC2}; }}""")
        save_em_btn.clicked.connect(self._save_recovery_email)
        efl.addWidget(save_em_btn)

        self._em_form.setVisible(False)
        ecl.addWidget(self._em_form)

        self._update_em_badge()

        pl.addWidget(email_card)
        pl.addStretch()
        self._scroll_lay.addWidget(panel)
        self._section_widgets["security"] = panel
        panel.setVisible(False)

    def _build_password_panel(self):
        """Backward-compatible alias for _build_security_panel."""
        return self._build_security_panel()

    # ── Form state ───────────────────────────────────────────────────────

    def _toggle_pw_form(self):
        showing = not self._pw_form.isVisible()
        self._pw_form.setVisible(showing)
        has_pw = bool(self._cfg.get("password_hash"))
        if showing:
            self._pw_toggle_btn.setText("✕  Cancel")
        else:
            self._pw_toggle_btn.setText(
                "🔑  Change Password" if has_pw else "🔑  Set Password")
            self._reset_pw_form()

    def _reset_pw_form(self):
        if getattr(self, "_old_pw", None):
            self._old_pw.clear()
        if getattr(self, "_new_pw", None):
            self._new_pw.clear()
        if getattr(self, "_con_pw", None):
            self._con_pw.clear()
        if getattr(self, "_pw_err", None):
            self._pw_err.setText("")
        if getattr(self, "_pw_form", None):
            self._pw_form.setVisible(False)
        if getattr(self, "_pw_toggle_btn", None):
            has_pw = bool(self._cfg.get("password_hash"))
            self._pw_toggle_btn.setText(
                "🔑  Change Password" if has_pw else "🔑  Set Password")

    def _reset_rec_form(self):
        if getattr(self, "_rec_pw_in", None):
            self._rec_pw_in.clear()
        if getattr(self, "_rec_err", None):
            self._rec_err.setText("")
        if getattr(self, "_rec_result_box", None):
            self._rec_result_box.setVisible(False)
        if getattr(self, "_rec_form", None):
            self._rec_form.setVisible(False)
        if getattr(self, "_rec_toggle_btn", None):
            has_rec = bool(self._cfg.get("recovery_key_hash"))
            self._rec_toggle_btn.setText(
                "🔑  Regenerate Recovery Key" if has_rec else "🔑  Generate Recovery Key")

    def _reset_em_form(self):
        cur_email = self._cfg.get("recovery_email", "").strip()
        if getattr(self, "_em_pw_in", None):
            self._em_pw_in.clear()
        if getattr(self, "_em_in", None):
            self._em_in.setText(cur_email)
        if getattr(self, "_em_err", None):
            self._em_err.setText("")
        if getattr(self, "_em_form", None):
            self._em_form.setVisible(False)
        if getattr(self, "_em_toggle_btn", None):
            self._em_toggle_btn.setText(
                "✉️  Change Recovery Email" if cur_email else "✉️  Set Recovery Email")

    def _reset_all_security_forms(self):
        self._reset_pw_form()
        self._reset_rec_form()
        self._reset_em_form()

    def _toggle_rec_form(self):
        showing = not self._rec_form.isVisible()
        if showing:
            self._rec_form.setVisible(True)
            has_pw = bool(self._cfg.get("password_hash"))
            self._rec_pw_label.setVisible(has_pw)
            self._rec_pw_in.setVisible(has_pw)
            self._rec_toggle_btn.setText("✕  Cancel")
            self._rec_err.setText("")
            self._rec_result_box.setVisible(False)
            self._rec_pw_in.clear()
        else:
            self._reset_rec_form()

    # ── Actions ──────────────────────────────────────────────────────────

    def _generate_new_recovery_key(self):
        has_pw = bool(self._cfg.get("password_hash"))
        if has_pw:
            pw = self._rec_pw_in.text()
            if hash_pw(pw) != self._cfg.get("password_hash", ""):
                self._rec_err.setStyleSheet(f"color: {_RED}; background: transparent;")
                self._rec_err.setText("✗ Incorrect master password.")
                return

        new_key = generate_recovery_key()
        self._latest_generated_rec_key = new_key
        self._cfg["recovery_key_hash"] = hash_recovery_key(new_key)
        self._cfg["recovery_key_enabled"] = True
        save_config(self._cfg)
        self._update_rec_badge()
        log_security_event("recovery_key_regenerated", "Control Panel", "New Master Recovery Key generated")

        self._rec_err.setStyleSheet(f"color: {_GREEN}; background: transparent;")
        self._rec_err.setText("✓ New recovery key generated! Please save it securely.")
        self._rec_key_display.setText(new_key)
        self._rec_result_box.setVisible(True)
        self._rec_pw_in.clear()

    def _copy_generated_key(self):
        key = getattr(self, "_latest_generated_rec_key", "")
        if key:
            cb = QApplication.clipboard()
            if cb:
                cb.setText(key)
            self._rec_copy_btn.setText("✓  Copied!")
            QTimer.singleShot(2000, lambda: self._rec_copy_btn.setText("📋  Copy Key"))

    def _save_generated_key_file(self):
        key = getattr(self, "_latest_generated_rec_key", "")
        if not key:
            return
        import os
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop_dir):
            desktop_dir = os.path.expanduser("~")
        default_target = os.path.join(desktop_dir, "DeskWarden-Recovery-Key.txt")

        with suppress_faulthandler():
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Emergency Recovery Key",
                default_target,
                "Text Files (*.txt);;All Files (*.*)",
            )
        if path:
            try:
                content = (
                    "=====================================================\n"
                    "        DESKWARDEN EMERGENCY RECOVERY KEY            \n"
                    "=====================================================\n\n"
                    f"Recovery Key: {key}\n\n"
                    "IMPORTANT:\n"
                    "- Keep this file in a safe, secure place.\n"
                    "- If you ever forget your DeskWarden Master Password, use\n"
                    "  this key on the lock screen or auth dialog to reset it.\n"
                    "- Each key can only be used once or until regenerated.\n"
                    "=====================================================\n"
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self._rec_file_btn.setText("✓  Saved!")
                QTimer.singleShot(2000, lambda: self._rec_file_btn.setText("💾  Save to File"))
            except Exception as e:
                self._rec_err.setText(f"Failed to save file: {e}")

    def _save_pw(self):
        o = self._old_pw.text() if self._old_pw else ""
        n = self._new_pw.text()
        c = self._con_pw.text()
        has_pw = bool(self._cfg.get("password_hash"))
        if has_pw and hash_pw(o) != self._cfg.get("password_hash",""):
            self._pw_err.setStyleSheet(f"color: {_RED}; background: transparent;")
            self._pw_err.setText("✗ Current password is incorrect."); return
        if len(n) < 4:
            self._pw_err.setStyleSheet(f"color: {_RED}; background: transparent;")
            self._pw_err.setText("✗ Must be at least 4 characters."); return
        if n != c:
            self._pw_err.setStyleSheet(f"color: {_RED}; background: transparent;")
            self._pw_err.setText("✗ Passwords do not match."); return
        self._cfg["password_hash"] = hash_pw(n)
        save_config(self._cfg)
        try:
            from ..recovery_dialog import close_active_recovery_dialog
            close_active_recovery_dialog()
        except Exception:
            pass
        log_security_event("password_changed", "Control Panel", "Master password updated successfully")
        self._pw_err.setStyleSheet(f"color: {_GREEN}; background: transparent;")
        self._pw_err.setText("✓ Password saved.")
        if self._old_pw: self._old_pw.clear()
        self._new_pw.clear(); self._con_pw.clear()
        self._pw_badge.setText("✓ Set")
        self._pw_badge.setStyleSheet(f"""
            color: white; background: {_GREEN};
            border-radius: 10px; padding: 2px 10px;""")

    def _toggle_em_form(self):
        showing = not self._em_form.isVisible()
        if showing:
            self._em_form.setVisible(True)
            cur_email = self._cfg.get("recovery_email", "").strip()
            has_pw = bool(self._cfg.get("password_hash"))
            self._em_pw_label.setVisible(has_pw)
            self._em_pw_in.setVisible(has_pw)
            self._em_toggle_btn.setText("✕  Cancel")
            self._em_err.setText("")
            self._em_pw_in.clear()
            self._em_in.setText(cur_email)
        else:
            self._reset_em_form()

    def _save_recovery_email(self):
        has_pw = bool(self._cfg.get("password_hash"))
        if has_pw:
            pw = self._em_pw_in.text()
            if hash_pw(pw) != self._cfg.get("password_hash", ""):
                self._em_err.setStyleSheet(f"color: {_RED}; background: transparent;")
                self._em_err.setText("✗ Incorrect master password.")
                return

        new_em = self._em_in.text().strip()
        if new_em:
            if "@" not in new_em or "." not in new_em.split("@")[-1]:
                self._em_err.setStyleSheet(f"color: {_RED}; background: transparent;")
                self._em_err.setText("✗ Please enter a valid email address.")
                return

        if new_em:
            self._cfg["recovery_email"] = new_em
            self._cfg["recovery_email_enabled"] = True
            log_security_event("recovery_email_updated", "Control Panel", f"Recovery email updated to {mask_email(new_em)}")
        else:
            self._cfg["recovery_email"] = ""
            self._cfg["recovery_email_enabled"] = False
            log_security_event("recovery_email_updated", "Control Panel", "Recovery email removed")
        save_config(self._cfg)
        self._update_em_badge()

        self._em_info_lbl.setText(
            f"Registered: {new_em}" if new_em else "No recovery email registered."
        )
        self._em_err.setStyleSheet(f"color: {_GREEN}; background: transparent;")
        self._em_err.setText("✓ Recovery email saved successfully.")
        self._em_pw_in.clear()

    # ── Recovery Toggle & Refresh Handlers ────────────────────────────────

    def _on_rec_key_toggled(self, checked):
        self._cfg["recovery_key_enabled"] = bool(checked)
        save_config(self._cfg)
        self._update_rec_badge()
        status_txt = "enabled" if checked else "disabled"
        log_security_event("recovery_key_toggled", "Control Panel", f"Recovery key method {status_txt}")

    def _update_rec_badge(self):
        has_rec = bool(self._cfg.get("recovery_key_hash"))
        enabled = bool(self._cfg.get("recovery_key_enabled", True if has_rec else False))
        if not has_rec:
            self._rec_badge.setText("✗ Not Generated")
            self._rec_badge.setStyleSheet(f"color: white; background: {_RED}; border-radius: 10px; padding: 2px 10px;")
            self._rec_toggle_switch.blockSignals(True)
            self._rec_toggle_switch.setChecked(False)
            self._rec_toggle_switch.setEnabled(False)
            self._rec_toggle_switch.blockSignals(False)
            self._rec_toggle_switch.setToolTip("Generate a recovery key first to enable this method")
            if hasattr(self, "_rec_warn_lbl"):
                self._rec_warn_lbl.setVisible(False)
        elif enabled:
            self._rec_badge.setText("✓ Active")
            self._rec_badge.setStyleSheet(f"color: white; background: {_GREEN}; border-radius: 10px; padding: 2px 10px;")
            self._rec_toggle_switch.blockSignals(True)
            self._rec_toggle_switch.setChecked(True)
            self._rec_toggle_switch.setEnabled(True)
            self._rec_toggle_switch.blockSignals(False)
            self._rec_toggle_switch.setToolTip("Emergency Recovery Key is active. Click to disable.")
            if hasattr(self, "_rec_warn_lbl"):
                self._rec_warn_lbl.setVisible(False)
        else:
            self._rec_badge.setText("⏸ Disabled")
            self._rec_badge.setStyleSheet("color: #cbd5e1; background: #334155; border-radius: 10px; padding: 2px 10px;")
            self._rec_toggle_switch.blockSignals(True)
            self._rec_toggle_switch.setChecked(False)
            self._rec_toggle_switch.setEnabled(True)
            self._rec_toggle_switch.blockSignals(False)
            self._rec_toggle_switch.setToolTip("Emergency Recovery Key is disabled. Click to enable.")
            if hasattr(self, "_rec_warn_lbl"):
                self._rec_warn_lbl.setVisible(True)

    def _on_rec_email_toggled(self, checked):
        self._cfg["recovery_email_enabled"] = bool(checked)
        save_config(self._cfg)
        self._update_em_badge()
        status_txt = "enabled" if checked else "disabled"
        log_security_event("recovery_email_toggled", "Control Panel", f"Recovery email method {status_txt}")

    def _update_em_badge(self):
        cur_email = self._cfg.get("recovery_email", "").strip()
        has_em = bool(cur_email)
        enabled = bool(self._cfg.get("recovery_email_enabled", True if has_em else False))
        if not has_em:
            self._em_badge.setText("✗ Not Set")
            self._em_badge.setStyleSheet(f"color: white; background: {_MUTE}; border-radius: 10px; padding: 2px 10px;")
            self._em_toggle_switch.blockSignals(True)
            self._em_toggle_switch.setChecked(False)
            self._em_toggle_switch.setEnabled(False)
            self._em_toggle_switch.blockSignals(False)
            self._em_toggle_switch.setToolTip("Configure a recovery email first to enable this method")
            if hasattr(self, "_em_warn_lbl"):
                self._em_warn_lbl.setVisible(False)
        elif enabled:
            self._em_badge.setText("✓ Configured")
            self._em_badge.setStyleSheet(f"color: white; background: {_GREEN}; border-radius: 10px; padding: 2px 10px;")
            self._em_toggle_switch.blockSignals(True)
            self._em_toggle_switch.setChecked(True)
            self._em_toggle_switch.setEnabled(True)
            self._em_toggle_switch.blockSignals(False)
            self._em_toggle_switch.setToolTip("Recovery Email is active. Click to disable.")
            if hasattr(self, "_em_warn_lbl"):
                self._em_warn_lbl.setVisible(False)
        else:
            self._em_badge.setText("⏸ Disabled")
            self._em_badge.setStyleSheet("color: #cbd5e1; background: #334155; border-radius: 10px; padding: 2px 10px;")
            self._em_toggle_switch.blockSignals(True)
            self._em_toggle_switch.setChecked(False)
            self._em_toggle_switch.setEnabled(True)
            self._em_toggle_switch.blockSignals(False)
            self._em_toggle_switch.setToolTip("Recovery Email is disabled. Click to enable.")
            if hasattr(self, "_em_warn_lbl"):
                self._em_warn_lbl.setVisible(True)

    def _refresh_security_panel(self):
        """Refreshes all badges, toggle switches, and display labels from current config."""
        from ...core.config import load_config
        self._cfg = load_config()
        self._reset_all_security_forms()
        has_pw = bool(self._cfg.get("password_hash"))
        if hasattr(self, "_pw_badge"):
            self._pw_badge.setText("✓ Set" if has_pw else "✗ Not set")
            self._pw_badge.setStyleSheet(f"color: white; background: {_GREEN if has_pw else _RED}; border-radius: 10px; padding: 2px 10px;")
        if hasattr(self, "_rec_toggle_switch"):
            self._update_rec_badge()
        if hasattr(self, "_em_toggle_switch"):
            self._update_em_badge()
        if hasattr(self, "_em_info_lbl"):
            cur_email = self._cfg.get("recovery_email", "").strip()
            self._em_info_lbl.setText(f"Registered: {cur_email}" if cur_email else "No recovery email registered.")


# Backward compatibility alias
_PasswordPanelMixin = _SecurityPanelMixin
