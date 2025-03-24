# events/events_generator.py
import pandas as pd
import calendar
from datetime import datetime
from convertdate import islamic
import holidays

# Función actualizada con más ciudades importantes de EE.UU. y su correspondiente código de estado
def _get_regions_code(city_list):
    city_to_state = {
        "New York": "NY",
        "Los Angeles": "CA",
        "Chicago": "IL",
        "Houston": "TX",
        "Phoenix": "AZ",
        "Philadelphia": "PA",
        "San Antonio": "TX",
        "San Diego": "CA",
        "Dallas": "TX",
        "San Jose": "CA",
        "Austin": "TX",
        "Jacksonville": "FL",
        "Fort Worth": "TX",
        "Columbus": "OH",
        "Indianapolis": "IN",
        "Charlotte": "NC",
        "San Francisco": "CA",
        "Seattle": "WA",
        "Denver": "CO",
        "Washington": "DC",
        "Boston": "MA",
        "El Paso": "TX",
        "Nashville": "TN",
        "Detroit": "MI",
        "Oklahoma City": "OK",
        "Portland": "OR",
        "Las Vegas": "NV",
        "Memphis": "TN",
        "Louisville": "KY",
        "Baltimore": "MD",
        "Milwaukee": "WI",
        "Albuquerque": "NM",
        "Tucson": "AZ",
        "Fresno": "CA",
        "Mesa": "AZ",
        "Sacramento": "CA",
        "Atlanta": "GA",
        "Kansas City": "MO",
        "Colorado Springs": "CO",
        "Miami": "FL",
        "Raleigh": "NC",
        "Omaha": "NE",
        "Long Beach": "CA",
        "Virginia Beach": "VA",
        "Oakland": "CA",
        "Minneapolis": "MN",
        "Tulsa": "OK",
        "Arlington": "TX",
        "Tampa": "FL",
        "New Orleans": "LA",
        "Wichita": "KS",
        "Cleveland": "OH",
        "Bakersfield": "CA",
        "Aurora": "CO",
        "Anaheim": "CA",
        "Honolulu": "HI",
        "Santa Ana": "CA",
        "Riverside": "CA",
        "Corpus Christi": "TX",
        "Lexington": "KY",
        "Henderson": "NV",
        "Stockton": "CA",
        "Saint Paul": "MN",
        "Cincinnati": "OH",
        "St. Louis": "MO",
        "Pittsburgh": "PA",
        "Greensboro": "NC",
        "Lincoln": "NE",
        "Anchorage": "AK",
        "Plano": "TX",
        "Orlando": "FL",
        "Irvine": "CA",
        "Newark": "NJ",
        "Toledo": "OH",
        "Durham": "NC",
        "Chula Vista": "CA",
        "Fort Wayne": "IN",
        "Jersey City": "NJ",
        "St. Petersburg": "FL"
    }

    result = {}
    for city in city_list:
        normalized = city.strip().title()
        result[city] = city_to_state.get(normalized, "Unknown")

    return result

# Función para obtener el primer domingo de febrero (SuperBowl)
def _get_superbowl_date(year):
    # Super Bowl es el primer domingo de febrero
    first_feb = datetime(year, 2, 1)
    weekday = first_feb.weekday()
    days_to_sunday = (6 - weekday) % 7
    return first_feb + pd.Timedelta(days=days_to_sunday)

# Función para obtener el inicio de Ramadan
def _get_ramadan_start(year):
    # Ramadan comienza en la fecha determinada por el calendario islámico
    # Para calcular la fecha de inicio de Ramadan, utilizamos una librería como `convertdate`
    # Esta librería ofrece un cálculo aproximado en función de los años
    hijri_year = islamic.from_gregorian(year, 1, 1)[0]
    y, m, d = islamic.to_gregorian(hijri_year, 9, 1)
    return datetime(y, m, d)

