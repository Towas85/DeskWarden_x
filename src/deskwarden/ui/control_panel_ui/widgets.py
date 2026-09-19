"""
DeskWarden - ui/control_panel_ui/widgets.py

"""

from PyQt6.QtWidgets import (
    QFrame, QLabel, QPushButton, QWidget, QSizePolicy,
    QGraphicsDropShadowEffect, QHBoxLayout, QAbstractButton,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QPainterPath, QBrush, QPen, QCursor,
)

from ...core.logging_utils import dlog
from .theme import (
    _CARD, _CARD2, _BORD, _ACC, _ACC2, _MUTE, _FG, _GREEN,
    _STRIP_X_OFFSET, _STRIP_WIDTH,
)


class _Card(QFrame):
    def __init__(self, parent=None, bg=_CARD, border=_BORD,
                 radius=14, accent_color=None, hoverable=False):
        super().__init__(parent)
        self._bg       = QColor(bg)
        self._border   = QColor(border)
        self._radius   = radius
        self._accent   = QColor(accent_color) if accent_color else None
        self._hoverable = hoverable
        self._hovered  = False
        self.setAutoFillBackground(False)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def enterEvent(self, ev):
        if self._hoverable:
            self._hovered = True
            self.update()
        super().enterEvent(ev)

    def leaveEvent(self, ev):
        if self._hoverable:
            self._hovered = False
            self.update()
        super().leaveEvent(ev)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(r.x(), r.y(), r.width(), r.height(),
                            self._radius, self._radius)
        p.fillPath(path, QBrush(self._bg))
        border_color = self._border
        if self._hoverable and self._hovered:
            border_color = self._accent if self._accent else QColor(_ACC2)
        p.setPen(QPen(border_color, 1))
        p.drawPath(path)
        if self._accent:
            strip = QPainterPath()
            strip.addRoundedRect(r.x() + _STRIP_X_OFFSET, r.y(),
                                 _STRIP_WIDTH, r.height(), 2, 2)
            p.fillPath(strip, QBrush(self._accent))


class _IconBox(QLabel):
    def __init__(self, glyph, size=38, bg="#1e0d40", fg="#c4b5fd",
                 radius=10, parent=None):
        super().__init__(glyph, parent)
        self._bg = QColor(bg)
        self._r  = radius
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI Emoji", size // 3))
        self.setStyleSheet(f"color: {fg}; background: transparent;")

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(),
                            self._r, self._r)
        p.fillPath(path, QBrush(self._bg))
        super().paintEvent(ev)


class _AppIconBox(QFrame):
    def __init__(self, pixmap=None, glyph="🔒", size=40,
                 bg="#1e0d40", fg="#c4b5fd", radius=12, parent=None):
        super().__init__(parent)
        self._pixmap = pixmap if (pixmap and not pixmap.isNull()) else None
        self._glyph  = glyph
        self._fg     = QColor(fg)
        self._bg     = QColor("#1c1830" if self._pixmap else bg)
        self._r      = radius
        self.setFixedSize(size, size)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(),
                            self._r, self._r)
        p.fillPath(path, QBrush(self._bg))
        if self._pixmap:
            p.setClipPath(path)
            pw = float(self._pixmap.width())
            ph = float(self._pixmap.height())
            dpr = self._pixmap.devicePixelRatio()
            if dpr > 0:
                pw /= dpr
                ph /= dpr
            target_size = min(30.0, float(self.width() - 6), float(self.height() - 6))
            scale = min(target_size / max(pw, 1.0), target_size / max(ph, 1.0))
            dw = pw * scale
            dh = ph * scale
            dx = (float(self.width()) - dw) / 2.0
            dy = (float(self.height()) - dh) / 2.0
            target_rect = QRectF(dx, dy, dw, dh)
            p.drawPixmap(target_rect, self._pixmap, QRectF(0, 0, self._pixmap.width(), self._pixmap.height()))
        else:
            p.setPen(QPen(self._fg))
            p.setFont(QFont("Segoe UI Emoji", 17))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._glyph)


class _NavBtn(QPushButton):
    def __init__(self, icon, text, active=False, parent=None):
        super().__init__(f"  {icon}  {text}", parent)
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 9))
        self._upd(active)
        self.toggled.connect(self._upd)

    def _upd(self, c=False):
        if c:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #221050, stop:1 #160d38);
                    color: {_ACC2}; border: none;
                    border-left: 3px solid {_ACC};
                    border-radius: 10px; text-align: left;
                    padding-left: 10px; font-size: 9pt; font-weight: bold;
                }}""")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {_MUTE};
                    border: none; border-radius: 10px;
                    text-align: left; padding-left: 14px; font-size: 9pt;
                }}
                QPushButton:hover {{
                    background: #130f24; color: #b0a0e0;
                }}""")


