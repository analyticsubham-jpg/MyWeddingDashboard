import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="My Wedding Expense Dashboard",
    page_icon="💍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CONSTANTS & BUDGETS
# -----------------------------------------------------------------------------
TOTAL_BUDGET = 853000

EXPECTED_BUDGETS = {
    "banquet": 35000,
    "catering": 400000,
    "decorator": 110000,
    "photography": 100000,
    "band_party": 46000,
    "makeup": 17000,
    "marriage_card": 5000,
    "vehicle": 40000,
    "pronami": 30000,
    "tattha": 30000,
    "shopping": 40000,
    "miscellaneous": 0
}

DEFAULT_DATA = {
    "banquet": {
        "name": "Sanai Bhawan",
        "contacts": "9046288819 / 9475807506",
        "total_fare": 25000,
        "electric_rate": 20,
        "diesel_rate_per_hr": 5,
        "advance_paid": 5000,
        "booking_date": "Jan 22, 2026",
        "facilities": ["200 Chairs", "25 Tables", "Music System", "2 rooms with Bed"],
        "electric_start_reading": 0,
        "electric_end_reading": 0,
        "diesel_hours": 0.0,
        "diesel_price_per_liter": 95,
        "settlement_payments": [],
        "extra_expenses": []
    },
    "catering": {
        "vendor": "Shanti Caterer",
        "contact": "7478714579 (Biman)",
        "per_plate_rate": 650,
        "booking_date": "Jan 29, 2026",
        "advance_paid": 2000,
        "number_of_plates": 0,
        "ashirwad_catering_expenses": [],
        "daily_food_expenses": []
    },
    "decorator": {
        "vendor": "Ishtikutuk",
        "contact": "9733431683",
        "contracted_total": 100000,
        "advance_paid": 10000,
        "max_budget": 110000,
        "extra_adjustments": []
    },
    "photography": {
        "vendor": "Bijit Photography",
        "contact": "8927482343",
        "wedding_gross": 145000,
        "groom_wedding_share": 70000,
        "bride_wedding_share": 75000,
        "subham_advance_paid": 42000,
        "pre_wedding_items": [],
        "wedding_extra_items": []
    },
    "band_party": {
        "vendor": "Bajna",
        "contact": "9734939796",
        "total": 46000,
        "advance_paid": 5000,
        "adjustments": []
    },
    "makeup": {
        "vendor": "Gaya Baidya",
        "contact": "7001418719",
        "total": 17000,
        "advance_paid": 3000,
        "adjustments": []
    },
    "marriage_card": {
        "per_card_price": 0,
        "total_cards": 0,
        "extra_cost": 0
    },
    "vehicle": {
        "expenses": []
    },
    "pronami": {
        "expenses": []
    },
    "tattha": {
        "patipatra": [],
        "ashirwad": []
    },
    "shopping": {
        "moumita": [],
        "father": [],
        "mother": [],
        "my_shopping": [],
        "briddhi": []
    },
    "miscellaneous": {
        "expenses": []
    }
}

# -----------------------------------------------------------------------------
# CLOUD PERSISTENCE
# -----------------------------------------------------------------------------
BIN_ID = st.secrets.get("JSONBIN_BIN_ID", "")
API_KEY = st.secrets.get("JSONBIN_API_KEY", "")

def load_data():
    if BIN_ID and API_KEY:
        try:
            url = f"https://api.jsonbin.io/v3/b/{BIN_ID}/latest"
            headers = {"X-Master-Key": API_KEY}
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                record = res.json().get("record", {})
                if record and "banquet" in record:
                    return record
        except Exception:
            pass
    return DEFAULT_DATA

def save_data(data):
    st.session_state.db = data
    if BIN_ID and API_KEY:
        try:
            url = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
            headers = {
                "Content-Type": "application/json",
                "X-Master-Key": API_KEY
            }
            requests.put(url, headers=headers, json=data)
        except Exception as e:
            st.error(f"Save failed: {e}")

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

