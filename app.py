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
        "expenses": [] # list of {"desc": ..., "amount": ...}
    },
    "pronami": {
        "expenses": [] # list of {"desc": ..., "amount": ...}
    },
    "tattha": {
        "patipatra": [], # list of {"desc": ..., "amount": ...}
        "ashirwad": []  # list of {"desc": ..., "amount": ...}
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
            loaded_data = json.load(f)
            if "tattha" not in loaded_data:
                loaded_data["tattha"] = {"patipatra": [], "ashirwad": []}
            return loaded_data
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
banquet_extra = sum(item["amount"] for item in b_data.get("extra_expenses", []))
banquet_total_spend = b_data["advance_paid"] + electric_cost + diesel_cost + banquet_extra
banquet_expected_budget = b_data["budget"]

# 2. Catering
c_data = db["catering"]
main_catering_total = c_data["number_of_plates"] * c_data["per_plate_rate"]
daily_food_total = sum(item["amount"] for item in c_data.get("daily_food_expenses", []))
catering_total_spend = (c_data["advance_paid"] if c_data["number_of_plates"] == 0 else main_catering_total) + c_data["ashirwad_catering_total"] + daily_food_total
catering_expected_budget = 0 

# 3. Decorator
d_data = db["decorator"]
decorator_extra = sum(item["amount"] for item in d_data.get("extra_adjustments", []))
decorator_total_spend = d_data["advance_paid"] + decorator_extra
decorator_expected_budget = d_data["contracted_total"]

# 4. Photography
p_data = db["photography"]
pre_wedding_total = sum(item["amount"] for item in p_data.get("pre_wedding_items", []))
wedding_extra_total = sum(item["amount"] for item in p_data.get("wedding_extra_items", []))
shared_photo_extras = pre_wedding_total + wedding_extra_total
photography_gross_spend = p_data["subham_advance_paid"] + shared_photo_extras
photography_expected_budget = p_data["wedding_gross"] + 30000

groom_photo_share = p_data["groom_wedding_share"] + (shared_photo_extras / 2.0)
bride_photo_share = p_data["bride_wedding_share"] + (shared_photo_extras / 2.0)
photo_receivable_from_bride = bride_photo_share

# 5. Band Party
bp_data = db["band_party"]
band_total_spend = bp_data["advance_paid"] + sum(item["amount"] for item in bp_data.get("adjustments", []))
band_expected_budget = bp_data["total"]

# 6. Makeup
m_data = db["makeup"]
makeup_total_spend = m_data["advance_paid"] + sum(item["amount"] for item in m_data.get("adjustments", []))
makeup_expected_budget = m_data["total"]

# 7. Marriage Card
mc_data = db["marriage_card"]
card_total_spend = (mc_data["per_card_price"] * mc_data["total_cards"]) + mc_data["extra_cost"]
card_expected_budget = 0

# 8. Vehicle
v_total_spend = sum(item["amount"] for item in db["vehicle"].get("expenses", []))
v_expected_budget = 0

# 9. Pronami
pr_total_spend = sum(item["amount"] for item in db["pronami"].get("expenses", []))
pr_expected_budget = 0

# 10. Tattha
t_patipatra = sum(item["amount"] for item in db["tattha"].get("patipatra", []))
t_ashirwad = sum(item["amount"] for item in db["tattha"].get("ashirwad", []))
tattha_total_spend = t_patipatra + t_ashirwad
tattha_expected_budget = 0

# 11. Shopping
s_moumita = sum(item["amount"] for item in db["shopping"].get("moumita", []))
s_father = sum(item["amount"] for item in db["shopping"].get("father", []))
s_mother = sum(item["amount"] for item in db["shopping"].get("mother", []))
s_my = sum(item["amount"] for item in db["shopping"].get("my_shopping", []))
s_briddhi = sum(item["amount"] for item in db["shopping"].get("briddhi", []))
shopping_total_spend = s_moumita + s_father + s_mother + s_my + s_briddhi
shopping_expected_budget = 0

# Grand Totals
grand_actual_spend = (
    banquet_total_spend + catering_total_spend + decorator_total_spend + photography_gross_spend +
    band_total_spend + makeup_total_spend + card_total_spend + v_total_spend + pr_total_spend +
    tattha_total_spend + shopping_total_spend
)

remaining_budget = TOTAL_BUDGET - grand_actual_spend

total_advances_paid = (
    b_data["advance_paid"] + c_data["advance_paid"] + d_data["advance_paid"] +
    p_data["subham_advance_paid"] + bp_data["advance_paid"] + m_data["advance_paid"]
)

# -----------------------------------------------------------------------------
# MAIN UI
# -----------------------------------------------------------------------------
st.title("💍 My Wedding Expense & Status Dashboard")
st.caption("Real-time updates, persistent cloud/local file storage & mobile ready")

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
    "11. Shopping"
])

