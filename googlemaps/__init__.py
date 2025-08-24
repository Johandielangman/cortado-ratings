import streamlit.components.v1 as components
import os


def googlemaps(api_key=None, key=None):
    if api_key is None:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key is None:
        raise ValueError(
            "Google Maps API key is required. Please provide it via:\n"
            "1. googlemaps(api_key='your_key')\n"
            "2. st.secrets['GOOGLE_MAPS_API_KEY']\n"
            "3. Environment variable GOOGLE_MAPS_API_KEY"
        )

    component = components.declare_component(
        "googlemaps",
        path="./googlemaps"
    )

    return component(api_key=api_key, key=key)


googlemaps_component = googlemaps
