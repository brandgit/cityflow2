"""
Page Perturbations RATP du dashboard
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.utils.data_loader import load_metrics


def show(date: str, data_source: str):
    """Page Perturbations RATP"""
    st.title("🚇 Perturbations RATP")
    st.markdown(f"**Date:** {date}")
    
    with st.spinner("Chargement des données RATP..."):
        data = load_metrics("traffic", date, data_source)
    
    if not data:
        st.error("❌ Aucune donnée RATP disponible.")
        return
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = data.get("total_disruptions_count", 0)
        st.metric("Total perturbations", f"{total:,}")
    
    with col2:
        active = data.get("active_disruptions_count", 0)
        st.metric("Perturbations actives", f"{active:,}")
    
    with col3:
        reliability = data.get("reliability_index", 0) * 100
        st.metric("Indice de fiabilité", f"{reliability:.1f}%")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Par sévérité")
        create_severity_chart(data)
    
    with col2:
        st.subheader("🚇 Lignes impactées")
        create_lignes_chart(data)
    
    # Alertes
    st.markdown("---")
    st.subheader("⚠️ Alertes critiques")
    
    alerts = data.get("alerts", [])
    if alerts:
        st.warning(f"⚠️ {len(alerts)} alertes critiques")
        for i, alert in enumerate(alerts[:10], 1):
            lignes = alert.get("lignes", [])
            lignes_str = ", ".join([f"Ligne {l}" for l in lignes]) if lignes else "Pas de ligne spécifique"
            with st.expander(f"{i}. {lignes_str} - Priorité {alert.get('priority', 0)}"):
                st.write(f"**Durée:** {alert.get('duration_hours', 0):.1f}h")
                st.write(f"**ID:** {alert.get('id', 'Inconnu')}")
    else:
        st.success("✅ Aucune alerte critique")


def create_severity_chart(data):
    """Graphique par sévérité"""
    disruptions = data.get("disruptions_by_severity", {})
    
    fig = px.bar(
        x=list(disruptions.keys()),
        y=list(disruptions.values()),
        labels={"x": "Sévérité", "y": "Nombre"},
        color=list(disruptions.values()),
        color_continuous_scale="Reds"
    )
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def create_lignes_chart(data):
    """Graphique des lignes impactées"""
    top_lignes = data.get("top_lignes_impactees", [])
    
    if not top_lignes:
        st.info("Pas de lignes impactées")
        return
    
    df = pd.DataFrame(top_lignes)
    fig = px.bar(df, x="ligne", y="count", labels={"ligne": "Ligne", "count": "Perturbations"})
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

