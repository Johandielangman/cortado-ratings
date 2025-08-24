# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~
#      /\_/\
#     ( o.o )
#      > ^ <
#
# Author: Johan Hanekom
# Date: August 2025
#
# ~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~

# =============== // STANDARD IMPORT // ===============

import time

# =============== // LIBRARY IMPORT // ===============

import streamlit as st
from streamlit_star_rating import st_star_rating

# =============== // MODULE IMPORT // ===============

from googlemaps import googlemaps
from cortado import Cortado, DC


@st.cache_resource(ttl=30)
def get_cortado_instance():
    return Cortado()


st.set_page_config(
    page_title="New Rating",
    page_icon="🎉"
)

st.title("New Rating 🎉")

with st.spinner("Setting up the DB connection..."):
    cortado_instance = get_cortado_instance()

st.write("We're so excited for your new rating submission!")
st.write("Please tell us how you would like to find the restaurant:")


def clear_form():
    for key in ("rating", "location_selector", "form_data"):
        if key in st.session_state:
            del st.session_state[key]

    # Clear form data
    st.session_state.form_data = {
        "restaurant": {
            "name": "",
            "address": None,
            "google_place_id": None,
            "latitude": None,
            "longitude": None,
            "website": "",
            "restaurant_rating": None
        },
        "user": {
            "name": None,
            "email": None
        },
        "rating": {
            "stars": None,
            "price_zar": 0.0,
            "num_shots": None,
            "take_away": False,
            "notes": "",
            "cookie": False
        }
    }


if "form_data" not in st.session_state:
    clear_form()


st.subheader("✏️ Review / Edit Location Details")
st.write("You can either use the google search below or manually enter the details")

try:
    location_data = googlemaps(
        key="location_selector"
    )
    if location_data:
        st.success(f"✅ Successfully fetched information from: {location_data.get('place_name', 'Unknown')}")
        st.session_state.form_data["restaurant"].update({
            "name": location_data.get("place_name", ""),
            "address": location_data.get("formatted_address", ""),
            "google_place_id": location_data.get("place_id"),
            "latitude": float(location_data.get("latitude")) if location_data.get("latitude") else None,
            "longitude": float(location_data.get("longitude")) if location_data.get("longitude") else None,
            "website": location_data.get("website", ""),
            "restaurant_rating": float(location_data.get("rating")) if location_data.get("rating") else None
        })
except Exception as e:
    st.error(f"❌ Google Maps API error: {str(e)}")
    st.info("💡 Toggle off 'Use Google Maps API' to enter location details manually")
    use_google_api = False


with st.form("manual_location_form"):
    st.write("**Restaurant Information**")
    col1, col2 = st.columns(2)
    with col1:
        restaurant_name = st.text_input(
            "Restaurant Name*",
            value=st.session_state.form_data["restaurant"]["name"],
            placeholder="e.g., Vovo Telo Bakery & Café"
        )
        website = st.text_input(
            "Website",
            value=st.session_state.form_data["restaurant"]["website"],
            placeholder="https://example.com"
        )
        latitude = st.number_input(
            "Latitude",
            value=st.session_state.form_data["restaurant"]["latitude"],
            format="%.6f",
            help="Optional - GPS coordinates"
        )
        longitude = st.number_input(
            "Longitude",
            value=st.session_state.form_data["restaurant"]["longitude"],
            format="%.6f",
            help="Optional - GPS coordinates"
        )
    with col2:
        google_place_id = st.text_input(
            "Google Place Id",
            value=st.session_state.form_data["restaurant"]["google_place_id"],
            placeholder=""
        )
        google_rating = st.number_input(
            "Google Rating",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state.form_data["restaurant"]["restaurant_rating"]) if (
                st.session_state.form_data["restaurant"]["restaurant_rating"]
            ) else 0.0,
            step=0.1,
            help="Optional - Google's rating for this place"
        )
        address = st.text_area(
            "Address",
            value=st.session_state.form_data["restaurant"]["address"],
            placeholder="Full address of the restaurant"
        )
    submitted = st.form_submit_button("📍 Save Location Details")
    if submitted:
        if restaurant_name.strip():
            st.session_state.form_data["restaurant"].update({
                "name": restaurant_name,
                "address": address if address.strip() else None,
                "google_place_id": google_place_id if google_place_id.strip() else None,
                "latitude": latitude if latitude != 0.0 else None,
                "longitude": longitude if longitude != 0.0 else None,
                "website": website if website.strip() else None,
                "restaurant_rating": google_rating if google_rating > 0.0 else None
            })
            st.success(f"✅ Location details saved for '{restaurant_name}'")
        else:
            st.error("❌ Restaurant name is required")


