import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

st.set_page_config(page_title="Hotel Price Analysis", page_icon=":bar_chart", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
image = Image.open('hotellogo.jpg')
col1, col2 = st.columns([0.2,0.8])
with col1:
    st.image(image,width=200)
    
with col2:
    st.header('Hotel Price Analyser', divider='rainbow')
    

# Function to fetch data from the SQLite database based on user input
def fetch_data(region=None, country=None, month=None):
    print("Inside fetch_data function")  # Add print statement
    conn = sqlite3.connect("/fake_hotel_pricing_with1000entries.db")
    print("Connection established")  # Add print statement

    query = "SELECT * FROM hotel_pricing"
    conditions = []

    if region:
        conditions.append(f"region = '{region}'")
    if country:
        conditions.append(f"country = '{country}'")
    if month:
        conditions.append(f"month = '{month}'")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit app
def main():
    print("Inside main function")  # Add print statement
    st.title("Hotel Pricing Data Explorer")

    # Fetch unique values for regions, countries, and months
    conn = sqlite3.connect("/fake_hotel_pricing_with1000entries.db")
    print("Connection established")  # Add print statement
    regions = pd.read_sql("SELECT DISTINCT region FROM hotel_pricing", conn)["region"].tolist()
    countries = pd.read_sql("SELECT DISTINCT country FROM hotel_pricing", conn)["country"].tolist()
    months = pd.read_sql("SELECT DISTINCT month FROM hotel_pricing", conn)["month"].tolist()
    conn.close()
    print("Connection closed")  # Add print statement

    # Sidebar filters
    st.sidebar.header("Filters")
    selected_region = st.sidebar.selectbox("Select Region", ["All"] + regions)

    # Dynamically update country options based on selected region
    if selected_region != "All":
        conn = sqlite3.connect("/fake_hotel_pricing_with1000entries.db")
        print("Connection established")  # Add print statement
        countries = pd.read_sql(f"SELECT DISTINCT country FROM hotel_pricing WHERE region = '{selected_region}'", conn)["country"].tolist()
        conn.close()
        print("Connection closed")  # Add print statement
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries)

    selected_month = st.sidebar.selectbox("Select Month", ["All"] + months)

    # Fetch data based on filters
    filtered_data = fetch_data(region=selected_region if selected_region != "All" else None,
                               country=selected_country if selected_country != "All" else None,
                               month=selected_month if selected_month != "All" else None)

    # Create two columns layout
    col1, col2 = st.columns([2, 3])

    with col1:
        # Display filtered data
        st.subheader("Filtered Data")
        # Exclude the 'id' column from the DataFrame
        filtered_data_display = filtered_data.drop(columns=['id'], errors='ignore')
        st.write(filtered_data_display)

    with col2:
        # Display pie chart
        st.subheader("Price Distribution")
        if not filtered_data.empty:
            price_distribution = filtered_data["price"].value_counts()
            if len(price_distribution) > 1:
                fig, ax = plt.subplots()
                ax.pie(price_distribution, labels=price_distribution.index, autopct='%1.1f%%', colors=sns.color_palette("pastel"))
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                ax.set_title("Price Distribution")
                st.pyplot(fig)
            else:
                st.write("Not enough data to display a pie chart.")
        else:
            st.write("No data to display.")

        # Display bar chart
    st.subheader("Prices by Month")
    if not filtered_data.empty:
            if selected_month != "All":
                filtered_data = filtered_data[filtered_data["month"] == selected_month]
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x="month", y="price", data=filtered_data, ax=ax, palette="Blues_d")
            ax.set_xlabel("Month")
            ax.set_ylabel("Price")
            ax.set_title("Prices by Month")
            st.pyplot(fig)

if __name__ == "__main__":
    print("Starting Streamlit app")  # Add print statement
    main()