def get_current_date():
    return datetime.now().strftime("%d-%b-%Y %H:%M")

# -----------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------
b_data = db.setdefault("banquet", DEFAULT_DATA["banquet"])
units_consumed = max(0, b_data.get("electric_end_reading", 0) - b_data.get("electric_start_reading", 0))
electric_cost = units_consumed * b_data.get("electric_rate", 20)
diesel_hours = float(b_data.get("diesel_hours", 0.0))
diesel_cost = diesel_hours * b_data.get("diesel_rate_per_hr", 5) * b_data.get("diesel_price_per_liter", 95)
banquet_calculated_total_cost = b_data.get("total_fare", 25000) + electric_cost + diesel_cost + sum(item["amount"] for item in b_data.get("extra_expenses", []))
banquet_additional_payments = sum(item["amount"] for item in b_data.get("settlement_payments", []))
banquet_total_paid = b_data.get("advance_paid", 5000) + banquet_additional_payments
banquet_pending_balance = max(0, banquet_calculated_total_cost - banquet_total_paid)
banquet_total_spend = banquet_total_paid

c_data = db.setdefault("catering", DEFAULT_DATA["catering"])
main_catering_total = c_data.get("number_of_plates", 0) * c_data.get("per_plate_rate", 650)
ashirwad_catering_total = sum(item["amount"] for item in c_data.setdefault("ashirwad_catering_expenses", []))
daily_food_total = sum(item["amount"] for item in c_data.setdefault("daily_food_expenses", []))
catering_total_spend = (c_data.get("advance_paid", 0) if c_data.get("number_of_plates", 0) == 0 else main_catering_total) + ashirwad_catering_total + daily_food_total

d_data = db.setdefault("decorator", DEFAULT_DATA["decorator"])
decorator_total_spend = d_data.get("advance_paid", 0) + sum(item["amount"] for item in d_data.setdefault("extra_adjustments", []))

p_data = db.setdefault("photography", DEFAULT_DATA["photography"])
pre_wedding_total = sum(item["amount"] for item in p_data.setdefault("pre_wedding_items", []))
wedding_extra_total = sum(item["amount"] for item in p_data.setdefault("wedding_extra_items", []))
shared_photo_extras = pre_wedding_total + wedding_extra_total
photography_gross_spend = p_data.get("subham_advance_paid", 0) + shared_photo_extras
groom_photo_share = p_data.get("groom_wedding_share", 70000) + (shared_photo_extras / 2.0)
bride_photo_share = p_data.get("bride_wedding_share", 75000) + (shared_photo_extras / 2.0)
photo_receivable_from_bride = bride_photo_share

bp_data = db.setdefault("band_party", DEFAULT_DATA["band_party"])
band_total_spend = bp_data.get("advance_paid", 0) + sum(item["amount"] for item in bp_data.setdefault("adjustments", []))

m_data = db.setdefault("makeup", DEFAULT_DATA["makeup"])
makeup_total_spend = m_data.get("advance_paid", 0) + sum(item["amount"] for item in m_data.setdefault("adjustments", []))

mc_data = db.setdefault("marriage_card", DEFAULT_DATA["marriage_card"])
card_total_spend = (mc_data.get("per_card_price", 0) * mc_data.get("total_cards", 0)) + mc_data.get("extra_cost", 0)

v_total_spend = sum(item["amount"] for item in db.setdefault("vehicle", {}).setdefault("expenses", []))
pr_total_spend = sum(item["amount"] for item in db.setdefault("pronami", {}).setdefault("expenses", []))
tattha_total_spend = sum(item["amount"] for item in db.setdefault("tattha", {}).setdefault("patipatra", [])) + sum(item["amount"] for item in db.setdefault("tattha", {}).setdefault("ashirwad", []))

