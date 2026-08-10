import streamlit as st
import pandas as pd
import json
import os

# Page Configuration
st.set_page_config(
    page_title="Wedding Expense Dashboard",
    page_icon="💍",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CONSTANTS & INITIAL DATA STRUCTURE
# -----------------------------------------------------------------------------
TOTAL_BUDGET = 800000

DEFAULT_DATA = {
    "banquet": {
        "name": "Sanai Bhawan",
        "contacts": "9046288819 / 9475807506",
        "total_fare": 25000,
        "electric_rate": 20,
        "diesel_rate_per_hr": 5, # Liters per hour
        "budget": 35000,
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
        "ashirwad_catering_total": 0,
        "daily_food_expenses": [] # list of {"desc": ..., "amount": ...}
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
        "pre_wedding_items": [], # list of {"desc": ..., "amount": ...}
        "wedding_extra_items": [] # list of {"desc": ..., "amount": ...}
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
        "expenses": [] # list of {"section": ..., "amount": ...}
    },
    "pronami": {
        "expenses": [] # list of {"desc": ..., "amount": ...}
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
    }
}

DATA_FILE = "wedding_data.json"

# -----------------------------------------------------------------------------
# PERSISTENCE HELPERS
# -----------------------------------------------------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

db = st.session_state.db

# -----------------------------------------------------------------------------
# CALCULATIONS
# -----------------------------------------------------------------------------
# 1. Banquet
b_data = db["banquet"]
units_consumed = max(0, b_data["electric_end_reading"] - b_data["electric_start_reading"])
electric_cost = units_consumed * b_data["electric_rate"]
diesel_cost = b_data["diesel_hours"] * b_data["diesel_rate_per_hr"] * b_data["diesel_price_per_liter"]
banquet_extra = sum(item["amount"] for item in b_data["extra_expenses"])
banquet_total = b_data["total_fare"] + electric_cost + diesel_cost + banquet_extra

# 2. Catering
c_data = db["catering"]
main_catering_total = c_data["number_of_plates"] * c_data["per_plate_rate"]
daily_food_total = sum(item["amount"] for item in c_data["daily_food_expenses"])
catering_total = main_catering_total + c_data["ashirwad_catering_total"] + daily_food_total

# 3. Decorator
d_data = db["decorator"]
decorator_extra = sum(item["amount"] for item in d_data["extra_adjustments"])
decorator_total = d_data["contracted_total"] + decorator_extra

# 4. Photography
p_data = db["photography"]
pre_wedding_total = sum(item["amount"] for item in p_data["pre_wedding_items"])
wedding_extra_total = sum(item["amount"] for item in p_data["wedding_extra_items"])
shared_photo_extras = pre_wedding_total + wedding_extra_total
photography_gross_total = p_data["wedding_gross"] + shared_photo_extras

groom_photo_share = p_data["groom_wedding_share"] + (shared_photo_extras / 2.0)
bride_photo_share = p_data["bride_wedding_share"] + (shared_photo_extras / 2.0)
photo_receivable_from_bride = bride_photo_share # Assuming Subham manages vendor total settlement

# 5. Band Party
bp_data = db["band_party"]
band_total = bp_data["total"] + sum(item["amount"] for item in bp_data["adjustments"])

# 6. Makeup
m_data = db["makeup"]
makeup_total = m_data["total"] + sum(item["amount"] for item in m_data["adjustments"])

# 7. Marriage Card
mc_data = db["marriage_card"]
card_total = (mc_data["per_card_price"] * mc_data["total_cards"]) + mc_data["extra_cost"]

# 8. Vehicle
v_total = sum(item["amount"] for item in db["vehicle"]["expenses"])

# 9. Pronami
pr_total = sum(item["amount"] for item in db["pronami"]["expenses"])

# 10. Tattha
t_patipatra = sum(item["amount"] for item in db["tattha"]["patipatra"])
t_ashirwad = sum(item["amount"] for item in db["tattha"]["ashirwad"])
tattha_total = t_patipatra + t_ashirwad

# 11. Shopping
s_moumita = sum(item["amount"] for item in db["shopping"]["moumita"])
s_father = sum(item["amount"] for item in db["shopping"]["father"])
s_mother = sum(item["amount"] for item in db["shopping"]["mother"])
s_my = sum(item["amount"] for item in db["shopping"]["my_shopping"])
s_briddhi = sum(item["amount"] for item in db["shopping"]["briddhi"])
shopping_total = s_moumita + s_father + s_mother + s_my + s_briddhi

# Overall Grand Total
grand_total_spent = (
    banquet_total + catering_total + decorator_total + photography_gross_total +
    band_total + makeup_total + card_total + v_total + pr_total +
    tattha_total + shopping_total
)

remaining_budget = TOTAL_BUDGET - grand_total_spent

# Advances Summary
total_advances_paid = (
    b_data["advance_paid"] + c_data["advance_paid"] + d_data["advance_paid"] +
    p_data["subham_advance_paid"] + bp_data["advance_paid"] + m_data["advance_paid"]
)

# -----------------------------------------------------------------------------
# MAIN UI
# -----------------------------------------------------------------------------
st.title("💍 My Wedding Expense & Status Dashboard")
st.caption("Real-time updates, local/cloud persistent storage & mobile ready")

# KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Overall Budget", f"₹{TOTAL_BUDGET:,.2f}")
col2.metric("Total Actual Spent", f"₹{grand_total_spent:,.2f}")
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
    "11. Shopping"
])