if st.session_state.form_data["restaurant"]["name"]:
    st.subheader("⭐ Your Rating")

    with st.form("rating_form"):
        st.write("**User Information**")
        st.write("Tell us about the person making the rating!")
        col1, col2 = st.columns(2)

        with col1:
            user_name = st.text_input(
                "Your Name*",
                placeholder="Enter your name"
            )

        with col2:
            user_email = st.text_input(
                "Email (Optional)",
                placeholder="your.email@example.com"
            )
        st.write("**Rating Details**")
        col1, col2 = st.columns(2)
        with col1:
            price_zar = st.number_input(
                "Price (ZAR)*",
                min_value=0.0,
                value=None,
                placeholder=0.0,
                step=0.50,
                format="%.2f",
                help="Price of the cortado in South African Rand"
            )
        with col2:
            num_shots = st.selectbox(
                "Number of espresso shots",
                options=[None, "single", "double"],
                index=st.session_state.form_data["rating"]["num_shots"],
                help="How many espresso shots were in your cortado?"
            )
        st.write("Rating")
        stars = st_star_rating(
            None,
            size=30,
            maxValue=5,
            defaultValue=0,
            key="rating"
        )
        cookie = st.checkbox(
            "🍪 Did they include a cookie?",
            value=st.session_state.form_data["rating"]["cookie"],
            help="Did they serve a cookie with your cortado?"
        )
        take_away = st.checkbox(
            "🥡 Did you get it as a take-away?",
            value=st.session_state.form_data["rating"]["take_away"],
            help="Did you get your cortado as a take-away?"
        )
        notes = st.text_area(
            "Notes (Optional)",
            value=st.session_state.form_data["rating"]["notes"],
            placeholder="Share your thoughts about the cortado...",
            height=100
        )
        submitted = st.form_submit_button("🎯 Submit Rating", use_container_width=True)
        if submitted:
            if not user_name.strip():
                st.error("❌ Please enter your name")
            elif (
                price_zar and
                price_zar <= 0
            ):
                st.error("❌ Please enter a valid price")
            else:
                with st.spinner("Submitting your rating..."):
                    try:
                        restaurant = DC.Restaurant(
                            name=st.session_state.form_data["restaurant"]["name"],
                            address=st.session_state.form_data["restaurant"]["address"],
                            google_place_id=st.session_state.form_data["restaurant"]["google_place_id"],
                            latitude=st.session_state.form_data["restaurant"]["latitude"],
                            longitude=st.session_state.form_data["restaurant"]["longitude"],
                            website=st.session_state.form_data["restaurant"]["website"],
                            restaurant_rating=st.session_state.form_data["restaurant"]["restaurant_rating"]
                        )
                        user = DC.User(
                            name=user_name.strip(),
                            email=user_email.strip() if user_email.strip() else None
                        )
                        rating = DC.Rating(
                            stars=stars,
                            price_zar=price_zar,
                            notes=notes.strip() if notes.strip() else None,
                            cookie=cookie,
                            take_away=take_away,
                            num_shots=num_shots
                        )
                        cortado_instance.new_rating(
                            restaurant=restaurant,
                            user=user,
                            rating=rating
                        )
                        st.success("✅ Rating submitted successfully!")
                        time.sleep(2)
                        clear_form()
                        st.rerun()
                    except Exception as e:
                        print(e)
                        st.error("Please try again or contact support if the problem persists.")
else:
    st.info("👆 Please select or enter a restaurant location first")

st.divider()
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 View Ratings Dashboard", use_container_width=True):
        st.switch_page("main.py")

with col2:
    if st.button("🔙 Reset Form", use_container_width=True):
        clear_form()
        st.rerun()
