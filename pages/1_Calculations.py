import streamlit as st
import pandas as pd
import numpy as np
import io

# Local Libraries
from utilities import bouwer_rice_1989
from utilities import utilities

st.write(
    "Use the button below to upload a .csv with the rising head test data. It must contain two columns with the following names: 'Displacement' and 'Elapsed Time'."
)
uploaded_file = st.file_uploader("Upload data as a .csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)


col1, col2, col3 = st.columns(3)

with col1:
    test_name = st.text_input("Test Name", value="BH-01")
    unit_time = st.selectbox("Time (`time` column)", ["seconds"])
    unit_length = st.selectbox("Length (`displacement` column)", ["feet", "meters"])
with col2:
    casing_radius = st.number_input("Well Radius, $r_c$", value=2 / 12)
    well_screen_length = st.number_input("Well Screen Length, $L_e$", value=30)
    well_radius = st.number_input("Well Radius $r_w$", value=4.75 / 12)

with col3:
    water_table_height_above_aquiclude = st.number_input(
        "Water column height (above top of aquiclude), $H$", value=150
    )
    water_column_height = st.number_input(
        "Water column height (above bottom of well screen), $L_w$", value=50
    )

coefficient_A = bouwer_rice_1989.ln_Re_rw_coeff(
    kind="A", L_e=well_screen_length, r_w=well_radius
)
coefficient_B = bouwer_rice_1989.ln_Re_rw_coeff(
    kind="B", L_e=well_screen_length, r_w=well_radius
)
coefficient_C = bouwer_rice_1989.ln_Re_rw_coeff(
    kind="C", L_e=well_screen_length, r_w=well_radius
)

st.markdown(
    r"""If all relevant data has been provided, a chart will be displayed below. Use the selectors above the chart to decide what portion of the plot to used for the slope $\frac{\ln{\frac{y_0}{y_t}}}{t}$"""
)
if "df" in globals():
    # fig = utilities.plot_df(df, unit_length, unit_time)
    # st.plotly_chart(fig)
    ln_Re_rw = bouwer_rice_1989.ln_Re_rw(
        water_column_height=water_column_height,
        water_table_height_above_aquiclude=water_table_height_above_aquiclude,
        well_radius=well_radius,
        screen_length=well_screen_length,
        A=coefficient_A,
        B=coefficient_B,
    )

    col1, col2 = st.columns(2)
    with col1:
        t0 = st.number_input(
            "$t_0$",
            min_value=df["time"].min(),
            max_value=df["time"].max(),
            value=df["time"].min(),
        )
    with col2:
        tn = st.number_input(
            "$t_n$",
            min_value=t0 + 1,
            max_value=df["time"].max(),
            value=df["time"].max(),
        )

    dfx = df[df["time"].between(t0, tn)]
    y0 = dfx["displacement"].iloc[0]
    slope, intercept = bouwer_rice_1989.ln_yt(y0, dfx)
    ln_yt = -slope

    k = bouwer_rice_1989.hydraulic_conductivity(
        casing_radius=casing_radius,
        screen_length=well_screen_length,
        ln_Re_rw=ln_Re_rw,
        ln_yt=ln_yt,
    )
    fig = bouwer_rice_1989.plot_results(
        name=test_name,
        units_length=unit_length,
        units_time=unit_time,
        static_water_level=4.5,
        displacement=df["displacement"],
        elapsed_time=df["time"],
        k=k,
        slope=slope,
        intercept=intercept,
    )
    st.plotly_chart(fig)

    # Create an in-memory buffer
    buffer = io.BytesIO()

    # Save the figure as a pdf to the buffer
    fig.write_image(file=buffer, format="pdf")

    # Download the pdf from the buffer
    st.download_button(
        label="Download PDF",
        data=buffer,
        file_name="Results.pdf",
        mime="application/pdf",
    )
