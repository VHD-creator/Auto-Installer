import customtkinter as ctk

class Styles:
    # Font Families (Sử dụng Inter nếu có, nếu không sẽ tự động fallback về Segoe UI)
    FONT_FAMILY_MAIN = "Inter" 
    FONT_FAMILY_MONO = "Consolas"

    # Font Sizes & Weights (Làm thanh thoát hơn)
    FONT_TITLE_LARGE = (FONT_FAMILY_MAIN, 20, "bold")
    FONT_TITLE_MEDIUM = (FONT_FAMILY_MAIN, 17, "bold")
    FONT_TITLE_SMALL = (FONT_FAMILY_MAIN, 15, "bold")
    
    FONT_BUTTON = (FONT_FAMILY_MAIN, 14, "bold")
    FONT_BUTTON_SMALL = (FONT_FAMILY_MAIN, 13, "bold")
    
    FONT_LABEL_BOLD = (FONT_FAMILY_MAIN, 13, "bold")
    FONT_LABEL = (FONT_FAMILY_MAIN, 13)
    FONT_DESC = (FONT_FAMILY_MAIN, 11)
    FONT_INFO = (FONT_FAMILY_MAIN, 14)
    
    FONT_LOG = (FONT_FAMILY_MONO, 12)
    FONT_LOG_BOLD = (FONT_FAMILY_MONO, 12, "bold")


    # Colors (Optional: can be expanded if needed)
    COLOR_PRIMARY = "#3498db"
    COLOR_SUCCESS = "#2ecc71"
    COLOR_SUCCESS_HOVER = "#27ae60"
    COLOR_ERROR = "#e74c3c"
    COLOR_ERROR_HOVER = "#c0392b"
    COLOR_WARNING = "#f1c40f"
    
    TEXT_PRIMARY = ("#1f2328", "#f0f6fc")
    TEXT_SECONDARY = ("#656d76", "#8b949e")
