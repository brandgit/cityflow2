"""
Application principale Streamlit pour CityFlow Analytics Dashboard
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration de la page
st.set_page_config(
    page_title="CityFlow Analytics Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚦 CityFlow Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=CityFlow", use_container_width=True)
    st.title("📊 Navigation")
    
    # Sélection de la date
    st.subheader("📅 Sélection de la date")
    selected_date = st.date_input(
        "Date des données",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    date_str = selected_date.strftime("%Y-%m-%d")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Choisir une vue",
        [
            "🏠 Vue d'ensemble",
            "🚴 Vélos Vélib'",
            "🚗 Trafic Routier",
            "🚧 Chantiers",
            "🌤️ Météo",
            "🚇 Perturbations RATP",
            "📈 Rapport Quotidien"
        ]
    )
    
    st.markdown("---")
    
    # Source de données
    st.subheader("⚙️ Configuration")
    data_source = st.selectbox(
        "Source de données",
        ["MongoDB Local", "Fichiers JSON", "API"],
        help="Choisir la source de données à utiliser"
    )
    
    st.markdown("---")
    
    # Informations
    st.info("""
    **CityFlow Analytics**
    
    Dashboard de visualisation des données urbaines de Paris.
    
    📊 Métriques en temps réel  
    📈 Analyses détaillées  
    🗺️ Visualisations géographiques
    """)

# Import des pages
from pages import (
    show_overview,
    show_bikes,
    show_traffic_routier,
    show_chantiers,
    show_weather,
    show_traffic_ratp,
    show_rapport
)

# Routing
if page == "🏠 Vue d'ensemble":
    show_overview(date_str, data_source)
elif page == "🚴 Vélos Vélib'":
    show_bikes(date_str, data_source)
elif page == "🚗 Trafic Routier":
    show_traffic_routier(date_str, data_source)
elif page == "🚧 Chantiers":
    show_chantiers(date_str, data_source)
elif page == "🌤️ Météo":
    show_weather(date_str, data_source)
elif page == "🚇 Perturbations RATP":
    show_traffic_ratp(date_str, data_source)
elif page == "📈 Rapport Quotidien":
    show_rapport(date_str, data_source)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem;'>
    <p>CityFlow Analytics Dashboard © 2025 | Données: Open Data Paris & RATP</p>
</div>
""", unsafe_allow_html=True)

