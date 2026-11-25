import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src import doe
from src.data import designs
from src.ui import show, table, footer, COLORS

st.title("Design space: where each design puts its experiments")
fc, do = designs()
allruns = pd.concat([fc.assign(Design="fcCCD"), do.assign(Design="D-optimal")], ignore_index=True)
cols = {f: {"fcCCD": None} for f in doe.FACTORS}
actual = {"X1": "X1_time_h", "X2": "X2_ZnCl2_mol", "X3": "X3_conc_mM", "X4": "X4_equiv_2a"}

t1, t2, t3, t4 = st.tabs(["2-D projection", "3-D view", "Parallel coordinates", "Information metrics"])

with t1:
    a, b = st.columns(2)
    fx = a.selectbox("x", doe.FACTORS, 0, format_func=doe.LABELS.get, key="px")
    fy = b.selectbox("y", [f for f in doe.FACTORS if f != fx], 0, format_func=doe.LABELS.get, key="py")
    grid = doe.candidate_grid()
    gi, gj = doe.FACTORS.index(fx), doe.FACTORS.index(fy)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=doe.decode(grid[:, gi], fx), y=doe.decode(grid[:, gj], fy), mode="markers",
                             name="81 candidate points", marker=dict(color="lightgrey", size=6)))
    for name, d, sym, sz in [("fcCCD", fc, "circle-open", 18), ("D-optimal", do, "diamond", 11)]:
        fig.add_trace(go.Scatter(x=d[actual[fx]], y=d[actual[fy]], mode="markers", name=name,
                                 marker=dict(symbol=sym, size=sz, color=COLORS[name], line=dict(width=2)),
                                 text=[f"run {r}: {y:.0f}%" for r, y in zip(d.run, d.Y_pct_3a)], hoverinfo="text"))
    fig.update_layout(xaxis_title=doe.LABELS[fx], yaxis_title=doe.LABELS[fy], height=520)
    show(fig)
    st.caption("Projections overlap because many of the 4-D points collapse onto the same 2-D location.")

with t2:
    a, b, c = st.columns(3)
    f1 = a.selectbox("x", doe.FACTORS, 0, format_func=doe.LABELS.get, key="3x")
    f2 = b.selectbox("y", doe.FACTORS, 1, format_func=doe.LABELS.get, key="3y")
    f3 = c.selectbox("z", doe.FACTORS, 3, format_func=doe.LABELS.get, key="3z")
    fig = px.scatter_3d(allruns, x=actual[f1], y=actual[f2], z=actual[f3], color="Y_pct_3a", symbol="Design",
                        color_continuous_scale="Viridis", hover_data=["run", "Design"])
    fig.update_layout(height=600, scene=dict(xaxis_title=doe.LABELS[f1], yaxis_title=doe.LABELS[f2], zaxis_title=doe.LABELS[f3]))
    show(fig)

with t3:
    which = st.radio("Design", ["fcCCD", "D-optimal"], horizontal=True)
    d = fc if which == "fcCCD" else do
    fig = px.parallel_coordinates(d, dimensions=list(actual.values()) + ["Y_pct_3a"], color="Y_pct_3a",
                                  color_continuous_scale="Viridis",
                                  labels={"X1_time_h": "Time (h)", "X2_ZnCl2_mol": "ZnCl2 (mol%)", "X3_conc_mM": "Conc. (mM)",
                                          "X4_equiv_2a": "2a (equiv)", "Y_pct_3a": "Y (%)"})
    show(fig)

with t4:
    rows = []
    for name, d in [("fcCCD", fc), ("D-optimal", do), ("Full 3^4 grid", None)]:
        C = doe.candidate_grid() if d is None else d[doe.CODED].values
        X = doe.design_matrix(C)
        rows.append(dict(Design=name, Runs=len(C), **{"log det(X'X/N)": round(doe.logdet_info(C), 3),
                         "trace (X'X)^-1": round(float(np.trace(np.linalg.pinv(X.T @ X))), 4)}))
    table(pd.DataFrame(rows))
    st.caption("Higher log-determinant = more information per run; trace of the dispersion matrix reproduces the SI values "
               "(2.3543 for fcCCD, 3.6539 for D-optimal). The paper's Fig. S2 (log-determinant vs number of runs, 15-25) is not reproduced here.")
    shared = int(do.also_in_fcCCD.sum())
    st.markdown(f"**{shared} of 17** D-optimal design points coincide with fcCCD points.")
    table(do[["run", "lab_ref", "X1_time_h", "X2_ZnCl2_mol", "X3_conc_mM", "X4_equiv_2a", "Y_pct_3a", "also_in_fcCCD"]])
footer()
