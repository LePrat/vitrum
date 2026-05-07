class UIStyles:
    TRANSPARENCY = int(50 * 255 / 100)
    BG_COLOR = f"rgba(30, 30, 30, {TRANSPARENCY})"
    RADIUS = "12px"
    MAIN_CONTAINER = f"""
        QWidget#MainContainer {{
            background-color: {BG_COLOR};
            border-radius: {RADIUS};
            border: 1px solid rgba(255, 255, 255, 40);
        }}
    """
    TOOLBAR = f"""
    QToolBar {{
        background: rgba(255, 255, 255, 70);
        border-bottom: 1px solid rgba(255, 255, 255, 20);
        border-top-left-radius: {RADIUS};
        border-top-right-radius: {RADIUS};
        padding: 4px;
    }}

    QToolBar > QWidget {{
        height: 24px;
        max-height: 24px;
        min-height: 24px;
    }}

    QToolButton {{ 
        color: white; 
        padding: 5px; 
    }}

    QToolButton:hover {{ 
        background: rgba(255, 255, 255, 30); 
        border-radius: 4px; 
    }}
    """
    OPACITY_TOOL = """
        QSpinBox {
            background: rgba(0, 0, 0, 100);
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 4px;
            padding: 2px;
        }
    """
    CIRCLE_SPINBOX = """
        QDoubleSpinBox {
            background: rgba(0, 0, 0, 100);
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
            border-radius: 4px;
            padding: 2px;
        }
    """
    MENU = """
        QMenu {
            background-color: #2b2b2b;
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
        }
        QMenu::item:selected {
            background-color: rgba(255, 255, 255, 30);
        }
        """
    FILE_MENU = """
        QToolButton {
            background: rgba(0, 0, 0, 100);
            color: white;
            border: 1px solid rgba(255, 255, 255, 30);
            padding: 4px 10px;
        }
        QToolButton:hover {
            background: rgba(255, 255, 255, 30);
        }
        QToolButton::menu-indicator {
            image: none;
        }
    """
