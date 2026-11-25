import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src import doe
from src.data import load, designs
from src.ui import show, table, footer, COLORS

st.title("Model diagnostics: fit vs prediction")
fc, do = designs()
which = st.radio("Design", ["fcCCD", "D-optimal"], horizontal=True)
d = fc if which == "fcCCD" else do
r = doe.fit_ols(d[doe.CODED].values, d.Y_pct_3a.values)
y = d.Y_pct_3a.values

m = st.columns(5)
m[0].metric("R\u00b2", f"{r['r2']:.3f}")
m[1].metric("Adjusted R\u00b2", f"{r['adj_r2']:.3f}")
m[2].metric("Q\u00b2 (LOO)", f"{r['q2']:.2f}")
m[3].metric("RMSECV (%)", f"{r['rmsecv']:.1f}")
m[4].metric("Residual d.f.", r["dof"])

c1, c2 = st.columns(2)
fig = go.Figure()
fig.add_trace(go.Scatter(x=y, y=r["fitted"], mode="markers", name="fitted", marker=dict(color=COLORS[which], size=9)))
fig.add_trace(go.Scatter(x=y, y=r["loo_pred"], mode="markers", name="leave-one-out",
                         marker=dict(symbol="x", size=9, color="black")))
fig.add_trace(go.Scatter(x=[0, 110], y=[0, 110], mode="lines", name="y = x", line=dict(dash="dash", color="grey")))
fig.update_layout(title="Observed vs predicted", xaxis_title="Observed (%)", yaxis_title="Predicted (%)", height=450)
with c1:
    show(fig)
fig2 = go.Figure(go.Bar(x=d.run, y=r["resid"], name="residual", marker_color=COLORS[which]))
fig2.add_trace(go.Bar(x=d.run, y=r["loo_resid"], name="LOO residual", marker_color="black", opacity=0.5))
fig2.update_layout(title="Residuals by run", barmode="group", xaxis_title="Run", yaxis_title="Residual (%)", height=450)
with c2:
    show(fig2)

st.subheader("Published vs recomputed")
s = load("model_stats").set_index("metric")
table(s.reset_index())
do_r2 = doe.fit_ols(do[doe.CODED].values, do.Y_pct_3a.values)["r2"]
st.markdown(f"""
- The **fit** looks excellent for the D-optimal design (R\u00b2 = {do_r2:.3f}), but with only 2 residual degrees of freedom (17 runs, 15 coefficients) the model can nearly interpolate its data.
- **Prediction** is what matters: the SI's cross-validation gives Q\u00b2 = -70.98% (D-optimal) vs +43.86% (fcCCD), so the smaller design predicts held-out runs *worse*, even though it identifies the same optimum and the same dominant effects.
""")
st.caption("Q\u00b2 here = 1 - PRESS/SS_total and can differ slightly from the value printed in the SI; RMSECV matches the SI (18.15 / 33.6).")
footer()
