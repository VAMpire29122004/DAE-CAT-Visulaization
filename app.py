import streamlit as st
from src.data import load, designs
from src.ui import show, table, footer, CITATION

st.set_page_config(page_title="Tale of Two Designs - DoE explorer", page_icon="\U0001F9EA", layout="wide")

st.title("A Tale of Two Designs: fcCCD vs D-optimal DoE")
st.markdown("Interactive companion to the photo-induced, ZnCl\u2082-catalysed **C-3 selenylation of N-methylindole** "
            "(1a + (PhSe)\u2082 \u2192 3a). Use the sidebar pages to explore the designs, results, fitted models and kinetics.")
st.caption(CITATION)

fc, do = designs()
stats = load("model_stats").set_index("metric")
c = st.columns(4)
c[0].metric("fcCCD runs", len(fc))
c[1].metric("D-optimal runs", len(do), f"-{len(fc) - len(do)} ({(len(fc) - len(do)) / len(fc):.0%} fewer)", delta_color="off")
c[2].metric("Best conversion", f"{max(fc.Y_pct_3a.max(), do.Y_pct_3a.max()):.0f}%")
c[3].metric("Runs with \u226590%", int((fc.Y_pct_3a >= 90).sum()), help="in the fcCCD")

st.subheader("The four factors (3 levels each)")
table(load("variables"))

st.subheader("Headline findings from the paper")
st.markdown("""
- **Time** is the dominant linear factor; **catalyst loading** shows strong negative curvature (optimum near the middle); **concentration** is negligible.
- A **D-optimal** plan with 17 runs recovered essentially the same optimum and coefficient pattern as the 25-run **fcCCD**.
- **FlowNMR** shows a roughly linear (zero-order-like) profile, consistent with concentration not mattering.
- TEMPO does not suppress the reaction (85%), argon kills it (10%), O\u2082 restores it (84%) \u2192 O\u2082 re-oxidises PhSeH to (PhSe)\u2082.
""")

with st.expander("Data notes and inconsistencies I found while transcribing"):
    st.markdown("""
- **Refit check:** OLS on the run tables in `data/` reproduces the published coefficients for both designs, so the transcription is consistent with the SI models.
- **D-optimal run (5, 5, 242, 1.0):** SI Table S4 gives **36%**; main-text Table 2 entry 26 gives **56%**. The CSV uses the SI value (the one the SI model was fitted to).
- **D-optimal run (5, 12.5, 161, 1.5):** SI Table S4 gives **78%** (labelled LR087/LR122); the same point in the fcCCD is **93%**.
- **"% explained variance" in the SI is the *adjusted* R\u00b2** (76.29% / 96.24%); raw R\u00b2 is 90.1% / 99.5%.
- The D-optimal model has only **2 residual degrees of freedom** (17 runs, 15 coefficients); its leave-one-out Q\u00b2 is strongly negative in the SI (-70.98%).
- The abstract says "25% fewer" runs; 8 of 25 is **32%** (used in the body and conclusion).
- The fcCCD table lists a single centre row although the text mentions triplicate centre runs (pure-error variance s\u00b2 = 2.44).
- The paper says no interactions are noteworthy, yet classical p-values give b13 (and b12 in the fcCCD) p < 0.01; resampling p-values call nothing significant except b0/b1.
""")
footer()