class _PillBtn(QPushButton):
    def __init__(self, text, active=False, color=_ACC, parent=None):
        super().__init__(text, parent)
        self._color = color
        self._active_glow = None
        self.setCheckable(True)
        self.setChecked(active)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Fixed)
        self.setFixedHeight(32)
        f = QFont("Segoe UI", 9)
        f.setBold(active)
        self.setFont(f)
        self._upd(active)
        self.toggled.connect(self._on_tog)

    def _on_tog(self, c):
        f = self.font(); f.setBold(c); self.setFont(f)
        self._upd(c)
        if c:
            fx = QGraphicsDropShadowEffect()
            fx.setBlurRadius(8)
            fx.setColor(QColor(self._color))
            fx.setOffset(0, 0)
            self._active_glow = fx
            self.setGraphicsEffect(fx)
        else:
            self._active_glow = None
            self.setGraphicsEffect(None)

    def enterEvent(self, ev):
        if self.isChecked() and self._active_glow:
            self._active_glow.setBlurRadius(14)
            _second = {
                "#22d3ee": "#7c3aed",   
                "#22c55e": "#22d3ee",   
            }.get(self._color, f"{self._color}cc")
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self._color}, stop:1 {_second});
                    color: white;
                    border: 1.5px solid rgba(255,255,255,0.55);
                    border-radius: 8px; padding: 0 12px;
                }}""")
        elif not self.isChecked():
            r = int(self._color[1:3], 16)
            g = int(self._color[3:5], 16)
            b = int(self._color[5:7], 16)

            _opacity = 0.4   
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {_CARD2}; color: {_FG};
                    border: 1px solid rgba({r},{g},{b},{_opacity});
                    border-radius: 8px; padding: 0 12px;
                }}""")
        super().enterEvent(ev)

    def leaveEvent(self, ev):
        if self.isChecked() and self._active_glow:
            self._active_glow.setBlurRadius(8)
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self._color}; color: white;
                    border: none; border-radius: 8px; padding: 0 12px;
                }}
                QPushButton:hover {{
                    background: {self._color};
                    border: 1px solid rgba(255,255,255,0.35);
                }}""")
        elif not self.isChecked():
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {_CARD2}; color: {_MUTE};
                    border: 1px solid {_BORD}; border-radius: 8px;
                    padding: 0 12px;
                }}""")
        super().leaveEvent(ev)

    def _upd(self, c):
        if c:
            fx = QGraphicsDropShadowEffect()
            fx.setBlurRadius(8)
            fx.setColor(QColor(self._color))
            fx.setOffset(0, 0)
            self._active_glow = fx
            self.setGraphicsEffect(fx)
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self._color}; color: white;
                    border: none; border-radius: 8px; padding: 0 12px;
                }}
                QPushButton:hover {{
                    background: {self._color};
                    border: 1px solid rgba(255,255,255,0.35);
                }}""")
        else:
            self._active_glow = None
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {_CARD2}; color: {_MUTE};
                    border: 1px solid {_BORD}; border-radius: 8px;
                    padding: 0 12px;
                }}""")

# ── Sidebar live-status widgets (spinner + rotating info ticker) ────