s_data = db.setdefault("shopping", DEFAULT_DATA["shopping"])
shopping_total_spend = (
    sum(item["amount"] for item in s_data.setdefault("moumita", [])) +
    sum(item["amount"] for item in s_data.setdefault("father", [])) +
    sum(item["amount"] for item in s_data.setdefault("mother", [])) +
    sum(item["amount"] for item in s_data.setdefault("my_shopping", [])) +
    sum(item["amount"] for item in s_data.setdefault("briddhi", []))
)

misc_total_spend = sum(item["amount"] for item in db.setdefault("miscellaneous", {}).setdefault("expenses", []))

grand_actual_spend = (
    banquet_total_spend + catering_total_spend + decorator_total_spend + photography_gross_spend +
    band_total_spend + makeup_total_spend + card_total_spend + v_total_spend + pr_total_spend +
    tattha_total_spend + shopping_total_spend + misc_total_spend
)
remaining_budget = TOTAL_BUDGET - grand_actual_spend
total_advances_paid = (
    b_data.get("advance_paid", 0) + c_data.get("advance_paid", 0) + d_data.get("advance_paid", 0) +
    p_data.get("subham_advance_paid", 0) + bp_data.get("advance_paid", 0) + m_data.get("advance_paid", 0)
)

# -----------------------------------------------------------------------------
# MAIN UI
# -----------------------------------------------------------------------------
st.title("💍 My Wedding Expense Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Overall Budget", f"₹{TOTAL_BUDGET:,.2f}")
col2.metric("Total Actual Spent", f"₹{grand_actual_spend:,.2f}")
col3.metric("Remaining Budget", f"₹{remaining_budget:,.2f}", delta_color="normal" if remaining_budget >= 0 else "inverse")
col4.metric("Total Advances Paid", f"₹{total_advances_paid:,.2f}")

st.divider()

tabs = st.tabs([
    "📊 Overview", "1. Banquet Hall", "2. Catering", "3. Decorator",
    "4. Photography", "5. Band Party", "6. Makeup", "7. Marriage Card",
    "8. Vehicle", "9. Pronami", "10. Tattha", "11. Shopping", "12. Miscellaneous"
])

# TAB 0: OVERVIEW
with tabs[0]:
    st.subheader("Category Wise Breakdown")
    categories_data = [
        {"Category": "Banquet Hall", "Expected Budget (₹)": EXPECTED_BUDGETS["banquet"], "Actual Spend (₹)": banquet_total_spend},
        {"Category": "Catering", "Expected Budget (₹)": EXPECTED_BUDGETS["catering"], "Actual Spend (₹)": catering_total_spend},
        {"Category": "Decorator", "Expected Budget (₹)": EXPECTED_BUDGETS["decorator"], "Actual Spend (₹)": decorator_total_spend},
        {"Category": "Photography", "Expected Budget (₹)": EXPECTED_BUDGETS["photography"], "Actual Spend (₹)": photography_gross_spend},
        {"Category": "Band Party", "Expected Budget (₹)": EXPECTED_BUDGETS["band_party"], "Actual Spend (₹)": band_total_spend},
        {"Category": "Makeup", "Expected Budget (₹)": EXPECTED_BUDGETS["makeup"], "Actual Spend (₹)": makeup_total_spend},
        {"Category": "Marriage Card", "Expected Budget (₹)": EXPECTED_BUDGETS["marriage_card"], "Actual Spend (₹)": card_total_spend},
        {"Category": "Vehicle", "Expected Budget (₹)": EXPECTED_BUDGETS["vehicle"], "Actual Spend (₹)": v_total_spend},
        {"Category": "Pronami", "Expected Budget (₹)": EXPECTED_BUDGETS["pronami"], "Actual Spend (₹)": pr_total_spend},
        {"Category": "Tattha", "Expected Budget (₹)": EXPECTED_BUDGETS["tattha"], "Actual Spend (₹)": tattha_total_spend},
        {"Category": "Shopping", "Expected Budget (₹)": EXPECTED_BUDGETS["shopping"], "Actual Spend (₹)": shopping_total_spend},
        {"Category": "Miscellaneous (Others)", "Expected Budget (₹)": EXPECTED_BUDGETS["miscellaneous"], "Actual Spend (₹)": misc_total_spend},
    ]
    df = pd.DataFrame(categories_data)
    df["Spend %"] = df.apply(lambda r: (r["Actual Spend (₹)"] / (r["Expected Budget (₹)"] if r["Expected Budget (₹)"] > 0 else TOTAL_BUDGET)) * 100, axis=1)

    def highlight_overbudget(s):
        return ['color: red; font-weight: bold' if v > 100 else '' for v in s]

    styled_df = df.style.format({
        "Expected Budget (₹)": lambda x: f"₹{x:,.2f}",
        "Actual Spend (₹)": lambda x: f"₹{x:,.2f}",
        "Spend %": lambda x: f"{x:.1f}%"
    }).apply(highlight_overbudget, subset=["Spend %"])

    st.dataframe(styled_df, use_container_width=True)

