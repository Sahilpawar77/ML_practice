import os
import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIG - MUST BE FIRST STREAMLIT COMMAND
# ============================================================

st.set_page_config(
    page_title="Rainfall Dashboard",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# >>> SOURCE FILE PATH - CHANGE THIS TO YOUR LOCAL FILE <<<
# Supports .csv, .xlsx, .xls
# Examples:
#   r"C:\Users\YourName\Documents\weather_data.csv"
#   "/Users/yourname/Documents/weather_data.xlsx"
# ============================================================

SOURCE_FILE_PATH = r"C:\path\to\your\weather_data.csv"

# If QPF is already in mm, keep 1.
# If QPF is in inches, change this to 25.4.
RAINFALL_MULTIPLIER = 1


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #eaf7ff 0%, #f7fbff 45%, #eefbf4 100%);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #d9f0ff 0%, #ffffff 100%);
            border-right: 2px solid #b5d9f2;
        }

        .dashboard-title {
            background: linear-gradient(90deg, #bde7ff, #e9f8ff, #d8ffd8);
            border: 2px solid #79b8e8;
            border-radius: 14px;
            padding: 14px 18px;
            box-shadow: 0 4px 15px rgba(0, 93, 158, 0.18);
            margin-bottom: 12px;
        }

        .dashboard-title h1 {
            font-size: 34px;
            color: #04253d;
            margin: 0;
            font-weight: 800;
        }

        .dashboard-title p {
            margin: 0;
            color: #17445c;
            font-size: 14px;
            font-weight: 600;
        }

        .source-badge {
            color: #e53935;
            font-size: 22px;
            font-weight: 700;
            text-align: right;
            font-style: italic;
            padding-top: 22px;
        }

        .nav-button {
            background: linear-gradient(180deg, #fff7e9, #eedcc0);
            border: 2px solid #111;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            font-weight: 800;
            color: #111;
            box-shadow: 0 4px 10px rgba(0,0,0,0.20);
            min-height: 54px;
        }

        .nav-button-active {
            background: linear-gradient(180deg, #55bf42, #2f8625);
            border: 2px solid #111;
            border-radius: 10px;
            padding: 12px;
            text-align: center;
            font-weight: 800;
            color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.25);
            min-height: 54px;
        }

        .metric-card {
            background: rgba(255,255,255,0.92);
            border-radius: 16px;
            padding: 18px;
            border: 1px solid #c6e4f8;
            box-shadow: 0 6px 20px rgba(34, 121, 171, 0.16);
            min-height: 112px;
        }

        .metric-label {
            color: #496777;
            font-size: 14px;
            font-weight: 700;
        }

        .metric-value {
            color: #06354d;
            font-size: 30px;
            font-weight: 900;
            margin-top: 5px;
        }

        .metric-sub {
            color: #5f7886;
            font-size: 13px;
            font-weight: 600;
        }

        .section-title {
            background: linear-gradient(90deg, #007a3d, #00a65a);
            color: white;
            border-radius: 8px;
            padding: 8px 12px;
            text-align: center;
            font-weight: 900;
            margin-top: 10px;
            margin-bottom: 8px;
            box-shadow: 0 3px 10px rgba(0, 100, 50, 0.22);
        }

        .alert-box {
            background: white;
            border-radius: 12px;
            padding: 14px;
            border: 1px solid #cbe7f7;
            box-shadow: 0 4px 14px rgba(0, 80, 120, 0.10);
            font-size: 14px;
        }

        .note-red {
            color: #e53935;
            font-size: 14px;
            font-weight: 800;
        }

        table.weather-matrix {
            border-collapse: collapse;
            width: 100%;
            background: white;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(0, 80, 120, 0.12);
        }

        table.weather-matrix th {
            background: #008b4c;
            color: white;
            border: 1px solid #004b2a;
            padding: 7px;
            text-align: center;
            font-weight: 800;
            white-space: nowrap;
        }

        table.weather-matrix td {
            border: 1px solid #777;
            padding: 6px;
            text-align: right;
            background: #f4f4f4;
            white-space: nowrap;
        }

        table.weather-matrix td:first-child {
            text-align: left;
            font-weight: 800;
            background: #e8f4ff;
        }

        .rain-green {
            background: #55ef8a !important;
            color: #003d1e;
            font-weight: 900;
        }

        .rain-yellow {
            background: #fff176 !important;
            color: #5c4b00;
            font-weight: 900;
        }

        .rain-orange {
            background: #ffb74d !important;
            color: #5c2300;
            font-weight: 900;
        }

        .rain-red {
            background: #ef5350 !important;
            color: white;
            font-weight: 900;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def rainfall_class(value):
    try:
        v = float(value)
    except Exception:
        return ""

    if v <= 10:
        return "rain-green"
    elif v <= 115.5:
        return "rain-yellow"
    elif v <= 204.4:
        return "rain-orange"
    else:
        return "rain-red"


def rainfall_label(value):
    try:
        v = float(value)
    except Exception:
        return "No data"

    if v <= 10:
        return "Light / No significant rainfall"
    elif v <= 115.5:
        return "Moderate rain - minor disruption possible"
    elif v <= 204.4:
        return "Heavy rain - higher disruption risk"
    else:
        return "Extreme rain - severe risk"


def format_number(value, decimals=2):
    if value is None:
        return "-"

    try:
        if pd.isna(value):
            return "-"
        return f"{float(value):,.{decimals}f}"
    except Exception:
        return str(value)


# ============================================================
# LOAD LOCAL DATA
# Reads SOURCE_FILE_PATH once (cached) and builds all the
# derived columns that used to be computed in the Snowflake
# BASE_CTE SQL.
# ============================================================

@st.cache_data(ttl=900)
def load_base_data():
    if not os.path.exists(SOURCE_FILE_PATH):
        st.error(
            f"Could not find the source file:\n\n{SOURCE_FILE_PATH}\n\n"
            "Update SOURCE_FILE_PATH near the top of streamlit_app.py "
            "to point to your local CSV/Excel file."
        )
        st.stop()

    ext = os.path.splitext(SOURCE_FILE_PATH)[1].lower()

    if ext == ".csv":
        raw = pd.read_csv(SOURCE_FILE_PATH)
    elif ext in (".xlsx", ".xls"):
        raw = pd.read_excel(SOURCE_FILE_PATH)
    else:
        st.error("Unsupported file type. SOURCE_FILE_PATH must be .csv, .xlsx, or .xls")
        st.stop()

    # Normalize column names to uppercase to match the original SQL column names
    raw.columns = [str(c).strip().upper() for c in raw.columns]

    def col(name):
        return raw[name] if name in raw.columns else pd.Series([None] * len(raw))

    df = pd.DataFrame()
    df["STATES"] = col("STATES")
    df["DISTRICT"] = col("DISTRICT")
    df["TALUKA"] = col("TALUKA")

    ts_primary = pd.to_datetime(col("VALID_TIME_LOCAL"), errors="coerce")
    ts_fallback = pd.to_datetime(col("DATETIME_LOCAL"), errors="coerce")
    df["FORECAST_TS"] = ts_primary.fillna(ts_fallback)

    # Drop rows with no usable timestamp (same as the SQL WHERE clause)
    df = df[df["FORECAST_TS"].notna()].copy()

    df["FORECAST_DATE"] = df["FORECAST_TS"].dt.date
    df["FORECAST_TIME"] = df["FORECAST_TS"].dt.strftime("%I:%M %p")
    df["MONTH_NAME"] = df["FORECAST_TS"].dt.strftime("%B")
    df["YEAR_NUM"] = df["FORECAST_TS"].dt.year
    df["MONTH_NUM"] = df["FORECAST_TS"].dt.month

    df["RAINFALL_MM"] = pd.to_numeric(col("QPF"), errors="coerce") * RAINFALL_MULTIPLIER
    df["PRECIP_CHANCE"] = pd.to_numeric(col("PRECIP_CHANCE"), errors="coerce")

    df["WEATHER"] = col("WX_PHRASE_SHORT")
    df["WEATHER_LONG"] = col("WX_PHRASE_LONG")

    df["TEMPERATURE_C"] = pd.to_numeric(col("TEMPERATURE"), errors="coerce")
    df["HUMIDITY"] = pd.to_numeric(col("RELATIVE_HUMIDITY"), errors="coerce")
    df["FEELS_LIKE_C"] = pd.to_numeric(col("TEMPERATURE_FEELS_LIKE"), errors="coerce")
    df["WIND_SPEED_KMH"] = pd.to_numeric(col("WIND_SPEED"), errors="coerce")

    df["WIND_DIRECTION"] = col("WIND_DIRECTION_CARDINAL")
    df["UV_DESCRIPTION"] = col("UV_DESCRIPTION")

    df["CLOUD_COVER"] = pd.to_numeric(col("CLOUD_COVER"), errors="coerce")
    df["LATITUDE"] = pd.to_numeric(col("LATITUDE"), errors="coerce")
    df["LONGITUDE"] = pd.to_numeric(col("LONGITUDE"), errors="coerce")

    df["DBT_LOADED_AT"] = col("DBT_LOADED_AT")

    return df


# ============================================================
# DATA FUNCTIONS (pandas equivalents of the old SQL queries)
# ============================================================

def get_last_refresh(df):
    if df.empty or df["DBT_LOADED_AT"].dropna().empty:
        return "Not available"
    return str(df["DBT_LOADED_AT"].dropna().max())


def get_years(df):
    return sorted(df["YEAR_NUM"].dropna().astype(int).unique().tolist(), reverse=True)


def get_months(df, year_num):
    sub = df[df["YEAR_NUM"] == year_num][["MONTH_NUM", "MONTH_NAME"]].drop_duplicates()
    sub = sub.sort_values("MONTH_NUM")
    return {row["MONTH_NAME"]: int(row["MONTH_NUM"]) for _, row in sub.iterrows()}


def get_states(df, year_num, month_num):
    sub = df[(df["YEAR_NUM"] == year_num) & (df["MONTH_NUM"] == month_num)]
    return sorted(sub["STATES"].dropna().unique().tolist())


def get_districts(df, year_num, month_num, state_name):
    sub = df[
        (df["YEAR_NUM"] == year_num)
        & (df["MONTH_NUM"] == month_num)
        & (df["STATES"] == state_name)
    ]
    return sorted(sub["DISTRICT"].dropna().unique().tolist())


def get_talukas(df, year_num, month_num, state_name, district_name):
    sub = df[
        (df["YEAR_NUM"] == year_num)
        & (df["MONTH_NUM"] == month_num)
        & (df["STATES"] == state_name)
        & (df["DISTRICT"] == district_name)
    ]
    return sorted(sub["TALUKA"].dropna().unique().tolist())


def get_available_dates(df, year_num, month_num, state_name, district_name, taluka_list):
    sub = df[
        (df["YEAR_NUM"] == year_num)
        & (df["MONTH_NUM"] == month_num)
        & (df["STATES"] == state_name)
        & (df["DISTRICT"] == district_name)
        & (df["TALUKA"].isin(taluka_list))
    ]

    dates = sub["FORECAST_DATE"].dropna().unique()
    dates = sorted(dates)

    out = pd.DataFrame({"FORECAST_DATE": dates})
    out["DAY_NO"] = pd.to_datetime(out["FORECAST_DATE"]).dt.strftime("%d")
    out["DATE_LABEL"] = pd.to_datetime(out["FORECAST_DATE"]).dt.strftime("%a, %b %d, %Y")
    return out


def get_daily_forecast(df, year_num, month_num, state_name, district_name, taluka_list):
    sub = df[
        (df["YEAR_NUM"] == year_num)
        & (df["MONTH_NUM"] == month_num)
        & (df["STATES"] == state_name)
        & (df["DISTRICT"] == district_name)
        & (df["TALUKA"].isin(taluka_list))
    ]

    if sub.empty:
        return sub

    grouped = (
        sub.groupby(["TALUKA", "FORECAST_DATE"], as_index=False)
        .agg(
            TEMPERATURE_C=("TEMPERATURE_C", "mean"),
            WIND_SPEED_KMH=("WIND_SPEED_KMH", "mean"),
            RAINFALL_MM=("RAINFALL_MM", "sum"),
            AVG_PRECIP_CHANCE=("PRECIP_CHANCE", "mean"),
            AVG_HUMIDITY=("HUMIDITY", "mean"),
        )
    )

    grouped["TEMPERATURE_C"] = grouped["TEMPERATURE_C"].round(1)
    grouped["WIND_SPEED_KMH"] = grouped["WIND_SPEED_KMH"].round(1)
    grouped["RAINFALL_MM"] = grouped["RAINFALL_MM"].round(2)
    grouped["AVG_PRECIP_CHANCE"] = grouped["AVG_PRECIP_CHANCE"].round(1)
    grouped["AVG_HUMIDITY"] = grouped["AVG_HUMIDITY"].round(1)

    grouped["DATE_LABEL"] = pd.to_datetime(grouped["FORECAST_DATE"]).dt.strftime("%a, %b %d, %Y")

    return grouped.sort_values(["FORECAST_DATE", "TALUKA"])


def get_hourly_forecast(df, state_name, district_name, taluka_name, forecast_date):
    sub = df[
        (df["STATES"] == state_name)
        & (df["DISTRICT"] == district_name)
        & (df["TALUKA"] == taluka_name)
        & (df["FORECAST_DATE"].astype(str) == str(forecast_date))
    ].copy()

    if sub.empty:
        return sub

    sub["RAINFALL_MM"] = sub["RAINFALL_MM"].round(2)
    sub["PRECIP_CHANCE"] = sub["PRECIP_CHANCE"].round(1)
    sub["TEMPERATURE_C"] = sub["TEMPERATURE_C"].round(1)
    sub["HUMIDITY"] = sub["HUMIDITY"].round(1)
    sub["FEELS_LIKE_C"] = sub["FEELS_LIKE_C"].round(1)
    sub["WIND_SPEED_KMH"] = sub["WIND_SPEED_KMH"].round(1)
    sub["CLOUD_COVER"] = sub["CLOUD_COVER"].round(1)

    return sub.sort_values("FORECAST_TS")


def get_map_data(df, state_name, district_name, selected_date, taluka_list):
    sub = df[
        (df["STATES"] == state_name)
        & (df["DISTRICT"] == district_name)
        & (df["FORECAST_DATE"].astype(str) == str(selected_date))
        & (df["TALUKA"].isin(taluka_list))
        & (df["LATITUDE"].notna())
        & (df["LONGITUDE"].notna())
    ]

    if sub.empty:
        return sub

    grouped = (
        sub.groupby(["TALUKA", "FORECAST_DATE", "LATITUDE", "LONGITUDE"], as_index=False)
        .agg(
            RAINFALL_MM=("RAINFALL_MM", "sum"),
            TEMPERATURE_C=("TEMPERATURE_C", "mean"),
        )
    )

    grouped["RAINFALL_MM"] = grouped["RAINFALL_MM"].round(2)
    grouped["TEMPERATURE_C"] = grouped["TEMPERATURE_C"].round(1)
    grouped = grouped.rename(columns={"LATITUDE": "LAT", "LONGITUDE": "LON"})

    return grouped


# ============================================================
# LOAD DATA
# ============================================================

base_df = load_base_data()

if base_df.empty:
    st.error("No valid forecast rows found in the source file (check VALID_TIME_LOCAL / DATETIME_LOCAL columns).")
    st.stop()


# ============================================================
# HEADER
# ============================================================

last_refresh = get_last_refresh(base_df)

header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.markdown(
        f"""
        <div class="dashboard-title">
            <h1>🌦️ Rainfall Dashboard</h1>
            <p>Last Refresh: {last_refresh}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with header_col2:
    st.markdown(
        """
        <div class="source-badge">
            Source: IBM
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# NAVIGATION STYLE HEADER
# ============================================================

nav_cols = st.columns(6)

nav_items = [
    ("🏠 Home Page", False),
    ("IBM Daily/Hourly Forecast", True),
    ("Plant Daily/Hourly Forecast", False),
    ("IBM Weather Forecast", False),
    ("IBM Weather Actual", False),
    ("IBM Excess & Deficient Talukas", False),
]

for col, item in zip(nav_cols, nav_items):
    label, active = item
    css_class = "nav-button-active" if active else "nav-button"

    with col:
        st.markdown(
            f"""
            <div class="{css_class}">
                {label}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown("## 🌧️ Rainfall Alerts")

st.sidebar.markdown(
    """
    <div class="alert-box">
        <b>Rainfall Alert Logic:</b><br><br>
        🟢 <b>Green:</b> No significant rainfall<br>
        🟡 <b>Yellow:</b> 10.1–115.5 mm - Minor disruptions possible<br>
        🟠 <b>Orange:</b> 115.6–204.4 mm - Higher disruption risk<br>
        🔴 <b>Red:</b> >204.5 mm - Severe risk to life and property
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Filters")

year_options = get_years(base_df)

if not year_options:
    st.error("No valid forecast dates found in the source file.")
    st.stop()

selected_year = st.sidebar.selectbox(
    "Year",
    year_options,
    index=0
)

month_label_map = get_months(base_df, selected_year)

if not month_label_map:
    st.error("No month data found for selected year.")
    st.stop()

selected_month_name = st.sidebar.selectbox(
    "Month",
    list(month_label_map.keys()),
    index=0
)

selected_month = month_label_map[selected_month_name]

state_options = get_states(base_df, selected_year, selected_month)

if not state_options:
    st.error("No states found for selected year/month.")
    st.stop()

selected_state = st.sidebar.selectbox(
    "State",
    state_options
)

district_options = get_districts(base_df, selected_year, selected_month, selected_state)

if not district_options:
    st.error("No districts found for selected state.")
    st.stop()

selected_district = st.sidebar.selectbox(
    "District",
    district_options
)

taluka_options = get_talukas(base_df, selected_year, selected_month, selected_state, selected_district)

if not taluka_options:
    st.error("No talukas found for selected district.")
    st.stop()

selected_talukas = st.sidebar.multiselect(
    "Taluka",
    taluka_options,
    default=taluka_options[: min(5, len(taluka_options))]
)

if not selected_talukas:
    st.warning("Please select at least one taluka.")
    st.stop()


# ============================================================
# LOAD FILTERED DATA
# ============================================================

dates_df = get_available_dates(
    base_df,
    selected_year,
    selected_month,
    selected_state,
    selected_district,
    selected_talukas
)

if dates_df.empty:
    st.warning("No forecast dates available for selected filters.")
    st.stop()

daily_df = get_daily_forecast(
    base_df,
    selected_year,
    selected_month,
    selected_state,
    selected_district,
    selected_talukas
)

if daily_df.empty:
    st.warning("No daily forecast data available.")
    st.stop()


# ============================================================
# DATE SELECTOR
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Date Selection
    </div>
    """,
    unsafe_allow_html=True
)

if "selected_forecast_date" not in st.session_state:
    st.session_state.selected_forecast_date = str(dates_df.iloc[0]["FORECAST_DATE"])

available_date_values = dates_df["FORECAST_DATE"].astype(str).tolist()

if st.session_state.selected_forecast_date not in available_date_values:
    st.session_state.selected_forecast_date = available_date_values[0]

date_button_count = min(len(dates_df), 10)

date_cols = st.columns(date_button_count)

for idx, (_, row) in enumerate(dates_df.head(10).iterrows()):
    with date_cols[idx]:
        day_no = row["DAY_NO"]
        date_value = str(row["FORECAST_DATE"])

        button_type = "primary" if date_value == st.session_state.selected_forecast_date else "secondary"

        if st.button(
            str(day_no),
            key=f"date_{date_value}",
            use_container_width=True,
            type=button_type
        ):
            st.session_state.selected_forecast_date = date_value

selected_date = st.session_state.selected_forecast_date

selected_taluka_for_hourly = st.selectbox(
    "Hourly Forecast Taluka",
    selected_talukas,
    index=0
)


# ============================================================
# HOURLY DATA
# ============================================================

hourly_df = get_hourly_forecast(
    base_df,
    selected_state,
    selected_district,
    selected_taluka_for_hourly,
    selected_date
)


# ============================================================
# KPI CARDS
# ============================================================

selected_daily = daily_df[
    (daily_df["TALUKA"] == selected_taluka_for_hourly)
    & (daily_df["FORECAST_DATE"].astype(str) == str(selected_date))
]

if not selected_daily.empty:
    daily_row = selected_daily.iloc[0]
    total_rain = daily_row["RAINFALL_MM"]
    avg_temp = daily_row["TEMPERATURE_C"]
    avg_wind = daily_row["WIND_SPEED_KMH"]
    avg_precip = daily_row["AVG_PRECIP_CHANCE"]
else:
    total_rain = None
    avg_temp = None
    avg_wind = None
    avg_precip = None

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Rainfall</div>
            <div class="metric-value">{format_number(total_rain)} mm</div>
            <div class="metric-sub">{rainfall_label(total_rain)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Temperature</div>
            <div class="metric-value">{format_number(avg_temp, 1)} °C</div>
            <div class="metric-sub">Average forecast temperature</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Wind Speed</div>
            <div class="metric-value">{format_number(avg_wind, 1)} km/hr</div>
            <div class="metric-sub">Average wind speed</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with kpi4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Precipitation Chance</div>
            <div class="metric-value">{format_number(avg_precip, 1)}%</div>
            <div class="metric-sub">Average precipitation chance</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DAILY WEATHER MATRIX
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Day Wise Weather Forecast
    </div>
    """,
    unsafe_allow_html=True
)

date_order = (
    daily_df[["FORECAST_DATE", "DATE_LABEL"]]
    .drop_duplicates()
    .sort_values("FORECAST_DATE")
)

html = """
<div style="overflow-x:auto; max-height:360px; border-radius:10px;">
<table class="weather-matrix">
<thead>
<tr>
    <th rowspan="2">Taluka</th>
"""

for _, drow in date_order.iterrows():
    html += f'<th colspan="3">{drow["DATE_LABEL"]}</th>'

html += """
</tr>
<tr>
"""

for _ in date_order.iterrows():
    html += """
        <th>Temperature(°C)</th>
        <th>Wind Speed(km/hr)</th>
        <th>Rainfall(mm)</th>
    """

html += """
</tr>
</thead>
<tbody>
"""

for taluka in selected_talukas:
    html += f"<tr><td>{taluka}</td>"

    for _, drow in date_order.iterrows():
        d = drow["FORECAST_DATE"]

        record = daily_df[
            (daily_df["TALUKA"] == taluka)
            & (daily_df["FORECAST_DATE"] == d)
        ]

        if record.empty:
            html += "<td>-</td><td>-</td><td>-</td>"
        else:
            r = record.iloc[0]
            rain_value = r["RAINFALL_MM"]
            rain_css = rainfall_class(rain_value)

            html += f"<td>{format_number(r['TEMPERATURE_C'], 1)}</td>"
            html += f"<td>{format_number(r['WIND_SPEED_KMH'], 1)}</td>"
            html += f'<td class="{rain_css}">{format_number(rain_value, 2)}</td>'

    html += "</tr>"

html += """
</tbody>
</table>
</div>
"""

st.markdown(html, unsafe_allow_html=True)


# ============================================================
# DAILY CHARTS
# ============================================================

chart_col1, chart_col2 = st.columns([1.2, 1])

with chart_col1:
    st.markdown(
        """
        <div class="section-title">
            Rainfall Trend by Date
        </div>
        """,
        unsafe_allow_html=True
    )

    rain_fig = px.bar(
        daily_df,
        x="FORECAST_DATE",
        y="RAINFALL_MM",
        color="TALUKA",
        barmode="group",
        text="RAINFALL_MM",
        labels={
            "FORECAST_DATE": "Date",
            "RAINFALL_MM": "Rainfall (mm)",
            "TALUKA": "Taluka"
        },
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    rain_fig.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    rain_fig.update_layout(
        height=420,
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        legend_title_text="Taluka"
    )

    st.plotly_chart(rain_fig, use_container_width=True)

with chart_col2:
    st.markdown(
        """
        <div class="section-title">
            Rainfall Risk Distribution
        </div>
        """,
        unsafe_allow_html=True
    )

    risk_df = daily_df.copy()
    risk_df["RISK"] = risk_df["RAINFALL_MM"].apply(rainfall_label)

    risk_count = (
        risk_df.groupby("RISK")
        .size()
        .reset_index(name="COUNT")
    )

    risk_fig = px.pie(
        risk_count,
        names="RISK",
        values="COUNT",
        hole=0.55,
        color="RISK",
        color_discrete_map={
            "Light / No significant rainfall": "#2ecc71",
            "Moderate rain - minor disruption possible": "#f4d03f",
            "Heavy rain - higher disruption risk": "#e67e22",
            "Extreme rain - severe risk": "#e74c3c"
        }
    )

    risk_fig.update_layout(
        height=420,
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    st.plotly_chart(risk_fig, use_container_width=True)


# ============================================================
# HOURLY WEATHER FORECAST TABLE
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Hourly Weather Forecast
    </div>
    """,
    unsafe_allow_html=True
)

if hourly_df.empty:
    st.warning("No hourly forecast data available for selected taluka and date.")
else:
    hourly_display = hourly_df[
        [
            "FORECAST_TIME",
            "RAINFALL_MM",
            "PRECIP_CHANCE",
            "WEATHER",
            "TEMPERATURE_C",
            "HUMIDITY",
            "FEELS_LIKE_C",
            "WIND_SPEED_KMH",
            "WIND_DIRECTION",
            "UV_DESCRIPTION",
            "CLOUD_COVER"
        ]
    ].copy()

    hourly_display = hourly_display.rename(
        columns={
            "FORECAST_TIME": "Time",
            "RAINFALL_MM": "Rainfall(mm)",
            "PRECIP_CHANCE": "Precipitation Chance(%)",
            "WEATHER": "Weather",
            "TEMPERATURE_C": "Temperature(°C)",
            "HUMIDITY": "Humidity(%)",
            "FEELS_LIKE_C": "Temperature Feels Like(°C)",
            "WIND_SPEED_KMH": "Wind Speed(km/hr)",
            "WIND_DIRECTION": "Wind Direction",
            "UV_DESCRIPTION": "UV Description",
            "CLOUD_COVER": "Cloud Cover(%)"
        }
    )

    def style_hourly(df):
        styled = pd.DataFrame("", index=df.index, columns=df.columns)

        if "Rainfall(mm)" in df.columns:
            for idx, value in df["Rainfall(mm)"].items():
                css = rainfall_class(value)

                if css == "rain-green":
                    styled.loc[idx, "Rainfall(mm)"] = "background-color:#55ef8a; color:#003d1e; font-weight:bold;"
                elif css == "rain-yellow":
                    styled.loc[idx, "Rainfall(mm)"] = "background-color:#fff176; color:#5c4b00; font-weight:bold;"
                elif css == "rain-orange":
                    styled.loc[idx, "Rainfall(mm)"] = "background-color:#ffb74d; color:#5c2300; font-weight:bold;"
                elif css == "rain-red":
                    styled.loc[idx, "Rainfall(mm)"] = "background-color:#ef5350; color:white; font-weight:bold;"

        if "Precipitation Chance(%)" in df.columns:
            for idx, value in df["Precipitation Chance(%)"].items():
                try:
                    v = float(value)

                    if v >= 70:
                        styled.loc[idx, "Precipitation Chance(%)"] = "background-color:#0d47a1; color:white; font-weight:bold;"
                    elif v >= 40:
                        styled.loc[idx, "Precipitation Chance(%)"] = "background-color:#42a5f5; color:white; font-weight:bold;"
                    elif v >= 20:
                        styled.loc[idx, "Precipitation Chance(%)"] = "background-color:#bbdefb; color:#0d47a1; font-weight:bold;"
                except Exception:
                    pass

        return styled

    st.dataframe(
        hourly_display.style.apply(style_hourly, axis=None),
        use_container_width=True,
        height=420
    )

    st.markdown(
        """
        <p class="note-red">
            * By default, hourly forecast is selected for the chosen date.
            To see another hourly forecast, click a date above.
        </p>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# HOURLY CHARTS
# ============================================================

if not hourly_df.empty:
    hcol1, hcol2 = st.columns(2)

    with hcol1:
        st.markdown(
            """
            <div class="section-title">
                Hourly Rainfall & Precipitation Chance
            </div>
            """,
            unsafe_allow_html=True
        )

        hourly_rain_fig = px.bar(
            hourly_df,
            x="FORECAST_TIME",
            y="RAINFALL_MM",
            color="PRECIP_CHANCE",
            color_continuous_scale=["#b3e5fc", "#0288d1", "#01579b"],
            labels={
                "FORECAST_TIME": "Time",
                "RAINFALL_MM": "Rainfall (mm)",
                "PRECIP_CHANCE": "Precipitation Chance (%)"
            }
        )

        hourly_rain_fig.update_layout(
            height=380,
            plot_bgcolor="rgba(255,255,255,0)",
            paper_bgcolor="rgba(255,255,255,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(hourly_rain_fig, use_container_width=True)

    with hcol2:
        st.markdown(
            """
            <div class="section-title">
                Temperature vs Feels Like
            </div>
            """,
            unsafe_allow_html=True
        )

        temp_long = hourly_df[
            ["FORECAST_TIME", "TEMPERATURE_C", "FEELS_LIKE_C"]
        ].melt(
            id_vars="FORECAST_TIME",
            value_vars=["TEMPERATURE_C", "FEELS_LIKE_C"],
            var_name="Metric",
            value_name="Value"
        )

        temp_long["Metric"] = temp_long["Metric"].replace(
            {
                "TEMPERATURE_C": "Temperature",
                "FEELS_LIKE_C": "Feels Like"
            }
        )

        temp_fig = px.line(
            temp_long,
            x="FORECAST_TIME",
            y="Value",
            color="Metric",
            markers=True,
            labels={
                "FORECAST_TIME": "Time",
                "Value": "Temperature (°C)"
            },
            color_discrete_map={
                "Temperature": "#ff7043",
                "Feels Like": "#d84315"
            }
        )

        temp_fig.update_layout(
            height=380,
            plot_bgcolor="rgba(255,255,255,0)",
            paper_bgcolor="rgba(255,255,255,0)",
            margin=dict(l=20, r=20, t=40, b=20)
        )

        st.plotly_chart(temp_fig, use_container_width=True)


# ============================================================
# MAP VIEW
# ============================================================

st.markdown(
    """
    <div class="section-title">
        Taluka Weather Map
    </div>
    """,
    unsafe_allow_html=True
)

map_df = get_map_data(
    base_df,
    selected_state,
    selected_district,
    selected_date,
    selected_talukas
)

if not map_df.empty:
    fig_map = px.scatter_mapbox(
        map_df,
        lat="LAT",
        lon="LON",
        size="RAINFALL_MM",
        color="RAINFALL_MM",
        hover_name="TALUKA",
        hover_data={
            "RAINFALL_MM": True,
            "TEMPERATURE_C": True,
            "LAT": False,
            "LON": False
        },
        color_continuous_scale=["#2ecc71", "#f4d03f", "#e67e22", "#e74c3c"],
        size_max=35,
        zoom=6,
        height=480
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("Map cannot be shown because latitude/longitude data is not available for the selected filters.")


# ============================================================
# RAW DATA PREVIEW
# ============================================================

with st.expander("Show Raw Daily Forecast Data"):
    st.dataframe(daily_df, use_container_width=True)

with st.expander("Show Raw Hourly Forecast Data"):
    st.dataframe(hourly_df, use_container_width=True)
