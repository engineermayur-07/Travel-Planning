import streamlit as st
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import date, datetime
from fpdf import FPDF
import pandas as pd
import os

# --- INITIALIZATION & DATA ---
geolocator = Nominatim(user_agent="travel_itinerary_streamlit")

def apply_custom_style():
    st.markdown("""
        <style>
        /* 1. Use CSS Variables for Universal Visibility */
        :root {
            --primary-text: var(--text-color); /* Streamlit's built-in text variable */
        }

        /* 2. Global Text Visibility */
        .stMarkdown, p, label, .stHeader {
            color: var(--text-color) !important; 
        }

        /* 3. SIDEBAR: Force visibility regardless of theme */
        section[data-testid="stSidebar"] {
            /* Keep your light red background but ensure text stays dark for contrast */
            background-color: #fab1a0 !important; 
        }
        
        section[data-testid="stSidebar"] .stMarkdown p, 
        section[data-testid="stSidebar"] label {
            color: #1a252f !important; /* Dark Blue for readability on Light Red */
            font-weight: 600 !important;
        }

        /* 4. INPUT BOXES: Ensure white background in dark mode for clarity */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #1a252f !important;
            border: 1px solid #ced4da !important;
        }

        /* 5. TABS: Make them pop in dark mode */
        button[data-baseweb="tab"] p {
            color: var(--text-color);
        }
        button[aria-selected="true"] p {
            color: #27ae60 !important; /* Keep your Safarnama Green */
            font-weight: bold;
        }

        /* 6. EXPANDERS (Daily Menus) */
        .streamlit-expanderHeader {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid var(--secondary-background-color) !important;
        }
        </style>
    """, unsafe_allow_html=True)
# Call this at the start of your code
apply_custom_style()
def load_data():
    with open("travel_data.json", "r") as file:
        return json.load(file)

data = load_data()
destinations = data["destinations"]
hotel_menu = data["hotel_menu"]

# --- HELPER FUNCTIONS ---
def calc_dist(start, end):
    try:
        loc1 = geolocator.geocode(start)
        loc2 = geolocator.geocode(end)
        return geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).km
    except:
        return None
def clean_text(text):
    """Replaces Unicode symbols with PDF-safe equivalents."""
    if isinstance(text, str):
        return text.replace("₹", "Rs.").replace("\u20b9", "Rs.")
    return text