# TAB 1: BANQUET
with tabs[1]:
    st.header("1. Banquet Hall - Sanai Bhawan")
    st.info(f"**Contact:** {b_data.get('contacts')} | **Advance:** ₹{b_data.get('advance_paid', 5000):,}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Meter & Fuel Readings")
        start_r = st.number_input("Electric Machine Start Reading", value=int(b_data.get("electric_start_reading", 0)), key="b_start_r")
        end_r = st.number_input("Electric Machine End Reading", value=int(b_data.get("electric_end_reading", 0)), key="b_end_r")
        hrs = st.number_input("Diesel Run Hours (5L/hr)", value=float(b_data.get("diesel_hours", 0.0)), key="b_diesel_hrs")
        if st.button("Save Readings", key="btn_save_readings"):
            b_data["electric_start_reading"] = start_r
            b_data["electric_end_reading"] = end_r
            b_data["diesel_hours"] = hrs
            save_data(db)
            st.rerun()
    with c2:
        st.subheader("Financial Status")
        st.write(f"**Base Fare:** ₹25,000 | **Electricity:** ₹{electric_cost:,} | **Diesel:** ₹{diesel_cost:,}")
        st.write(f"**Total Cost:** ₹{banquet_calculated_total_cost:,} | **Paid So Far:** ₹{banquet_total_paid:,}")
        st.write(f"**Pending Balance Due:** ₹{banquet_pending_balance:,}")

    st.subheader("Record Payment to Vendor")
    bp_desc = st.text_input("Payment Description", key="b_pay_desc")
    bp_amt = st.number_input("Amount Paid", key="b_pay_amt", value=0.0)
    if st.button("Save Payment", key="btn_save_banquet_payment"):
        if bp_desc and bp_amt > 0:
            b_data.setdefault("settlement_payments", []).append({"desc": bp_desc, "amount": bp_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in b_data.get("settlement_payments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 2: CATERING
with tabs[2]:
    st.header("2. Catering - Shanti Caterer")
    st.info(f"**Contact:** {c_data.get('contact')} | **Rate:** ₹650/plate")
    plates = st.number_input("Total Number of Plates", value=int(c_data.get("number_of_plates", 0)), step=1, key="c_plates_input")
    if st.button("Update Plates Count", key="btn_update_plates"):
        c_data["number_of_plates"] = plates
        save_data(db)
        st.rerun()
    st.subheader(f"Main Catering: ₹{main_catering_total:,}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ashirwad Catering")
        ash_desc = st.text_input("Ashirwad Description", key="c_ash_desc")
        ash_amt = st.number_input("Amount", key="c_ash_amt", value=0.0)
        if st.button("Add/Deduct Ashirwad", key="btn_c_ash"):
            if ash_desc and ash_amt != 0:
                c_data.setdefault("ashirwad_catering_expenses", []).append({"desc": ash_desc, "amount": ash_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in c_data.get("ashirwad_catering_expenses", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
    with c2:
        st.subheader("Daily Food")
        df_desc = st.text_input("Daily Food Description", key="c_df_desc")
        df_amt = st.number_input("Amount", key="c_df_amt", value=0.0)
        if st.button("Add/Deduct Daily Food", key="btn_c_df"):
            if df_desc and df_amt != 0:
                c_data.setdefault("daily_food_expenses", []).append({"desc": df_desc, "amount": df_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in c_data.get("daily_food_expenses", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 3: DECORATOR
with tabs[3]:
    st.header("3. Decorator - Ishtikutuk")
    st.info(f"**Contracted Total:** ₹1,00,000 | **Advance Paid:** ₹10,000")
    dec_desc = st.text_input("Adjustment Description", key="dec_desc")
    dec_amt = st.number_input("Amount", key="dec_amt", value=0.0)
    if st.button("Save Decorator Adjustment", key="btn_save_decorator"):
        if dec_desc and dec_amt != 0:
            d_data.setdefault("extra_adjustments", []).append({"desc": dec_desc, "amount": dec_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in d_data.get("extra_adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 4: PHOTOGRAPHY
with tabs[4]:
    st.header("4. Photography - Bijit Photography")
    st.write(f"**Subham Share:** ₹{groom_photo_share:,.2f} | **Bride Share:** ₹{bride_photo_share:,.2f} | **Advance Paid by Subham:** ₹42,000")
    st.warning(f"**Receivable from Bride Side:** ₹{photo_receivable_from_bride:,.2f}")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Pre-Wedding Items")
        pw_desc = st.text_input("Pre-Wedding Description", key="p_pw_desc")
        pw_amt = st.number_input("Amount", key="p_pw_amt", value=0.0)
        if st.button("Add Pre-Wedding", key="btn_add_pw"):
            if pw_desc and pw_amt != 0:
                p_data.setdefault("pre_wedding_items", []).append({"desc": pw_desc, "amount": pw_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in p_data.get("pre_wedding_items", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
    with c2:
        st.subheader("Wedding Extra Items")
        we_desc = st.text_input("Extra Description", key="p_we_desc")
        we_amt = st.number_input("Amount", key="p_we_amt", value=0.0)
        if st.button("Add Wedding Extra", key="btn_add_we"):
            if we_desc and we_amt != 0:
                p_data.setdefault("wedding_extra_items", []).append({"desc": we_desc, "amount": we_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in p_data.get("wedding_extra_items", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 5: BAND PARTY
with tabs[5]:
    st.header("5. Band Party - Bajna")
    st.info("**Contracted Total:** ₹46,000 | **Advance Paid:** ₹5,000")
    b_desc = st.text_input("Adjustment Description", key="bp_adj_desc")
    b_amt = st.number_input("Amount", key="bp_adj_amt", value=0.0)
    if st.button("Save Band Adjustment", key="btn_save_band"):
        if b_desc and b_amt != 0:
            bp_data.setdefault("adjustments", []).append({"desc": b_desc, "amount": b_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in bp_data.get("adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 6: MAKEUP
with tabs[6]:
    st.header("6. Makeup - Gaya Baidya")
    st.info("**Contracted Total:** ₹17,000 | **Advance Paid:** ₹3,000")
    m_desc = st.text_input("Adjustment Description", key="mk_adj_desc")
    m_amt = st.number_input("Amount", key="mk_adj_amt", value=0.0)
    if st.button("Save Makeup Adjustment", key="btn_save_makeup"):
        if m_desc and m_amt != 0:
            m_data.setdefault("adjustments", []).append({"desc": m_desc, "amount": m_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in m_data.get("adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 7: MARRIAGE CARD
with tabs[7]:
    st.header("7. Marriage Card")
    c_rate = st.number_input("Rate per Card (₹)", value=float(mc_data.get("per_card_price", 0)), key="mc_rate")
    c_count = st.number_input("Card Count", value=int(mc_data.get("total_cards", 0)), step=1, key="mc_count")
    c_extra = st.number_input("Extra Charges (₹)", value=float(mc_data.get("extra_cost", 0)), key="mc_extra")
    if st.button("Save Card Details", key="btn_save_card"):
        mc_data["per_card_price"] = c_rate
        mc_data["total_cards"] = c_count
        mc_data["extra_cost"] = c_extra
        save_data(db)
        st.rerun()
    st.subheader(f"Total Card Expense: ₹{card_total_spend:,}")

# TAB 8: VEHICLE
with tabs[8]:
    st.header("8. Vehicle")
    v_desc = st.text_input("Vehicle Expense Description", key="vh_desc")
    v_amt = st.number_input("Amount", key="vh_amt", value=0.0)
    if st.button("Add/Deduct Vehicle Expense", key="btn_save_vehicle"):
        if v_desc and v_amt != 0:
            db["vehicle"].setdefault("expenses", []).append({"desc": v_desc, "amount": v_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in db["vehicle"].get("expenses", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 9: PRONAMI
with tabs[9]:
    st.header("9. Pronami")
    pr_desc = st.text_input("Pronami Description", key="pr_item_desc")
    pr_amt = st.number_input("Amount", key="pr_item_amt", value=0.0)
    if st.button("Add/Deduct Pronami", key="btn_save_pronami"):
        if pr_desc and pr_amt != 0:
            db["pronami"].setdefault("expenses", []).append({"desc": pr_desc, "amount": pr_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in db["pronami"].get("expenses", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 10: TATTHA
with tabs[10]:
    st.header("10. Tattha")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Patipatra Tattha")
        p_desc = st.text_input("Item Description", key="t_pati_desc")
        p_amt = st.number_input("Amount", key="t_pati_amt", value=0.0)
        if st.button("Add/Deduct Patipatra", key="btn_save_t_patipatra"):
            if p_desc and p_amt != 0:
                db["tattha"].setdefault("patipatra", []).append({"desc": p_desc, "amount": p_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in db["tattha"].get("patipatra", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
    with c2:
        st.subheader("2. Ashirwad Tattha")
        a_desc = st.text_input("Item Description", key="t_ash_desc")
        a_amt = st.number_input("Amount", key="t_ash_amt", value=0.0)
        if st.button("Add/Deduct Ashirwad", key="btn_save_t_ashirwad"):
            if a_desc and a_amt != 0:
                db["tattha"].setdefault("ashirwad", []).append({"desc": a_desc, "amount": a_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in db["tattha"].get("ashirwad", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 11: SHOPPING
with tabs[11]:
    st.header("11. Shopping")
    shop_sec = st.selectbox("Category", ["moumita", "father", "mother", "my_shopping", "briddhi"], format_func=lambda x: {"moumita": "Moumita Shopping", "father": "Father Shopping", "mother": "Mother Shopping", "my_shopping": "My Shopping", "briddhi": "Briddhi Shopping"}[x], key="s_cat_select")
    s_desc = st.text_input("Item Description", key="s_item_desc")
    s_amt = st.number_input("Amount", key="s_item_amt", value=0.0)
    if st.button("Save Shopping", key="btn_save_shopping"):
        if s_desc and s_amt != 0:
            db["shopping"].setdefault(shop_sec, []).append({"desc": s_desc, "amount": s_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in db["shopping"].get(shop_sec, []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# TAB 12: MISCELLANEOUS
with tabs[12]:
    st.header("12. Miscellaneous")
    misc_desc = st.text_input("Expense Description", key="misc_item_desc")
    misc_amt = st.number_input("Amount", key="misc_item_amt", value=0.0)
    if st.button("Save Miscellaneous", key="btn_save_misc"):
        if misc_desc and misc_amt != 0:
            db["miscellaneous"].setdefault("expenses", []).append({"desc": misc_desc, "amount": misc_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
    for item in db["miscellaneous"].get("expenses", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