# Función para obtener Thanksgiving (4º jueves de noviembre)
def _get_thanksgiving_date(year):
    # Thanksgiving es el cuarto jueves de noviembre
    nov_1st = datetime(year, 11, 1)
    weekday = nov_1st.weekday()
    days_to_thursday = (3 - weekday) % 7
    return nov_1st + pd.Timedelta(days=days_to_thursday + 21)  # Añadir 21 días para el cuarto jueves

# Función para obtener la fecha de Pascua (Easter)
def _get_easter_date(year):
    # Método de "Computus" para calcular la fecha de Pascua
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return datetime(year, month, day)

# Función para crear un DataFrame con los festivos
def _create_holiday_df(region, holiday_list):
    return pd.DataFrame({
        "date": holiday_list.keys(),
        "holiday": holiday_list.values(),
        "region": region
    })

# Función para obtener los festivos nacionales y de las ciudades
def _get_holidays_for_cities(cities, year):
    # Festivos nacionales de EE.UU.
    us_holidays = holidays.US(years=year)
    
    # Crear DataFrame con los festivos nacionales
    us_df = _create_holiday_df("EEUU", us_holidays)
    
    # Crear lista para almacenar los DataFrames de las ciudades
    city_dfs = []
    
    # Iterar sobre las ciudades
    for city_name, state_code in cities.items():
        # Obtener festivos específicos por ciudad
        city_holidays = holidays.US(state=state_code, years=year)
        
        # Crear DataFrame para la ciudad
        city_df = _create_holiday_df(city_name, city_holidays)
        
        # Verificar qué festivos nacionales no están reflejados en las ciudades y agregarlos
        def add_missing_holidays(city_df, city_name):
            missing_holidays = us_df[~us_df["date"].isin(city_df["date"])].copy()
            missing_holidays["region"] = city_name
            return pd.concat([city_df, missing_holidays], ignore_index=True)
        
        # Actualizar el DataFrame de la ciudad
        city_df = add_missing_holidays(city_df, city_name)
        
        # Agregar el DataFrame de la ciudad a la lista
        city_dfs.append(city_df)
    
    # Combinar todos los festivos en un solo DataFrame
    holidays_df = pd.concat(city_dfs, ignore_index=True)
    
    # Cambiar la columna 'date' a tipo datetime para asegurar consistencia
    holidays_df['date'] = pd.to_datetime(holidays_df['date'])
    
    return holidays_df

# Convertir eventos (SuperBowl, Ramadan, etc.) a formato largo
def _transform_events_to_df(events_df, regions):
    records = []
    for _, row in events_df.iterrows():
        year = row["Year"]
        for event in ["SuperBowl", "Ramadan", "Thanksgiving", "Easter"]:
            for region in regions:
                records.append({
                    "date": row[event],
                    "event": event,
                    "region": region
                })
    return pd.DataFrame(records)

def create_events_df(year_input, regions_input):
    region_codes =  _get_regions_code(regions_input)
    years = range(year_input, year_input+2) 
    events = {
        "Year": [],
        "SuperBowl": [],
        "Ramadan": [],
        "Thanksgiving": [],
        "Easter": []
    }

    for year in years:
        events["Year"].append(year)
        events["SuperBowl"].append(_get_superbowl_date(year))
        events["Ramadan"].append(_get_ramadan_start(year))
        events["Thanksgiving"].append(_get_thanksgiving_date(year))
        events["Easter"].append(_get_easter_date(year))
        holidays_df = _get_holidays_for_cities(region_codes, year)

    # Crear DataFrame con las fechas de los eventos
    events_df = pd.DataFrame(events)

    format_events_df = _transform_events_to_df(events_df, region_codes)
    # Unir eventos personalizados con festivos oficiales
    all_events_df = pd.concat([holidays_df, format_events_df], ignore_index=True)
    all_events_df['date'] = pd.to_datetime(all_events_df['date'])
    all_events_df.sort_values(by="date", inplace=True)

    # Esta opcion devuelve todos los eventos y festivos en un solo DataFrame
    # return all_events_df

    # Esta opción devuelve los eventos personalizados y los festivos oficiales en dos DataFrames separados
    return format_events_df, holidays_df
