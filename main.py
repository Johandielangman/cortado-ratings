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

import os
from datetime import datetime

# =============== // LIBRARY IMPORT // ===============

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# =============== // MODULE IMPORT // ===============

from cortado.db_utils import CortadoDB
from cortado.datastructures import Rating, Restaurant, User

# =============== // PAGE CONFIG // ===============

st.set_page_config(
    page_title="Cortado Ratings",
    page_icon="☕",
    layout="wide"
)

# =============== // CACHING FUNCTIONS // ===============


@st.cache_data(ttl=30)
def get_ratings_data():
    try:
        db = CortadoDB()
        session = db.get_session()
        ratings_query = session.query(
            Rating.id,
            Rating.stars,
            Rating.price_zar,
            Rating.notes,
            Rating.cookie,
            Rating.take_away,
            Rating.num_shots,
            Rating.created_at,
            Restaurant.name.label('restaurant_name'),
            Restaurant.address,
            Restaurant.latitude,
            Restaurant.longitude,
            Restaurant.restaurant_rating,
            User.name.label('user_name'),
            User.email
        ).join(Restaurant).join(User)

        ratings = ratings_query.all()
        session.close()

        data = []
        for rating in ratings:
            data.append({
                'id': rating.id,
                'stars': rating.stars,
                'price_zar': rating.price_zar,
                'notes': rating.notes,
                'cookie': rating.cookie,
                'num_shots': rating.num_shots,
                'take_away': rating.take_away,
                'created_at': datetime.fromtimestamp(rating.created_at),
                'restaurant_name': rating.restaurant_name,
                'address': rating.address,
                'latitude': rating.latitude,
                'longitude': rating.longitude,
                'restaurant_rating': rating.restaurant_rating,
                'user_name': rating.user_name,
                'email': rating.email
            })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=30)
def get_statistics(df):
    if df.empty:
        return {
            'total_ratings': 0,
            'average_rating': 0,
            'total_cookies': 0,
            'unique_restaurants': 0,
            'unique_users': 0,
            'average_price': 0,
            'total_spent': 0
        }
    return {
        'total_ratings': len(df),
        'average_rating': df['stars'].mean(),
        'total_cookies': df['cookie'].sum(),
        'unique_restaurants': df['restaurant_name'].nunique(),
        'unique_users': df['user_name'].nunique(),
        'average_price': df['price_zar'].mean() if df['price_zar'].notna().any() else 0,
        'total_spent': df['price_zar'].sum() if df['price_zar'].notna().any() else 0
    }

# =============== // VISUALIZATION FUNCTIONS // ===============


def create_price_vs_rating_scatter(df):
    if df.empty or df['price_zar'].isna().all():
        return None
    df_clean = df.dropna(subset=['price_zar'])
    fig = px.scatter(
        df_clean,
        x='price_zar',
        y='stars',
        color='restaurant_name',
        size='stars',
        hover_data=['user_name', 'created_at'],
        title="💰 Price vs Rating Analysis"
    )
    fig.update_layout(
        template="plotly_white",
        height=500
    )
    return fig


def create_map_view(df):
    if df.empty or df[['latitude', 'longitude']].isna().all().all():
        return None

    # Filter out rows with missing coordinates
    df_map = df.dropna(subset=['latitude', 'longitude'])
    if df_map.empty:
        return None

    # Calculate center of map
    center_lat = df_map['latitude'].mean()
    center_lon = df_map['longitude'].mean()

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='CartoDB positron'
    )

    # Add markers for each restaurant
    restaurant_data = df_map.groupby(['restaurant_name', 'latitude', 'longitude']).agg({
        'stars': 'mean',
        'id': 'count',
        'cookie': 'sum',
        'address': 'first'
    }).reset_index()

    for _, row in restaurant_data.iterrows():
        if row['stars'] >= 4.5:
            color = 'green'
        elif row['stars'] >= 3.5:
            color = 'orange'
        else:
            color = 'red'
        popup_text = f"""
        <b>{row['restaurant_name']}</b><br>
        Rating: {row['stars']:.1f}⭐<br>
        Total Ratings: {row['id']}<br>
        Cookies: {row['cookie']}🍪<br>
        Address: {row['address'] or 'N/A'}
        """

        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{row['restaurant_name']} ({row['stars']:.1f}⭐)",
            icon=folium.Icon(color=color, icon='coffee', prefix='fa')
        ).add_to(m)
    return m

