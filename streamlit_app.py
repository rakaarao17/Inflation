import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Analysing Indian Inflation Trends and Forecasting CPI Changes",
    page_icon="💰",
    layout="wide"
)

# Cache data loading to improve performance
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, parse_dates=["Date"])
        
        # Create additional columns
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.strftime('%b')
        df['Inflation_Combined'] = df['Inflation Rate'].fillna(df['Forecast_Inflation'])
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Sidebar Controls
st.sidebar.title("🔧 Dashboard Controls")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Dashboard Title (shown regardless of file upload)
st.title("📊 India's Inflation Analysis Dashboard (2014–2028)")
st.caption("Developed as part of M.Tech Analytics Mini Project 🔬")

st.markdown("""
Welcome to a professional analytics dashboard built using Python and Streamlit to monitor and forecast inflation trends.  
This combines actual data and future forecasts in an interactive, presentation-ready format.
""")

# Check if a file is uploaded
if uploaded_file is not None:
    # Load and process the data
    df = load_data(uploaded_file)

    if df is not None:
        # Sidebar controls (only shown after file upload)
        year_range = st.sidebar.slider("Year Range", int(df['Year'].min()), int(df['Year'].max()), (2014, 2028))
        chart_type = st.sidebar.radio("Chart Section", ["Line Charts", "Heatmap", "Raw Data"])
        show_stats = st.sidebar.checkbox("Show Summary Stats", value=True)

        # Filter by year
        filtered_df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

        # --- Summary Stats
        if show_stats:
            # Max / Min / Avg forecast
            max_inflation_value = df["Inflation Rate"].max()
            min_inflation_value = df["Inflation Rate"].min()
            
            max_inflation_date = pd.to_datetime(
                df[df["Inflation Rate"] == max_inflation_value]["Date"].values[0]
            ).strftime("%B %Y")
            
            min_inflation_date = pd.to_datetime(
                df[df["Inflation Rate"] == min_inflation_value]["Date"].values[0]
            ).strftime("%B %Y")
            
            avg_forecast = df["Forecast_Inflation"].mean()

            # Layout columns
            col1, col2, col3 = st.columns(3)

            # 🔺 Max Inflation – Red ▲ + red date
            col1.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #eee; border-radius: 12px; background-color:#ffecec;">
                <h5 style="margin: 0; color: #d62728;">📈 Max Inflation</h5>
                <h3 style="margin: 0; color: #d62728;">{max_inflation_value:.2f}%</h3>
                <p style="margin: 0;">
                    <span style='font-size:18px; color: #d62728;'>▲</span>
                    <span style='color:#d62728;'>{max_inflation_date}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            # 🔻 Min Inflation – Green ▼ + green date
            col2.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #eee; border-radius: 12px; background-color:#e6ffed;">
                <h5 style="margin: 0; color: #2ca02c;">📉 Min Inflation</h5>
                <h3 style="margin: 0; color: #2ca02c;">{min_inflation_value:.2f}%</h3>
                <p style="margin: 0;">
                    <span style='font-size:18px; color: #2ca02c;'>▼</span>
                    <span style='color:#2ca02c;'>{min_inflation_date}</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            # ℹ️ Forecast – Blue card + neutral coloring
            col3.markdown(f"""
            <div style="padding: 1rem; border: 1px solid #eee; border-radius: 12px; background-color:#eaf4ff;">
                <h5 style="margin: 0; color: #007acc;">📘 Avg Forecast (2025–2028)</h5>
                <h3 style="margin: 0; color: #007acc;">{avg_forecast:.2f}%</h3>
                <p style="margin: 0;">
                    <span style='font-size:18px; color: #1f77b4;'>ℹ️</span>
                    <span style='color:#1f77b4;'>Informational</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Add pleasing space between metrics and visualizations
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")  # Horizontal separator
        st.markdown("<br>", unsafe_allow_html=True)

        # Dynamically determine forecast start date
        forecast_start = df[df['Inflation Rate'].isna()]['Date'].min()

        # --- Chart Sections
        if chart_type == "Line Charts":
            st.subheader("📈 Monthly Inflation Rate (Actual + Forecast)")

            fig = px.line(filtered_df, x='Date', y='Inflation_Combined',
                          title="Inflation Trend Over Time (Actual + Forecast)",
                          labels={"Inflation_Combined": "Inflation (%)"},
                          color_discrete_sequence=["#1f77b4"])

            # ✅ Add vertical dashed line for forecast start
            if pd.notna(forecast_start):
                fig.add_shape(
                    type="line",
                    x0=forecast_start,
                    x1=forecast_start,
                    y0=0,
                    y1=1,
                    xref='x',
                    yref='paper',
                    line=dict(color="red", width=2, dash="dash")
                )

                fig.add_annotation(
                    x=forecast_start,
                    yref="paper",
                    y=1.05,
                    showarrow=False,
                    text=f"📉 Forecast Starts ({forecast_start.strftime('%Y')})",
                    bgcolor="#ffffff",
                    font=dict(color="red", size=12)
                )

            st.plotly_chart(fig, use_container_width=True)

            # ✅ ROLLING AVG BLOCK - properly aligned
            st.subheader("🌀 Rolling Average Inflation Rate")
            fig2 = px.line(filtered_df, x="Date", y="Rolling_Avg_Inflation",
                           title="Rolling Average Inflation Trend",
                           labels={"Rolling_Avg_Inflation": "Rolling Avg (%)"},
                           color_discrete_sequence=["#ff7f0e"])
            st.plotly_chart(fig2, use_container_width=True)

            # ✅ ACTUAL vs FORECAST
            st.subheader("🔮 Actual vs Forecast Inflation Curve")
            fig3 = px.line(df, x="Date", y=["Inflation Rate", "Forecast_Inflation"],
                           labels={"value": "Inflation (%)", "variable": "Data Type"},
                           color_discrete_map={"Inflation Rate": "green", "Forecast_Inflation": "red"},
                           title="Actual vs Forecast Comparison")
            st.plotly_chart(fig3, use_container_width=True)

        elif chart_type == "Heatmap":
            st.subheader("🔥 Month-Year Heatmap of Inflation Rates")

            heat_df = filtered_df.copy()
            pivot = heat_df.pivot_table(index='Month', columns='Year', values='Inflation_Combined')
            # Reorder months
            all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            pivot = pivot.reindex(all_months)

            fig4, ax4 = plt.subplots(figsize=(14, 6))
            sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=.5, ax=ax4)
            ax4.set_title("Monthly Inflation Heatmap by Year")
            st.pyplot(fig4)

        elif chart_type == "Raw Data":
            st.subheader("📄 View Filtered Raw Dataset")
            st.dataframe(filtered_df, use_container_width=True)

            csv = filtered_df.to_csv(index=False).encode()
            st.download_button("📥 Download Filtered CSV", csv, "filtered_inflation.csv", "text/csv")

        # --- Footer
        st.markdown("---")
        st.markdown("""
        📘 **Project by:** Arasada Rakesh | M.Tech – Data Science  
        📂 **Data Source:** Ministry of Statistics and Programme Implementation (MOSPI), Government of India.
        """)
else:
    # Message shown when no file is uploaded
    st.info("Please upload a CSV file using the sidebar to view the dashboard content.")
