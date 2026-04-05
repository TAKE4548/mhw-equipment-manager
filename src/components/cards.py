import streamlit as st

def get_badge_html(text, bgcolor="#444", color="white"):
    return f'<span style="background-color: {bgcolor}; color: {color}; padding: 1px 6px; border-radius: 3px; font-size: 0.75em; font-weight: bold; display: inline-block; min-width: 35px; text-align: center; margin-right: 8px;">{text}</span>'

def inject_card_css():
    st.markdown("""
        <style>
        .slim-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 6px;
            margin-bottom: 6px;
            gap: 12px;
            width: 100%;
        }
        .slim-main {
            display: flex;
            align-items: center;
            flex-grow: 1;
            min-width: 0;
        }
        .slim-info {
            display: flex;
            flex-direction: column;
            min-width: 0;
            flex-grow: 1;
        }
        .slim-title {
            font-weight: bold;
            font-size: 0.95em;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .slim-sub {
            font-size: 0.75em;
            color: #888;
            margin-top: 2px;
        }
        .slim-bonus {
            font-size: 0.75em;
            background: #2a2a2a;
            padding: 2px 8px;
            border-radius: 4px;
            color: #ccc;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 350px;
        }
        @media (max-width: 600px) {
            .slim-card {
                flex-wrap: wrap;
                padding: 10px;
            }
            .slim-bonus {
                max-width: 100%;
                margin-top: 4px;
                width: 100%;
            }
        }
        </style>
    """, unsafe_allow_html=True)

def render_slim_card(badge_html, title_text, sub_text, bonus_html, subtitle=None):
    subtitle_html = f' <span style="font-weight: normal; color: #666; font-size: 0.8em;">({subtitle})</span>' if subtitle else ""
    card_html = f"""
    <div class="slim-card">
        <div class="slim-main">
            {badge_html}
            <div class="slim-info">
                <div class="slim-title">{title_text}{subtitle_html}</div>
                <div class="slim-sub">{sub_text}</div>
            </div>
        </div>
        <div class="slim-bonus">{bonus_html}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
