# features/feature_builder.py
import pandas as pd
from datetime import datetime

def generate_dataframe(store_API, item_API, date_API, df_stores, df_region, prices_bbdd, events_df, holidays_df):
    # 1. Normalizar fecha
    if isinstance(date_API, str):
        date_API = datetime.strptime(date_API, "%Y-%m-%d")

    # 2. Extraer store_code y región
    store_code = df_stores.get(store_API, {}).get("store_code", "UNKNOWN")
    region_code = store_code.split('_')[0]
    region = df_region['city'].get(region_code, "Unknown")

    # 3. Extraer partes del item
    item_parts = item_API.split('_')
    item_category = item_parts[0]
    item_department = f"{item_parts[0]}_{item_parts[1]}"
    id = f"{item_API}_{store_code}"

    # 4. Precio
    sell_price = prices_bbdd.at[id, 'sell_price'] if id in prices_bbdd.index else None

    # 5. Comprobación de eventos y festivos
    matched_event = events_df[(events_df['region'] == region) & (events_df['date'] == date_API)]
    matched_holiday = holidays_df[(holidays_df['region'] == region) & (holidays_df['date'] == date_API)]

    event_name = matched_event['event'].values[0] if not matched_event.empty else "No"
    event_flag = 1 if not matched_event.empty else 0

    holiday_name = matched_holiday['holiday'].values[0] if not matched_holiday.empty else "No"
    holiday_flag = 1 if not matched_holiday.empty else 0

    data = {
        "year": [date_API.year],
        "month": [date_API.month],
        "quarter": [((date_API.month - 1) // 3) + 1],
        "week": [date_API.isocalendar()[1]],
        "day": [date_API.day],
        "weekday_int": [date_API.weekday() + 1],
        "holidays_boolean": [holiday_flag],
        "event_boolean": [event_flag],
    }
    return pd.DataFrame(data)
