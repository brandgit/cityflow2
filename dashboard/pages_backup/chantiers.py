"""
Page Chantiers du dashboard
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from dashboard.utils.data_loader import load_metrics


def show(date: str, data_source: str):
    """Page Chantiers"""
    st.title("🚧 Chantiers")
    st.markdown(f"**Date:** {date}")
    
    with st.spinner("Chargement des données chantiers..."):
        data = load_metrics("chantiers", date, data_source)
    
    if not data:
        st.error("❌ Aucune donnée de chantiers disponible.")
        return
    
    global_metrics = data.get("global_metrics", {})
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Chantiers actifs", f"{global_metrics.get('nombre_chantiers_actifs', 0):,}")
    
    with col2:
        duree_moy = global_metrics.get('duree_moyenne_jours', 0)
        st.metric("Durée moyenne", f"{duree_moy:.0f} jours")
    
    with col3:
        surface_tot = global_metrics.get('surface_totale_impactee_m2', 0)
        st.metric("Surface totale", f"{surface_tot:,.0f} m²")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Par arrondissement")
        create_chantiers_by_arrondissement(data)
    
    with col2:
        st.subheader("📈 Par niveau d'impact")
        create_impact_chart(data)
    
    # Top chantiers
    st.markdown("---")
    st.subheader("🏆 Top 10 chantiers les plus impactants")
    
    top_chantiers = data.get("top_10_chantiers_impact", [])
    if top_chantiers:
        for i, chantier in enumerate(top_chantiers[:10], 1):
            with st.expander(f"{i}. {chantier.get('designation', 'Inconnu')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Arrondissement:** {chantier.get('arrondissement', 'Inconnu')}")
                    st.write(f"**Impact:** {chantier.get('niveau_impact', 'Inconnu')}")
                with col2:
                    st.write(f"**Durée:** {chantier.get('duree_jours', 0):.0f} jours")
                    st.write(f"**Surface:** {chantier.get('surface_m2', 0):,.0f} m²")
    else:
        st.info("Pas de données disponibles")


def create_chantiers_by_arrondissement(data):
    """Graphique par arrondissement"""
    stats = data.get("statistiques_arrondissement", {})
    if not stats:
        st.info("Pas de données")
        return
    
    df = pd.DataFrame([
        {"Arrondissement": k, "Nombre": v}
        for k, v in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
    ])
    
    fig = px.bar(df, x="Arrondissement", y="Nombre", color="Nombre",
                 color_continuous_scale="Reds")
    fig.update_layout(height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def create_impact_chart(data):
    """Graphique par impact"""
    stats = data.get("statistiques_impact", {})
    
    impact_data = {
        "Élevé": stats.get("chantiers_impact_eleve", 0),
        "Moyen": stats.get("chantiers_impact_moyen", 0),
        "Faible": stats.get("chantiers_impact_faible", 0)
    }
    
    fig = px.pie(values=list(impact_data.values()), names=list(impact_data.keys()),
                 color_discrete_sequence=["#d62728", "#ff7f0e", "#2ca02c"])
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

