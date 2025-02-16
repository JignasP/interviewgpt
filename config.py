"""Configuration file for the application"""

# Add the OpenAI API key directly
OPENAI_API_KEY = "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"

# UI Configuration
UI_CONFIG = {
    'WINDOW_SIZE': '1000x800',
    'MIN_WINDOW_SIZE': (900, 700),
    'DARK_BG': '#1a1a1a',
    'SUCCESS_COLOR': '#00ff99',
    'WARNING_COLOR': '#ffaa00',
    'ERROR_COLOR': '#ff3333',
    'DISABLED_COLOR': '#888888',
    'BUTTON_HEIGHT': 40,
    'FONT_FAMILY': 'Roboto',
    'MATCH_COLORS': {
        'high': '#4CAF50',          # Green
        'moderately high': '#8BC34A',  # Light Green
        'moderate': '#FFC107',      # Amber
        'low': '#FF5722',          # Deep Orange
    },
    'FEEDBACK_BG': '#262626',  # Slightly lighter than DARK_BG
    'FEEDBACK_TEXT': '#e0e0e0',  # Light grey for feedback text
    'FEEDBACK_HEIGHT': 100,  # Height of the feedback section
}
