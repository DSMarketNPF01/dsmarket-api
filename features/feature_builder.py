import pandas as pd
from datetime import datetime

def generate_dataframe(store_code, region, item, date_API, sell_price, events_df, holidays_df):
    # 1. Normalizar fecha
    if isinstance(date_API, str):
        date_API = datetime.strptime(date_API, "%Y-%m-%d")

    # 2. Comprobación de eventos y festivos
    matched_event = events_df[(events_df['region'] == region) & (events_df['date'] == date_API)]
    matched_holiday = holidays_df[(holidays_df['region'] == region) & (holidays_df['date'] == date_API)]

    event_flag = 1 if not matched_event.empty else 0
    holiday_flag = 1 if not matched_holiday.empty else 0

    # 3. Features temporales + eventos
    data = {
        "year": [date_API.year],
        "month": [date_API.month],
        "quarter": [((date_API.month - 1) // 3) + 1],
        "week": [date_API.isocalendar()[1]],
        "day": [date_API.day],
        "weekday_int": [date_API.weekday() + 1],
        "holidays_boolean": [holiday_flag],
        "event_boolean": [event_flag],
        # "sell_price": [sell_price]
    }

    return pd.DataFrame(data)
