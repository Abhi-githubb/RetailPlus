"""
Custom CSS and Styling Engine for RetailPulse SaaS Dashboard.
Provides a modern dark-slate aesthetic, glowing metric cards, typography,
custom tooltips, and clean tabular formatting.
"""

def load_custom_css() -> str:
    """Returns custom CSS to inject into Streamlit."""
    return """
    <style>
        /* Modern Fonts and Global Styling */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        /* Top Header & Branding */
        .brand-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        }

        .brand-title {
            font-size: 1.75rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.5px;
        }

        .brand-tagline {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 0.2rem;
        }

        .live-badge {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            border: 1px solid rgba(16, 185, 129, 0.3);
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
        }

        /* Metric Cards */
        .metric-card {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.07);
            box-shadow: 0 4px 15px -2px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, border-color 0.2s ease;
            margin-bottom: 1rem;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 189, 248, 0.3);
        }

        .metric-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 0.35rem;
            letter-spacing: -0.5px;
        }

        .metric-footer {
            display: flex;
            align-items: center;
            font-size: 0.78rem;
            gap: 0.4rem;
        }

        .delta-positive {
            color: #34d399;
            font-weight: 600;
        }

        .delta-negative {
            color: #f87171;
            font-weight: 600;
        }

        .delta-neutral {
            color: #94a3b8;
        }

        /* Insight Box */
        .insight-box {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
            border-left: 4px solid #38bdf8;
            border-radius: 0 10px 10px 0;
            padding: 1rem 1.25rem;
            margin: 1.25rem 0;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .insight-header {
            font-size: 0.85rem;
            font-weight: 700;
            color: #38bdf8;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .insight-text {
            font-size: 0.92rem;
            color: #cbd5e1;
            line-height: 1.5;
            margin: 0;
        }

        /* Tab and Sidebar Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            background-color: transparent;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(56, 189, 248, 0.15) !important;
            color: #38bdf8 !important;
        }

        /* DataFrames */
        .dataframe {
            font-size: 0.85rem !important;
        }
    </style>
    """
