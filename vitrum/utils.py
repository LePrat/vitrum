from PySide6.QtWidgets import QPushButton


def create_btn(text, callback, is_close=False, width=32):
    btn = QPushButton(text)
    btn.setFixedSize(width, 28)
    hover_color = "#e81123" if is_close else "rgba(255, 255, 255, 40)"
    btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; color: white; border-radius: 4px; font-size: 14px; }}
        QPushButton:hover {{ background: {hover_color}; }}
    """)
    if callback is not None:
        btn.clicked.connect(callback)
    return btn
