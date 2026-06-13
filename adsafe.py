import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import google.generativeai as genai

# Page layout configuration
st.set_page_config(page_title="AdSpend SafeZones", layout="wide")

st.title("AdSpend SafeZones Optimizer")
st.subheader("Algorithmic Budget Fencing Prototype Powered by Google Gemini")
st.write("---")

# SECURE API KEY RESOLUTION (OPTION 1)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.sidebar.header("API Authentication")
    api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

st.write("### Step 1: Upload Your Performance Report")
st.caption(
    "Supports direct, unedited CSV exports from Google Ads Manager or Meta Ads Manager."
)
uploaded_file = st.file_uploader("Upload your campaign CSV file:", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # AUTOMATIC COLUMN MAPPING MATRIX
        name_variants = [
            "Campaign",
            "Campaign Name",
            "Campaign/Target Name",
            "Ad Set Name",
            "Ad Set",
            "Placement",
        ]
        cpc_variants = [
            "CPC",
            "Avg. CPC",
            "Average CPC",
            "Cost per inline link click (CPC)",
            "Cost per link click",
            "Cost Per Click",
        ]
        cvr_variants = [
            "CVR",
            "Conv. rate",
            "Conversion Rate",
            "Link click conversion rate",
            "Conversion Rate (%)",
            "Result Rate",
        ]

        matched_name_col = next(
            (col for col in df.columns if col in name_variants), None
        )
        matched_cpc_col = next((col for col in df.columns if col in cpc_variants), None)
        matched_cvr_col = next((col for col in df.columns if col in cvr_variants), None)

        if matched_cpc_col and matched_cvr_col:
            st.success(
                f"Parser connected! Mapping identified: Axis X = '{matched_cpc_col}', Axis Y = '{matched_cvr_col}'"
            )

            df_clean = pd.DataFrame()
            if matched_name_col:
                df_clean["Campaign/Target Name"] = df[matched_name_col]
            else:
                df_clean["Campaign/Target Name"] = [
                    f"Segment {i+1}" for i in range(len(df))
                ]

            df_clean["CPC"] = pd.to_numeric(
                df[matched_cpc_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors="coerce",
            )
            df_clean["CVR"] = pd.to_numeric(
                df[matched_cvr_col].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors="coerce",
            )
            df_clean = df_clean.dropna(subset=["CPC", "CVR"]).reset_index(drop=True)

            points = df_clean[["CPC", "CVR"]].values

            if len(np.unique(points, axis=0)) < 3:
                st.error(
                    "The algorithm requires at least 3 distinct spatial coordinates to compute a closed geometric boundary."
                )
                st.stop()

            st.write("---")
            st.write("### Step 2: Campaign Distribution Map")

            if st.button("Run Convex Hull Optimizer & Ask Gemini", type="primary"):
                if not api_key:
                    st.error(
                        "Gemini API Key not found. Please set it up in Streamlit Cloud Secrets or enter it via the sidebar fallback."
                    )
                    st.stop()

                genai.configure(api_key=api_key)

                hull = ConvexHull(points)
                hull_indices = hull.vertices

                total_segments = len(points)
                champions_count = len(hull_indices)
                outliers_count = total_segments - champions_count

                champions_df = df_clean.iloc[hull_indices]
                outliers_df = df_clean.drop(df_clean.index[hull_indices])

                simulated_waste_ratio = outliers_count / total_segments
                simulated_savings_rm = 10000 * (simulated_waste_ratio * 0.35)

                st.write("### Step 3: Optimization & Cost Savings Result Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="Flagged Waste Outliers",
                        value=f"{outliers_count} Targets",
                    )
                with col2:
                    st.metric(
                        label="SafeZone Champions Inside Fence",
                        value=f"{champions_count} Targets",
                    )
                with col3:
                    st.metric(
                        label="Potential Ad Spend Waste Cut",
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

                # ─── LAYMAN-TERM AI SUMMARY GENERATOR ───
                st.write("---")
                st.write("### Step 4: Live Gemini AI Consultant Insights")

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
                You are a premium, automated business assistant integrated inside the "AdSpend SafeZones" web app dashboard.
                You are writing a practical, easy-to-understand campaign review report for a business owner who does not know advanced math or programming.
                
                Our system just ran an optimization algorithm on their advertising data.
                - Total ad target groups evaluated: {total_segments}
                - Top-performing benchmark groups (The green "SafeZone" area): {champions_count}
                - Inefficient, cash-wasting groups (The red "Outliers" outside the area): {outliers_count}
                
                Here is the data table for the good benchmark groups:
                {champions_text}
                
                Here is the data table for the wasteful outlier groups:
                {outliers_text}
                
                Write a highly practical, conversational, yet professional executive review in clean Markdown format.
                
                CRITICAL INSTRUCTIONS:
                - DO NOT use math/programming jargon like "Convex Hull", "vertices", "coordinates", "matrix", or "spatial geometry".
                - Use clear, simple everyday language and analogies. Think of the green shape as a "protective safety fence" and the red dots as "leaks in their wallet".
                - DO NOT say things like "Here is your report", "Hello business owner", or sign off with text like "Best regards".
                - DO NOT include any emojis anywhere in your text.

                Structure the report EXACTLY with these sections:
                
                ### AD CAMPAIGN HEALTH CHECK
                * Write a simple 2 to 3 sentence summary explaining what the graph shows in plain English. 
                * Explain that the green shape connects their most efficient ad campaigns to form a "Safety Fence". 
                * Explain that any red dots outside this fence are bad investments that are draining their budget for very little return.
                
                ### CAMPAIGNS TO PAUSE IMMEDIATELY
                * Use a simple blockquote (>) or clear text lines to list the names of the wasteful outlier groups provided to you.
                * For each wasteful group, explain in plain words why it is losing money (e.g., "charging you too much money for too few actual sales/results").
                * Provide simple, step-by-step instructions telling them to log into their Google Ads or Meta Ads dashboard, find these exact groups, and click the "Pause" button right away to stop losing money.
                
                ### HOW TO GROW YOUR SUCCESSFUL ADS
                * Present a simple markdown table of the good benchmark groups (Name, CPC, CVR) so the user knows who their winners are.
                * Give 3 simple, practical tips on how they can use this information to make more money, such as:
                  1. Turning off the bad ads and moving that extra cash over to these winning ads.
                  2. Creating new target audiences that copy the exact style, locations, or habits of their best-performing ad group.
                  3. Setting a maximum price limit on what they are willing to pay for an ad click based on their winners.
                """

                with st.spinner(
                    "Sending campaign metrics to Gemini AI core systems..."
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
                "Validation Error: Could not automatically find matching CPC or Conversion Rate columns in your file header. Please ensure your report contains standard performance columns."
            )
    except Exception as e:
        st.error(f"Error compiling file properties: {str(e)}")
else:
    st.info(
        "Application standby state. Drag-and-drop or load an unedited Google or Meta campaign spreadsheet to launch the simulation engine."
    )
