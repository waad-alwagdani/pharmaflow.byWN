# PharmaFlow by WaadAlwagdani
# © 2026 Waad Alwagdani, PharmD (وعد الوقداني) · waadnalwagdani@gmail.com
# All rights reserved. Not to be copied, reused or redistributed without written permission.

"""PharmaFlow dashboard.  Run from the project root:  streamlit run dashboard/app.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import altair as alt
import pandas as pd
import streamlit as st

from pharmaflow import load_clean, metrics

VIOLET, GREEN, AMBER, RED, INK, INK2, INK3, HAIR = "#6b4fe0", "#1e9e6e", "#c58a0b", "#c8443a", "#16131f", "#575366", "#9893a8", "#ebe8f2"
FONTS = "https://fonts.googleapis.com/css2?family=Readex+Pro:wght@200;300;400;500&family=IBM+Plex+Sans+Arabic:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap"

st.set_page_config(page_title="PharmaFlow by WaadAlwagdani", page_icon="📦", layout="wide",
                   menu_items={"About": "PharmaFlow by WaadAlwagdani · © 2026 Waad Alwagdani, PharmD. All rights reserved."})
st.html(f"""<style>
@import url("{FONTS}");
/* PharmaFlow by WaadAlwagdani */
.stApp,.stApp p,.stApp label,.stApp input,.stApp li,.stApp td,.stApp th,[data-testid="stMarkdownContainer"],.pf-bar,.pf-hero,.pf-kpis,.pf-foot,.pf-insight{{font-family:"IBM Plex Sans Arabic",system-ui,-apple-system,"Segoe UI",sans-serif}}
.stApp{{background:#fff}} header[data-testid="stHeader"]{{background:transparent}}
.block-container{{max-width:1240px;padding-top:1.4rem}}
.pf-bar{{display:flex;justify-content:space-between;align-items:center;padding-bottom:14px;border-bottom:1px solid {HAIR};margin-bottom:26px;font-size:12px;color:{INK3}}}
.pf-mark{{font-family:"Readex Pro",system-ui,sans-serif;font-weight:500;font-size:15px;color:{INK}}} .pf-mark span{{color:{INK3};font-weight:300}}
.pf-mark small{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:10.5px;color:{VIOLET};margin-left:8px}}
.pf-hero h1{{font-family:"Readex Pro",system-ui,sans-serif!important;font-weight:300!important;font-size:clamp(30px,4.4vw,50px)!important;line-height:1.12!important;margin:0 0 8px;padding:0;color:{INK}}}
.pf-hero h1 em{{font-style:normal;color:{VIOLET}}} .pf-hero p{{color:{INK2};max-width:72ch;margin:0 0 22px}}
.pf-kpis{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border:1px solid {HAIR};border-radius:14px;overflow:hidden;margin-bottom:22px}}
@media(max-width:800px){{.pf-kpis{{grid-template-columns:repeat(2,1fr)}}}}
.pf-k{{padding:16px 20px;border-right:1px solid {HAIR};background:#fcfbfe}} .pf-k:last-child{{border-right:0}}
.pf-k span{{display:block;font-size:11.5px;color:{INK3}}} .pf-k b{{font-family:"Readex Pro",system-ui,sans-serif;font-weight:300;font-size:30px;color:{INK};letter-spacing:-.02em}}
.pf-k small{{display:block;font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:10.5px;color:{INK2}}} .pf-k.v b{{color:{VIOLET}}} .pf-k.g b{{color:{GREEN}}}
.pf-insight{{padding:14px 16px;border-radius:10px;background:#f1edff;color:#2b2266;font-size:13px;line-height:1.8;margin:4px 0 8px}}
.pf-insight b{{color:{VIOLET}}}
h3{{font-family:"Readex Pro",system-ui,sans-serif!important;font-weight:400!important;font-size:17px!important;color:{INK}!important}}
[data-testid="stWidgetLabel"] p{{font-size:12px!important;color:{INK2}!important;font-weight:500!important}}
section[data-testid="stSidebar"]{{background:#f7f5fc;border-right:1px solid {HAIR}}}
.react-aria-ComboBox>div,div[data-baseweb="select"]>div{{background:#fff!important;border-radius:9px!important;border-color:#dcd8e8!important}}
.pf-foot{{margin-top:34px;padding-top:16px;border-top:1px solid {HAIR};display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px 30px;font-size:11.5px;color:{INK3}}}
.pf-foot b{{font-family:"Readex Pro",system-ui,sans-serif;font-weight:500;font-size:14px;color:{INK};display:block}} .pf-foot span{{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;color:{VIOLET}}}
</style>""")


@st.cache_data
def data() -> pd.DataFrame:
    return load_clean()


df_all = data()

# ---------------- filters ----------------
with st.sidebar:
    st.markdown("### Filters")
    years = st.slider("Scheduled year", int(df_all.year.min()), int(df_all.year.max()), (int(df_all.year.min()), int(df_all.year.max())))
    products = st.multiselect("Product group", sorted(df_all.product_name.unique()), default=[])
    modes = st.multiselect("Shipment mode", sorted(df_all.shipment_mode.unique()), default=[])
    fulfil = st.multiselect("Fulfilled via", sorted(df_all.fulfill_via.unique()), default=[])
    countries = st.multiselect("Country", df_all.country.value_counts().index.tolist(), default=[])
    st.caption("Empty filter = all values.")

df = df_all[df_all.year.between(*years)]
for col, sel in [("product_name", products), ("shipment_mode", modes), ("fulfill_via", fulfil), ("country", countries)]:
    if sel:
        df = df[df[col].isin(sel)]

st.html(f"""<div class="pf-bar"><div class="pf-mark">Pharma<span>Flow</span><small>by WaadAlwagdani</small></div>
<div>USAID SCMS delivery history · 2006–2015</div></div>
<div class="pf-hero"><h1>Global medicine shipments,<br><em>delivery and cost</em></h1>
<p>Delivery performance, lead time and freight cost across 10,324 shipment lines of antiretrovirals and HIV and malaria test kits to 43 countries.</p></div>""")

if df.empty:
    st.warning("No shipments match these filters.")
    st.stop()

k = metrics.kpis(df)
st.html(f"""<div class="pf-kpis">
<div class="pf-k"><span>Shipment lines</span><b>{k['shipments']:,}</b><small>{k['countries']} countries · {k['vendors']} vendors</small></div>
<div class="pf-k v"><span>Commodity value</span><b>${k['value_usd'] / 1e6:,.0f}M</b><small>freight ${k['freight_usd'] / 1e6:,.1f}M recorded</small></div>
<div class="pf-k g"><span>On-time delivery</span><b>{k['on_time_rate']:.1f}%</b><small>median {k['median_delay_when_late']:.0f} days late when late</small></div>
<div class="pf-k"><span>PO → delivery lead time</span><b>{k['median_lead_time']:.0f} d</b><small>median freight {k['freight_pct_median']:.1f}% of value</small></div></div>""")

@alt.theme.register("pf", enable=True)
def _pf_theme():
    return {"config": {
    "view": {"stroke": None}, "font": "IBM Plex Sans Arabic, -apple-system, Segoe UI, Helvetica, Arial, sans-serif",
    "axis": {"labelColor": INK3, "titleColor": INK2, "gridColor": HAIR, "domainColor": HAIR, "tickColor": HAIR, "labelFontSize": 11, "titleFontWeight": 400},
    "legend": {"labelColor": INK2, "titleColor": INK2}, "title": {"color": INK, "fontWeight": 400, "anchor": "start", "fontSize": 14}}}

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("### On-time rate by year")
    y = metrics.yearly(df).reset_index()
    line = alt.Chart(y).mark_line(color=VIOLET, strokeWidth=2.5, point=alt.OverlayMarkDef(color=VIOLET, size=50)).encode(
        x=alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("on_time_rate:Q", title="% on time", scale=alt.Scale(domain=[max(0, y.on_time_rate.min() - 10), 100])),
        tooltip=[alt.Tooltip("year:O"), alt.Tooltip("shipments:Q", format=","), alt.Tooltip("on_time_rate:Q", format=".1f", title="on time %")])
    st.altair_chart(line.properties(height=300), width="stretch")
with c2:
    st.markdown("### How late are shipments?")
    b = metrics.delay_buckets(df).rename_axis("bucket").reset_index(name="shipments")
    b["share"] = b.shipments / b.shipments.sum()
    st.altair_chart(alt.Chart(b).mark_bar(cornerRadiusEnd=3).encode(
        y=alt.Y("bucket:N", sort=list(b.bucket), title=None, axis=alt.Axis(labelLimit=200, minExtent=110)),
        x=alt.X("shipments:Q", title="Shipments"),
        color=alt.Color("bucket:N", scale=alt.Scale(domain=list(b.bucket), range=[GREEN, GREEN, AMBER, AMBER, RED]), legend=None),
        tooltip=["bucket", alt.Tooltip("shipments:Q", format=","), alt.Tooltip("share:Q", format=".1%")]).properties(height=300), width="stretch")

c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown("### Shipment mode: cost per kg vs punctuality")
    m = metrics.mode_cost_comparison(df).reset_index()
    if len(m):
        base = alt.Chart(m).encode(x=alt.X("median_freight_per_kg:Q", title="Median freight USD / kg"),
                                   y=alt.Y("on_time_rate:Q", title="% on time", scale=alt.Scale(zero=False)))
        pts = base.mark_circle(color=VIOLET, opacity=.85).encode(size=alt.Size("shipments:Q", legend=None, scale=alt.Scale(range=[150, 1600])),
                                                                 tooltip=["shipment_mode", alt.Tooltip("shipments:Q", format=","),
                                                                          alt.Tooltip("median_freight_per_kg:Q", format=".2f"), alt.Tooltip("on_time_rate:Q", format=".1f")])
        lbl = base.mark_text(dy=-22, color=INK2, fontSize=12).encode(text="shipment_mode")
        st.altair_chart(pts + lbl, width="stretch")
with c4:
    st.markdown("### Direct drop vs regional distribution centre")
    f = metrics.by(df, "fulfill_via").reset_index()
    st.altair_chart(alt.Chart(f).mark_bar(cornerRadiusEnd=3, size=34).encode(
        y=alt.Y("fulfill_via:N", title=None, axis=alt.Axis(labelLimit=200, minExtent=95)), x=alt.X("on_time_rate:Q", title="% on time", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color("fulfill_via:N", scale=alt.Scale(range=[VIOLET, GREEN]), legend=None),
        tooltip=["fulfill_via", alt.Tooltip("shipments:Q", format=","), alt.Tooltip("on_time_rate:Q", format=".1f"),
                 alt.Tooltip("median_freight_pct:Q", format=".1f", title="freight % of value")]).properties(height=170),
        width="stretch")
    if len(f) == 2:
        rdc, direct = f.set_index("fulfill_via").loc[["From RDC", "Direct Drop"], "on_time_rate"]
        st.html(f'<div class="pf-insight">Direct drop from the manufacturer was on time <b>{direct:.1f}%</b> of the time, '
                f'against <b>{rdc:.1f}%</b> for shipments through regional distribution centres.</div>')

st.markdown("### Countries")
cty = metrics.by(df, "country", 20).reset_index()
st.altair_chart(alt.Chart(cty.head(20)).mark_bar(cornerRadiusEnd=3).encode(
    x=alt.X("value_usd:Q", title="Commodity value (USD)", axis=alt.Axis(format="$.2s")),
    y=alt.Y("country:N", sort="-x", title=None, axis=alt.Axis(labelLimit=220, minExtent=120, labelOverlap=False)),
    color=alt.Color("on_time_rate:Q", title="% on time", scale=alt.Scale(domain=[60, 100], range=[RED, "#f5e9c8", GREEN])),
    tooltip=["country", alt.Tooltip("shipments:Q", format=","), alt.Tooltip("value_usd:Q", format="$,.0f"),
             alt.Tooltip("on_time_rate:Q", format=".1f"), alt.Tooltip("mean_delay_days:Q", format=".1f")]).properties(height=560),
    width="stretch")

st.markdown("### Vendor scorecard")
minv = st.slider("Minimum shipments per vendor", 10, 300, 50, step=10)
sc = metrics.vendor_scorecard(df, minv)[["shipments", "value_share_pct", "on_time_rate", "mean_delay_days", "late_p90_days", "median_lead_time"]]
st.dataframe(sc, column_config={
    "shipments": st.column_config.NumberColumn("Shipments", format="%d"),
    "value_share_pct": st.column_config.ProgressColumn("Value share", format="%.1f%%", min_value=0, max_value=100),
    "on_time_rate": st.column_config.ProgressColumn("On time", format="%.1f%%", min_value=0, max_value=100),
    "mean_delay_days": st.column_config.NumberColumn("Mean delay (d)", format="%.1f"),
    "late_p90_days": st.column_config.NumberColumn("P90 delay (d)", format="%.0f"),
    "median_lead_time": st.column_config.NumberColumn("Lead time (d)", format="%.0f")})

st.markdown("### ARV price trend")
mol = st.selectbox("Molecule", ["Efavirenz/Lamivudine/Tenofovir", "Lamivudine/Zidovudine", "Lamivudine/Nevirapine/Zidovudine", "Nevirapine", "Efavirenz"])
pt = metrics.price_trend(df, mol).reset_index()
if len(pt):
    st.altair_chart(alt.Chart(pt).mark_line(color=GREEN, strokeWidth=2.5, point=alt.OverlayMarkDef(color=GREEN, size=50)).encode(
        x=alt.X("year:O", title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("median_pack_price:Q", title="Median USD per pack", scale=alt.Scale(zero=False)),
        tooltip=["year", alt.Tooltip("median_pack_price:Q", format="$.2f"), "count"]).properties(height=260), width="stretch")
else:
    st.info("No shipments of this molecule in the current filter.")

st.download_button("Download filtered data (CSV)", df.to_csv(index=False).encode(), "pharmaflow_filtered.csv", "text/csv", type="primary")

st.html(f"""<div class="pf-foot"><div><b>PharmaFlow by WaadAlwagdani</b><span>Waad Alwagdani, PharmD · وعد الوقداني</span></div>
<div>Data: USAID Supply Chain Management System delivery history (public domain).<br>
© 2026 Waad Alwagdani. All rights reserved. Not to be copied, reused or redistributed without written permission.</div></div>""")
