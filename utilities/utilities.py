import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

pio.templates["simple_white"]["layout"]["xaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["mirror"] = True
pio.templates["simple_white"]["layout"]["xaxis"]["showgrid"] = True
pio.templates["simple_white"]["layout"]["yaxis"]["showgrid"] = True
pio.templates.default = "simple_white"


def plot_df(df, unit_length, unit_time):
    fig = (
        px.scatter(
            df,
            x="time",
            y="displacement",
        )
        .update_traces(
            marker=dict(
                color="black",
                size=2,
            )
        )
        .update_layout(
            height=500,
            width=700,
            xaxis=dict(
                title=dict(
                    text=f"Time, {unit_time}",
                ),
                range=[df["time"].min(), df["time"].max()],
            ),
            yaxis=dict(
                title=dict(
                    text=f"Displacement, {unit_length}",
                ),
                type="log",
                exponentformat="E",
                range=[
                    np.log(df["displacement"].min()),
                    np.log(df["displacement"].max()),
                ],
            ),
        )
    )

    return fig