class _StatusSpinner(QWidget):

    def __init__(self, size=12, color=_GREEN, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._color = QColor(color)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def set_color(self, color):
        try:
            self._color = QColor(color)
            self.update()
        except Exception:
            pass

    def _tick(self):
        self._angle = (self._angle + 9) % 360
        self.update()

    def paintEvent(self, ev):
        try:
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            pen = QPen(self._color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            r = self.rect().adjusted(1, 1, -1, -1)
            p.drawArc(r, int(self._angle * 16), int(250 * 16))
            p.end()
        except Exception:
            pass

    def stop(self):
        try:
            self._timer.stop()
        except Exception:
            pass


class _RotatingStatus(QWidget):

    def __init__(self, get_items_fn, spinner=None, interval_ms=3000, parent=None):
        super().__init__(parent)
        self._get_items = get_items_fn
        self._spinner = spinner
        self._idx = 0
        self._cur_anim = None
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)
        self._label = QLabel("")
        self._label.setFont(QFont("Segoe UI", 8, QFont.Weight.Medium))
        self._label.setStyleSheet(f"color: {_GREEN}; background: transparent;")
        self._label.setWordWrap(False)
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self._full_text = ""
        self._label_max_w = 168   
        self._label.setMaximumWidth(self._label_max_w)
        lay.addWidget(self._label)
        try:
            from PyQt6.QtWidgets import QGraphicsOpacityEffect as _RSOpacityFx
            self._fx = _RSOpacityFx(self._label)
            self._fx.setOpacity(1.0)
            self._label.setGraphicsEffect(self._fx)
        except Exception:
            self._fx = None
        self._set_current(initial=True)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._timer.start(max(int(interval_ms), 1000))

    def _safe_items(self):
        try:
            items = self._get_items()
            if items:
                return items
        except Exception as _e:
            try:
                dlog("ERROR", f"_sidebar_status_items failed: {type(_e).__name__}: {_e}")
            except Exception:
                pass
            return [(f"Status error: {type(_e).__name__}", "#fbbf24")]
        return [("Status: no items", "#fbbf24")]

    def _set_current(self, initial=False):
        try:
            items = self._safe_items()
            if self._idx >= len(items):
                self._idx = 0
            text, color = items[self._idx]
            self._full_text = text
            fm = self._label.fontMetrics()
            elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, self._label_max_w)
            self._label.setText(elided)
            self._label.setToolTip(text)
            self._label.setStyleSheet(f"color: {color}; background: transparent;")
            if self._spinner is not None:
                self._spinner.set_color(color)
            if self._fx is not None:
                if initial:
                    self._fx.setOpacity(1.0)
                else:
                    self._fx.setOpacity(0.0)
                    anim = QPropertyAnimation(self._fx, b"opacity", self)
                    anim.setDuration(320)
                    anim.setStartValue(0.0)
                    anim.setEndValue(1.0)
                    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
                    self._cur_anim = anim
                    anim.start()
        except Exception:
            pass

    def _advance(self):
        try:
            items = self._safe_items()
            if not items:
                return
            if self._fx is None:
                self._idx = (self._idx + 1) % len(items)
                self._set_current()
                return
            fade_out = QPropertyAnimation(self._fx, b"opacity", self)
            fade_out.setDuration(260)
            fade_out.setStartValue(self._fx.opacity())
            fade_out.setEndValue(0.0)
            fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
            n_items = len(items)
            def _on_out_done():
                try:
                    self._idx = (self._idx + 1) % max(n_items, 1)
                    self._set_current()
                except Exception:
                    pass
            fade_out.finished.connect(_on_out_done)
            self._cur_anim = fade_out
            fade_out.start()
        except Exception:
            pass

    def stop(self):
        try:
            self._timer.stop()
        except Exception:
            pass


class _ToggleSwitch(QAbstractButton):
    """Modern iOS/fluent style pill toggle switch widget with smooth animation."""

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(38, 20)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._thumb_pos = 20.0 if checked else 2.0
        self._anim = QPropertyAnimation(self, b"thumb_pos", self)
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.toggled.connect(self._on_toggled)

    def get_thumb_pos(self):
        return self._thumb_pos

    def set_thumb_pos(self, pos):
        self._thumb_pos = float(pos)
        self.update()

    thumb_pos = pyqtProperty(float, get_thumb_pos, set_thumb_pos)

    def _on_toggled(self, checked):
        end = 20.0 if checked else 2.0
        self._anim.stop()
        self._anim.setStartValue(self._thumb_pos)
        self._anim.setEndValue(end)
        self._anim.start()

    def setChecked(self, checked):
        super().setChecked(checked)
        self._thumb_pos = 20.0 if checked else 2.0
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.rect()
        enabled = self.isEnabled()
        checked = self.isChecked()

        if not enabled:
            bg = QColor("#161424")
            border = QColor("#2a2545")
            thumb_c = QColor("#443f60")
        elif checked:
            bg = QColor("#7c3aed")
            border = QColor("#9d5cff")
            thumb_c = QColor("#ffffff")
        else:
            bg = QColor("#1e1b2e")
            border = QColor("#3f3a5e")
            thumb_c = QColor("#94a3b8")

        # Track pill
        path = QPainterPath()
        path.addRoundedRect(1.0, 1.0, float(r.width() - 2), float(r.height() - 2), 9.0, 9.0)
        p.fillPath(path, QBrush(bg))
        p.setPen(QPen(border, 1.2))
        p.drawPath(path)

        # Thumb
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(thumb_c))
        p.drawEllipse(int(self._thumb_pos), 3, 14, 14)



