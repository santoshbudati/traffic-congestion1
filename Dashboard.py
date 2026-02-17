import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title("🚦 Smart School Traffic Dashboard")


DATA_PATH = "traffic.geojson"

# ---------- LOAD DATA ----------
@st.cache_data(ttl=60)
def load_geojson():
    with open(DATA_PATH) as f:
        return json.load(f)

data = load_geojson()

# ---------- BUILD TABLE ----------
rows = []
for feat in data["features"]:
    p = feat["properties"]
    rows.append({
        "School": p.get("School Name"),
        "Color": p.get("Traffic Color"),
        "Congestion %": round(p.get("Congestion Score", 0)*100, 1),
        "Speed": p.get("Current Speed (km/h)"),
        "FreeFlow": p.get("Free Flow Speed (km/h)")
    })

df = pd.DataFrame(rows)

# ---------- SIDEBAR INSIGHTS ----------
st.sidebar.header("Live Insights")

if len(df) > 0:
    worst = df.sort_values("Congestion %", ascending=False).head(5)

    st.sidebar.subheader("Top Congested Now")
    for i, (_, r) in enumerate(worst.iterrows(), start=1):
        st.sidebar.write(f"{i}. {r['School']}")
# ---------- MAP ----------
m = folium.Map(location=[16.30, 80.44], zoom_start=12)

for feat in data["features"]:
    lat = feat["geometry"]["coordinates"][1]
    lng = feat["geometry"]["coordinates"][0]
    p = feat["properties"]

    color = p.get("Traffic Color","grey").lower()
    score = round(p.get("Congestion Score",0)*100,1)

    popup = f"""
    <b>{p.get('School Name')}</b><br>
    Traffic: {color}<br>
    Congestion: {score}%<br>
    Speed: {p.get('Current Speed (km/h)')}/{p.get('Free Flow Speed (km/h)')}
    """

    folium.CircleMarker(
    location=[lat, lng],
    radius=6,
    stroke=False,          # removes ring border
    fill=True,
    fill_color=color,
    fill_opacity=1.0,      # full solid color
    popup=popup
).add_to(m)


st_folium(m, width=1400, height=700)
st.markdown("""
<div style="
background:#ffffff;
padding:18px;
border-radius:12px;
margin-top:18px;
width:420px;
box-shadow:0 2px 8px rgba(0,0,0,0.25);
color:#000000;
font-weight:600;
">

<h4 style="margin-bottom:12px; color:#000000;">Traffic Legend</h4>

<div style="display:flex; justify-content:space-between; margin-top:6px;">
<span>Free Flow</span>
<span style="width:18px;height:18px;background:green;display:inline-block;"></span>
</div>

<div style="display:flex; justify-content:space-between; margin-top:6px;">
<span>Moderate Traffic</span>
<span style="width:18px;height:18px;background:orange;display:inline-block;"></span>
</div>

<div style="display:flex; justify-content:space-between; margin-top:6px;">
<span>Heavy Traffic</span>
<span style="width:18px;height:18px;background:red;display:inline-block;"></span>
</div>

</div>
""", unsafe_allow_html=True)
# # ---------- TABLE VIEW ----------
# st.subheader("Live Traffic Table")
# st.dataframe(df)

# ---------- AUTO REFRESH ----------
time.sleep(60)
st.rerun()
