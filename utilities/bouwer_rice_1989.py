from statistics import linear_regression

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

pio.templates["simple_white"]["layout"]["xaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["xaxis"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["showgrid"] = True
pio.templates.default = "simple_white"


def hydraulic_conductivity(
    casing_radius: float,
    screen_length: float,
    ln_Re_rw: float,
    ln_yt: float,
) -> float:
    """
    Determine hydraulic conductivity based on the Bouwer and Rice methods as
    described in 'The Bouwer and Rice Slug Test - An Update0 (1989).

    Parameters
    ----------
    casing_radius: float
        Inside radius of the well casing, use same units as `screen_length`

    screen_length: float
        Length of well screening, use same units as `casing_radius`

    ln_Re_rw: float
        Dimensionless ratio representing the relationship between the geometry
        factor R_e and the well radius r_w.
        Use function `bouwer_rice_ln_Re_rw` to determine the value to use.

    ln_yt: float
        Dimensionless value representing the slope of the straight line of
        elapsed time and normalized water table displacement.
        Use function `bouwer_rice_ln_yt` to determine the value to use.

    Returns
    -------
    hydraulic_conductivity: float
        Units will be consistent with those used for the input parameters.
        Be sure to use consistent units with all input parameters (and the
        functions used to derive input parameters).

    Notes
    -----
    Be sure to use consistent units with all input parameters (and the
    functions used to derive input parameters).
    .. math::
        k = r_c^{2}\frac{\ln{\frac{R_e}{r_w}}}{2L_e}\frac{1}{t}\ln{\frac{y_0}{y_t}}

    Reference
    ---------
    Bouwer, H. 1989. The Bouwer and Rice Slug Test - An Update. GROUND WATER.
    Vol. 27. No. 3.
    """

    return ((casing_radius**2 * ln_Re_rw) / (2 * screen_length)) * ln_yt


def ln_yt(y0: float, df: pd.DataFrame) -> float:
    """
    Determine the dimensionless value representing the slope of the straight
    line of elapsed time and normalized water table displacement. Use this for
    the ln_yt term for the function `hydraulic_conductivity`.

    Parameters
    ----------
    y0: float
        Static water level as measured the beginning of the test. Corresponds to
        the y0 value described in Bouwer (1989).

    df: pd.DataFrame
        Pandas dataframe with at least two columns: `displacement` and `time`. They must be named as specified and sorted with `time` ascending from t=0. Ensure that the data is cleaned before use.

    Returns
    -------
    slope, intercept: float
        `slope` is the dimensionless value representing the slope of the straight line of
        elapsed time and normalized water table displacement. For the `ln_yt` term in `hydraulic_conductivity` use -1 * `slope`.

    Notes
    -----
    Displacement values used should be only those from the straight-line
    portion of the curve.

    Reference
    ---------
    Bouwer, H. 1989. The Bouwer and Rice Slug Test - An Update. GROUND WATER.
    Vol. 27. No. 3.
    """
    # df["y0/yt"] = df["displacement"] / y0
    # df["ln(y0/yt)"] = np.log(df["y0/yt"])
    # df = df[(df["ln(y0/yt)"].notnull()) & (np.isinf(df["ln(y0/yt)"]) == False)]
    # slope, intercept = linear_regression(df["time"], df["ln(y0/yt)"])
    df["ln(displacement)"] = np.log(df["displacement"])
    df = df[
        (df["ln(displacement)"].notnull()) & (np.isinf(df["ln(displacement)"]) == False)
    ]
    slope, intercept = linear_regression(df["time"], df["ln(displacement)"])
    return slope, intercept


def ln_Re_rw(
    water_column_height: float,
    water_table_height_above_aquiclude: float,
    well_radius: float,
    screen_length: float,
    A: float,
    B: float,
) -> float:
    """
    Determine the dimensionless ratio representing the relationship between the
    geometry factor R_e and the well radius r_w. Use this for the ln_Re_rw term
    for the function `bouwer_rice_hydraulic_conductivity_1989`.

    Use this ONLY if:
    `water_column_height` < `water_table_height_above_aquiclude`

    Parameters
    ----------
    water_column_height: float
        Height of water column measured from the bottom of the screen to the
        water table (in the 'undisturbed' condition). Corresponds to the L_w
        value described in Bouwer (1989).

    water_table_height_above_aquiclude: float
        Height of water column above the aquiclude. Corresponds to the H value
        described in Bouwer (1989).

    well_radius: float
        Radius of the borehole in which the well is installed. This should be
        the largest radius represented in the well (where the sand pack touches
        native soil or rock). Corresponds to the r_w value described in Bouwer
        (1989).

    screen_length: float
        Length of well screening. Corresponds to the L_e value described in
        Bouwer (1989).

    A: float
        Dimensionless number derived from the plot published in Bouwer (1989).

    B: float
        Dimensionless number derived from the plot published in Bouwer (1989).

    Returns
    -------
    ln_Re_rw: float
        Dimensionless ratio representing the relationship between the geometry
        factor R_e and the well radius r_w.

    Notes
    -----
    Be sure to use consistent units with all input parameters (and the
    functions used to derive input parameters).

    Reference
    ---------
    Bouwer, H. 1989. The Bouwer and Rice Slug Test - An Update. GROUND WATER.
    Vol. 27. No. 3.
    """
    expression0 = 1.1 / np.log(water_column_height / well_radius)
    expression1_numerator = A + B * np.log(
        (water_table_height_above_aquiclude - water_column_height) / (well_radius)
    )
    expression1_denominator = screen_length / well_radius

    ln_Re_rw = (expression0 + (expression1_numerator / expression1_denominator)) ** -1

    return ln_Re_rw


def plot_results(
    name: str,
    units_length: str,
    units_time: str,
    static_water_level: float,
    displacement: list,
    elapsed_time: list,
    k: float,
    slope: float,
    intercept: float,
) -> go.Figure:
    """
    Plots the results of a hydraulic conductivity analysis using the Bouwer and
    Rice methodology (Bouwer, 1989).

    Parameters
    ----------
    name: str
        Well or test name to use as identification.

    units: str
        Units to report on the plot. Make sure these are consistent with those
        used in the analysis.

    static_water_level: float


    normalized_displacement: list,
    elapsed_time: list,
    k: float,
    slope: float,
    intercept: float,

    Returns
    -------
    hydraulic_conductivity: float
        Units will be consistent with those used for the input parameters.
        Be sure to use consistent units with all input parameters (and the
        functions used to derive input parameters).

    Notes
    -----
    Be sure to use consistent units with all input parameters (and the
    functions used to derive input parameters).

    Reference
    ---------
    Bouwer, H. 1989. The Bouwer and Rice Slug Test - An Update. GROUND WATER.
    Vol. 27. No. 3.
    """
    unit_abbreviations = {"feet": "ft", "seconds": "s"}
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=elapsed_time,
            y=displacement,
            mode="markers",
            marker=dict(
                color="black",
                size=2,
            ),
        )
    )
    fig.update_layout(
        height=500,
        width=800,
        xaxis=dict(
            title=dict(
                text="Time, s",
            ),
            range=[elapsed_time.min(), elapsed_time.max()],
        ),
        yaxis=dict(
            title=dict(
                text=f"Displacement, {units_length}",
            ),
            type="log",
            exponentformat="E",
            range=[
                np.floor(np.log10(displacement).min()),
                np.ceil(np.log10(displacement).max()),
            ],
        ),
    )
    annotation_text = (
        annotation_text
    ) = f"""Test Well: {name}<br>Static Water Level: {static_water_level} {units_length}<br>Solution Type: Bouwer Rice<br>Hydraulic Conductivity: {k:.0E} {unit_abbreviations[units_length]}/{unit_abbreviations[units_time]}"""
    fig.add_annotation(
        text=annotation_text,
        showarrow=False,
        align="right",
        bgcolor="white",
        xref="x domain",
        x=0.99,
        yref="y domain",
        y=1,
    )
    trend_x = np.linspace(elapsed_time.min(), elapsed_time.max())
    trend_y = np.e ** (slope * trend_x + intercept)

    fig.add_trace(
        go.Scatter(x=trend_x, y=trend_y, line=dict(color="gray", width=2))
    ).update_layout(showlegend=False)
    return fig


def ln_Re_rw_coeff_plot():
    from utilities.ln_Re_rw_coeff_curves import ln_Re_rw_coeff_curves

    ln_Re_rw_coeff_curves.keys()

    dfs = []
    for curve, data in ln_Re_rw_coeff_curves.items():
        dfx = pd.DataFrame(data)
        dfx["curve"] = curve
        dfs.append(dfx)

    df = pd.concat(dfs)
    df
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for c in ["A", "C"]:
        dfx = df[df["curve"] == c]
        fig.add_trace(go.Scatter(x=dfx["x"], y=dfx["y"], name=c), secondary_y=False)

    dfx = df[df["curve"] == "B"]
    fig.add_trace(go.Scatter(x=dfx["x"], y=dfx["y"], name="B"), secondary_y=True)

    fig.update_layout(
        xaxis=dict(title=r"L_e/r_w", type="log", minor=dict(showgrid=True)),
        yaxis1=dict(
            title=dict(text="A and C"),
            range=[0, 14],
        ),
        yaxis2=dict(
            title=dict(text="B"),
            range=[0, 7],
            tickmode="sync",
        ),
        legend=dict(x=0.01, y=0.99),
        margin=dict(t=10, b=10, l=10, r=10),
    )
    return fig
