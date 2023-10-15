import streamlit as st
from utilities import bouwer_rice_1989

st.title("Bouwer Rice Hydraulic Conductivity")

st.write("Governing equiations:")

st.latex(r"k = r_c^{2}\frac{\ln{R_e/r_w}}{2L_e}\ln{\frac{y_0}{y_t}}\frac{1}{t}")

st.markdown(
    r"""Where:\
         $k$ is the hydraulic conductivity\
         $r_c$ is the inside radius of the well casing\
         $R_e$ is the effective radial distance over which y is dissipated (the geometry factor)\
         $r_w$ is the radial distance of the undisturbed portion of the aquifer (from well centerline)\
         $L_e$ is the length of the well screen\
         $L_w$ is the vertical distance from the bottom of the well to the static water table outside the well\
         $y_0$ is the vertical distance between the water level inside the well and the static water table outside the well\
         $y_t$ is the is the vertical distance between the water level inside the well and the static water table outside the well at elapsed time $t$\
         \
        The geometry factor ($R_e$) is typically difficult to determine, so Bouwers and Rice performed analyses on various system geometries to develop a relationships to define $\ln{\frac{R_e}{r_w}}$. They developed the equations below from those analyses:"""
)

st.markdown(r"When $L_w < H$:")
st.latex(
    r"\ln{\frac{R_e}{r_w}}=\left[\frac{1.1}{\ln{L_w/r_w}}+\frac{A+B\ln{[(H-L_w)/r_w]}}{L_e/r_w}\right]^{-1}"
)

st.markdown(r"When $L_w = H$:")
st.latex(
    r"\ln{\frac{R_e}{r_w}}=\left[\frac{1.1}{\ln{L_w/r_w}}+\frac{C}{L_e/r_w}\right]^{-1}"
)

st.markdown(
    r"The $A$, $B$, and $C$ terms are dimensionless and can be determined using the ratio $L_e/r_w$ and the plot published in Bouwers (1989). The published chart is reproduced below."
)

st.plotly_chart(bouwer_rice_1989.ln_Re_rw_coeff_plot())
