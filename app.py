import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="My Wedding Expense Dashboard",
    page_icon="💍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CONSTANTS & INITIAL DATA STRUCTURE
# -----------------------------------------------------------------------------
TOTAL_BUDGET = 833000

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
        "diesel_hours": 0,
        "diesel_price_per_liter": 95,
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

DATA_FILE = "wedding_data.json"

# -----------------------------------------------------------------------------
# PERSISTENCE HELPERS
# -----------------------------------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                loaded_data = json.load(f)
                return loaded_data
        except Exception:
            pass
    return DEFAULT_DATA

def save_data(data):
    st.session_state.db = data
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# Ensure missing keys exist in active session database dynamically
if "tattha" not in db:
    db["tattha"] = {"patipatra": [], "ashirwad": []}
if "catering" in db and "ashirwad_catering_expenses" not in db["catering"]:
    db["catering"]["ashirwad_catering_expenses"] = []
if "miscellaneous" not in db:
    db["miscellaneous"] = {"expenses": []}

def get_current_date():
    return datetime.now().strftime("%d-%b-%Y %H:%M")

# -----------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------
# 1. Banquet
b_data = db["banquet"]
units_consumed = max(0, b_data.get("electric_end_reading", 0) - b_data.get("electric_start_reading", 0))
electric_cost = units_consumed * b_data.get("electric_rate", 20)
diesel_cost = b_data.get("diesel_hours", 0) * b_data.get("diesel_rate_per_hr", 5) * b_data.get("diesel_price_per_liter", 95)
banquet_extra = sum(item["amount"] for item in b_data.get("extra_expenses", []))
banquet_total_spend = b_data.get("advance_paid", 0) + electric_cost + diesel_cost + banquet_extra

# 2. Catering
c_data = db["catering"]
main_catering_total = c_data.get("number_of_plates", 0) * c_data.get("per_plate_rate", 650)
ashirwad_catering_expenses = c_data.setdefault("ashirwad_catering_expenses", [])
ashirwad_catering_total = sum(item["amount"] for item in ashirwad_catering_expenses)
daily_food_expenses = c_data.setdefault("daily_food_expenses", [])
daily_food_total = sum(item["amount"] for item in daily_food_expenses)
catering_total_spend = (c_data.get("advance_paid", 0) if c_data.get("number_of_plates", 0) == 0 else main_catering_total) + ashirwad_catering_total + daily_food_total

# 3. Decorator
d_data = db["decorator"]
decorator_extra = sum(item["amount"] for item in d_data.get("extra_adjustments", []))
decorator_total_spend = d_data.get("advance_paid", 0) + decorator_extra

# 4. Photography
p_data = db["photography"]
pre_wedding_total = sum(item["amount"] for item in p_data.get("pre_wedding_items", []))
wedding_extra_total = sum(item["amount"] for item in p_data.get("wedding_extra_items", []))
shared_photo_extras = pre_wedding_total + wedding_extra_total
photography_gross_spend = p_data.get("subham_advance_paid", 0) + shared_photo_extras

groom_photo_share = p_data.get("groom_wedding_share", 70000) + (shared_photo_extras / 2.0)
bride_photo_share = p_data.get("bride_wedding_share", 75000) + (shared_photo_extras / 2.0)
photo_receivable_from_bride = bride_photo_share

# 5. Band Party
bp_data = db["band_party"]
band_total_spend = bp_data.get("advance_paid", 0) + sum(item["amount"] for item in bp_data.get("adjustments", []))

# 6. Makeup
m_data = db["makeup"]
makeup_total_spend = m_data.get("advance_paid", 0) + sum(item["amount"] for item in m_data.get("adjustments", []))

# 7. Marriage Card
mc_data = db["marriage_card"]
card_total_spend = (mc_data.get("per_card_price", 0) * mc_data.get("total_cards", 0)) + mc_data.get("extra_cost", 0)

# 8. Vehicle
v_total_spend = sum(item["amount"] for item in db["vehicle"].get("expenses", []))

# 9. Pronami
pr_total_spend = sum(item["amount"] for item in db["pronami"].get("expenses", []))

# 10. Tattha
t_patipatra = sum(item["amount"] for item in db["tattha"].get("patipatra", []))
t_ashirwad = sum(item["amount"] for item in db["tattha"].get("ashirwad", []))
tattha_total_spend = t_patipatra + t_ashirwad