def add_sticky_footer():
    footer_style = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50; /* Matches your Midnight Blue theme */
        color: white;
        text-align: center;
        padding: 7px 0;
        font-size: 18px;
        z-index: 999;
        border-top: 2px solid #27ae60; /* Subtle green line to match primary color */
    }
    
    /* This adds padding to the bottom of the app so the footer doesn't hide content */
    .main .block-container {
        padding-bottom: 60px;
    }
    </style>
    
    <div class="footer">
        <p> 🗺️ SAFARNAMA Travel Services © 2026 | All Rights Reserved</p>
        <p> Developed with ❤️ by Mayur B. Gund and Rohit J. Khokale</p>

    </div>
    """
    st.markdown(footer_style, unsafe_allow_html=True)

# Call this at the very end of your app.py script
add_sticky_footer()

def generate_pdf(dest, start, arrival, departure, days, members, dist, mode, hotel, room_type, rooms, food_list, activities_list, total_breakdown, total):
    pdf = FPDF()
    pdf.add_page()
    
    # --- 1. HEADER WITH LOGO ---
    # Image(path, x, y, width)
    try:
        if os.path.exists("logo.jpg"):
            pdf.image("logo.jpg", 10, 8, 33)
    except:
        pass
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(44, 62, 80) # Dark Blue/Grey
    pdf.cell(0, 10, txt="SAFARNAMA", ln=True, align='R')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt="Your Journey, Our Passion", ln=True, align='R')
    pdf.ln(15)

    # Decorative Line
    pdf.set_draw_color(44, 62, 80)
    pdf.line(10, 45, 200, 45)
    pdf.ln(5)

    # --- 2. TRIP OVERVIEW BOX ---
    pdf.set_fill_color(240, 240, 240) # Light Grey background
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f" TRIP TO {dest.upper()}", ln=True, fill=True)
    
    pdf.set_font("Arial", size=11)
    pdf.set_text_color(0, 0, 0)
    
    # Two-column layout for details
    col_width = 90
    pdf.cell(col_width, 8, txt=f"From: {start}", ln=0)
    pdf.cell(col_width, 8, txt=f"Distance: {dist:.2f} km", ln=1)
    
    pdf.cell(col_width, 8, txt=f"Arrival: {arrival}", ln=0)
    pdf.cell(col_width, 8, txt=f"Departure: {departure}", ln=1)
    
    pdf.cell(col_width, 8, txt=f"Travelers: {members}", ln=0)
    pdf.cell(col_width, 8, txt=f"Duration: {days} Days", ln=1)
    
    # --- 3. ACCOMMODATION ---
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="ACCOMMODATION", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt=f"Stay at {hotel}\nRoom Type: {room_type} ({rooms} rooms)", border='L')

    # --- 4. FOOD & ACTIVITIES ---
    # We use two columns if possible, or stacked with icons
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="DAILY MEAL PLAN", ln=True)
    pdf.set_font("Arial", size=10)
    for item in food_list:
        pdf.cell(0, 7, txt=f"  > {item}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="PLANNED ACTIVITIES", ln=True)
    pdf.set_font("Arial", size=10)
    for act in activities_list:
        pdf.cell(0, 7, txt=f"  * {act}", ln=True)

    # --- 5. BUDGET SUMMARY (The Invoice Look) ---
    pdf.ln(10)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt=" BUDGET BREAKDOWN", ln=True, fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    for label, cost in total_breakdown.items():
        pdf.cell(140, 8, txt=label, border='B', ln=0)
        pdf.cell(50, 8, txt=f"Rs. {cost:,.2f}", border='B', ln=1, align='R')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(192, 57, 43) # Soft Red
    pdf.cell(0, 12, txt=f"GRAND TOTAL: Rs. {total:,.2f}", ln=True, align='R')

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, txt="Generated by Safarnama Travel Services - Concept Project", align='C')

    # Note: Clean symbols logic as discussed before
    return pdf.output(dest="S").encode("latin-1", errors="replace")
# --- STREAMLIT UI ---
st.set_page_config(page_title="UDAAN TRAVEL SERVICE", layout="wide")
st.title("🗺️ SAFARNAMA TRAVEL SERVICES")
st.markdown("---")

# Sidebar for Initial Setup
with st.sidebar:
    # Add this at the beginning of your sidebar logic
    # Ensure logo.png is in your project folder
    try:
        st.image("logo.jpg", width=150)
    except:
        pass
    st.title("📍 Plan Your Trip")
    start_city = st.text_input("Starting City", placeholder="e.g. Pune")
    
    category = st.selectbox("Destination Category", ["Hills and Mountains", "Coastal", "Devotional Sites"])
    available_cities = destinations.get(category, [])
    dest_city = st.selectbox("Select Destination", available_cities)
    
    col1, col2 = st.columns(2)
    arrival = col1.date_input("Arrival Date", min_value=date.today())
    departure = col2.date_input("Departure Date", min_value=arrival)
    
    days = (departure - arrival).days or 1
    members = st.number_input("Total Members", min_value=1, max_value=100, value=1)

# Logic Calculation
if st.sidebar.button("Calculate Distance & Fetch Options"):
    dist = calc_dist(start_city, dest_city)
    if dist:
        st.session_state['dist'] = dist
        st.success(f"Distance calculated: {dist:.2f} km")
    else:
        st.error("Could not find locations. Please check spellings.")

# Main Interface (Tabs for better UX)
if 'dist' in st.session_state:
    tab1, tab2, tab3, tab4 = st.tabs(["🚗 Transport", "🏨 Hotel", "🍱 Food & Activities", "📋 Itinerary"])

    with tab1:
        st.header("Select Transport Mode")
        modes = {
            "Rented Car": 10, "Personal Car": 1, "Train": 3, "Plane": 8
        }
        selected_mode = st.radio("Choose your mode:", list(modes.keys()))
        if selected_mode=="Personal Car":
            t_cost = modes[selected_mode] * st.session_state['dist'] 
        else:
            t_cost = modes[selected_mode] * st.session_state['dist'] * members
        st.info(f"Estimated Transport Cost: ₹{t_cost:,.2f}")

    with tab2:
        st.header("Accommodation Selection")
        h_cat = st.selectbox("Hotel Luxury Level", ["Luxury", "Mid-range", "Budget"])
        hotel_list = destinations[dest_city]["hotels"][h_cat]
        
        selected_hotel_data = st.selectbox("Choose Hotel", hotel_list, format_func=lambda x: x[0])
        
        # Room logic
        room_options = ["Classic Chamber", "Deluxe Chamber", "Family Chamber"] if h_cat != "Budget" else ["Classic Chamber", "Family Chamber"]
        room_sel = st.selectbox("Room Type", room_options)
        room_idx = room_options.index(room_sel) + 1
        room_price = selected_hotel_data[room_idx]
        
        num_rooms = st.slider("Number of Rooms", 1, 10, 1)
        h_cost = room_price * num_rooms * days
        st.info(f"Hotel Stay Cost: ₹{h_cost:,.2f}")

    with tab3:
        st.header("🍱 Daily Food & Activity Planning")
        
        # --- ACTIVITIES SECTION ---
        st.subheader("Planned Activities")
        possible_acts = destinations[dest_city]["activities"]
        chosen_acts = st.multiselect("What do you want to do during your stay?", possible_acts)
        a_cost = len(chosen_acts) * 1000 

        st.markdown("---")
        
        # --- DAILY FOOD SELECTION LOGIC ---
        st.subheader("Hotel Meal Planning")
        
        # Use session_state to keep track of total food cost
        if 'total_food_cost' not in st.session_state:
            st.session_state.total_food_cost = 0
        if 'food_summary' not in st.session_state:
            st.session_state.food_summary = []

        # Reset button to clear food choices if the user wants to restart planning
        if st.button("Reset Food Plan"):
            st.session_state.total_food_cost = 0
            st.session_state.food_summary = []

        temp_food_cost = 0
        temp_summary = []

        # Loop through each day exactly like your backend logic
        for day_num in range(1, days + 1):
            with st.expander(f"Day {day_num} Menu Selection"):
                st.write(f"Plan your meals for Day {day_num}")
                
                # 1. BREAKFAST
                b_cat = st.radio(f"Breakfast Type (Day {day_num})", ["VEG", "NON-VEG"], key=f"b_cat_{day_num}")
                b_items = list(hotel_menu["Breakfast"][b_cat].keys())
                b_sel = st.selectbox(f"Select Breakfast (Day {day_num})", ["Skip"] + b_items, key=f"b_sel_{day_num}")
                
                if b_sel != "Skip":
                    b_qty = st.number_input(f"Breakfast Qty (Day {day_num})", 1, 10, 1, key=f"b_qty_{day_num}")
                    cost = hotel_menu["Breakfast"][b_cat][b_sel] * b_qty
                    temp_food_cost += cost
                    temp_summary.append(f"Day {day_num} Breakfast: {b_sel} (x{b_qty}) - {cost}")

                # 2. LUNCH
                l_cat = st.radio(f"Lunch Type (Day {day_num})", ["VEG", "NON-VEG"], key=f"l_cat_{day_num}")
                l_items = list(hotel_menu["Lunch"][l_cat].keys())
                l_sel = st.selectbox(f"Select Lunch (Day {day_num})", ["Skip"] + l_items, key=f"l_sel_{day_num}")
                
                if l_sel != "Skip":
                    l_qty = st.number_input(f"Lunch Qty (Day {day_num})", 1, 10, 1, key=f"l_qty_{day_num}")
                    # Logic to find price in either VEG or NON-VEG
                    price = hotel_menu["Lunch"][l_cat][l_sel] or hotel_menu["Lunch"]["NON-VEG"].get(l_sel)
                    cost = price * l_qty
                    temp_food_cost += cost
                    temp_summary.append(f"Day {day_num} Lunch: {l_sel} (x{l_qty}) - {cost}")

                # 3. DINNER
                d_cat = st.radio(f"Dinner Type (Day {day_num})", ["VEG", "NON-VEG"], key=f"d_cat_{day_num}")
                d_items = list(hotel_menu["Dinner"][d_cat].keys())
                d_sel = st.selectbox(f"Select Dinner (Day {day_num})", ["Skip"] + d_items, key=f"d_sel_{day_num}")
                
                if d_sel != "Skip":
                    d_qty = st.number_input(f"Dinner Qty (Day {day_num})", 1, 10, 1, key=f"d_qty_{day_num}")
                    price = hotel_menu["Dinner"][d_cat][d_sel] or hotel_menu["Dinner"]["NON-VEG"].get(d_sel)
                    cost = price * d_qty
                    temp_food_cost += cost
                    temp_summary.append(f"Day {day_num} Dinner: {d_sel} (x{d_qty}) - {cost}")

        # Update session state with the current loop calculations
        st.session_state.total_food_cost = temp_food_cost
        st.session_state.food_summary = temp_summary
        
        st.info(f"Current Total Food Budget: {st.session_state.total_food_cost:,.2f}")
        # --- MISCELLANEOUS & LOCAL TRANSPORT ---
        st.markdown("---")
        st.subheader("🚌 Local Transport & Misc Expenses")
        
        col_m1, col_m2 = st.columns(2)
    
        with col_m1:
            st.write("**Public Transport**")
            # Matches your logic: avg cost is 5000-10000 per day
            daily_pub_transport = st.number_input(
                "Daily Transport Budget (Rs)", 
                min_value=0, 
                value=5000, 
                step=500,
                help="Includes local cabs, autos, or bike rentals per day."
            )
            
        with col_m2:
            st.write("**Other Miscellaneous**")
            # Matches your logic: shopping, food outside, etc.
            daily_other_mis = st.number_input(
                "Other Daily Expenses (Rs)", 
                min_value=0, 
                value=5000, 
                step=500,
                help="Covers shopping, street food, and tips per day."
            )

        # Calculation logic from your mis_cost function
        total_mis_per_day = daily_pub_transport + daily_other_mis
        final_mis_cost = total_mis_per_day * days
        
        st.warning(f"Total Miscellaneous Budget for {days} days: Rs{final_mis_cost:,.2f}")
        # Inside Tab 4
        total_cost = t_cost + h_cost + st.session_state.total_food_cost + a_cost + final_mis_cost
    with tab4:
        st.header("Finalize & Download")
        
        # 1. Prepare the cost breakdown dictionary for the PDF
        breakdown = {
            "Transport Cost": t_cost,
            "Hotel Stay Cost": h_cost,
            "Food Cost": st.session_state.total_food_cost,
            "Activities Cost": a_cost,
            "Misc & Local Transport": final_mis_cost
        }
        
        # 2. Trigger the PDF generation
        if st.download_button(
            label="📩 Download Detailed PDF Itinerary",
            data=generate_pdf(
                dest_city, 
                start_city, 
                arrival, 
                departure, 
                days, 
                members, 
                st.session_state['dist'], 
                selected_mode, 
                selected_hotel_data[0], 
                room_sel, 
                num_rooms, 
                st.session_state.food_summary, # Daily food list
                chosen_acts,                    # Activities list
                breakdown, 
                total_cost
            ),
            file_name=f"Safarnama_{dest_city}.pdf",
            mime="application/pdf"
        ):
            st.balloons() # Celebration for finishing!
