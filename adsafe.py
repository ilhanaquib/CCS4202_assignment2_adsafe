import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import google.generativeai as genai

# Page layout configuration
st.set_page_config(page_title="AdSpend SafeZones", layout="wide")

st.title("🎯 AdSpend SafeZones Optimizer")
st.subheader("Algorithmic Budget Fencing Prototype Powered by Google Gemini")
st.write("---")

# ─── SECURE API KEY RESOLUTION (OPTION 1) ───
# Check if the key exists in Streamlit Cloud Secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Local fallback option if secrets.toml doesn't exist on your machine
    st.sidebar.header("🔑 API Authentication")
    api_key = st.sidebar.text_input(
        "Enter Gemini API Key:",
        type="password",
        help="Paste your free key from Google AI Studio here for local testing.",
    )

# Formatting Guide expander
with st.expander("ℹ️ How should my CSV file be formatted?", expanded=False):
    st.markdown("""
    To map your ad campaign data correctly, your uploaded CSV file **must** include these exact column headers:
    * `Campaign/Target Name` : The label of the audience segment or keyword.
    * `CPC` : Cost Per Click in local currency (e.g., RM 1.50). *Maps to the X-axis.*
    * `CVR` : Conversion Rate expressed as a percentage value (e.g., 5.5 for 5.5%). *Maps to the Y-axis.*
    """)
    sample_df = pd.DataFrame(
        {
            "Campaign/Target Name": [
                "KL Tech Lovers",
                "Selangor Coffee",
                "Penang Foodies",
            ],
            "CPC": [1.20, 3.80, 0.90],
            "CVR": [6.5, 1.2, 7.8],
        }
    )
    st.dataframe(sample_df, hide_index=True)

