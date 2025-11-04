"""
Page Vue d'ensemble du dashboard
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dashboard.utils.data_loader import load_all_metrics
from dashboard.utils.charts import create_gauge_chart, create_kpi_card


def show(date: str, data_source: str):
    """
    Affiche la vue d'ensemble du dashboard
    
    Args:
        date: Date au format YYYY-MM-DD
        data_source: Source de données (MongoDB, Fichiers JSON, API)
    """
    st.title("🏠 Vue d'ensemble")
    st.markdown(f"**Date:** {date}")
    
    # Charger toutes les métriques
    with st.spinner("Chargement des données..."):
        metrics = load_all_metrics(date, data_source)
    
    if not metrics:
        st.error("❌ Aucune donnée disponible pour cette date.")
        st.info("💡 Lancez d'abord le traitement des données avec `python3 main.py`")
        return
    
    # KPIs principaux
    st.subheader("📊 Indicateurs clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        bikes_data = metrics.get("bikes", {})
        # bikes_data contient directement metrics, top_counters, etc.
        total_stations = len(bikes_data.get("top_counters", [])) if bikes_data else 0
        st.metric(
            "🚴 Compteurs Vélo actifs",
            f"{total_stations:,}",
            delta=None,
            help="Nombre de compteurs vélo avec données"
        )
    
    with col2:
        traffic_data = metrics.get("traffic", {})
        reliability = traffic_data.get("reliability_index", 0) * 100
        st.metric(
            "🚇 Fiabilité RATP",
            f"{reliability:.1f}%",
            delta=None,
            help="Indice de fiabilité du réseau RATP"
        )
    
    with col3:
        comptages_data = metrics.get("comptages", {})
        global_m = comptages_data.get("global_metrics", {}) if comptages_data else {}
        total_troncons = global_m.get("nombre_troncons_actifs", 0)
        st.metric(
            "🚗 Tronçons surveillés",
            f"{total_troncons:,}",
            delta=None,
            help="Nombre de tronçons routiers avec données"
        )
    
    with col4:
        chantiers_data = metrics.get("chantiers", {})
        # Pour chantiers, total_chantiers_actifs est directement à la racine
        chantiers_actifs = chantiers_data.get("total_chantiers_actifs", 0) if chantiers_data else 0
        st.metric(
            "🚧 Chantiers actifs",
            f"{chantiers_actifs:,}",
            delta=None,
            help="Nombre de chantiers perturbant la circulation"
        )
    
    st.markdown("---")
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚴 Distribution Vélib'")
        if bikes_data:
            create_bikes_distribution_chart(bikes_data)
        else:
            st.info("Pas de données Vélib' disponibles")
    
    with col2:
        st.subheader("🚗 État du trafic routier")
        if comptages_data:
            create_traffic_state_chart(comptages_data)
        else:
            st.info("Pas de données de trafic disponibles")
    
    # Deuxième ligne de graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚇 Perturbations RATP par sévérité")
        if traffic_data:
            create_disruptions_chart(traffic_data)
        else:
            st.info("Pas de données RATP disponibles")
    
    with col2:
        st.subheader("🚧 Chantiers par type d'impact")
        if chantiers_data:
            create_chantiers_impact_chart(chantiers_data)
        else:
            st.info("Pas de données chantiers disponibles")
    
    st.markdown("---")
    
    # Top alertes
    st.subheader("⚠️ Alertes principales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚗 Top 5 zones de congestion**")
        if comptages_data:
            alertes = comptages_data.get("alertes_congestion", [])[:5]
            if alertes:
                for i, alerte in enumerate(alertes, 1):
                    with st.expander(f"{i}. {alerte.get('libelle', 'Inconnu')} - {alerte.get('zone_fallback', 'Zone inconnue')}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Débit journalier", f"{alerte.get('debit_journalier_total', 0):,.0f}")
                            st.metric("Taux occupation", f"{alerte.get('taux_occupation_moyen', 0):.1f}%")
                        with col_b:
                            st.metric("Temps perdu", f"{alerte.get('temps_perdu_total_minutes', 0):,.0f} min")
                            st.metric("État", alerte.get('etat_trafic_dominant', 'Inconnu'))
            else:
                st.success("✅ Pas d'alerte de congestion")
        else:
            st.info("Pas de données disponibles")
    
    with col2:
        st.markdown("**🚇 Top 5 lignes RATP impactées**")
        if traffic_data:
            top_lignes = traffic_data.get("top_lignes_impactees", [])[:5]
            if top_lignes:
                for i, ligne in enumerate(top_lignes, 1):
                    st.markdown(f"{i}. **Ligne {ligne.get('ligne')}** - {ligne.get('count')} perturbations")
            else:
                st.success("✅ Pas de perturbations sur les lignes")
        else:
            st.info("Pas de données disponibles")


def create_bikes_distribution_chart(data):
    """Crée un graphique de distribution des vélos"""
    metrics_list = data.get("metrics", [])
    
    if not metrics_list:
        st.info("Pas de données vélo disponibles")
        return
    
    # Calculer totaux depuis la liste de métriques
    total_jour = sum(m.get("total_jour", 0) for m in metrics_list)
    nb_compteurs = len(data.get("top_counters", []))
    
    fig = go.Figure(data=[
        go.Bar(
            x=["Total passages", "Compteurs actifs"],
            y=[total_jour, nb_compteurs],
            marker_color=['#1f77b4', '#ff7f0e']
        )
    ])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_traffic_state_chart(data):
    """Crée un graphique de l'état du trafic"""
    global_metrics = data.get("global_metrics", {})
    etat_trafic = global_metrics.get("repartition_etat_trafic", {})
    
    if not etat_trafic:
        st.info("Pas de données d'état de trafic")
        return
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(etat_trafic.keys()),
            values=list(etat_trafic.values()),
            hole=0.4,
            marker_colors=['#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
        )
    ])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_disruptions_chart(data):
    """Crée un graphique des perturbations RATP"""
    disruptions = data.get("disruptions_by_severity", {})
    
    if not disruptions:
        st.info("Pas de données de perturbations")
        return
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(disruptions.keys()),
            y=list(disruptions.values()),
            marker_color=['#d62728', '#ff7f0e', '#ffbb78', '#2ca02c']
        )
    ])
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        xaxis_title="Sévérité",
        yaxis_title="Nombre"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_chantiers_impact_chart(data):
    """Crée un graphique des chantiers par impact"""
    # Pour chantiers, les données sont structurées différemment
    impact_by_arr = data.get("impact_by_arrondissement", {})
    total_chantiers = data.get("total_chantiers_actifs", 0)
    
    if not impact_by_arr and total_chantiers == 0:
        st.info("Pas de données de chantiers")
        return
    
    # Créer un graphique par arrondissement si disponible
    if impact_by_arr:
        # Prendre les top 10 arrondissements
        top_arr = sorted(impact_by_arr.items(), key=lambda x: x[1], reverse=True)[:10]
        
        fig = go.Figure(data=[
            go.Bar(
                x=[arr for arr, _ in top_arr],
                y=[impact for _, impact in top_arr],
                marker_color='#d62728'
            )
        ])
        
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False,
            xaxis_title="Arrondissement",
            yaxis_title="Impact cumulé (%)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.metric("Total chantiers", total_chantiers)