# -----------------------------------------------------------------------------
# TAB 0: OVERVIEW
# -----------------------------------------------------------------------------
with tabs[0]:
    st.subheader("Category Wise Breakdown")
    
    categories_data = [
        {"Category": "Banquet Hall", "Expected Budget (₹)": banquet_expected_budget, "Actual Spend (₹)": banquet_total_spend},
        {"Category": "Catering", "Expected Budget (₹)": catering_expected_budget, "Actual Spend (₹)": catering_total_spend},
        {"Category": "Decorator", "Expected Budget (₹)": decorator_expected_budget, "Actual Spend (₹)": decorator_total_spend},
        {"Category": "Photography", "Expected Budget (₹)": photography_expected_budget, "Actual Spend (₹)": photography_gross_spend},
        {"Category": "Band Party", "Expected Budget (₹)": band_expected_budget, "Actual Spend (₹)": band_total_spend},
        {"Category": "Makeup", "Expected Budget (₹)": makeup_expected_budget, "Actual Spend (₹)": makeup_total_spend},
        {"Category": "Marriage Card", "Expected Budget (₹)": card_expected_budget, "Actual Spend (₹)": card_total_spend},
        {"Category": "Vehicle", "Expected Budget (₹)": v_expected_budget, "Actual Spend (₹)": v_total_spend},
        {"Category": "Pronami", "Expected Budget (₹)": pr_expected_budget, "Actual Spend (₹)": pr_total_spend},
        {"Category": "Tattha", "Expected Budget (₹)": tattha_expected_budget, "Actual Spend (₹)": tattha_total_spend},
        {"Category": "Shopping", "Expected Budget (₹)": shopping_expected_budget, "Actual Spend (₹)": shopping_total_spend},
    ]

    df = pd.DataFrame(categories_data)
    
    # Compute Spend %
    def calc_pct(row):
        ref = row["Expected Budget (₹)"] if row["Expected Budget (₹)"] > 0 else TOTAL_BUDGET
        return (row["Actual Spend (₹)"] / ref) * 100 if ref > 0 else 0.0

    df["Spend %"] = df.apply(calc_pct, axis=1)

    # Style overbudget (>100%) cleanly
    def style_dataframe(df):
        def highlight_overbudget(s):
            return ['color: red; font-weight: bold' if v > 100 else '' for v in s]
        
        return df.style.format({
            "Expected Budget (₹)": lambda x: f"₹{x:,.2f}" if x > 0 else "N/A",
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
        st.write(f"**Actual Spend So Far:** ₹{banquet_total_spend:,}")
        st.write(f"**Expected Budget:** ₹{b_data['budget']:,}")

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
# TAB 3: DECORATOR
# -----------------------------------------------------------------------------
with tabs[3]:
    st.header("3. Decorator - Ishtikutuk")
    st.info(f"**Contact:** {d_data['contact']} | **Contracted Total (Budget):** ₹{d_data['contracted_total']:,} | **Advance Paid:** ₹{d_data['advance_paid']:,} | **Max Budget:** ₹{d_data['max_budget']:,}")
    
    st.subheader("Add / Deduct Extra Decoration Charges")
    dec_desc = st.text_input("Description (e.g. Extra Lighting / Stage Change)", key="dec_desc")
    dec_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="dec_amt")
    
    if st.button("Save Decoration Adjustment"):
        if dec_desc and dec_amt != 0:
            d_data["extra_adjustments"].append({"desc": dec_desc, "amount": dec_amt})
            save_data(db)
            st.success("Adjustment Saved!")
            st.rerun()
            
    st.subheader(f"Current Actual Spend (Advance + Extras): ₹{decorator_total_spend:,}")
    st.write(f"**Remaining Balance Payable Later:** ₹{(d_data['contracted_total'] - d_data['advance_paid']):,}")
    for item in d_data["extra_adjustments"]:
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
        pw_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="pw_amt")
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
        we_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="we_amt")
        if st.button("Add Wedding Extra"):
            if we_desc and we_amt != 0:
                p_data["wedding_extra_items"].append({"desc": we_desc, "amount": we_amt})
                save_data(db)
                st.rerun()
        for item in p_data["wedding_extra_items"]:
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 5: BAND PARTY
# -----------------------------------------------------------------------------
with tabs[5]:
    st.header("5. Band Party - Bajna")
    st.info(f"**Contact:** {bp_data['contact']} | **Contracted Total:** ₹{bp_data['total']:,} | **Advance Paid:** ₹{bp_data['advance_paid']:,}")
    
    bp_desc = st.text_input("Adjustment Description", key="bp_desc")
    bp_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="bp_amt")
    if st.button("Save Band Party Adjustment"):
        if bp_desc and bp_amt != 0:
            bp_data["adjustments"].append({"desc": bp_desc, "amount": bp_amt})
            save_data(db)
            st.rerun()
            
    st.subheader(f"Current Actual Spend: ₹{band_total_spend:,}")
    for item in bp_data["adjustments"]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 6: MAKEUP