# Main File Upload Interface
st.write("### 📂 Step 1: Upload Your Performance Report")
uploaded_file = st.file_uploader("Upload your campaign CSV file:", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if "CPC" in df.columns and "CVR" in df.columns:
            st.success(
                "✨ Report loaded successfully! Core targeting coordinates found."
            )

            if "Campaign/Target Name" not in df.columns:
                df["Campaign/Target Name"] = [f"Segment {i+1}" for i in range(len(df))]

            points = df[["CPC", "CVR"]].values

            if len(np.unique(points, axis=0)) < 3:
                st.error(
                    "❌ The algorithm requires at least 3 distinct spatial coordinates to compute a closed geometric boundary."
                )
                st.stop()

            st.write("---")
            st.write("### 📊 Step 2: Campaign Distribution Map")

            if st.button("🚀 Run Convex Hull Optimizer & Ask Gemini", type="primary"):
                # Validate API key exists before triggering code
                if not api_key:
                    st.error(
                        "⚠️ Gemini API Key not found. Please set it up in Streamlit Cloud Secrets or enter it via the sidebar fallback."
                    )
                    st.stop()

                # Configure the Gemini Engine Client
                genai.configure(api_key=api_key)

                # Execute Convex Hull Algorithm
                hull = ConvexHull(points)
                hull_indices = hull.vertices

                total_segments = len(points)
                champions_count = len(hull_indices)
                outliers_count = total_segments - champions_count

                champions_df = df.iloc[hull_indices]
                outliers_df = df.drop(df.index[hull_indices])

                # Financial Math Simulation Formulas
                simulated_waste_ratio = outliers_count / total_segments
                simulated_savings_rm = 10000 * (simulated_waste_ratio * 0.35)

                st.write("### 💰 Step 3: Optimization & Cost Savings Result Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="🔴 Flagged Waste Outliers",
                        value=f"{outliers_count} Targets",
                    )
                with col2:
                    st.metric(
                        label="🛡️ SafeZone Champions Inside Fence",
                        value=f"{champions_count} Targets",
                    )
                with col3:
                    st.metric(
                        label="💵 Potential Ad Spend Waste Cut",
                        value=f"RM {simulated_savings_rm:,.2f}",
                    )

                # Plotting the Bounded Hull Map
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.scatter(
                    points[:, 0],
                    points[:, 1],
                    color="#EF4444",
                    alpha=0.6,
                    label="Wasteful Outliers (Cut Spend)",
                    zorder=2,
                )
                ax.scatter(
                    points[hull_indices, 0],
                    points[hull_indices, 1],
                    color="#10B981",
                    s=120,
                    edgecolor="black",
                    label="Champion Benchmarks",
                    zorder=4,
                )

                for simplex in hull.simplices:
                    ax.plot(
                        points[simplex, 0],
                        points[simplex, 1],
                        color="#10B981",
                        linestyle="-",
                        linewidth=2.5,
                        zorder=3,
                    )

                ax.fill(
                    points[hull_indices, 0],
                    points[hull_indices, 1],
                    color="#10B981",
                    alpha=0.15,
                    label="SafeZone Enclosure",
                )
                ax.set_xlabel("Cost Per Click (CPC) - Lower is Better")
                ax.set_ylabel("Conversion Rate (CVR %) - Higher is Better")
                ax.set_title(
                    "Algorithmic Convex Hull SafeZone Partitioning Map",
                    fontweight="bold",
                )
                ax.grid(True, linestyle="--", alpha=0.4)
                ax.legend(loc="upper right")
                st.pyplot(fig)

                # ─── GEMINI GENERATIVE COMPILATION ───
                st.write("---")
                st.write("### 🤖 Step 4: Live Gemini AI Consultant Insights")

                champions_text = champions_df[
                    ["Campaign/Target Name", "CPC", "CVR"]
                ].to_string(index=False)
                outliers_text = (
                    outliers_df[["Campaign/Target Name", "CPC", "CVR"]].to_string(
                        index=False
                    )
                    if not outliers_df.empty
                    else "None"
                )

                ai_prompt = f"""
                You are an expert digital marketing consultant analyzing a mathematical campaign optimization chart.
                We ran a Convex Hull algorithm on the client's ad spend coordinates.
                The algorithm found {champions_count} Champion segments forming the geometric SafeZone, and flagged {outliers_count} segments as wasteful outliers outside the boundary.
                
                Here are the Champion Segments (Inside the green fence):
                {champions_text}
                
                Here are the Outlier Segments (Outside the fence bleeding cash):
                {outliers_text}
                
                Please write a brief, professional summary report for the business owner in Markdown format. 
                Include:
                1. What this graph fundamentally means for their cash flow.
                2. Explicit actionable advice on how to change their settings directly inside Google Ads or Meta Ads Manager to pause the specific bad outliers named above.
                3. Tactical targeting adjustment tips to copy their anchors.
                Keep it concise, direct, and conversational.
                """

                with st.spinner(
                    "🧠 Sending campaign metrics to Gemini AI core systems..."
                ):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash")
                        response = model.generate_content(ai_prompt)

                        with st.chat_message("assistant"):
                            st.markdown(response.text)

                    except Exception as ai_err:
                        st.error(
                            f"Failed to communicate with Google AI Servers: {str(ai_err)}"
                        )
            else:
                # Baseline map state before button click
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.scatter(points[:, 0], points[:, 1], color="#9CA3AF", alpha=0.8, s=60)
                ax.set_xlabel("Cost Per Click (CPC)")
                ax.set_ylabel("Conversion Rate (CVR %)")
                st.pyplot(fig)
                st.caption(
                    "Click the primary button above to evaluate your coordinates and trigger the automated AI analysis ecosystem."
                )
        else:
            st.error(
                "❌ Validation Failed! Your CSV file must explicitly include 'CPC' and 'CVR' column headers."
            )
    except Exception as e:
        st.error(f"❌ Error compiling file properties: {str(e)}")
else:
    st.info(
        "💡 Application standby state. Drag-and-drop or load a campaign spreadsheet to launch the simulation dashboard engine."
    )
