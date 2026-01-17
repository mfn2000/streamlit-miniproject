import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------ PAGE CONFIG ------------------------
st.set_page_config(
    page_title="NY/NJ Flight Delay Dashboard",
    layout="wide"
)

st.markdown("""
<style>
/* Main app container */
.st-emotion-cache-zy6yx3 {
    padding-bottom: 2.5rem !important;  
    background-image: linear-gradient(to bottom, #011f4c 0%, #2d74dc 35%, #e9eef6 35%, #e9eef6 100%) !important;
    background-color: #f2f2f2 !important;
}
            
.st-emotion-cache-1jsf23j {
    font-size: 1rem;
    color: #ffffff !important;
}
            
.st-bq {
    background-color: #2d74dc;
}
</style>
""", unsafe_allow_html=True)

# ------------------------ Header and Filter ------------------------
header_left, header_right = st.columns([2, 1])

with header_left:
    st.markdown("""
    <div>
        <h1 style="
            color:#ffffff; 
            font-family: Arial, sans-serif; 
            font-weight:bold;
            margin:0;
            padding:0;
        ">FLIGHT DELAY ANALYSIS</h1>
        <p style="
            color:#ffffff; 
            font-size:16px;
            margin-bottom:30px;
            padding:0;
        ">Port Authority of New York & New Jersey • Jun - Dec 2024</p>
    </div>
    """, unsafe_allow_html=True)

with header_right:
    f1, f2 = st.columns(2)

# ------------------------ LOAD DATA ------------------------
@st.cache_data
def load_data():
    all_sheets = pd.read_excel("data/flight_data.xlsx", sheet_name=None)
    return (
        all_sheets["flights"],
        all_sheets["airports"],
        all_sheets["airlines"],
        all_sheets["aircrafts"]
    )

flights_df, airports_df, airlines_df, aircrafts_df = load_data()

# ------------------------ MAPPING & SESSION STATE ------------------------
airport_name_map = airports_df.set_index("airport_code")["name"].to_dict()
airline_name_map = airlines_df.set_index("airline_id")["airline"].to_dict()

# Airport filter session state
airport_list = sorted(flights_df["origin"].unique())
available_airports = [-1] + airport_list  # -1 = All

if "airport_max_sel" not in st.session_state:
    st.session_state.airport_max_sel = len(available_airports)
if "selected_airports" not in st.session_state:
    st.session_state.selected_airports = [-1]

# Airline filter session state
airline_list = sorted(flights_df["airline_id"].unique())
available_airlines = [-1] + airline_list  # -1 = All

if "airline_max_sel" not in st.session_state:
    st.session_state.airline_max_sel = len(available_airlines)
if "selected_airlines" not in st.session_state:
    st.session_state.selected_airlines = [-1]

# ------------------------ FILTER CALLBACK LOGIC ------------------------
def airport_select_logic():
    sel = st.session_state.airport_filter
    if -1 in sel or len(sel) == 0:
        st.session_state.selected_airports = [-1]
        st.session_state.airport_max_sel = 1
    else:
        st.session_state.selected_airports = sel
        st.session_state.airport_max_sel = len(available_airports)

def airline_select_logic():
    sel = st.session_state.airline_filter
    if -1 in sel or len(sel) == 0:
        st.session_state.selected_airlines = [-1]
        st.session_state.airline_max_sel = 1
    else:
        st.session_state.selected_airlines = sel
        st.session_state.airline_max_sel = len(available_airlines)

# ------------------------ MULTISELECT FILTERS ------------------------
with f1:
    st.multiselect(
        "Airport",
        options=available_airports,
        default=st.session_state.selected_airports,
        key="airport_filter",
        format_func=lambda x: "All" if x == -1 else airport_name_map.get(x, x),
        max_selections=st.session_state.airport_max_sel,
        on_change=airport_select_logic
    )

with f2:
    st.multiselect(
        "Airline",
        options=available_airlines,
        default=st.session_state.selected_airlines,
        key="airline_filter",
        format_func=lambda x: "All" if x == -1 else airline_name_map.get(x, x),
        max_selections=st.session_state.airline_max_sel,
        on_change=airline_select_logic
    )

# ------------------------ APPLY FILTER ------------------------
airport_filter_values = (
    airport_list if -1 in st.session_state.selected_airports
    else st.session_state.selected_airports
)

airline_filter_values = (
    airline_list if -1 in st.session_state.selected_airlines
    else st.session_state.selected_airlines
)

filtered_df = flights_df[
    (flights_df["origin"].isin(airport_filter_values)) &
    (flights_df["airline_id"].isin(airline_filter_values))
]

# ------------------------ KPI ------------------------
# Total cancelations
total_cancelations = filtered_df["departure"].isna().sum()

# Total flights (including cancelations)
total_flights = len(filtered_df)

# departed flights
flights_not_cancelled = filtered_df[filtered_df["departure"].notna()].copy()

# Delay (>15 mins)
flights_not_cancelled["delayed"] = flights_not_cancelled["departure_delay"] > 15

