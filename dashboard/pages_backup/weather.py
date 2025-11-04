"""
Page Météo du dashboard
"""

import streamlit as st
from dashboard.utils.data_loader import load_metrics


def show(date: str, data_source: str):
    """Page Météo"""
    st.title("🌤️ Météo")
    st.markdown(f"**Date:** {date}")
    
    with st.spinner("Chargement des données météo..."):
        data = load_metrics("weather", date, data_source)
    
    if not data:
        st.error("❌ Aucune donnée météo disponible.")
        return
    
    st.info("📊 Page météo en cours de développement")
    st.json(data)

