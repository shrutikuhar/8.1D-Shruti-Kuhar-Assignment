from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Sydney HomeValue | Price Estimator",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "best_model.joblib"
TEST_RMSE = 737_523


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


model = load_model()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    :root { --navy:#102a43; --teal:#0f766e; --cream:#f8faf7; --gold:#d9a441; }
    .stApp { background: linear-gradient(180deg,#f7fbfa 0%,#ffffff 36%); color:#172b3a; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    #MainMenu, footer, header { visibility:hidden; }
    .block-container { max-width:1180px; padding-top:1rem; padding-bottom:3rem; }
    .nav { display:flex; justify-content:space-between; align-items:center; padding:.45rem 0 1rem; }
    .brand { color:var(--navy); font-weight:800; font-size:1.2rem; letter-spacing:-.03em; }
    .brand span { color:var(--teal); }
    .tag { padding:.35rem .8rem; border:1px solid #cfe6e2; border-radius:999px; color:var(--teal); font-size:.82rem; font-weight:700; }
    .hero { position:relative; overflow:hidden; border-radius:28px; padding:4.5rem 4rem; min-height:370px;
      background:linear-gradient(115deg,rgba(10,39,55,.96),rgba(15,118,110,.82)),
      radial-gradient(circle at 85% 25%,#87d1c6 0%,transparent 36%); box-shadow:0 24px 70px rgba(16,42,67,.18); }
    .hero:after { content:'⌂  △  ▱  ⌂  △'; position:absolute; right:-10px; bottom:-45px; font-size:9rem; opacity:.08; color:white; letter-spacing:-2rem; }
    .eyebrow { color:#9fe2d8; text-transform:uppercase; letter-spacing:.16em; font-weight:700; font-size:.78rem; }
    .hero h1 { font-family:'Playfair Display',serif; color:white; font-size:4rem; line-height:1.03; margin:.6rem 0 1rem; max-width:650px; }
    .hero p { color:#dcebea; font-size:1.08rem; line-height:1.75; max-width:650px; }
    .pill { display:inline-block; margin:.55rem .35rem 0 0; padding:.45rem .85rem; border-radius:999px; background:rgba(255,255,255,.12); color:white; font-size:.83rem; }
    .section-title { font-family:'Playfair Display',serif; color:var(--navy); font-size:2rem; margin:2.7rem 0 .25rem; }
    .section-copy { color:#5d7180; margin-bottom:1.35rem; }
    [data-testid="stForm"] { background:white; border:1px solid #e2ece9; border-radius:22px; padding:1.4rem 1.6rem 1.7rem; box-shadow:0 12px 40px rgba(16,42,67,.07); }
    .stButton button, .stFormSubmitButton button { border:0; border-radius:12px; background:linear-gradient(90deg,#0f766e,#15998d); color:white; font-weight:700; min-height:3rem; }
    .result { background:linear-gradient(135deg,#0e3b43,#0f766e); border-radius:22px; padding:2rem; color:white; box-shadow:0 18px 50px rgba(15,118,110,.2); }
    .result-label { color:#a9e7dd; font-size:.8rem; text-transform:uppercase; letter-spacing:.14em; font-weight:700; }
    .result-price { font-family:'Playfair Display',serif; font-size:3.2rem; font-weight:700; margin:.25rem 0; }
    .result-range { color:#d8f3ee; font-size:1rem; }
    .insight { border-left:4px solid var(--gold); background:#fffaf0; border-radius:0 12px 12px 0; padding:1rem 1.2rem; margin-top:1rem; color:#514424; }
    .feature-card { height:100%; background:white; border:1px solid #e4eeeb; border-radius:18px; padding:1.25rem; box-shadow:0 8px 25px rgba(16,42,67,.05); }
    .feature-card h4 { color:var(--navy); margin:.35rem 0; }
    .feature-card p { color:#637785; font-size:.9rem; line-height:1.55; }
    .icon { font-size:1.6rem; }
    .fineprint { color:#70838f; font-size:.82rem; line-height:1.55; }
    @media(max-width:700px){ .hero{padding:3rem 1.5rem}.hero h1{font-size:2.7rem}.block-container{padding-left:1rem;padding-right:1rem} }
    </style>
    """,
    unsafe_allow_html=True,
)


def yes_no(value):
    return "Yes" if value else "No"


def make_row(values):
    bedrooms = float(values["Bedrooms"])
    floor_area = values.get("FloorAreaSqm", np.nan)
    return pd.DataFrame([{
        "Bedrooms": bedrooms,
        "Bathrooms": float(values["Bathrooms"]),
        "CarSpaces": float(values["CarSpaces"]),
        "FloorAreaSqm": floor_area,
        "LandSizeSqm": values.get("LandSizeSqm", np.nan),
        "FloorAreaMissing": int(pd.isna(floor_area)),
        "LandSizeMissing": int(pd.isna(values.get("LandSizeSqm", np.nan))),
        "SaleMonth": int(values["SaleMonth"]),
        "TotalRooms": bedrooms + float(values["Bathrooms"]),
        "AmenityCount": sum(values[c] == "Yes" for c in AMENITIES),
        "FloorAreaPerBedroom": floor_area / bedrooms if bedrooms > 0 and pd.notna(floor_area) else np.nan,
        "Suburb": values["Suburb"],
        "PropertyType": values["PropertyType"],
        **{c: values[c] for c in AMENITIES},
    }])


AMENITIES = ["Pool", "OpenPlan", "Balcony", "AirConditioning", "Study", "RenovatedUpdated", "WaterHarbourView"]
MONTHS = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

st.markdown('<div class="nav"><div class="brand">Sydney <span>HomeValue</span></div><div class="tag">ML-powered decision support</div></div>', unsafe_allow_html=True)
st.markdown(
    """<section class="hero"><div class="eyebrow">Sydney property intelligence</div>
    <h1>Your home starts here.</h1>
    <p>Explore an evidence-based sale-price estimate for properties in Parramatta, Newtown and Mosman—three distinct Sydney markets.</p>
    <span class="pill">108 verified sold listings</span><span class="pill">Random Forest model</span><span class="pill">Instant estimate</span></section>""",
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Estimate a property’s value</div><div class="section-copy">Enter the information available from the listing. Floor area and land size can be left blank.</div>', unsafe_allow_html=True)

with st.form("valuation_form"):
    a, b, c = st.columns(3)
    with a:
        suburb = st.selectbox("Suburb", ["Parramatta", "Newtown", "Mosman"])
        property_type = st.selectbox("Property type", ["Apartment", "Unit", "Studio", "Townhouse", "Terrace", "House", "Retirement Living"])
        sale_month = st.selectbox("Expected sale month", list(MONTHS), format_func=lambda x: MONTHS[x], index=8)
    with b:
        bedrooms = st.number_input("Bedrooms", 0, 10, 2)
        bathrooms = st.number_input("Bathrooms", 1, 8, 1)
        car_spaces = st.number_input("Car spaces", 0, 8, 1)
    with c:
        floor_area_text = st.text_input("Floor area (m², optional)", placeholder="e.g. 95")
        land_size_text = st.text_input("Land size (m², optional)", placeholder="e.g. 320")
        st.caption("Leave either field empty when the listing does not report it.")

    st.markdown("##### Property features")
    cols = st.columns(4)
    amenity_values = {}
    labels = {"Pool":"Swimming pool", "OpenPlan":"Open-plan living", "Balcony":"Balcony", "AirConditioning":"Air conditioning", "Study":"Study", "RenovatedUpdated":"Renovated/updated", "WaterHarbourView":"Water/harbour view"}
    for i, key in enumerate(AMENITIES):
        amenity_values[key] = yes_no(cols[i % 4].checkbox(labels[key]))
    submitted = st.form_submit_button("Calculate estimated sale price", use_container_width=True)

if submitted:
    try:
        floor_area = float(floor_area_text) if floor_area_text.strip() else np.nan
        land_size = float(land_size_text) if land_size_text.strip() else np.nan
        values = {"Suburb":suburb,"PropertyType":property_type,"SaleMonth":sale_month,"Bedrooms":bedrooms,"Bathrooms":bathrooms,"CarSpaces":car_spaces,"FloorAreaSqm":floor_area,"LandSizeSqm":land_size,**amenity_values}
        estimate = max(0, float(model.predict(make_row(values))[0]))
        lower, upper = max(0, estimate - TEST_RMSE), estimate + TEST_RMSE
        market_text = {
            "Parramatta":"a high-density metropolitan market where apartments and transport access dominate",
            "Newtown":"an inner-city lifestyle market with strong demand for terraces and character homes",
            "Mosman":"a premium harbour-side market where location, views and dwelling quality can create large price differences",
        }[suburb]
        st.markdown(f'<div class="result"><div class="result-label">Estimated sale price</div><div class="result-price">${estimate:,.0f}</div><div class="result-range">Indicative uncertainty band: ${lower:,.0f} – ${upper:,.0f}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight"><b>Market context:</b> This property belongs to {market_text}. The estimate should be checked against recent comparable sales.</div>', unsafe_allow_html=True)
    except ValueError:
        st.error("Please enter numeric values for floor area and land size, or leave them blank.")

st.markdown('<div class="section-title">Batch valuation</div><div class="section-copy">Upload multiple properties using the downloadable template.</div>', unsafe_allow_html=True)
template_values = {"Suburb":"Parramatta","PropertyType":"Apartment","SaleMonth":9,"Bedrooms":2,"Bathrooms":2,"CarSpaces":1,"FloorAreaSqm":95,"LandSizeSqm":np.nan,**{c:"No" for c in AMENITIES}}
template = pd.DataFrame([template_values])
st.download_button("Download CSV template", template.to_csv(index=False), "property_upload_template.csv", "text/csv")
uploaded = st.file_uploader("Upload completed CSV", type="csv")
if uploaded is not None:
    try:
        batch = pd.read_csv(uploaded)
        missing = [c for c in template.columns if c not in batch.columns]
        if missing:
            st.error("Missing columns: " + ", ".join(missing))
        else:
            predictions = []
            for _, record in batch.iterrows():
                predictions.append(max(0, float(model.predict(make_row(record.to_dict()))[0])))
            output = batch.copy(); output["EstimatedSalePriceAUD"] = np.round(predictions).astype(int)
            st.dataframe(output, use_container_width=True)
            st.download_button("Download predictions", output.to_csv(index=False), "sydney_property_predictions.csv", "text/csv")
    except Exception as exc:
        st.error(f"The file could not be processed: {exc}")

st.markdown('<div class="section-title">How the estimate is produced</div>', unsafe_allow_html=True)
x, y, z = st.columns(3)
x.markdown('<div class="feature-card"><div class="icon">📍</div><h4>Local market</h4><p>Suburb and property type capture major differences between Sydney housing segments.</p></div>', unsafe_allow_html=True)
y.markdown('<div class="feature-card"><div class="icon">🛋️</div><h4>Property characteristics</h4><p>Rooms, usable area, parking and listed amenities describe the property’s practical value.</p></div>', unsafe_allow_html=True)
z.markdown('<div class="feature-card"><div class="icon">📊</div><h4>Comparable patterns</h4><p>A Random Forest learns nonlinear relationships from 108 sold properties across the three suburbs.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Responsible use</div>', unsafe_allow_html=True)
st.markdown("""<div class="fineprint">This website is an educational decision-support prototype, not a professional valuation or financial recommendation. The held-out model performance was MAE ≈ A$316,376, RMSE ≈ A$737,523 and R² ≈ 0.604. Predictions may be unreliable for unusual, luxury or poorly documented properties. Important factors such as exact location, condition, renovation quality, views, noise, school catchments and market conditions are not fully captured. A licensed valuer and recent comparable sales should be consulted before making a financial decision.</div>""", unsafe_allow_html=True)

st.markdown("---")
st.caption("Sydney HomeValue · Machine Learning Mini Project · Data current to the collected sale period")
