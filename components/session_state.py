from copy import deepcopy

import streamlit as st


def ensure_session_state(defaults: dict) -> None:
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(value)