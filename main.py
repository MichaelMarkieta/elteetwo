import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(page_title="Lactate Threshold Dashboard", layout="wide")
st.title("🏃‍♂️ Lactate Threshold Historical Dashboard (2023 - 2025)")
st.markdown(
    "Cross-examine step-test curves, longitudinal threshold shifts, and training zones over the last 3 years."
)

# -----------------------------------------------------------------------------
# 1. HARDCODED HISTORICAL DATASET
# -----------------------------------------------------------------------------

# Summary Threshold Data
thresholds_data = [
    {
        "Date": "2023-07-19",
        "LT1_Speed": 10.20,
        "LT1_Pace": "5:53",
        "LT1_HR": 163,
        "LT2_Speed": 12.10,
        "LT2_Pace": "4:58",
        "LT2_HR": 179,
    },
    {
        "Date": "2024-02-07",
        "LT1_Speed": 10.56,
        "LT1_Pace": "5:42",
        "LT1_HR": 173,
        "LT2_Speed": 12.31,
        "LT2_Pace": "4:53",
        "LT2_HR": 185,
    },
    {
        "Date": "2025-01-15",
        "LT1_Speed": 11.00,
        "LT1_Pace": "5:27",
        "LT1_HR": 171,
        "LT2_Speed": 12.57,
        "LT2_Pace": "4:46",
        "LT2_HR": 181,
    },
    {
        "Date": "2025-05-17",
        "LT1_Speed": 11.70,
        "LT1_Pace": "5:08",
        "LT1_HR": 168,
        "LT2_Speed": 13.51,
        "LT2_Pace": "4:26",
        "LT2_HR": 180,
    },
    {
        "Date": "2025-08-09",
        "LT1_Speed": 11.60,
        "LT1_Pace": "5:10",
        "LT1_HR": 172,
        "LT2_Speed": 13.62,
        "LT2_Pace": "4:24",
        "LT2_HR": 184,
    },
]
df_thresh = pd.DataFrame(thresholds_data)
df_thresh["Date_Parsed"] = pd.to_datetime(df_thresh["Date"])

# Raw Stage Curve Data
raw_curves = {
    "2023-07-19": pd.DataFrame(
        {
            "Speed": [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            "Lactate": [2.1, 2.3, 2.2, 2.8, 3.8, 5.8, 7.4, 11.0],
            "HR": [148, 162, 167, 174, 182, 187, 192, 194],
        }
    ),
    "2024-02-07": pd.DataFrame(
        {
            "Speed": [8.0, 9.0, 10.0, 11.0, 12.0, 13.0],
            "Lactate": [1.9, 1.9, 2.4, 2.6, 3.4, 5.5],
            "HR": [140, 152, 168, 176, 182, 188],
        }
    ),
    "2025-01-15": pd.DataFrame(
        {
            "Speed": [8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0],
            "Lactate": [1.4, 1.3, 1.7, 1.9, 3.3, 4.8, 6.0],
            "HR": [134, 146, 157, 171, 179, 182, 186],
        }
    ),
    "2025-05-17": pd.DataFrame(
        {
            "Speed": [9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0],
            "Lactate": [1.5, 1.5, 1.7, 2.3, 3.0, 5.1, 7.2],
            "HR": [146, 155, 161, 172, 178, 182, 187],
        }
    ),
    "2025-08-09": pd.DataFrame(
        {
            "Speed": [10.0, 11.0, 12.0, 13.0, 14.0],
            "Lactate": [1.4, 1.2, 2.2, 2.8, 4.8],
            "HR": [156, 167, 176, 181, 186],
        }
    ),
}

# -----------------------------------------------------------------------------
# 2. DASHBOARD TABS
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📈 Curve Overlap Matrix", "📊 Longitudinal Trends", "🔀 Training Zone Comparison"]
)