# Delay rate (%)
delay_rate = flights_not_cancelled["delayed"].mean() * 100 if not flights_not_cancelled.empty else 0

# On-time rate (%)
# On-time = 1-15 mins, including early departure (<0)
flights_not_cancelled["on_time"] = flights_not_cancelled["departure_delay"] <= 15
on_time_rate = flights_not_cancelled["on_time"].mean() * 100 if not flights_not_cancelled.empty else 0

# ------------------------ ICON SVG ------------------------
plane_svg = """
<svg xmlns="http://www.w3.org/2000/svg" fill="black" viewBox="0 0 24 24" width="24" height="24">
<path d="M21 16v-2l-8-5V3.5a.5.5 0 0 0-1 0V9l-8 5v2l8-1.5V21h1v-6.5l8 1.5z"/>
</svg>
"""

clock_svg = """
<svg xmlns="http://www.w3.org/2000/svg" fill="black" viewBox="0 0 24 24" width="24" height="24">
<circle cx="12" cy="12" r="10" stroke="black" stroke-width="2" fill="none"/>
<line x1="12" y1="6" x2="12" y2="12" stroke="black" stroke-width="2"/>
<line x1="12" y1="12" x2="16" y2="14" stroke="black" stroke-width="2"/>
</svg>
"""

check_svg = """
<svg xmlns="http://www.w3.org/2000/svg" fill="black" viewBox="0 0 24 24" width="24" height="24">
<circle cx="12" cy="12" r="10" fill="none" stroke="black" stroke-width="2"/>
<path d="M6 12l4 4 8-8" stroke="black" stroke-width="2" fill="none"/>
</svg>
"""

cross_svg = """
<svg xmlns="http://www.w3.org/2000/svg" fill="black" viewBox="0 0 24 24" width="24" height="24">
<circle cx="12" cy="12" r="10" fill="none" stroke="black" stroke-width="2"/>
<line x1="6" y1="6" x2="18" y2="18" stroke="black" stroke-width="2"/>
<line x1="18" y1="6" x2="6" y2="18" stroke="black" stroke-width="2"/>
</svg>
"""

# KPI BOX FUNCTION 
def kpi_box_html(label, value, sublabel, icon_svg):
    return f"""
    <div style="
        background-color: rgb(240, 242, 246);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        text-align: left;
    ">
        <div style="position:absolute; top:15px; right:15px;">{icon_svg}</div>
        <div style="font-size:14px; color:#555555;">{label}</div>
        <div style="font-size:28px; font-weight:bold; margin:5px 0;">{value}</div>
        <div style="font-size:14px; color:#555555;">{sublabel}</div>
    </div>
    """

# show KPI boxes
cols = st.columns(4, gap="small")
kpis = [
    ("Total Flights", f"{total_flights:,}", "6-month period", plane_svg),
    ("Delay Rate", f"{delay_rate:.1f}%", "Delay > 15 min", clock_svg),
    ("On-Time Rate", f"{on_time_rate:.1f}%", "Flights within 15 min", check_svg),
    ("Cancelations", f"{total_cancelations:,}", "Total cancelled flights", cross_svg)
]

for col, (label, value, sublabel, icon) in zip(cols, kpis):
    col.markdown(kpi_box_html(label, value, sublabel, icon), unsafe_allow_html=True)

st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# ---------------- Map visualization: DELAY RATE PER AIRPORT ----------------
map_delay_df = (
    filtered_df[filtered_df["departure"].notna()]
    .assign(delayed=lambda x: x["departure_delay"] > 15)
    .groupby("origin", as_index=False)
    .agg(
        total_flights=("flight", "count"),
        delayed_flights=("delayed", "sum")
    )
)

map_delay_df["delay_rate"] = (
    map_delay_df["delayed_flights"] / map_delay_df["total_flights"] * 100
)

map_delay_df = map_delay_df.merge(
    airports_df,
    left_on="origin",
    right_on="airport_code",
    how="left"
)

# label for bubble
map_delay_df["label"] = map_delay_df.apply(
    lambda x: f"{x['origin']}\n{x['delay_rate']:.0f}%", axis=1
)

fig_map = px.scatter_map(
    map_delay_df,
    lat="latitude",
    lon="longitude",
    size="delay_rate",
    color="delay_rate",
    color_continuous_scale="Bluered",
    size_max=35,
    zoom=7,
    height=450,
    text="label",
    hover_data={}
)

fig_map.update_layout(
    map_style="carto-positron",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    coloraxis_colorbar=dict(
        title="Delay Rate (%)",
        title_font=dict(
            color="#4E4E4E", 
            size=14,
            family="Arial"
        ),
        thickness=15,           
        len=0.6,               
        y=0.5,               
        yanchor='middle'  
    ),
    paper_bgcolor='rgba(245, 245, 245, 0)' 
)

fig_map.update_traces(
    textposition="middle center", 
    textfont=dict(
        size=10,                    
        color="white"                 
    ),
    hovertemplate=None
)

