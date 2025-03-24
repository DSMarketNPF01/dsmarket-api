# events/events_loader.py
import pandas as pd
from events.events_generator import create_events_df
from datetime import datetime

# Lista de regiones a consultar (puedes hacerla dinámica desde AlloyDB)
def get_regions():
    return [
        "New York", "Boston", "Philadelphia", "Chicago", "Houston",
        "San Francisco", "Los Angeles", "Seattle", "Miami", "Washington"
    ]

def load_events_and_holidays(year=None, regions=None):
    """
    Genera los DataFrames de eventos y festivos para las regiones dadas.
    Si no se indica año, se toma el actual.
    """
    if year is None:
        year = datetime.today().year

    if regions is None:
        regions = get_regions()

    # Crear eventos y festivos para el rango actual + 1 año
    events_df_raw, holidays_df_raw = create_events_df(year, regions)

    # Asegurar que las fechas estén en formato datetime
    events_df_raw['date'] = pd.to_datetime(events_df_raw['date'])
    holidays_df_raw['date'] = pd.to_datetime(holidays_df_raw['date'])

    return events_df_raw, holidays_df_raw

