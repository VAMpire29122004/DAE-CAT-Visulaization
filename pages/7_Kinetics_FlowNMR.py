import numpy as np
import plotly.graph_objects as go
import streamlit as st
from src.data import load
from src.ui import show, footer

st.title("FlowNMR kinetics")
k = load("flownmr_kinetics")
lo, hi = st.slider("Time window for the fit (min)", 0, int(k.time_min.max()), (0, int(k.time_min.max())), 5)
w = k[(k.time_min >= lo) & (k.time_min <= hi)]

def lin(x, y):
    s, i = np.polyfit(x, y, 1)
    res = y - (s * x + i)
    return s, i, 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()

s3, i3, r3 = lin(w.time_min.values, w.pct_3a.values)
s1, i1, r1 = lin(w.time_min.values, w.pct_1a.values)
pos = w[w.pct_1a > 0]
sl, il, rl = lin(pos.time_min.values, np.log(pos.pct_1a.values))

fig = go.Figure()
fig.add_trace(go.Scatter(x=k.time_min, y=k.pct_1a, name="1a (N-methylindole)", mode="markers"))
fig.add_trace(go.Scatter(x=k.time_min, y=k.pct_3a, name="3a (product)", mode="markers"))
t = np.array([lo, hi])
fig.add_trace(go.Scatter(x=t, y=s3 * t + i3, name="linear fit (3a)", line=dict(dash="dash")))
fig.update_layout(xaxis_title="Time (min)", yaxis_title="Relative amount (%)", height=480)
show(fig)

m = st.columns(4)
m[0].metric("Rate of 3a formation", f"{s3 * 60:.1f} %/h")
m[1].metric("Zero-order R\u00b2 (3a)", f"{r3:.4f}")
m[2].metric("Zero-order R\u00b2 (1a)", f"{r1:.4f}")
m[3].metric("First-order R\u00b2 (ln 1a)", f"{rl:.4f}")

resid = w.pct_3a.values - (s3 * w.time_min.values + i3)
f2 = go.Figure(go.Scatter(x=w.time_min, y=resid, mode="markers"))
f2.update_layout(title="Residuals of the linear fit (3a)", xaxis_title="Time (min)", yaxis_title="Residual (%)", height=300)
show(f2)
st.markdown("""
A straight line fits far better than a first-order exponential decay, consistent with a rate that does not depend on
substrate concentration (photon-limited behaviour) and with the DoE finding that concentration (X3) is negligible.
Values were read from SI Table S5 as integers (%), 3a = 100 - 1a; the paper reports 120 spectra, the table has 110 time points.
""")
footer()