# =============== // MAIN PAGE // ===============


def quick_stats_view(stats):
    st.subheader("📊 Quick Stats")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric(
            label="Total Ratings",
            value=f"{stats['total_ratings']:,}",
            delta=None
        )
    with col2:
        st.metric(
            label="Average Rating",
            value=f"{stats['average_rating']:.1f}⭐",
            delta=None
        )
    with col3:
        st.metric(
            label="Total Cookies",
            value=f"{stats['total_cookies']}🍪",
            delta=None
        )
    with col4:
        st.metric(
            label="Unique Restaurants",
            value=stats['unique_restaurants'],
            delta=None
        )
    with col5:
        st.metric(
            label="Average Price",
            value=f"R{stats['average_price']:.0f}" if stats['average_price'] > 0 else "N/A",
            delta=None
        )
    with col6:
        st.metric(
            label="Total Spent",
            value=f"R{stats['total_spent']:.0f}" if stats['total_spent'] > 0 else "N/A",
            delta=None
        )
    st.markdown("---")


def main():
    st.title("☕ Cortado Ratings Dashboard")
    st.markdown("---")
    with st.spinner("Loading delicious data... ☕"):
        df = get_ratings_data()
        stats = get_statistics(df)
    if df.empty:
        st.warning("No ratings found! Start by adding some ratings.")
        if st.button("⭐ Add Your First Rating", type="primary", use_container_width=True):
            st.switch_page("pages/new_rating.py")
        return

    quick_stats_view(stats)

    st.write("""
    Welcome to the Cortado ratings Dashboard! Where we like to drink and rate Cortados!

    Please feel free to make a new rating below.
    """)
    if st.button("⭐ Add New Rating", type="primary"):
        st.switch_page("pages/new_rating.py")

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs([
        "🗺️ Map View",
        "📊 Analytics",
        "📋 Data Table",
    ])

    with tab1:
        st.subheader("🗺️ Restaurant Locations")
        map_obj = create_map_view(df)
        if map_obj:
            st_folium(map_obj, height=500, zoom=5, use_container_width=True)
        else:
            st.info("No location data available for restaurants.")

    with tab2:
        st.subheader("📊 Rating Analytics")
        if not df['price_zar'].isna().all():
            fig2 = create_price_vs_rating_scatter(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
    with tab3:
        st.subheader("📋 All Ratings Data")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write("Filters:")
            selected_restaurants = st.multiselect(
                "Filter by Restaurant",
                options=df['restaurant_name'].unique(),
            )
            selected_num_shots = st.multiselect(
                "Filter by Number of Shots",
                options=df['num_shots'].unique(),
            )
            min_rating = st.slider("Minimum Rating", 1, 5, 1)
            show_cookies_only = st.checkbox("Show only cookies 🍪")
            show_take_away_only = st.checkbox("Show only take away 🥡")
        with col2:
            filtered_df = df.copy()
            if selected_restaurants:
                filtered_df = filtered_df[filtered_df['restaurant_name'].isin(selected_restaurants)]

            if selected_num_shots:
                filtered_df = filtered_df[filtered_df['num_shots'].isin(selected_num_shots)]

            if min_rating:
                filtered_df = filtered_df[filtered_df['stars'] >= min_rating]

            if show_cookies_only:
                # pandas best practice: use .loc for boolean indexing
                filtered_df = filtered_df.loc[filtered_df['cookie'] == True]  # noqa: E712

            if show_take_away_only:
                filtered_df = filtered_df.loc[filtered_df['take_away'] == True]  # noqa: E712

            # Display filtered data
            st.dataframe(
                filtered_df[[
                    'created_at', 'restaurant_name', 'stars', 'num_shots', 'price_zar',
                    'cookie', 'take_away', 'notes', 'user_name'
                ]].sort_values('created_at', ascending=False),
                use_container_width=True,
                hide_index=True
            )
    st.markdown("---")
    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Data refreshes every 30 seconds | "
        f"{os.getenv('K_REVISION', '')}"
    )


if __name__ == "__main__":
    main()
