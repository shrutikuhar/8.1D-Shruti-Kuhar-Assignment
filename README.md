# Sydney HomeValue

A Streamlit decision-support application that estimates sale prices for properties in Parramatta, Newtown and Mosman.

The public URL remains stable. Community Cloud may put an inactive application to sleep, but visitors can wake it using the same link.

## Run locally or in Google Colab

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files

- `app.py`: interface and prediction logic
- `best_model.joblib`: fitted Random Forest modelling pipeline
- `requirements.txt`: pinned deployment dependencies

## Important limitation

This is an educational prototype rather than a formal property valuation. Predictions should be assessed alongside recent comparable sales and professional judgement.
