import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src import doe
from src.data import load, designs
from src.ui import show, table, footer, COLORS

st.title("Quadratic model coefficients")
src_ = st.radio("Source", ["Published (SI, \u03c3 = 2.44 pure error)", "Refit here (OLS, residual-based SE)"], horizontal=True)
coef = load("coefficients")
fc, do = designs()

fig = go.Figure()
tab = pd.DataFrame({"term": coef.term})
for name, pre, d in [("fcCCD", "fcCCD", fc), ("D-optimal", "Dopt", do)]:
    if src_.startswith("Published"):
        b, ci, p = coef[f"{pre}_coef"], coef[f"{pre}_ci"], coef[f"{pre}_p"]
    else:
        r = doe.fit_ols(d[doe.CODED].values, d.Y_pct_3a.values)
        from scipy import stats
        b, p = r["coef"], r["p"]
        ci = stats.t.ppf(0.975, r["dof"]) * r["se"]
    fig.add_trace(go.Bar(name=name, x=coef.term, y=b, error_y=dict(type="data", array=np.asarray(ci)),
                         marker_color=COLORS[name]))
    tab[f"{name} coef"], tab[f"{name} 95% CI \u00b1"], tab[f"{name} p"] = np.round(b, 3), np.round(ci, 3), np.round(p, 4)
fig.update_layout(barmode="group", height=500, yaxis_title="Coefficient (% conversion per coded unit)")
show(fig)
table(tab)

st.markdown("""
**Reading it:** coefficients are in coded units (-1/0/+1), so they are directly comparable.
`b1` (time) dominates; `b22` is strongly negative (catalyst optimum near the centre); `b3` (concentration) is ~0.
""")
if src_.startswith("Refit"):
    st.warning("The D-optimal refit has 2 residual degrees of freedom, so its standard errors and p-values are very unreliable. "
               "The paper instead uses the pure-error variance from centre-point replicates (s\u00b2 = 2.44).")
with st.expander("Resampling significance (SI)"):
    table(coef[["term", "fcCCD_resamp_sd", "fcCCD_resamp_p", "Dopt_resamp_sd", "Dopt_resamp_p"]])
    st.caption("Under resampling, almost nothing except b0 (and b1 in the D-optimal fit) is significant.")
with st.expander("Variance inflation factors"):
    table(coef[["term", "fcCCD_vif", "Dopt_vif"]])
footer()