# --- TAB 1: CURVE OVERLAP MATRIX ---
with tab1:
    st.subheader("Raw Step-Test Curve Comparison")
    st.markdown("Select specific test dates to superimpose your lactate and heart rate curves.")
    
    selected_dates = st.multiselect("Select test dates to overlay:", list(raw_curves.keys()), default=list(raw_curves.keys())[-2:])
    
    # Add toggles side-by-side
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        show_lactate = st.toggle("Show Blood Lactate", value=True)
    with t_col2:
        show_hr = st.toggle("Show Heart Rate", value=True)
        
    # SMOOTHING FUNCTION
    def get_smooth_curve(x, y, degree=3, points=100):
        """Calculates a polynomial line of best fit for smooth plotting."""
        coefficients = np.polyfit(x, y, degree)
        poly_func = np.poly1d(coefficients)
        x_smooth = np.linspace(min(x), max(x), points)
        y_smooth = poly_func(x_smooth)
        return x_smooth, y_smooth
    
    if selected_dates:
        fig_curve = make_subplots(specs=[[{"secondary_y": True}]])
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, date in enumerate(selected_dates):
            df_stage = raw_curves[date]
            color = colors[i % len(colors)]
            
            # Conditionally render Lactate Curve
            if show_lactate:
                # 1. Plot the raw data as unconnected dots
                fig_curve.add_trace(
                    go.Scatter(x=df_stage["Speed"], y=df_stage["Lactate"], name=f"Raw Lactate ({date})",
                               line=dict(color=color), mode='markers', marker=dict(size=8), showlegend=False),
                    secondary_y=False
                )
                
                # 2. Plot the smoothed line of best fit
                x_smooth, y_smooth = get_smooth_curve(df_stage["Speed"], df_stage["Lactate"])
                fig_curve.add_trace(
                    go.Scatter(x=x_smooth, y=y_smooth, name=f"Lactate Trend ({date})",
                               line=dict(color=color, width=3, shape='spline'), mode='lines'),
                    secondary_y=False
                )
                
            # Conditionally render Heart Rate Curve
            if show_hr:
                # 1. Plot the raw HR data as unconnected dots
                fig_curve.add_trace(
                    go.Scatter(x=df_stage["Speed"], y=df_stage["HR"], name=f"Raw HR ({date})",
                               line=dict(color=color), mode='markers', marker=dict(size=6, symbol='x'), opacity=0.6, showlegend=False),
                    secondary_y=True
                )
                
                # 2. Plot the smoothed HR line (using degree=2 for HR as it is more linear)
                hr_x_smooth, hr_y_smooth = get_smooth_curve(df_stage["Speed"], df_stage["HR"], degree=2)
                fig_curve.add_trace(
                    go.Scatter(x=hr_x_smooth, y=hr_y_smooth, name=f"HR Trend ({date})",
                               line=dict(color=color, width=2, dash='dash', shape='spline'), mode='lines', opacity=0.6),
                    secondary_y=True
                )
                
        fig_curve.update_xaxes(title_text="Treadmill Speed (km/h)")
        
        # Logarithmic Y-axis for Lactate
        fig_curve.update_yaxes(
            title_text="Blood Lactate (mmol/L)", 
            type="log", 
            tickvals=[1, 1.5, 2, 3, 4, 6, 8, 12],
            secondary_y=False
        )
        fig_curve.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=True)
        fig_curve.update_layout(height=600, hovermode="x unified", legend=dict(x=0.01, y=0.99))
        
        st.plotly_chart(fig_curve, use_container_width=True)
    else:
        st.warning("Please select at least one test date.")

# --- TAB 2: LONGITUDINAL TRENDS ---
with tab2:
    st.subheader("Milestone Tracking Over Time")

    metric_choice = st.radio(
        "Select metric to view over time:", ["Speed (km/h)", "Heart Rate (bpm)"]
    )

    fig_trend = go.Figure()

    if metric_choice == "Speed (km/h)":
        fig_trend.add_trace(
            go.Scatter(
                x=df_thresh["Date"],
                y=df_thresh["LT1_Speed"],
                name="LT1 (Aerobic)",
                line=dict(color="green", width=3),
                mode="lines+markers+text",
                text=df_thresh["LT1_Pace"],
                textposition="top center",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=df_thresh["Date"],
                y=df_thresh["LT2_Speed"],
                name="LT2 (Anaerobic)",
                line=dict(color="red", width=3),
                mode="lines+markers+text",
                text=df_thresh["LT2_Pace"],
                textposition="top center",
            )
        )
        fig_trend.update_yaxes(title_text="Speed (km/h)")
    else:
        fig_trend.add_trace(
            go.Scatter(
                x=df_thresh["Date"],
                y=df_thresh["LT1_HR"],
                name="LT1 HR",
                line=dict(color="green", width=3, dash="dot"),
                mode="lines+markers",
            )
        )
        fig_trend.add_trace(
            go.Scatter(
                x=df_thresh["Date"],
                y=df_thresh["LT2_HR"],
                name="LT2 HR",
                line=dict(color="red", width=3, dash="dot"),
                mode="lines+markers",
            )
        )
        fig_trend.update_yaxes(title_text="Heart Rate (bpm)")

    fig_trend.update_xaxes(title_text="Test Date")
    fig_trend.update_layout(height=500, hovermode="closest")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.dataframe(df_thresh.drop(columns=["Date_Parsed"]))

# --- TAB 3: TRAINING ZONE COMPARISON ---
with tab3:
    st.subheader("Zone Boundary Shifts")
    st.markdown("Compare the shifting pace ranges between two testing periods.")

    # Simple explicit zone extraction for demonstration based on raw profile data
    col1, col2 = st.columns(2)
    with col1:
        date_a = st.selectbox("Baseline Test:", df_thresh["Date"].unique(), index=0)
    with col2:
        date_b = st.selectbox(
            "Comparison Test:", df_thresh["Date"].unique(), index=len(df_thresh) - 1
        )

    row_a = df_thresh[df_thresh["Date"] == date_a].iloc[0]
    row_b = df_thresh[df_thresh["Date"] == date_b].iloc[0]

    st.write(
        f"**LT2 Speed Shift:** {row_a['LT2_Speed']} km/h → {row_b['LT2_Speed']} km/h (Pace: {row_a['LT2_Pace']} → {row_b['LT2_Pace']})"
    )
