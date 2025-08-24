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

from datetime import datetime

# =============== // LIBRARY IMPORT // ===============

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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


@st.cache_data(ttl=300)
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


@st.cache_data(ttl=300)
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


def create_ratings_distribution_chart(df):
    if df.empty:
        return None
    ratings_count = df['stars'].value_counts().sort_index()
    fig = go.Figure(data=[
        go.Bar(
            x=ratings_count.index,
            y=ratings_count.values,
            text=ratings_count.values,
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="⭐ Rating Distribution",
        xaxis_title="Stars",
        yaxis_title="Number of Ratings",
        template="plotly_white",
        height=400
    )
    return fig


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


def create_restaurant_performance_chart(df):
    if df.empty:
        return None
    restaurant_stats = df.groupby('restaurant_name').agg({
        'stars': ['mean', 'count'],
        'cookie': 'sum',
        'price_zar': 'mean'
    }).round(2)

    restaurant_stats.columns = ['avg_rating', 'total_ratings', 'total_cookies', 'avg_price']
    restaurant_stats = restaurant_stats.reset_index()
    restaurant_stats = restaurant_stats.sort_values('avg_rating', ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=restaurant_stats['restaurant_name'],
        x=restaurant_stats['avg_rating'],
        name='Average Rating',
        orientation='h',
        marker_color='#4ECDC4',
        text=restaurant_stats['avg_rating'],
        textposition='auto',
    ))
    fig.update_layout(
        title="🏆 Restaurant Performance Rankings",
        xaxis_title="Average Rating",
        yaxis_title="Restaurant",
        template="plotly_white",
        height=max(400, len(restaurant_stats) * 50)
    )
    return fig


def create_temporal_analysis(df):
    """Create temporal analysis of ratings"""
    if df.empty:
        return None

    df['date'] = df['created_at'].dt.date
    daily_stats = df.groupby('date').agg({
        'stars': 'mean',
        'id': 'count'
    }).reset_index()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Average Rating Over Time', 'Number of Ratings Over Time'),
        vertical_spacing=0.15
    )
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['stars'],
            mode='lines+markers',
            name='Avg Rating',
            line=dict(color='#FF6B6B', width=3)
        ),
        row=1, col=1
    )
    fig.update_layout(
        title="📈 Ratings Timeline Analysis",
        template="plotly_white",
        height=600
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Map View",
        "📊 Analytics",
        "📈 Trends",
        "📋 Data Table",
        "🏆 Leaderboards"
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
        col1, col2 = st.columns(2)
        with col1:
            fig1 = create_ratings_distribution_chart(df)
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig3 = create_restaurant_performance_chart(df)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
        if not df['price_zar'].isna().all():
            fig2 = create_price_vs_rating_scatter(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
    with tab3:
        st.subheader("� Trends Over Time")
        fig4 = create_temporal_analysis(df)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis.")
    with tab4:
        st.subheader("📋 All Ratings Data")
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_restaurants = st.multiselect(
                "Filter by Restaurant",
                options=df['restaurant_name'].unique(),
            )
        with col2:
            min_rating = st.slider("Minimum Rating", 1, 5, 1)
        with col3:
            show_cookies_only = st.checkbox("Show only cookies 🍪")
        filtered_df = df.copy()
        if selected_restaurants:
            filtered_df = filtered_df[filtered_df['restaurant_name'].isin(selected_restaurants)]
        if min_rating:
            filtered_df = filtered_df[filtered_df['stars'] >= min_rating]

        if show_cookies_only:
            # pandas best practice: use .loc for boolean indexing
            filtered_df = filtered_df.loc[filtered_df['cookie'] == True]  # noqa: E712

        # Display filtered data
        st.dataframe(
            filtered_df[[
                'created_at', 'restaurant_name', 'stars', 'price_zar',
                'cookie', 'user_name', 'notes'
            ]].sort_values('created_at', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    with tab5:
        st.subheader("🏆 Leaderboards")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 🥇 Top Restaurants by Rating")
            restaurant_leaderboard = df.groupby('restaurant_name').agg({
                'stars': 'mean',
                'id': 'count'
            }).round(2).sort_values('stars', ascending=False).head(10)
            restaurant_leaderboard.columns = ['Avg Rating', 'Total Ratings']
            st.dataframe(restaurant_leaderboard, use_container_width=True)
        with col2:
            st.markdown("##### 🍪 Cookie Champions")
            cookie_leaderboard = df[df['cookie'] == True].groupby('restaurant_name').agg({   # noqa: E712
                'cookie': 'count'
            }).sort_values('cookie', ascending=False).head(10)
            cookie_leaderboard.columns = ['Cookies Earned']
            st.dataframe(cookie_leaderboard, use_container_width=True)
        st.markdown("##### 👥 Most Active Reviewers")
        user_leaderboard = df.groupby('user_name').agg({
            'id': 'count',
            'stars': 'mean',
            'cookie': 'sum'
        }).round(2).sort_values('id', ascending=False).head(10)
        user_leaderboard.columns = ['Total Reviews', 'Avg Rating Given', 'Cookies Found']
        st.dataframe(user_leaderboard, use_container_width=True)
    st.markdown("---")
    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Data refreshes every 5 minutes"
    )


if __name__ == "__main__":
    main()
