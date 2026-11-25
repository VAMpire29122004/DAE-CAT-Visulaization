import pandas as pd
import plotly.express as px
import streamlit as st
from src import doe
from src.data import designs
from src.ui import show, table, footer, COLORS

st.title("Experimental results")
fc, do = designs()
which = st.radio("Design", ["fcCCD", "D-optimal", "Both"], horizontal=True)
d = {"fcCCD": fc.assign(Design="fcCCD"), "D-optimal": do.assign(Design="D-optimal")}
df = pd.concat(d.values()) if which == "Both" else d[which]
thr = st.slider("Highlight conversions \u2265", 0, 100, 90)
df = df.assign(hit=df.Y_pct_3a >= thr)

fig = px.bar(df, x="run", y="Y_pct_3a", color="Design", pattern_shape="hit", pattern_shape_map={True: "", False: "/"},
             barmode="group", color_discrete_map=COLORS, hover_data=["X1_time_h", "X2_ZnCl2_mol", "X3_conc_mM", "X4_equiv_2a"])
fig.update_layout(yaxis_title="Conversion to 3a (%)", xaxis_title="Run", height=450)
show(fig)

st.subheader("Main effects on mean conversion")
rows = []
for f, col in zip(doe.FACTORS, ["X1_c", "X2_c", "X3_c", "X4_c"]):
    for lvl, g in df.groupby(col):
        rows.append(dict(factor=doe.LABELS[f], level=doe.decode(lvl, f), mean_Y=g.Y_pct_3a.mean(), n=len(g)))
me = pd.DataFrame(rows)
fig2 = px.line(me, x="level", y="mean_Y", facet_col="factor", markers=True)
fig2.update_xaxes(matches=None, title="")
fig2.update_yaxes(title="Mean Y (%)")
show(fig2)
st.caption("Raw marginal means. They are unbalanced for the D-optimal design, so use the fitted coefficients page for adjusted effects.")

st.subheader(f"Runs with conversion \u2265 {thr}%")
table(df[df.hit].drop(columns="hit").sort_values("Y_pct_3a", ascending=False))
footer()
