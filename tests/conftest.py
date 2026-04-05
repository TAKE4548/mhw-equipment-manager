import sys
from unittest.mock import MagicMock

# Mock streamlit before it gets imported by logic files
mock_st = MagicMock()
mock_st.session_state = {}
mock_st.secrets = {"connections": {"supabase": {"url": "", "key": ""}}}
mock_st.context = MagicMock()
mock_st.context.cookies = {}

sys.modules["streamlit"] = mock_st