# ------------------------ DELAY TREND DATA ------------------------
delay_df = filtered_df.copy()

# Convert data to datetime
delay_df["scheduled_departure"] = pd.to_datetime(delay_df["scheduled_departure"])
delay_df["departure"] = pd.to_datetime(delay_df["departure"])

# only consider departed flights
delay_df = delay_df[delay_df["departure"].notna()]
delay_df["month"] = delay_df["scheduled_departure"].dt.to_period("M")
delay_df["delayed"] = delay_df["departure_delay"] > 15
delay_trend = (
    delay_df
    .groupby(["month", "origin"], as_index=False)
    .agg(
        total_flights=("departure_delay", "count"),
        delayed_flights=("delayed", "sum")
    )
)

# measure delay rate for each month and airport
delay_trend["delay_rate"] = delay_trend["delayed_flights"] / delay_trend["total_flights"] * 100
delay_trend["month"] = delay_trend["month"].dt.to_timestamp()

col_left, col_right = st.columns(2, gap="medium")

# LEFT: MAP
with col_left:
    st.markdown(
        '<h3 style="color:#ffffff;">Airport Delay Performance</h3>',
        unsafe_allow_html=True
    )
    st.plotly_chart(fig_map, use_container_width=True)

# RIGHT: DELAY TREND 
with col_right:
    st.markdown(
        '<h3 style="color:#ffffff;">Monthly Delay Rate Trend</h3>',
        unsafe_allow_html=True
    )
    fig_trend = px.line(
        delay_trend,
        x="month",
        y="delay_rate",
        color="origin",
        markers=True,
        labels={
            "month": "Month",
            "delay_rate": "Delay Rate (%)",
            "origin": "Airport"
        }
    )

    fig_trend.update_layout(
        yaxis_tickformat=".1f",
        height=450,
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_trend, use_container_width=True)


# ------------------------ DELAY CATEGORY ------------------------
flights_for_bar = filtered_df[filtered_df["departure"].notna()].copy()

def categorize_delay(x):
    if x <= 15:
        return "On-time (within 15 min)"
    elif x <= 60:
        return "Moderate Delay (16-60 min)"
    else:
        return "Extreme Delay (> 60 min)"

flights_for_bar["delay_category"] = flights_for_bar["departure_delay"].apply(categorize_delay)

bar_data = (
    flights_for_bar
    .groupby(["airline_id", "delay_category"], as_index=False)
    .agg(total_flights=("flight", "count"))
)
st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# Merge airline names
bar_data_named = bar_data.merge(
    airlines_df,
    on="airline_id",
    how="left"
)

# ------------------------ TABLE DATA ------------------------
table_data = (
    bar_data_named
    .groupby("airline", as_index=False)["total_flights"]
    .sum()
    .sort_values("total_flights", ascending=False)
    .rename(columns={
        "airline_name": "Airline",
        "total_flights": "Total Flights"
    })
)

col_left, col_right = st.columns([1, 2], gap="large")


with col_left:
    st.markdown(
        '<h4 style="margin-bottom:5px;">Departed Flights by Airline</h4>',
        unsafe_allow_html=True
    )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

# Total departed flights per airline 
airline_order = (
    bar_data_named
    .groupby("airline", as_index=False)["total_flights"]
    .sum()
    .sort_values("total_flights", ascending=False)
)

airline_order_list = airline_order["airline"].tolist()

# Total flights per airline & delay category
data_grouped = (
    bar_data_named
    .groupby(["airline", "delay_category"], as_index=False)["total_flights"]
    .sum()
)

# Hitung persentase per airline
data_grouped["percent"] = data_grouped.groupby("airline")["total_flights"].transform(lambda x: 100 * x / x.sum())

# Buat label persentase hanya jika total_flights kategori >= 3250
data_grouped["label"] = data_grouped.apply(
    lambda row: f"{row['percent']:.1f}%" if row['total_flights'] >= 3200 else "",
    axis=1
)

with col_right:
    st.markdown(
        '<h4 style="margin-bottom:5px; text-align:center;">'
        'Delay Categories'
        '</h4>',
        unsafe_allow_html=True
    )

    fig_bar_h = px.bar(
        data_grouped,
        y="airline",
        x="total_flights",
        color="delay_category",
        orientation="h",
        barmode="stack",
        text="label",  # label cuma muncul untuk percent >= threshold
        category_orders={"airline": airline_order_list},
        color_discrete_map={
            "On-time (within 15 min)": "#3c51ad",
            "Moderate Delay (16-60 min)": "#ffda6b",
            "Extreme Delay (> 60 min)": "#ec8181"
        },
        labels={
            "total_flights": "Number of Flights",
            "delay_category": "Delay Category"
        }
    )

    fig_bar_h.update_traces(textposition='inside')  # label di dalam bar
    fig_bar_h.update_layout(
        xaxis_title="Number of Flights",
        yaxis_title=None,
        legend_title="Delay Category",
        template="plotly_white",
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_bar_h, use_container_width=True)