# 11. Shopping
s_moumita = sum(item["amount"] for item in db["shopping"].get("moumita", []))
s_father = sum(item["amount"] for item in db["shopping"].get("father", []))
s_mother = sum(item["amount"] for item in db["shopping"].get("mother", []))
s_my = sum(item["amount"] for item in db["shopping"].get("my_shopping", []))
s_briddhi = sum(item["amount"] for item in db["shopping"].get("briddhi", []))
shopping_total_spend = s_moumita + s_father + s_mother + s_my + s_briddhi

# 12. Miscellaneous (Others)
misc_total_spend = sum(item["amount"] for item in db.setdefault("miscellaneous", {}).get("expenses", []))

# Grand Totals
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
st.title("💍 My Wedding Expense & Status Dashboard")
st.caption("Real-time updates, date-stamped activity logging & mobile ready")

# KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Overall Budget", f"₹{TOTAL_BUDGET:,.2f}")
col2.metric("Total Actual Spent", f"₹{grand_actual_spend:,.2f}")
col3.metric("Remaining Budget", f"₹{remaining_budget:,.2f}", delta_color="normal" if remaining_budget >= 0 else "inverse")
col4.metric("Total Advances Paid", f"₹{total_advances_paid:,.2f}")

st.divider()

# TAB NAVIGATION FOR ALL PARAMETERS
tabs = st.tabs([
    "📊 Overview",
    "1. Banquet Hall",
    "2. Catering",
    "3. Decorator",
    "4. Photography",
    "5. Band Party",
    "6. Makeup",
    "7. Marriage Card",
    "8. Vehicle",
    "9. Pronami",
    "10. Tattha",
    "11. Shopping",
    "12. Miscellaneous"
])

# -----------------------------------------------------------------------------
# TAB 0: OVERVIEW
# -----------------------------------------------------------------------------
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
    
    def calc_pct(row):
        ref = row["Expected Budget (₹)"] if row["Expected Budget (₹)"] > 0 else TOTAL_BUDGET
        return (row["Actual Spend (₹)"] / ref) * 100 if ref > 0 else 0.0

    df["Spend %"] = df.apply(calc_pct, axis=1)

    def style_dataframe(df):
        def highlight_overbudget(s):
            return ['color: red; font-weight: bold' if v > 100 else '' for v in s]
        
        return df.style.format({
            "Expected Budget (₹)": lambda x: f"₹{x:,.2f}",
            "Actual Spend (₹)": lambda x: f"₹{x:,.2f}",
            "Spend %": lambda x: f"{x:.1f}%"
        }).apply(highlight_overbudget, subset=["Spend %"])

    st.dataframe(
        style_dataframe(df),
        use_container_width=True,
        column_config={
            "Category": st.column_config.Column(alignment="center"),
            "Expected Budget (₹)": st.column_config.Column(alignment="center"),
            "Actual Spend (₹)": st.column_config.Column(alignment="center"),
            "Spend %": st.column_config.Column(alignment="center"),
        }
    )

# -----------------------------------------------------------------------------
# TAB 1: BANQUET HALL
# -----------------------------------------------------------------------------
with tabs[1]:
    st.header("1. Banquet Hall - Sanai Bhawan")
    st.info(f"**Contact:** {b_data.get('contacts','')} | **Booked:** {b_data.get('booking_date','')} | **Advance Paid:** ₹{b_data.get('advance_paid',0):,}")
    st.markdown("**Facilities:** " + ", ".join(b_data.get("facilities", [])))
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Meter & Fuel Readings")
        start_r = st.number_input("Electric Machine Start Reading", value=int(b_data.get("electric_start_reading", 0)))
        end_r = st.number_input("Electric Machine End Reading", value=int(b_data.get("electric_end_reading", 0)))
        hrs = st.number_input("Diesel Run Hours (5L/hr)", value=float(b_data.get("diesel_hours", 0)))
        
        if st.button("Save Readings"):
            b_data["electric_start_reading"] = start_r
            b_data["electric_end_reading"] = end_r
            b_data["diesel_hours"] = hrs
            save_data(db)
            st.success("Readings Updated!")
            st.rerun()

    with c2:
        st.subheader("Financial Status")
        st.write(f"**Base Fare:** ₹{b_data.get('total_fare',0):,}")
        st.write(f"**Electricity ({units_consumed} units @ ₹20/unit):** ₹{electric_cost:,}")
        st.write(f"**Diesel ({hrs} hrs @ 5L/hr):** ₹{diesel_cost:,}")
        st.write(f"**Actual Spend So Far:** ₹{banquet_total_spend:,}")
        st.write(f"**Expected Budget:** ₹{EXPECTED_BUDGETS['banquet']:,}")

