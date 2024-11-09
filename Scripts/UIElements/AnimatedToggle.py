from PyQt6.QtCore import (
    Qt, QSize, QPoint, QPointF, QRectF,
    QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup,
    pyqtSlot, pyqtProperty)

from PyQt6.QtWidgets import QCheckBox, QApplication
from PyQt6.QtGui import QColor, QBrush, QPaintEvent, QPen, QPainter, QPalette

import winaccent

class AnimatedToggle(QCheckBox):
    _transparent_pen = QPen(Qt.GlobalColor.transparent)
    _light_gray_pen = QPen(Qt.GlobalColor.lightGray)

    def __init__(self,
                 parent=None,
                 duration = 300,
                 squish_amount = 2
                 ):
        super().__init__(parent=parent)

        self._bar_brush = QBrush(Qt.GlobalColor.gray)
        self._bar_checked_brush = QBrush(QColor(winaccent.accent_normal))

        self._handle_brush = QBrush(Qt.GlobalColor.white)
        self._handle_checked_brush = QBrush(QColor(winaccent.accent_light))

        self.setContentsMargins(8,0,8,0)
        self._handle_position = 0
        self._squish_amount = 0

        self.animation = QPropertyAnimation(self,b"handle_position", self)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutBack)
        self.animation.setDuration(duration)

        self.squish_animation = QPropertyAnimation(self,b"squish_amount", self)
        self.squish_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.squish_animation.setDuration(duration)
        self.squish_animation.setStartValue(0)
        self.squish_animation.setKeyValueAt(0.5,squish_amount)
        self.squish_animation.setEndValue(0)

        self.animations_group = QParallelAnimationGroup()
        self.animations_group.addAnimation(self.animation)
        self.animations_group.addAnimation(self.squish_animation)

        self.stateChanged.connect(self.setup_animation)
    
    def sizeHint(self):
        return QSize(58, 45)
    
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)
    
    @pyqtSlot(int)
    def setup_animation(self, value):
        self.animations_group.stop()
        if value:
            self.animation.setEndValue(1)
        else:
            self.animation.setEndValue(0)
        self.animations_group.start()
    
    def paintEvent(self, e: QPaintEvent):

        contRect = self.contentsRect()
        handle_radius = round(0.24*contRect.height())

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(self._transparent_pen)
        barRect = QRectF(
            0, 0,
            contRect.width() - handle_radius, 0.40 * contRect.height()
        )
        barRect.moveCenter(QPointF(contRect.center()))
        rounding = barRect.height() / 2
        trail_length = contRect.width() - 2 * handle_radius

        xPos = contRect.x() + handle_radius + trail_length * self._handle_position
        yScale = handle_radius - self._squish_amount
        xScale = handle_radius + self._squish_amount*3

        if self.isChecked():
            p.setBrush(self._bar_checked_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setBrush(self._handle_checked_brush)
        else:
            p.setBrush(self._bar_brush)
            p.drawRoundedRect(barRect, rounding, rounding)
            p.setPen(self._light_gray_pen)
            p.setBrush(self._handle_brush)
        
        p.drawEllipse(
            QPointF(xPos, barRect.center().y()),
            xScale, yScale
        )

        p.end()
    
    @pyqtProperty(float)
    def handle_position(self):
        return self._handle_position
    
    @handle_position.setter
    def handle_position(self, pos):
        self._handle_position = pos
        self.update()
    
    @pyqtProperty(float)
    def squish_amount(self):
        return self._squish_amount
    
    @squish_amount.setter
    def squish_amount(self, pos):
        self._squish_amount = pos
        self.update()