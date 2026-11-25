import streamlit as st

CITATION = ("Romano, Ceccucci, Tensi, Santi & Sancineto, *A Tale of Two Designs*, "
            "Chem. Methods 2025, 5, e202500008. doi:10.1002/cmtd.202500008")
COLORS = {"fcCCD": "#1f77b4", "D-optimal": "#e4572e"}


def show(fig):
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def table(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kw)


def footer():
    st.divider()
    st.caption("Data transcribed from the paper and its Supporting Information. " + CITATION)
