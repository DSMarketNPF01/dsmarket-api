# features/forecasting_utils.py
import pandas as pd
from sktime.forecasting.base import ForecastingHorizon

def generate_fh_from_date(last_date, horizon=28, index_type="datetime", freq="D"):
    """
    Genera un ForecastingHorizon a partir de una fecha, sin necesidad de y.

    last_date: fecha de la última observación (datetime o string tipo "YYYY-MM-DD")
    horizon: número de días a predecir
    index_type: "datetime" o "period"
    freq: frecuencia temporal (por defecto "D")
    """
    if isinstance(last_date, str):
        last_date = pd.to_datetime(last_date)

    start_date = last_date + pd.Timedelta(days=1)

    if index_type == "period":
        future_dates = pd.period_range(start=start_date, periods=horizon, freq=freq)
    else:
        future_dates = pd.date_range(start=start_date, periods=horizon, freq=freq)

    return ForecastingHorizon(future_dates, is_relative=False)
