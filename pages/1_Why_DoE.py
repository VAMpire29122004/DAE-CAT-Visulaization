import numpy as np
import plotly.graph_objects as go
import streamlit as st
from src import doe
from src.data import designs
from src.ui import show, footer

st.title("OFAT vs DoE (illustration)")
st.info("This runs a one-factor-at-a-time search on the **fitted fcCCD surface**. It is an illustration of the idea, "
        "not data from the paper, and for this fairly additive reaction OFAT may do reasonably well.")

fc, _ = designs()
fit = doe.fit_ols(fc[doe.CODED].values, fc.Y_pct_3a.values)
b = fit["coef"]

c1, c2, c3 = st.columns(3)
fx = c1.selectbox("First factor swept", doe.FACTORS, 0, format_func=doe.LABELS.get)
fy = c2.selectbox("Second factor swept", [f for f in doe.FACTORS if f != fx], 0, format_func=doe.LABELS.get)
cycles = c3.slider("OFAT cycles", 1, 3, 1)
others = [f for f in doe.FACTORS if f not in (fx, fy)]
fixed = {f: st.sidebar.slider(f"{doe.LABELS[f]} (coded)", -1.0, 1.0, 0.0, 0.5) for f in others}
sx = st.sidebar.select_slider("Start X (coded)", [-1.0, -0.5, 0.0, 0.5, 1.0], -1.0)
sy = st.sidebar.select_slider("Start Y (coded)", [-1.0, -0.5, 0.0, 0.5, 1.0], -1.0)

g, Z = doe.surface(b, fx, fy, fixed)


def f(x, y):
    C = np.zeros((1, 4))
    for k, v in fixed.items():
        C[0, doe.FACTORS.index(k)] = v
    C[0, doe.FACTORS.index(fx)], C[0, doe.FACTORS.index(fy)] = x, y
    return float(doe.predict(b, C)[0])


levels = np.linspace(-1, 1, 5)
x, y = sx, sy
path = [(x, y)]
for _ in range(cycles):
    x = max(levels, key=lambda v: f(v, y)); path.append((x, y))
    y = max(levels, key=lambda v: f(x, v)); path.append((x, y))
unique = list(dict.fromkeys(path))
ofat_best = f(*path[-1])
gx, gy = np.meshgrid(g, g)
i = np.unravel_index(np.argmax(Z), Z.shape)

fig = go.Figure(go.Contour(x=doe.decode(g, fx), y=doe.decode(g, fy), z=Z, colorscale="Viridis",
                           colorbar=dict(title="Y (%)"), contours=dict(showlabels=True)))
fig.add_trace(go.Scatter(x=doe.decode([p[0] for p in path], fx), y=doe.decode([p[1] for p in path], fy),
                         mode="lines+markers", name="OFAT path", line=dict(color="white", width=3)))
fig.add_trace(go.Scatter(x=[doe.decode(g[i[1]], fx)], y=[doe.decode(g[i[0]], fy)], mode="markers",
                         name="Model maximum", marker=dict(symbol="star", size=16, color="red")))
fig.update_layout(xaxis_title=doe.LABELS[fx], yaxis_title=doe.LABELS[fy], height=550)
show(fig)

m = st.columns(3)
m[0].metric("OFAT end-point (model)", f"{ofat_best:.1f}%")
m[1].metric("Model maximum on grid", f"{Z.max():.1f}%")
m[2].metric("OFAT distinct experiments", len(unique))
st.caption("Predicted values above 100% are not physical; they show the quadratic model extrapolating beyond a plateau. "
           "A DoE plan fixes all runs in advance and fits the whole surface at once, so interactions and curvature are estimable.")
footer()