# -----------------------------------------------------------------------------
with tabs[6]:
    st.header("6. Makeup - Gaya Baidya")
    st.info(f"**Contact:** {m_data['contact']} | **Contracted Total:** ₹{m_data['total']:,} | **Advance Paid:** ₹{m_data['advance_paid']:,}")
    
    m_desc = st.text_input("Adjustment Description", key="m_desc")
    m_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", key="m_amt")
    if st.button("Save Makeup Adjustment"):
        if m_desc and m_amt != 0:
            m_data["adjustments"].append({"desc": m_desc, "amount": m_amt})
            save_data(db)
            st.rerun()
            
    st.subheader(f"Current Actual Spend: ₹{makeup_total_spend:,}")
    for item in m_data["adjustments"]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 7: MARRIAGE CARD
# -----------------------------------------------------------------------------
with tabs[7]:
    st.header("7. Marriage Card")
    c_price = st.number_input("Price per Card (₹)", value=float(mc_data["per_card_price"]))
    c_count = st.number_input("Total Number of Cards", value=int(mc_data["total_cards"]), step=1)
    c_extra = st.number_input("Extra Charges / Delivery / Printing (₹)", value=float(mc_data["extra_cost"]))
    
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
            db["vehicle"]["expenses"].append({"desc": v_desc, "amount": v_amt})
            save_data(db)
            st.success("Vehicle entry saved!")
            st.rerun()
            
    st.subheader(f"Total Vehicle Expense: ₹{v_total_spend:,}")
    for item in db["vehicle"]["expenses"]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")

# -----------------------------------------------------------------------------
# TAB 9: PRONAMI
# -----------------------------------------------------------------------------
with tabs[9]:
    st.header("9. Pronami")
    pr_desc = st.text_input("Pronami Description (e.g. Choto Pisi pronami)")
    pr_amt = st.number_input("Amount (Positive to Add, Negative to Deduct)", value=0.0, key="pr_amt")
    
    if st.button("Add / Deduct Pronami Expense"):
        if pr_desc and pr_amt != 0:
            db["pronami"]["expenses"].append({"desc": pr_desc, "amount": pr_amt})
            save_data(db)
            st.success("Pronami entry saved!")
            st.rerun()
            
    st.subheader(f"Total Pronami Expense: ₹{pr_total_spend:,}")
    for item in db["pronami"]["expenses"]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")

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
                db["tattha"]["patipatra"].append({"desc": p_desc, "amount": p_amt})
                save_data(db)
                st.success("Patipatra item saved!")
                st.rerun()
                
        st.write(f"**Subtotal Patipatra Tattha:** ₹{t_patipatra:,}")
        for item in db["tattha"]["patipatra"]:
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")
            
    with col_t2:
        st.subheader("2. Ashirwad Tattha")
        a_desc = st.text_input("Item Description (e.g. Saree, Cosmetics)", key="a_tat_desc")
        a_amt = st.number_input("Amount (Use negative to deduct)", value=0.0, key="a_tat_amt")
        
        if st.button("Add / Deduct Ashirwad Item"):
            if a_desc and a_amt != 0:
                db["tattha"]["ashirwad"].append({"desc": a_desc, "amount": a_amt})
                save_data(db)
                st.success("Ashirwad item saved!")
                st.rerun()
                
        st.write(f"**Subtotal Ashirwad Tattha:** ₹{t_ashirwad:,}")
        for item in db["tattha"]["ashirwad"]:
            st.write(f"- {item['desc']}: ₹{item['amount']:,}")
            
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
            db["shopping"][selected_sec].append({"desc": item_desc, "amount": item_amt})
            save_data(db)
            st.success("Entry Saved!")
            st.rerun()
            
    st.subheader(f"Current Entries for {labels[sections.index(selected_sec)]}")
    for item in db["shopping"][selected_sec]:
        st.write(f"- {item['desc']}: ₹{item['amount']:,}")
