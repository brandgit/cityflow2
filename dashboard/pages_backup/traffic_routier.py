"""
Page Trafic Routier du dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.data_loader import load_metrics


def show(date: str, data_source: str):
    """
    Affiche la page Trafic Routier
    
    Args:
        date: Date au format YYYY-MM-DD
        data_source: Source de données
    """
    st.title("🚗 Trafic Routier")
    st.markdown(f"**Date:** {date}")
    
    # Charger les données
    with st.spinner("Chargement des données de trafic routier..."):
        data = load_metrics("comptages", date, data_source)
    
    if not data:
        st.error("❌ Aucune donnée de trafic routier disponible pour cette date.")
        return
    
    global_metrics = data.get("global_metrics", {})
    
    # KPIs
    st.subheader("📊 Métriques globales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Tronçons actifs",
            f"{global_metrics.get('nombre_troncons_actifs', 0):,}"
        )
    
    with col2:
        debit_total = global_metrics.get('debit_journalier_total', 0)
        st.metric(
            "Débit total",
            f"{debit_total:,.0f}",
            help="Nombre total de véhicules"
        )
    
    with col3:
        taux_moyen = global_metrics.get('taux_occupation_moyen', 0)
        st.metric(
            "Taux d'occupation moyen",
            f"{taux_moyen:.1f}%"
        )
    
    with col4:
        temps_perdu = global_metrics.get('temps_perdu_total_heures', 0)
        st.metric(
            "Temps perdu total",
            f"{temps_perdu:,.0f}h"
        )
    
    st.markdown("---")
    
    # État du trafic
    st.subheader("🚦 État du trafic")
    
    col1, col2 = st.columns(2)
    
    with col1:
        create_traffic_state_pie_chart(global_metrics)
    
    with col2:
        create_congestion_gauge(global_metrics)
    
    # Top 10 tronçons
    st.markdown("---")
    st.subheader("🏆 Top 10 tronçons")
    
    tab1, tab2 = st.tabs(["🔝 Plus fréquentés", "⚠️ Plus congestionnés"])
    
    with tab1:
        top_troncons = data.get("top_10_troncons", [])
        if top_troncons:
            df = pd.DataFrame(top_troncons)
            display_cols = ["libelle", "zone_fallback", "debit_journalier_total", 
                          "taux_occupation_moyen", "etat_trafic_dominant"]
            df = df[display_cols]
            df.columns = ["Tronçon", "Zone", "Débit", "Taux occ. (%)", "État"]
            df["Débit"] = df["Débit"].apply(lambda x: f"{x:,.0f}")
            df["Taux occ. (%)"] = df["Taux occ. (%)"].round(1)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Pas de données disponibles")
    
    with tab2:
        top_zones = data.get("top_10_zones_congestionnees", [])
        if top_zones:
            df = pd.DataFrame(top_zones)
            display_cols = ["libelle", "zone_fallback", "temps_perdu_total_minutes",
                          "debit_journalier_total", "etat_trafic_dominant"]
            df = df[display_cols]
            df.columns = ["Tronçon", "Zone", "Temps perdu (min)", "Débit", "État"]
            df["Temps perdu (min)"] = df["Temps perdu (min)"].apply(lambda x: f"{x:,.0f}")
            df["Débit"] = df["Débit"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Pas de données disponibles")
    
    # Alertes de congestion
    st.markdown("---")
    st.subheader("⚠️ Alertes de congestion")
    
    alertes = data.get("alertes_congestion", [])
    if alertes:
        st.warning(f"⚠️ {len(alertes)} alertes de congestion détectées")
        
        # Afficher les 10 premières
        for i, alerte in enumerate(alertes[:10], 1):
            with st.expander(f"{i}. {alerte.get('libelle', 'Inconnu')} - {alerte.get('zone_fallback', 'Zone inconnue')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Débit journalier", f"{alerte.get('debit_journalier_total', 0):,.0f}")
                with col2:
                    st.metric("Taux d'occupation", f"{alerte.get('taux_occupation_moyen', 0):.1f}%")
                with col3:
                    st.metric("Temps perdu", f"{alerte.get('temps_perdu_total_minutes', 0):,.0f} min")
                
                st.info(f"**État:** {alerte.get('etat_trafic_dominant', 'Inconnu')}")
    else:
        st.success("✅ Aucune alerte de congestion")
    
    # Analyse par zones
    st.markdown("---")
    st.subheader("🗺️ Analyse par zones")
    
    top_zones_affluence = data.get("top_zones_affluence", [])
    if top_zones_affluence:
        create_zones_chart(top_zones_affluence)
    else:
        st.info("Pas de données d'analyse par zones")


def create_traffic_state_pie_chart(metrics):
    """Graphique en camembert de l'état du trafic"""
    etat_trafic = metrics.get("repartition_etat_trafic", {})
    
    if not etat_trafic:
        st.info("Pas de données d'état de trafic")
        return
    
    fig = px.pie(
        values=list(etat_trafic.values()),
        names=list(etat_trafic.keys()),
        title="Répartition de l'état du trafic",
        color_discrete_sequence=px.colors.sequential.RdYlGn_r
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_congestion_gauge(metrics):
    """Jauge de congestion"""
    taux = metrics.get("taux_occupation_moyen", 0)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=taux,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Taux d'occupation moyen (%)"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 50], 'color': "yellow"},
                {'range': [50, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def create_zones_chart(zones_data):
    """Graphique d'analyse par zones"""
    df = pd.DataFrame(zones_data[:10])
    
    fig = px.bar(
        df,
        x="zone",
        y="debit_total",
        title="Top 10 zones par débit total",
        labels={"zone": "Zone", "debit_total": "Débit total"},
        color="debit_total",
        color_continuous_scale="Blues"
    )
    
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

