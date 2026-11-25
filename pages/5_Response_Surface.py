import plotly.graph_objects as go
import streamlit as st
from src import doe
from src.data import designs
from src.ui import show, footer

st.title("Response surface")
fc, do = designs()
mdl = st.radio("Model", ["fcCCD", "D-optimal"], horizontal=True)
d = fc if mdl == "fcCCD" else do
b = doe.fit_ols(d[doe.CODED].values, d.Y_pct_3a.values)["coef"]

a, c = st.columns(2)
fx = a.selectbox("x axis", doe.FACTORS, 0, format_func=doe.LABELS.get)
fy = c.selectbox("y axis", [f for f in doe.FACTORS if f != fx], 0, format_func=doe.LABELS.get)
fixed = {}
for f in doe.FACTORS:
    if f not in (fx, fy):
        v = st.sidebar.slider(doe.LABELS[f], float(doe.decode(-1, f)), float(doe.decode(1, f)), float(doe.CENTRE[f]))
        fixed[f] = float(doe.encode(v, f))
g, Z = doe.surface(b, fx, fy, fixed)
kind = st.radio("Plot", ["Contour", "3-D surface"], horizontal=True)
X, Y = doe.decode(g, fx), doe.decode(g, fy)
if kind == "Contour":
    fig = go.Figure(go.Contour(x=X, y=Y, z=Z, colorscale="Viridis", colorbar=dict(title="Y (%)"), contours=dict(showlabels=True)))
else:
    fig = go.Figure(go.Surface(x=X, y=Y, z=Z, colorscale="Viridis", colorbar=dict(title="Y (%)")))
    fig.update_layout(scene=dict(xaxis_title=doe.LABELS[fx], yaxis_title=doe.LABELS[fy], zaxis_title="Y (%)"))
pts = d
if kind == "Contour":
    fig.add_trace(go.Scatter(x=pts[{"X1": "X1_time_h", "X2": "X2_ZnCl2_mol", "X3": "X3_conc_mM", "X4": "X4_equiv_2a"}[fx]],
                             y=pts[{"X1": "X1_time_h", "X2": "X2_ZnCl2_mol", "X3": "X3_conc_mM", "X4": "X4_equiv_2a"}[fy]],
                             mode="markers", name="runs", marker=dict(color="white", size=7, line=dict(color="black", width=1))))
fig.update_layout(height=600, xaxis_title=doe.LABELS[fx], yaxis_title=doe.LABELS[fy])
show(fig)
i = Z.argmax()
st.metric("Max predicted on this slice", f"{Z.max():.1f}%",
          f"{doe.LABELS[fx]} = {X[i % len(g)]:.1f}, {doe.LABELS[fy]} = {Y[i // len(g)]:.1f}", delta_color="off")
st.caption("Predictions >100% are artefacts of a quadratic fit near a ceiling. Interpret the surface only inside the studied ranges.")
footer()
