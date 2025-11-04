"""
Page Vélib' du dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_metrics


def show(date: str, data_source: str):
    """
    Affiche la page Vélib'
    
    Args:
        date: Date au format YYYY-MM-DD
        data_source: Source de données
    """
    st.title("🚴 Vélos Vélib'")
    st.markdown(f"**Date:** {date}")
    
    # Charger les données
    with st.spinner("Chargement des données Vélib'..."):
        data = load_metrics("bikes", date, data_source)
    
    if not data:
        st.error("❌ Aucune donnée Vélib' disponible pour cette date.")
        return
    
    global_metrics = data.get("global_metrics", {})
    
    # KPIs
    st.subheader("📊 Métriques globales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Stations actives",
            f"{global_metrics.get('nombre_stations_actives', 0):,}",
            help="Nombre total de stations actives"
        )
    
    with col2:
        st.metric(
            "Vélos disponibles",
            f"{global_metrics.get('total_velos_disponibles', 0):,}",
            help="Total de vélos disponibles sur le réseau"
        )
    
    with col3:
        st.metric(
            "Vélos mécaniques",
            f"{global_metrics.get('total_velos_mecaniques', 0):,}",
            help="Nombre de vélos mécaniques"
        )
    
    with col4:
        st.metric(
            "Vélos électriques",
            f"{global_metrics.get('total_velos_electriques', 0):,}",
            help="Nombre de vélos électriques"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Places libres",
            f"{global_metrics.get('total_places_libres', 0):,}"
        )
    
    with col2:
        taux_remplissage = global_metrics.get('taux_remplissage_moyen', 0)
        st.metric(
            "Taux de remplissage moyen",
            f"{taux_remplissage:.1f}%"
        )
    
    with col3:
        taux_dispo = global_metrics.get('taux_disponibilite_velos', 0)
        st.metric(
            "Taux de disponibilité",
            f"{taux_dispo:.1f}%"
        )
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚴 Distribution des vélos")
        create_velos_distribution_chart(global_metrics)
    
    with col2:
        st.subheader("📍 Distribution des places")
        create_places_distribution_chart(global_metrics)
    
    # Top stations
    st.markdown("---")
    st.subheader("🏆 Top 10 stations")
    
    tab1, tab2, tab3 = st.tabs(["🔝 Plus utilisées", "⚠️ Saturées", "❌ Vides"])
    
    with tab1:
        top_stations = data.get("top_10_stations_utilisees", [])
        if top_stations:
            df = pd.DataFrame(top_stations)
            df = df[["name", "capacity", "num_bikes_available", "taux_remplissage"]]
            df.columns = ["Station", "Capacité", "Vélos disponibles", "Taux (%)"
]
            df["Taux (%)"] = df["Taux (%)"].round(1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Pas de données disponibles")
    
    with tab2:
        stations_saturees = data.get("alertes_stations_saturees", [])
        if stations_saturees:
            st.warning(f"⚠️ {len(stations_saturees)} stations saturées (>90%)")
            df = pd.DataFrame(stations_saturees)
            df = df[["name", "capacity", "num_bikes_available", "taux_remplissage"]]
            df.columns = ["Station", "Capacité", "Vélos disponibles", "Taux (%)"]
            df["Taux (%)"] = df["Taux (%)"].round(1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Aucune station saturée")
    
    with tab3:
        stations_vides = data.get("alertes_stations_vides", [])
        if stations_vides:
            st.error(f"❌ {len(stations_vides)} stations vides (<10%)")
            df = pd.DataFrame(stations_vides)
            df = df[["name", "capacity", "num_bikes_available", "taux_remplissage"]]
            df.columns = ["Station", "Capacité", "Vélos disponibles", "Taux (%)"]
            df["Taux (%)"] = df["Taux (%)"].round(1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ Aucune station vide")


def create_velos_distribution_chart(metrics):
    """Graphique de distribution des vélos"""
    data = {
        "Type": ["Mécaniques", "Électriques"],
        "Nombre": [
            metrics.get("total_velos_mecaniques", 0),
            metrics.get("total_velos_electriques", 0)
        ]
    }
    
    fig = px.pie(
        data,
        values="Nombre",
        names="Type",
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        hole=0.4
    )
    
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)


def create_places_distribution_chart(metrics):
    """Graphique de distribution des places"""
    total_capacity = metrics.get("capacite_totale_reseau", 0)
    total_bikes = metrics.get("total_velos_disponibles", 0)
    total_free = metrics.get("total_places_libres", 0)
    
    fig = go.Figure(data=[
        go.Bar(
            x=["Vélos", "Places libres"],
            y=[total_bikes, total_free],
            marker_color=["#1f77b4", "#2ca02c"],
            text=[f"{total_bikes:,}", f"{total_free:,}"],
            textposition="auto"
        )
    ])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        yaxis_title="Nombre"
    )
    
    st.plotly_chart(fig, use_container_width=True)

