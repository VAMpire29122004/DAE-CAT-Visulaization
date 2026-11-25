# DoE explorer: "A Tale of Two Designs"

Streamlit companion app for Romano et al., *Chem. Methods* 2025, 5, e202500008
(fcCCD vs D-optimal DoE for photo-induced C-3 selenylation of N-methylindole).

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
Push this folder to GitHub, then create an app pointing at `app.py`.

## Data
All CSVs in `data/` are transcribed from the paper and SI; `python build_data.py` regenerates them.
Check `data/` values against the SI before citing anything from the app.