# -----------------------------------------------------------------------------
# TAB 0: OVERVIEW
# -----------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Category Wise Breakdown")
    summary_df = pd.DataFrame([
        {"Category": "Banquet Hall", "Spent (₹)": banquet_total},
        {"Category": "Catering", "Spent (₹)": catering_total},
        {"Category": "Decorator", "Spent (₹)": decorator_total},
        {"Category": "Photography (Gross)", "Spent (₹)": photography_gross_total},
        {"Category": "Band Party", "Spent (₹)": band_total},
        {"Category": "Makeup", "Spent (₹)": makeup_total},
        {"Category": "Marriage Card", "Spent (₹)": card_total},
        {"Category": "Vehicle", "Spent (₹)": v_total},
        {"Category": "Pronami", "Spent (₹)": pr_total},
        {"Category": "Tattha", "Spent (₹)": tattha_total},
        {"Category": "Shopping", "Spent (₹)": shopping_total},
    ])
    st.dataframe(summary_df, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 1: BANQUET HALL
# -----------------------------------------------------------------------------
with tabs[1]:
    st.header("1. Banquet Hall - Sanai Bhawan")
    st.info(f"**Contact:** {b_data['contacts']} | **Booked:** {b_data['booking_date']} | **Advance Paid:** ₹{b_data['advance_paid']:,}")
    
    st.markdown("**Static Facilities Included:** " + ", ".join(b_data["facilities"]))
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Meter & Fuel Readings")
        start_r = st.number_input("Electric Machine Start Reading", value=int(b_data["electric_start_reading"]))
        end_r = st.number_input("Electric Machine End Reading", value=int(b_data["electric_end_reading"]))
        hrs = st.number_input("Diesel Run Hours (5L/hr)", value=float(b_data["diesel_hours"]))
        
        if st.button("Save Readings"):
            b_data["electric_start_reading"] = start_r
            b_data["electric_end_reading"] = end_r
            b_data["diesel_hours"] = hrs
            save_data(db)
            st.success("Readings Updated!")
            st.rerun()

    with c2:
        st.subheader("Financial Status")
        st.write(f"**Base Fare:** ₹{b_data['total_fare']:,}")
        st.write(f"**Electricity ({units_consumed} units @ ₹20/unit):** ₹{electric_cost:,}")
        st.write(f"**Diesel ({hrs} hrs @ 5L/hr):** ₹{diesel_cost:,}")
        st.write(f"**Total Calculated Expense:** ₹{banquet_total:,}")
        st.write(f"**Target Budget:** ₹{b_data['budget']:,}")
        st.write(f"**Balance Payable:** ₹{(banquet_total - b_data['advance_paid']):,}")

# -----------------------------------------------------------------------------
# TAB 2: CATERING
# -----------------------------------------------------------------------------
with tabs[2]:
    st.header("2. Catering - Shanti Caterer")
    st.info(f"**Contact:** {c_data['contact']} | **Rate:** ₹{c_data['per_plate_rate']}/plate | **Advance:** ₹{c_data['advance_paid']:,}")
    
    plates = st.number_input("Total Number of Plates", value=int(c_data["number_of_plates"]), step=1)
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
        ash_amt = st.number_input("Ashirwad Catering Final Amount (₹)", value=float(c_data["ashirwad_catering_total"]))
        if st.button("Update Ashirwad Total"):
            c_data["ashirwad_catering_total"] = ash_amt
            save_data(db)
            st.success("Ashirwad amount updated!")
            st.rerun()

    with col_b:
        st.subheader("Marriage Daily Food Expenses")
        d_desc = st.text_input("Food Item / Day Description", key="df_desc")
        d_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="df_amt")
        if st.button("Add/Deduct Daily Food Expense"):
            if d_desc and d_amt != 0:
                c_data["daily_food_expenses"].append({"desc": d_desc, "amount": d_amt})
                save_data(db)
                st.rerun()
        
        for idx, item in enumerate(c_data["daily_food_expenses"]):
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 4: PHOTOGRAPHY
# -----------------------------------------------------------------------------
with tabs[4]:
    st.header("4. Photography - Bijit Photography")
    st.info(f"**Contact:** {p_data['contact']} | **Total Wedding Base:** ₹{p_data['wedding_gross']:,}")
    
    st.subheader("Cost Sharing & Settlement Breakdown")
    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("Subham (Groom) Total Share", f"₹{groom_photo_share:,.2f}")
    s_col2.metric("Bride Total Share", f"₹{bride_photo_share:,.2f}")
    s_col3.metric("Subham Advance Paid", f"₹{p_data['subham_advance_paid']:,}")

    st.warning(f"**Settlement Note:** Subham paid ₹{p_data['subham_advance_paid']:,} advance. Receivable from Bride side for photo settlement: **₹{photo_receivable_from_bride:,.2f}**")

    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.subheader("Pre-Wedding Items")
        pw_desc = st.text_input("Pre-wedding expense desc (e.g. Breakfast, Vehicle)", key="pw_desc")
        pw_amt = st.number_input("Amount (₹)", key="pw_amt")
        if st.button("Add Pre-Wedding Expense"):
            if pw_desc and pw_amt != 0:
                p_data["pre_wedding_items"].append({"desc": pw_desc, "amount": pw_amt})
                save_data(db)
                st.rerun()
        for item in p_data["pre_wedding_items"]:
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")

    with col_p2:
        st.subheader("Wedding Extra Expenses")
        we_desc = st.text_input("Extra expense desc", key="we_desc")
        we_amt = st.number_input("Amount (₹)", key="we_amt")
        if st.button("Add Wedding Extra"):
            if we_desc and we_amt != 0:
                p_data["wedding_extra_items"].append({"desc": we_desc, "amount": we_amt})
                save_data(db)
                st.rerun()
        for item in p_data["wedding_extra_items"]:
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")

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
            db["shopping"][selected_sec].append({"desc": item_desc, "amount": item_amt})
            save_data(db)
            st.success("Entry Saved!")
            st.rerun()
            
    st.subheader(f"Current Entries for {labels[sections.index(selected_sec)]}")
    for item in db["shopping"][selected_sec]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")
