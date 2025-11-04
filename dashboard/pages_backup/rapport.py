"""
Page Rapport Quotidien du dashboard
"""

import streamlit as st
import pandas as pd
from dashboard.utils.data_loader import load_report


def show(date: str, data_source: str):
    """Page Rapport Quotidien"""
    st.title("📈 Rapport Quotidien")
    st.markdown(f"**Date:** {date}")
    
    with st.spinner("Chargement du rapport..."):
        data = load_report(date, data_source)
    
    if not data:
        st.error("❌ Aucun rapport disponible pour cette date.")
        st.info("💡 Générez d'abord le rapport avec `python3 main.py`")
        return
    
    # Résumé
    st.subheader("📊 Résumé")
    summary = data.get("summary", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Disponibilité Vélib'", f"{summary.get('taux_disponibilite_velos', 0):.1f}%")
    
    with col2:
        st.metric("Fiabilité RATP", f"{summary.get('reliability_index_ratp', 0)*100:.1f}%")
    
    with col3:
        st.metric("Niveau de congestion", f"{summary.get('niveau_congestion', 'N/A')}")
    
    st.markdown("---")
    
    # Détails
    st.subheader("📋 Détails par source")
    
    tab1, tab2, tab3 = st.tabs(["🚴 Vélib'", "🚗 Trafic", "🚧 Chantiers"])
    
    with tab1:
        bikes_data = data.get("bikes_summary", {})
        if bikes_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Stations actives", f"{bikes_data.get('nombre_stations', 0):,}")
                st.metric("Vélos disponibles", f"{bikes_data.get('velos_disponibles', 0):,}")
            with col2:
                st.metric("Places libres", f"{bikes_data.get('places_libres', 0):,}")
                st.metric("Taux de remplissage", f"{bikes_data.get('taux_remplissage', 0):.1f}%")
        else:
            st.info("Pas de données Vélib'")
    
    with tab2:
        traffic_data = data.get("traffic_summary", {})
        if traffic_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tronçons surveillés", f"{traffic_data.get('nombre_troncons', 0):,}")
                st.metric("Débit total", f"{traffic_data.get('debit_total', 0):,.0f}")
            with col2:
                st.metric("Alertes congestion", f"{traffic_data.get('alertes_congestion', 0):,}")
                st.metric("Temps perdu", f"{traffic_data.get('temps_perdu_total', 0):,.0f}h")
        else:
            st.info("Pas de données de trafic")
    
    with tab3:
        chantiers_data = data.get("chantiers_summary", {})
        if chantiers_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Chantiers actifs", f"{chantiers_data.get('nombre_chantiers', 0):,}")
                st.metric("Surface impactée", f"{chantiers_data.get('surface_totale', 0):,.0f} m²")
            with col2:
                st.metric("Impact élevé", f"{chantiers_data.get('impact_eleve', 0):,}")
                st.metric("Durée moyenne", f"{chantiers_data.get('duree_moyenne', 0):.0f} jours")
        else:
            st.info("Pas de données chantiers")
    
    # Alertes et recommandations
    st.markdown("---")
    st.subheader("⚠️ Alertes")
    
    alertes = data.get("alertes", [])
    if alertes:
        for alerte in alertes:
            st.warning(f"⚠️ {alerte}")
    else:
        st.success("✅ Aucune alerte")

