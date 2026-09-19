"""
DeskWarden - ui/control_panel_ui/first_run_dialog.py

Two-step first run onboarding wizard:
  Step 1: Master Password & Optional Recovery Email
  Step 2: Master Recovery Key generation, copying, saving, and red security warning
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect, QApplication, QStackedWidget, QFileDialog,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QCursor, QPixmap, QPainter, QPainterPath

from ...core.paths import asset_path
from ...core.config import load_config, save_config
from ...core.logging_utils import suppress_faulthandler
from ...core.security import (
    hash_pw, generate_recovery_key, hash_recovery_key, log_security_event,
)
from .theme import _CARD, _CARD2, _BORD, _ACC, _ACC2, _ACC3, _FG, _MUTE, _RED, _GREEN
from .widgets import _Card


class _FirstRunSetupDialog(QWidget):
    """Forces the user to set a master password and recovery options on first run,
    before the Control Panel interface is shown."""
    def __init__(self, on_done):
        super().__init__()
        self._on_done = on_done
        self._allow_close = False
        self._temp_pw = ""
        self._temp_email = ""
        self._generated_key = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(440, 520)

        sg = QApplication.instance().primaryScreen().geometry()
        self.move(sg.x() + (sg.width() - 440) // 2,
                  sg.y() + (sg.height() - 520) // 2)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = _Card(self, bg=_CARD, border=_BORD, radius=16)
        outer.addWidget(self._card)

        self._card_lay = QVBoxLayout(self._card)
        self._card_lay.setContentsMargins(24, 18, 24, 18)
        self._card_lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._card_lay.addWidget(self._stack)

        self._init_step1_ui()
        self._init_step2_ui()
        self._stack.setCurrentIndex(0)

    # ── Step 1: Password & Optional Email ──────────────────────────────────

    def _init_step1_ui(self):
        page1 = QWidget()
        p1_lay = QVBoxLayout(page1)
        p1_lay.setContentsMargins(4, 0, 4, 0)
        p1_lay.setSpacing(8)

        # Logo
        _pm = QPixmap(asset_path("icon.png"))
        if not _pm.isNull():
            _pm = _pm.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            class _LogoWidget(QWidget):
                def __init__(self, px):
                    super().__init__()
                    self._px = px
                    self.setFixedSize(64, 64)
                    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                def paintEvent(self, ev):
                    p = QPainter(self)
                    p.setRenderHint(QPainter.RenderHint.Antialiasing)
                    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                    path = QPainterPath()
                    path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
                    p.setClipPath(path)
                    p.drawPixmap(0, 0, self.width(), self.height(), self._px)
                    p.end()
            logo = _LogoWidget(_pm)
        else:
            logo = QLabel("🔒")
            logo.setFont(QFont("Segoe UI Emoji", 28))
            logo.setStyleSheet(f"color: {_ACC2}; background: transparent;")
            logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row = QHBoxLayout()
        logo_row.addStretch(); logo_row.addWidget(logo); logo_row.addStretch()
        p1_lay.addLayout(logo_row)

        title = QLabel("Welcome to DeskWarden")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {_FG}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p1_lay.addWidget(title)

        sub = QLabel("Set your master password and optional recovery email before you start.")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        p1_lay.addWidget(sub)

        _in_style = f"""
            QLineEdit {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px; padding: 0 12px;
                font-size: 9pt; font-family: 'Segoe UI';
            }}
            QLineEdit:focus {{ border: 1px solid {_ACC}; background: #16122a; }}
        """

        _pw_in_style = f"""
            QLineEdit {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
                padding: 0 46px 0 12px;
                font-size: 9pt; font-family: 'Segoe UI';
            }}
            QLineEdit:focus {{ border: 1px solid {_ACC}; background: #16122a; }}
        """

        def _create_pw_field(placeholder: str):
            pw_edit = QLineEdit()
            pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
            pw_edit.setPlaceholderText(placeholder)
            pw_edit.setFixedHeight(34)
            pw_edit.setStyleSheet(_pw_in_style)

            eye_btn = QPushButton("Show", pw_edit)
            eye_btn.setFixedSize(38, 22)
            eye_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            eye_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {_MUTE};
                    border: none; font-size: 7.5pt; font-weight: 600;
                    font-family: 'Segoe UI';
                }}
                QPushButton:hover {{ color: {_FG}; }}
            """)
            def _position_eye_btn():
                eye_btn.move(pw_edit.width() - eye_btn.width() - 6, (pw_edit.height() - eye_btn.height()) // 2)
            _orig_resize = pw_edit.resizeEvent
            def _pw_resize(ev):
                _orig_resize(ev)
                _position_eye_btn()
            pw_edit.resizeEvent = _pw_resize
            _position_eye_btn()

            _pw_visible = [False]
            def _toggle_eye():
                _pw_visible[0] = not _pw_visible[0]
                pw_edit.setEchoMode(QLineEdit.EchoMode.Normal if _pw_visible[0] else QLineEdit.EchoMode.Password)
                eye_btn.setText("Hide" if _pw_visible[0] else "Show")
                eye_btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; color: {_MUTE}; border: none;
                        font-size: 7.5pt; font-weight: 600; font-family: 'Segoe UI';
                    }}
                    QPushButton:hover {{ color: {_FG}; }}
                """)
            eye_btn.clicked.connect(_toggle_eye)

            return pw_edit

        nl = QLabel("New Master Password *")
        nl.setFont(QFont("Segoe UI", 9))
        nl.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        p1_lay.addWidget(nl)

        self._new_pw = _create_pw_field("Enter at least 4 characters")
        p1_lay.addWidget(self._new_pw)

        cnl = QLabel("Confirm Password *")
        cnl.setFont(QFont("Segoe UI", 9))
        cnl.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        p1_lay.addWidget(cnl)

        self._con_pw = _create_pw_field("Re-enter master password")
        p1_lay.addWidget(self._con_pw)

        eml = QLabel("Recovery Email (Optional)")
        eml.setFont(QFont("Segoe UI", 9))
        eml.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        p1_lay.addWidget(eml)

        self._email_in = QLineEdit()
        self._email_in.setPlaceholderText("e.g. user@example.com")
        self._email_in.setFixedHeight(34)
        self._email_in.setStyleSheet(_in_style)
        p1_lay.addWidget(self._email_in)

        self._err = QLabel("")
        self._err.setFont(QFont("Segoe UI", 9))
        self._err.setStyleSheet(f"color: {_RED}; background: transparent;")
        self._err.setWordWrap(True)
        p1_lay.addWidget(self._err)

        next_btn = QPushButton("Continue  ➔")
        next_btn.setFixedHeight(36)
        next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        next_btn.setAutoDefault(False)
        next_btn.setDefault(False)
        next_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {_ACC}, stop:1 {_ACC3});
                color: white; border: none; border-radius: 10px; padding: 0 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {_ACC2}, stop:1 {_ACC});
            }}""")
        next_btn.clicked.connect(self._step1_continue)
        p1_lay.addWidget(next_btn)

        skip_btn = QPushButton("Skip for now")
        skip_btn.setFixedHeight(28)
        skip_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        skip_btn.setFont(QFont("Segoe UI", 9))
        skip_btn.setAutoDefault(False)
        skip_btn.setDefault(False)
        skip_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {_MUTE}; border: none;
                border-radius: 8px; padding: 0 14px;
            }}
            QPushButton:hover {{ color: {_FG}; }}""")
        skip_btn.clicked.connect(self._skip)
        p1_lay.addWidget(skip_btn)

        self._new_pw.returnPressed.connect(self._step1_continue)
        self._con_pw.returnPressed.connect(self._step1_continue)
        self._email_in.returnPressed.connect(self._step1_continue)
        self._stack.addWidget(page1)

    # ── Step 2: Recovery Key ───────────────────────────────────────────────

    def _init_step2_ui(self):
        page2 = QWidget()
        p2_lay = QVBoxLayout(page2)
        p2_lay.setContentsMargins(4, 0, 4, 0)
        p2_lay.setSpacing(9)

        # Logo - Exact same position & 64x64 size as Step 1
        _pm = QPixmap(asset_path("icon.png"))
        if not _pm.isNull():
            _pm = _pm.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            class _LogoWidget2(QWidget):
                def __init__(self, px):
                    super().__init__()
                    self._px = px
                    self.setFixedSize(64, 64)
                    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                def paintEvent(self, ev):
                    p = QPainter(self)
                    p.setRenderHint(QPainter.RenderHint.Antialiasing)
                    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                    path = QPainterPath()
                    path.addRoundedRect(0, 0, self.width(), self.height(), 14, 14)
                    p.setClipPath(path)
                    p.drawPixmap(0, 0, self.width(), self.height(), self._px)
                    p.end()
            logo2 = _LogoWidget2(_pm)
        else:
            logo2 = QLabel("🔒")
            logo2.setFont(QFont("Segoe UI Emoji", 28))
            logo2.setStyleSheet(f"color: {_ACC2}; background: transparent;")
            logo2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_row2 = QHBoxLayout()
        logo_row2.addStretch(); logo_row2.addWidget(logo2); logo_row2.addStretch()
        p2_lay.addLayout(logo_row2)

        title = QLabel("Master Recovery Key")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #4ade80; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p2_lay.addWidget(title)

        sub = QLabel("Your emergency recovery key has been generated. Use this key to reset your master password if forgotten.")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {_MUTE}; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        p2_lay.addWidget(sub)

        # Key display box
        self._key_box = QLineEdit()
        self._key_box.setReadOnly(True)
        self._key_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._key_box.setFixedHeight(40)
        self._key_box.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self._key_box.setStyleSheet(f"""
            QLineEdit {{
                background: #0d0b1a;
                color: #a78bfa;
                border: 1px solid #3b2d6a;
                border-radius: 8px;
                padding: 0 10px;
                letter-spacing: 1.5px;
            }}
        """)
        p2_lay.addWidget(self._key_box)

        # Copy & Save buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._copy_btn = QPushButton("Copy Key")
        self._copy_btn.setFixedHeight(34)
        self._copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._copy_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._copy_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
            }}
            QPushButton:hover {{
                background: #251d45; border-color: {_ACC};
            }}
        """)
        self._copy_btn.clicked.connect(self._copy_key)
        btn_row.addWidget(self._copy_btn)

        self._save_file_btn = QPushButton("Save to Desktop")
        self._save_file_btn.setFixedHeight(34)
        self._save_file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._save_file_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._save_file_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 8px;
            }}
            QPushButton:hover {{
                background: #251d45; border-color: {_ACC};
            }}
        """)
        self._save_file_btn.clicked.connect(self._save_key_file)
        btn_row.addWidget(self._save_file_btn)
        p2_lay.addLayout(btn_row)

        # Red Warning Banner
        warn_box = QWidget()
        warn_box.setStyleSheet(f"""
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 8px;
            padding: 4px;
        """)
        w_lay = QVBoxLayout(warn_box)
        w_lay.setContentsMargins(12, 8, 12, 8)
        w_lay.setSpacing(2)

        warn_txt = QLabel(
            "<b>IMPORTANT:</b> Store this key in a secure place. "
            "If you forget your master password, this recovery key (or your email OTP) is the only way to recover access."
        )
        warn_txt.setFont(QFont("Segoe UI", 8))
        warn_txt.setStyleSheet("color: #f87171; background: transparent; border: none; line-height: 135%;")
        warn_txt.setWordWrap(True)
        w_lay.addWidget(warn_txt)
        p2_lay.addWidget(warn_box)
        p2_lay.addStretch(1)

        # Bottom action row with Back button and Launch button
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        back_btn = QPushButton("← Back")
        back_btn.setFixedHeight(36)
        back_btn.setFixedWidth(85)
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        back_btn.setAutoDefault(False)
        back_btn.setDefault(False)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_CARD2}; color: {_FG};
                border: 1px solid {_BORD}; border-radius: 10px;
            }}
            QPushButton:hover {{
                background: #251d45; border-color: {_ACC};
            }}
        """)
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        action_row.addWidget(back_btn)

        finish_btn = QPushButton("✓  Launch Application  ➔")
        finish_btn.setFixedHeight(36)
        finish_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        finish_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        finish_btn.setAutoDefault(False)
        finish_btn.setDefault(False)
        finish_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {_ACC}, stop:1 {_ACC3});
                color: white; border: none; border-radius: 10px; padding: 0 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {_ACC2}, stop:1 {_ACC});
            }}
        """)
        finish_btn.clicked.connect(self._finish_setup)
        action_row.addWidget(finish_btn, 1)

        p2_lay.addLayout(action_row)

        self._stack.addWidget(page2)

    # ── Events & Actions ──────────────────────────────────────────────────

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_Escape:
            ev.ignore(); return
        if (ev.key() == Qt.Key.Key_F4 and ev.modifiers() & Qt.KeyboardModifier.AltModifier):
            ev.ignore(); return
        super().keyPressEvent(ev)

    def closeEvent(self, ev):
        if self._allow_close:
            ev.accept()
        else:
            ev.ignore()

    def _step1_continue(self):
        n = self._new_pw.text()
        c = self._con_pw.text()
        em = self._email_in.text().strip()

        if len(n) < 4:
            self._err.setText("✗ Password must be at least 4 characters.")
            return
        if n != c:
            self._err.setText("✗ Passwords do not match.")
            return
        if em and ("@" not in em or "." not in em.split("@")[-1]):
            self._err.setText("✗ Please enter a valid email address.")
            return

        # Keep temporary state in memory — DO NOT save to disk yet!
        self._temp_pw = n
        self._temp_email = em
        if not self._generated_key:
            self._generated_key = generate_recovery_key()

        self._key_box.setText(self._generated_key)
        self._err.setText("")
        self._stack.setCurrentIndex(1)

    def _copy_key(self):
        if self._generated_key:
            cb = QApplication.clipboard()
            if cb:
                cb.setText(self._generated_key)
            self._copy_btn.setText("✓ Copied!")
            QTimer.singleShot(2000, lambda: self._copy_btn.setText("Copy Key"))

    def _save_key_file(self):
        if not self._generated_key:
            return
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(desktop_dir):
            desktop_dir = os.path.expanduser("~")
        default_target = os.path.join(desktop_dir, "DeskWarden-Recovery-Key.txt")

        with suppress_faulthandler():
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Master Recovery Key",
                default_target,
                "Text Files (*.txt);;All Files (*.*)",
            )
        if path:
            try:
                content = (
                    "=====================================================\n"
                    "        DESKWARDEN MASTER RECOVERY KEY               \n"
                    "=====================================================\n\n"
                    f"Recovery Key : {self._generated_key}\n\n"
                    "IMPORTANT:\n"
                    "- Keep this key in a safe place (offline or password manager).\n"
                    "- If you ever forget your master password, this key allows\n"
                    "  you to reset it and regain access to DeskWarden.\n"
                    "=====================================================\n"
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                self._save_file_btn.setText("✓ Saved!")
                QTimer.singleShot(2000, lambda: self._save_file_btn.setText("Save to Desktop"))
            except Exception:
                pass

    def _finish_setup(self):
        # Commit password and recovery settings to disk only now
        cfg = load_config()
        if hasattr(self, "_temp_pw") and self._temp_pw:
            cfg["password_hash"] = hash_pw(self._temp_pw)
            log_security_event("password_set", "First Run Setup", "Master password configured")
        if hasattr(self, "_temp_email") and self._temp_email:
            cfg["recovery_email"] = self._temp_email
            cfg["recovery_email_enabled"] = True
            log_security_event("email_configured", "First Run Setup", f"Recovery email set to {self._temp_email}")
        if self._generated_key:
            cfg["recovery_key_hash"] = hash_recovery_key(self._generated_key)
            cfg["recovery_key_enabled"] = True
            log_security_event("recovery_key_regenerated", "First Run Setup", "Master Recovery Key generated")
        save_config(cfg)

        self._allow_close = True
        self.close()
        self._on_done()

    def _skip(self):
        # Do not save any password or recovery key
        self._temp_pw = ""
        self._temp_email = ""
        self._generated_key = ""
        self._allow_close = True
        self.close()
        self._on_done()