# -----------------------------------------------------------------------------
# TAB 2: CATERING
# -----------------------------------------------------------------------------
with tabs[2]:
    st.header("2. Catering - Shanti Caterer")
    st.info(f"**Contact:** {c_data.get('contact','')} | **Rate:** ₹{c_data.get('per_plate_rate',650)}/plate | **Advance:** ₹{c_data.get('advance_paid',0):,}")
    
    plates = st.number_input("Total Number of Plates", value=int(c_data.get("number_of_plates", 0)), step=1)
    if st.button("Update Plate Count"):
        c_data["number_of_plates"] = plates
        save_data(db)
        st.success("Plates count saved!")
        st.rerun()
        
    st.subheader(f"Main Catering Total (Plates × ₹650): ₹{main_catering_total:,}")
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Ashirwad Catering Sub-section")
        ash_desc = st.text_input("Ashirwad Food / Item Description", key="ash_desc")
        ash_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="ash_amt", value=0.0)
        
        if st.button("Add/Deduct Ashirwad Expense"):
            if ash_desc and ash_amt != 0:
                c_data.setdefault("ashirwad_catering_expenses", []).append({"desc": ash_desc, "amount": ash_amt, "date": get_current_date()})
                save_data(db)
                st.success("Ashirwad entry updated!")
                st.rerun()
                
        st.write(f"**Total Ashirwad Catering Expense:** ₹{ashirwad_catering_total:,}")
        st.markdown("---")
        st.write("**Ashirwad Transaction Log:**")
        if not ashirwad_catering_expenses:
            st.caption("No items added yet.")
        for item in ashirwad_catering_expenses:
            st.write(f"- [{item.get('date', 'N/A')}] **{item['desc']}**: ₹{item['amount']:,}")

    with col_b:
        st.subheader("Marriage Daily Food Expenses")
        d_desc = st.text_input("Food Item / Day Description", key="df_desc")
        d_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="df_amt", value=0.0)
        
        if st.button("Add/Deduct Daily Food Expense"):
            if d_desc and d_amt != 0:
                c_data.setdefault("daily_food_expenses", []).append({"desc": d_desc, "amount": d_amt, "date": get_current_date()})
                save_data(db)
                st.success("Daily food entry saved!")
                st.rerun()
        
        st.write(f"**Total Daily Food Expense:** ₹{daily_food_total:,}")
        st.markdown("---")
        st.write("**Daily Food Transaction Log:**")
        if not daily_food_expenses:
            st.caption("No items added yet.")
        for item in daily_food_expenses:
            st.write(f"- [{item.get('date', 'N/A')}] **{item['desc']}**: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 3: DECORATOR
# -----------------------------------------------------------------------------
with tabs[3]:
    st.header("3. Decorator - Ishtikutuk")
    st.info(f"**Contact:** {d_data.get('contact','')} | **Contracted Total:** ₹{d_data.get('contracted_total',0):,} | **Advance Paid:** ₹{d_data.get('advance_paid',0):,}")
    
    st.subheader("Add / Deduct Extra Decoration Charges")
    dec_desc = st.text_input("Description (e.g. Extra Lighting / Stage Change)", key="dec_desc")
    dec_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="dec_amt", value=0.0)
    
    if st.button("Save Decoration Adjustment"):
        if dec_desc and dec_amt != 0:
            d_data.setdefault("extra_adjustments", []).append({"desc": dec_desc, "amount": dec_amt, "date": get_current_date()})
            save_data(db)
            st.success("Adjustment Saved!")
            st.rerun()
            
    st.subheader(f"Current Actual Spend: ₹{decorator_total_spend:,}")
    for item in d_data.get("extra_adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 4: PHOTOGRAPHY
# -----------------------------------------------------------------------------
with tabs[4]:
    st.header("4. Photography - Bijit Photography")
    st.info(f"**Contact:** {p_data.get('contact','')} | **Total Wedding Base:** ₹{p_data.get('wedding_gross',0):,}")
    
    st.subheader("Cost Sharing & Settlement Breakdown")
    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("Subham (Groom) Total Share", f"₹{groom_photo_share:,.2f}")
    s_col2.metric("Bride Total Share", f"₹{bride_photo_share:,.2f}")
    s_col3.metric("Subham Advance Paid", f"₹{p_data.get('subham_advance_paid',0):,}")

    st.warning(f"**Settlement Note:** Subham paid ₹{p_data.get('subham_advance_paid',0):,} advance. Receivable from Bride side: **₹{photo_receivable_from_bride:,.2f}**")

    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Pre-Wedding Items")
        pw_desc = st.text_input("Pre-wedding expense desc (e.g. Breakfast, Vehicle)", key="pw_desc")
        pw_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="pw_amt", value=0.0)
        if st.button("Add Pre-Wedding Expense"):
            if pw_desc and pw_amt != 0:
                p_data.setdefault("pre_wedding_items", []).append({"desc": pw_desc, "amount": pw_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in p_data.get("pre_wedding_items", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

    with col_p2:
        st.subheader("Wedding Extra Expenses")
        we_desc = st.text_input("Extra expense desc", key="we_desc")
        we_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="we_amt", value=0.0)
        if st.button("Add Wedding Extra"):
            if we_desc and we_amt != 0:
                p_data.setdefault("wedding_extra_items", []).append({"desc": we_desc, "amount": we_amt, "date": get_current_date()})
                save_data(db)
                st.rerun()
        for item in p_data.get("wedding_extra_items", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 5: BAND PARTY
# -----------------------------------------------------------------------------
with tabs[5]:
    st.header("5. Band Party - Bajna")
    st.info(f"**Contact:** {bp_data.get('contact','')} | **Contracted Total:** ₹{bp_data.get('total',0):,} | **Advance Paid:** ₹{bp_data.get('advance_paid',0):,}")
    
    bp_desc = st.text_input("Adjustment Description", key="bp_desc")
    bp_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="bp_amt", value=0.0)
    if st.button("Save Band Party Adjustment"):
        if bp_desc and bp_amt != 0:
            bp_data.setdefault("adjustments", []).append({"desc": bp_desc, "amount": bp_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
            
    st.subheader(f"Current Actual Spend: ₹{band_total_spend:,}")
    for item in bp_data.get("adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 6: MAKEUP
# -----------------------------------------------------------------------------
with tabs[6]:
    st.header("6. Makeup - Gaya Baidya")
    st.info(f"**Contact:** {m_data.get('contact','')} | **Contracted Total:** ₹{m_data.get('total',0):,} | **Advance Paid:** ₹{m_data.get('advance_paid',0):,}")
    
    m_desc = st.text_input("Adjustment Description", key="m_desc")
    m_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="m_amt", value=0.0)
    if st.button("Save Makeup Adjustment"):
        if m_desc and m_amt != 0:
            m_data.setdefault("adjustments", []).append({"desc": m_desc, "amount": m_amt, "date": get_current_date()})
            save_data(db)
            st.rerun()
            
    st.subheader(f"Current Actual Spend: ₹{makeup_total_spend:,}")
    for item in m_data.get("adjustments", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 7: MARRIAGE CARD
# -----------------------------------------------------------------------------
with tabs[7]:
    st.header("7. Marriage Card")
    c_price = st.number_input("Price per Card (₹)", value=float(mc_data.get("per_card_price", 0)))
    c_count = st.number_input("Total Number of Cards", value=int(mc_data.get("total_cards", 0)), step=1)
    c_extra = st.number_input("Extra Charges / Delivery / Printing (₹)", value=float(mc_data.get("extra_cost", 0)))
    
    if st.button("Save Card Details"):
        mc_data["per_card_price"] = c_price
        mc_data["total_cards"] = c_count
        mc_data["extra_cost"] = c_extra
        save_data(db)
        st.success("Marriage Card expense updated!")
        st.rerun()
        
    st.subheader(f"Total Marriage Card Expense: ₹{card_total_spend:,}")

# -----------------------------------------------------------------------------
# TAB 8: VEHICLE
# -----------------------------------------------------------------------------
with tabs[8]:
    st.header("8. Vehicle")
    v_desc = st.text_input("Vehicle Expense Description (e.g. Patipatra vehicle, Ashirwad vehicle)")
    v_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", value=0.0, key="v_amt")
    
    if st.button("Add / Deduct Vehicle Expense"):
        if v_desc and v_amt != 0:
            db["vehicle"].setdefault("expenses", []).append({"desc": v_desc, "amount": v_amt, "date": get_current_date()})
            save_data(db)
            st.success("Vehicle entry saved!")
            st.rerun()
            
    st.subheader(f"Total Vehicle Expense: ₹{v_total_spend:,}")
    for item in db["vehicle"].get("expenses", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 9: PRONAMI
# -----------------------------------------------------------------------------
with tabs[9]:
    st.header("9. Pronami")
    pr_desc = st.text_input("Pronami Description (e.g. Choto Pisi pronami)")
    pr_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", value=0.0, key="pr_amt")
    
    if st.button("Add / Deduct Pronami Expense"):
        if pr_desc and pr_amt != 0:
            db["pronami"].setdefault("expenses", []).append({"desc": pr_desc, "amount": pr_amt, "date": get_current_date()})
            save_data(db)
            st.success("Pronami entry saved!")
            st.rerun()
            
    st.subheader(f"Total Pronami Expense: ₹{pr_total_spend:,}")
    for item in db["pronami"].get("expenses", []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 10: TATTHA (PATIPATRA & ASHIRWAD)
# -----------------------------------------------------------------------------
with tabs[10]:
    st.header("10. Tattha (2 Sub-sections)")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("1. Patipatra Tattha")
        p_desc = st.text_input("Item Description (e.g. Saree, Sweets)", key="p_tat_desc")
        p_amt = st.number_input("Amount (Use negative to deduct)", value=0.0, key="p_tat_amt")
        
        if st.button("Add / Deduct Patipatra Item"):
            if p_desc and p_amt != 0:
                db["tattha"].setdefault("patipatra", []).append({"desc": p_desc, "amount": p_amt, "date": get_current_date()})
                save_data(db)
                st.success("Patipatra item saved!")
                st.rerun()
                
        st.write(f"**Subtotal Patipatra Tattha:** ₹{t_patipatra:,}")
        for item in db["tattha"].get("patipatra", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
            
    with col_t2:
        st.subheader("2. Ashirwad Tattha")
        a_desc = st.text_input("Item Description (e.g. Saree, Cosmetics)", key="a_tat_desc")
        a_amt = st.number_input("Amount (Use negative to deduct)", value=0.0, key="a_tat_amt")
        
        if st.button("Add / Deduct Ashirwad Item"):
            if a_desc and a_amt != 0:
                db["tattha"].setdefault("ashirwad", []).append({"desc": a_desc, "amount": a_amt, "date": get_current_date()})
                save_data(db)
                st.success("Ashirwad item saved!")
                st.rerun()
                
        st.write(f"**Subtotal Ashirwad Tattha:** ₹{t_ashirwad:,}")
        for item in db["tattha"].get("ashirwad", []):
            st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")
            
    st.divider()
    st.subheader(f"Total Combined Tattha Expense: ₹{tattha_total_spend:,}")

# -----------------------------------------------------------------------------
# TAB 11: SHOPPING
# -----------------------------------------------------------------------------
with tabs[11]:
    st.header("11. Shopping (5 Sub-sections)")
    sections = ["moumita", "father", "mother", "my_shopping", "briddhi"]
    labels = ["Moumita Shopping", "Father Shopping", "Mother Shopping", "My Shopping", "Briddhi Shopping"]
    
    selected_sec = st.selectbox("Select Shopping Category", options=sections, format_func=lambda x: labels[sections.index(x)])
    
    item_desc = st.text_input("Item Description")
    item_amt = st.number_input("Amount (Use negative value to deduct)", value=0.0)
    
    if st.button("Add / Deduct Shopping Expense"):
        if item_desc and item_amt != 0:
            db["shopping"].setdefault(selected_sec, []).append({"desc": item_desc, "amount": item_amt, "date": get_current_date()})
            save_data(db)
            st.success("Entry Saved!")
            st.rerun()
            
    st.subheader(f"Current Entries for {labels[sections.index(selected_sec)]}")
    for item in db["shopping"].get(selected_sec, []):
        st.write(f"- [{item.get('date', 'N/A')}] {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 12: MISCELLANEOUS
# -----------------------------------------------------------------------------
with tabs[12]:
    st.header("12. Miscellaneous (Other Expenses)")
    st.caption("Add any unlisted or uncategorized wedding expenses here.")
    
    misc_desc = st.text_input("Expense Description / Reason", key="misc_desc")
    misc_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", value=0.0, key="misc_amt")
    
    if st.button("Add / Deduct Miscellaneous Expense"):
        if misc_desc and misc_amt != 0:
            db.setdefault("miscellaneous", {}).setdefault("expenses", []).append({"desc": misc_desc, "amount": misc_amt, "date": get_current_date()})
            save_data(db)
            st.success("Miscellaneous expense entry saved!")
            st.rerun()
            
    st.subheader(f"Total Miscellaneous Expense: ₹{misc_total_spend:,}")
    st.markdown("---")
    st.write("**Miscellaneous Transaction Log:**")
    misc_list = db.get("miscellaneous", {}).get("expenses", [])
    if not misc_list:
        st.caption("No miscellaneous items added yet.")
    for item in misc_list:
        st.write(f"- [{item.get('date', 'N/A')}] **{item['desc']}**: ₹{item['amount']:,}")
