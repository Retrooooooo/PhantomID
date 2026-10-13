"""PhantomID - CustomTkinter Application Theme Configuration"""
import customtkinter as ctk

# Color palette - slate/teal professional theme
COLORS = {
    "background": "#EDF2F6",
    "surface": "#FFFFFF",
    "sidebar": "#193449",
    "sidebar_hover": "#2C526B",
    "text": "#203B4C",
    "muted": "#526A7A",
    "accent": "#087E83",
    "accent_hover": "#06666B",
    "soft": "#E1F2F1",
    "border": "#D4DFE6",
    "error": "#A32F36",
    "success": "#075C60",
    "card": "#FFFFFF",
}

def setup_theme():
    """Configure CustomTkinter global theme settings"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Custom color overrides
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = COLORS["background"]
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = COLORS["accent"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = COLORS["accent_hover"]
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = "#FFFFFF"
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = COLORS["surface"]
    ctk.ThemeManager.theme["CTkEntry"]["border_color"] = COLORS["border"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["fg_color"] = COLORS["background"]
    ctk.ThemeManager.theme["CTkScrollbar"]["button_color"] = COLORS["muted"]
    ctk.ThemeManager.theme["CTkScrollbar"]["button_hover_color"] = COLORS["accent"]

def get_colors():
    return COLORS

# Font definitions
FONTS = {
    "heading_large": ("Segoe UI", 28, "bold"),
    "heading_medium": ("Segoe UI", 22, "bold"),
    "heading_small": ("Segoe UI", 18, "bold"),
    "body_large": ("Segoe UI", 16),
    "body": ("Segoe UI", 13),
    "body_small": ("Segoe UI", 11),
    "caption": ("Segoe UI", 10),
    "mono": ("Consolas", 11),
}

def get_font(name):
    return FONTS.get(name, FONTS["body"])