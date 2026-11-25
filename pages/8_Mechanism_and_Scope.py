import plotly.express as px
import streamlit as st
from src.data import load
from src.ui import show, table, footer

st.title("Screening, mechanism and scope")
t1, t2, t3 = st.tabs(["Preliminary screening", "Mechanistic controls", "Scope"])

with t1:
    s = load("preliminary_screening")
    s["conversion_pct"] = s.conversion_pct.fillna(0)
    s["label"] = s.solvent + " | " + s.light + " | " + s.catalyst
    fig = px.bar(s, x="entry", y="conversion_pct", color="light", hover_data=["label", "time_h"], text="conversion_pct")
    fig.update_layout(yaxis_title="Conversion (%) (NC plotted as 0)", height=420)
    show(fig)
    table(load("preliminary_screening"))
    st.caption("Best preliminary result: ZnCl\u2082 in CH\u2083CN under blue LED, entry 8 (36%). No conversion in the dark, which shows light is required.")

with t2:
    c = load("mechanism_controls")
    fig = px.bar(c, x="experiment", y="conversion_or_yield_pct", color="atmosphere_or_additive", text="conversion_or_yield_pct")
    fig.update_layout(height=450, xaxis_title="", yaxis_title="Conversion / yield (%)", showlegend=False)
    show(fig)
    st.markdown("""
- **TEMPO (85%)**: radical trapping does not stop the reaction \u2192 an ionic pathway is favoured (a radical pathway is not fully excluded).
- **Argon (10%) vs O\u2082 (84%)**: oxygen is needed to re-oxidise PhSeH back to (PhSe)\u2082, closing the catalytic loop.
""")
    st.caption("The 67% 'air' reference is the fcCCD run 14 (7 h, 5 mol%, 323 mM, 2 equiv).")

with t3:
    sc = load("scope")
    sc["label"] = sc["product"] + " " + sc["substrate"] + " + " + sc["dichalcogenide"]
    fig = px.bar(sc, x="yield_pct", y="label", orientation="h", text="yield_pct", hover_data=["comment"])
    fig.update_layout(height=450, yaxis_title="", xaxis_title="Yield (%)")
    show(fig)
    table(sc)
footer()
