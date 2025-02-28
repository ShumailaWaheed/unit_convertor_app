import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

conversion_factors = {
    "Length": {"Metre": 1, "Kilometre": 0.001, "Centimetre": 100, "Millimetre": 1000, "Inch": 39.37, "Foot": 3.281, "Yard": 1.094, "Mile": 0.000621},
    "Weight": {"Kilogram": 1, "Gram": 1000, "Pound": 2.205, "Ounce": 35.274, "Stone": 0.157, "Ton": 0.0011},
    "Temperature": {"Celsius": lambda x: x, "Fahrenheit": lambda x: (x * 9/5) + 32, "Kelvin": lambda x: x + 273.15},
    "Volume": {"Litre": 1, "Millilitre": 1000, "Gallon": 0.219, "Pint": 1.76, "Cup": 4.227},
    "Area": {"Square Metre": 1, "Square Foot": 10.764, "Square Yard": 1.196, "Acre": 0.000247, "Hectare": 0.0001},
}

def convert_units(value, from_unit, to_unit, category):
    if category == "Temperature":
        return conversion_factors[category][to_unit](value)
    return value * (conversion_factors[category][to_unit] / conversion_factors[category][from_unit])

st.set_page_config(page_title="Advanced Unit Converter", page_icon="🔢", layout="wide")

st.sidebar.header("⚡ Quick Access")
category = st.sidebar.selectbox("Select Category", list(conversion_factors.keys()), key="category")
unit_options = list(conversion_factors[category].keys())

st.sidebar.header("🛠 Custom Conversion")
custom_from = st.sidebar.text_input("From Unit", key="custom_from")
custom_to = st.sidebar.text_input("To Unit", key="custom_to")
custom_factor = st.sidebar.number_input("Factor", value=1.0, key="custom_factor")
if st.sidebar.button("Add Custom Conversion"):
    if custom_from and custom_to and custom_factor:
        conversion_factors.setdefault("Custom", {})[custom_from] = 1
        conversion_factors["Custom"][custom_to] = custom_factor
        st.sidebar.success(f"Added custom conversion: 1 {custom_from} = {custom_factor} {custom_to}")

st.title("🔢 Advanced Unit Converter")

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    value = st.number_input("Enter Value", value=1.0, min_value=0.0, step=0.1, key="main_value")
    from_unit = st.selectbox("From", unit_options, key="from_unit")
with col2:
    st.markdown("# =")
with col3:
    to_unit = st.selectbox("To", unit_options, key="to_unit")
    try:
        converted_value = convert_units(value, from_unit, to_unit, category)
        st.markdown(f"# {converted_value:.2f}")
    except KeyError:
        st.error("Invalid unit conversion. Please check your inputs.")

st.subheader("🔁 Multi-Unit Conversion")
multi_units = st.multiselect("Select Units to Convert To", unit_options, default=[to_unit], key="multi_units")
if multi_units:
    multi_conversions = {unit: convert_units(value, from_unit, unit, category) for unit in multi_units}
    multi_df = pd.DataFrame(list(multi_conversions.items()), columns=["Unit", "Converted Value"])
    st.dataframe(multi_df)

if 'history' not in st.session_state:
    st.session_state['history'] = []
if st.button("Save to History", key="save_history"):
    st.session_state['history'].append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Category": category,
        "Value": value,
        "From": from_unit,
        "To": to_unit,
        "Converted": converted_value
    })
if st.session_state['history']:
    st.subheader("📜 Conversion History")
    history_df = pd.DataFrame(st.session_state['history'])
    st.dataframe(history_df)
    if st.button("Export History to CSV", key="export_csv"):
        history_df.to_csv("conversion_history.csv", index=False)
        st.success("History exported to conversion_history.csv")

st.subheader("📊 Conversion Analysis")
data = pd.DataFrame({
    "Unit": [from_unit, to_unit],
    "Value": [value, converted_value]
})

fig_bar = px.bar(data, x="Unit", y="Value", title=f"{category} Conversion", color="Unit", text="Value",
                 labels={"Value": "Converted Value", "Unit": "Unit"})
fig_bar.update_traces(textposition='outside')
st.plotly_chart(fig_bar)

if multi_units:
    multi_data = pd.DataFrame({
        "Unit": multi_units,
        "Value": [convert_units(value, from_unit, unit, category) for unit in multi_units]
    })
    fig_line = px.line(multi_data, x="Unit", y="Value", title=f"{category} Conversion to Multiple Units",
                       labels={"Value": "Converted Value", "Unit": "Unit"})
    fig_line.update_traces(mode='lines+markers', marker=dict(size=10))
    st.plotly_chart(fig_line)

fig_scatter = px.scatter(data, x="Unit", y="Value", title=f"{category} Conversion Scatter Plot",
                         labels={"Value": "Converted Value", "Unit": "Unit"})
fig_scatter.update_traces(marker=dict(size=15, color='red'))
st.plotly_chart(fig_scatter)

if multi_units:
    fig_subplots = go.Figure()
    for unit in multi_units:
        fig_subplots.add_trace(go.Scatter(x=[from_unit, unit], y=[value, convert_units(value, from_unit, unit, category)],
                                         mode='lines+markers', name=unit))
    fig_subplots.update_layout(title=f"{category} Conversion Comparison", xaxis_title="Unit", yaxis_title="Value")
    st.plotly_chart(fig_subplots)

st.subheader("ℹ️ Unit Information")
unit_info = {
    "Metre": "The metre is the base unit of length in the International System of Units (SI).",
    "Kilometre": "The kilometre is a unit of length in the metric system, equal to one thousand metres.",
    "Celsius": "Celsius is a scale and unit of measurement for temperature.",
    "Fahrenheit": "Fahrenheit is a temperature scale based on one proposed in 1724 by the physicist Daniel Gabriel Fahrenheit.",
    "Kilogram": "The kilogram is the base unit of mass in the International System of Units (SI).",
    "Litre": "The litre is a metric unit of volume.",
}
selected_unit = st.selectbox("Select Unit to Get Information", list(unit_info.keys()), key="unit_info")
st.write(unit_info[selected_unit])
