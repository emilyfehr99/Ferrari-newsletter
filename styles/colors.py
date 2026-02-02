"""
Ferrari F1 Newsletter - Brand Colors & Style Constants
Using official Ferrari brand colors
"""

# ============================================
# OFFICIAL FERRARI BRAND COLORS
# ============================================

COLORS = {
    # Primary Ferrari Colors
    "FERRARI_RED": "#EF1A2D",       # Primary brand red - PMS 185 C
    "FERRARI_YELLOW": "#FFF200",    # Accent yellow - PMS 803 C
    "FERRARI_BLACK": "#000000",     # Black - PMS Neutral Black C
    "FERRARI_WHITE": "#FFFFFF",     # White
    "FERRARI_GREEN": "#00A551",     # Italian flag green - PMS 2252 C
    
    # Extended Palette (derived shades)
    "RED_DARK": "#C41422",          # Darker red for gradients
    "RED_LIGHT": "#FF4D5A",         # Lighter red for hover states
    "GRAY_DARK": "#1a1a1a",         # Dark background
    "GRAY_MEDIUM": "#333333",       # Dividers
    "GRAY_LIGHT": "#888888",        # Secondary text
    "GRAY_LIGHTEST": "#F8F8F8",     # Light backgrounds
    
    # Category Colors
    "CATEGORY_RACE": "#EF1A2D",     # Race weekend news
    "CATEGORY_TECHNICAL": "#000000", # Technical updates
    "CATEGORY_DRIVER": "#00A551",   # Driver news
    "CATEGORY_STRATEGY": "#FFF200", # Strategy analysis
}

# RGB Values for image processing
RGB_COLORS = {
    "FERRARI_RED": (239, 26, 45),
    "FERRARI_YELLOW": (255, 242, 0),
    "FERRARI_BLACK": (0, 0, 0),
    "FERRARI_WHITE": (255, 255, 255),
    "FERRARI_GREEN": (0, 165, 81),
}

# CMYK Values for print (if needed)
CMYK_COLORS = {
    "FERRARI_RED": (0, 89, 81, 6),
    "FERRARI_YELLOW": (0, 5, 100, 0),
    "FERRARI_BLACK": (0, 0, 0, 100),
    "FERRARI_GREEN": (100, 0, 51, 35),
}

# ============================================
# TYPOGRAPHY
# ============================================

FONTS = {
    "HEADING": "'Formula1', Arial, sans-serif",
    "BODY": "Georgia, 'Times New Roman', serif",
    "META": "Arial, sans-serif",
}

# ============================================
# ICON MAPPINGS FOR TECHNICAL UPDATES
# ============================================

TECH_ICONS = {
    "engine": "⚙️",
    "aero": "🌬️",
    "suspension": "🔧",
    "electronics": "⚡",
    "strategy": "📊",
    "tires": "🔴",
    "brakes": "🛑",
    "fuel": "⛽",
    "upgrade": "📈",
    "general": "🏎️",
}

# Category styling
CATEGORY_STYLES = {
    "Race Weekend": {"color": COLORS["CATEGORY_RACE"], "icon": "🏁"},
    "Technical": {"color": COLORS["CATEGORY_TECHNICAL"], "icon": "⚙️"},
    "Driver News": {"color": COLORS["CATEGORY_DRIVER"], "icon": "👤"},
    "Strategy": {"color": COLORS["CATEGORY_STRATEGY"], "icon": "📊"},
    "Breaking": {"color": COLORS["FERRARI_RED"], "icon": "🔴"},
}
