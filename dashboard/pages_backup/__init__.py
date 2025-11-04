"""
Pages du dashboard Streamlit
"""

from .overview import show as show_overview
from .bikes import show as show_bikes
from .traffic_routier import show as show_traffic_routier
from .chantiers import show as show_chantiers
from .weather import show as show_weather
from .traffic_ratp import show as show_traffic_ratp
from .rapport import show as show_rapport

__all__ = [
    'show_overview',
    'show_bikes',
    'show_traffic_routier',
    'show_chantiers',
    'show_weather',
    'show_traffic_ratp',
    'show_rapport'
]

