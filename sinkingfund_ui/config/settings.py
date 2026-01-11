"""Application settings and configuration."""

# Application configuration.
APP_CONFIG = {
    "app_title": "Sinking Fund Calculator",
    "app_icon": "🏦",
    "version": "0.1.0",
    "author": "Greg Barbieri",
    "description": "A lightweight UI for the sinkingfund library."
}

# Page configuration for each page.
PAGE_CONFIG = {
    "dashboard": {
        "page_title": "Dashboard - Sinking Fund Calculator",
        "page_icon": "📊",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    },
    "calculator": {
        "page_title": "Calculator - Sinking Fund Calculator",
        "page_icon": "💰",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    },
    "analysis": {
        "page_title": "Analysis - Sinking Fund Calculator",
        "page_icon": "📈",
        "layout": "wide",
        "initial_sidebar_state": "expanded"
    }
}

# Chart configuration.
CHART_CONFIG = {
    "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    "default_height": 400,
    "margin": {"t": 50, "b": 50, "l": 50, "r": 50}
}

# Calculation defaults.
CALCULATION_DEFAULTS = {
    "target_amount": 10000.0,
    "time_horizon": 12,
    "interest_rate": 0.025,
    "payment_frequency": "Monthly"
}

# UI configuration.
UI_CONFIG = {
    "sidebar_width": 300,
    "chart_height": 400,
    "table_height": 300,
    "max_rows_display": 100
}