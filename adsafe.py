import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page configuration for an enterprise software look
st.set_page_config(page_title="AdSafe Analytics Suite", layout="wide")

st.title("AdSafe Intelligence Suite")
st.subheader("Multi-Engine Marketing Optimization Dashboard")
st.write("---")

# ─── DIVIDE & CONQUER ALGORITHMIC ENGINES ───


def run_search_term_cleaner_dc(df):
    """
    Idea 1: Google Ads Search-Term Cleaner
    Uses a Divide and Conquer approach to process search phrases,
    isolating low-performing terms to build an automated negative keyword list.
    """
    # Base case: if subset is small, extract the wasteful words directly
    if len(df) <= 2:
        wasteful_words = set()
        for _, row in df.iterrows():
            # Condition: High clicks, some cost, but ZERO conversions
            if row["Clicks"] > 10 and row["Conversions"] == 0:
                # Extract words from the phrase
                words = str(row["Search Term"]).lower().split()
                for word in words:
                    # Filter out generic transactional intent words to protect good traffic
                    if word not in ["buy", "purchase", "shop", "order", "laptop"]:
                        wasteful_words.add(word)
        return wasteful_words

    # Divide: Split data into two halves
    mid = len(df) // 2
    left_half = df.iloc[:mid]
    right_half = df.iloc[mid:]

    # Conquer: Recursively analyze each partition
    left_waste = run_search_term_cleaner_dc(left_half)
    right_waste = run_search_term_cleaner_dc(right_half)

    # Merge: Combine identified negative keyword candidates
    return left_waste.union(right_waste)


def run_keyword_opportunity_dc(df):
    """
    Idea 2: Keyword Opportunity Finder
    Uses a Divide and Conquer ranking filter to discover undervalued keyword
    arbitrage segments by recursively filtering out high-cost, low-volume traps.
    """
    # Create a custom efficiency score internally: Volume / (Competition_Numeric * CPC)
    # This prevents math breaking during division
    comp_map = {"low": 1, "medium": 2, "high": 3}
    df["Comp_Value"] = df["Competition"].astype(str).str.lower().map(comp_map).fillna(2)
    df["Opportunity_Score"] = df["Searches"] / (df["Comp_Value"] * df["CPC"])

    # Base case for Divide and Conquer sorting/filtering
    if len(df) <= 1:
        return df.to_dict("records")

    # Divide: Split data matrix down the median
    mid = len(df) // 2
    left_sorted = run_keyword_opportunity_dc(df.iloc[:mid])
    right_sorted = run_keyword_opportunity_dc(df.iloc[mid:])

    # Conquer & Merge: Combine subsets based on the efficiency opportunity score
    merged = []
    i = j = 0
    while i < len(left_sorted) and j < len(right_sorted):
        if left_sorted[i]["Opportunity_Score"] > right_sorted[j]["Opportunity_Score"]:
            merged.append(left_sorted[i])
            i += 1
        else:
            merged.append(right_sorted[j])
            j += 1

    merged.extend(left_sorted[i:])
    merged.extend(right_sorted[j:])
    return merged


def run_merge_sort_branches(branches_list):
    """
    Idea 5: Multi-Branch Sales Ranking
    Classic implementation of the Merge Sort Divide and Conquer algorithm
    to rank operational regional performance.
    """
    if len(branches_list) <= 1:
        return branches_list

    # Divide: Split the list of branch records in half
    mid = len(branches_list) // 2
    left_half = run_merge_sort_branches(branches_list[:mid])
    right_half = run_merge_sort_branches(branches_list[mid:])

    # Conquer & Merge: Structural linear assembly by revenue descending
    sorted_list = []
    i = j = 0
    while i < len(left_half) and j < len(right_half):
        if left_half[i]["Revenue"] > right_half[j]["Revenue"]:
            sorted_list.append(left_half[i])
            i += 1
        else:
            sorted_list.append(right_half[j])
            j += 1

    sorted_list.extend(left_half[i:])
    sorted_list.extend(right_half[j:])
    return sorted_list


# ─── CORE PIPELINE DATA PROFILER ───

st.write("### Step 1: Drop Your Operations Spreadsheet")
st.caption(
    "Our system automatically identifies your data profile type and provisions the appropriate engine module."
)
uploaded_file = st.file_uploader("Upload CSV file:", type=["csv"])

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        cols = [c.strip().lower() for c in raw_df.columns]

        # Scenario Routing Router Logic
        detected_module = None

        # Profile 1 Mapping Check (Search Terms Cleaner)
        if any("search" in c or "term" in c for c in cols) and "clicks" in cols:
            detected_module = "Idea 1: Search-Term Cleaner Engine"
            # Normalize headers for script logic
            term_col = next(
                c
                for c in raw_df.columns
                if "search" in c.lower() or "term" in c.lower()
            )
            clicks_col = next(c for c in raw_df.columns if "click" in c.lower())
            cost_col = next(
                c for c in raw_df.columns if "cost" in c.lower() or "spend" in c.lower()
            )
            conv_col = next(c for c in raw_df.columns if "conv" in c.lower())

            working_df = pd.DataFrame(
                {
                    "Search Term": raw_df[term_col],
                    "Clicks": pd.to_numeric(raw_df[clicks_col], errors="coerce"),
                    "Cost": pd.to_numeric(
                        raw_df[cost_col]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True),
                        errors="coerce",
                    ),
                    "Conversions": pd.to_numeric(raw_df[conv_col], errors="coerce"),
                }
            ).dropna()

        # Profile 2 Mapping Check (Keyword Opportunity Finder)
        elif any("keyword" in c for c in cols) and any(
            "search" in c or "vol" in c for c in cols
        ):
            detected_module = "Idea 2: Keyword Opportunity Arbitrage Engine"
            kw_col = next(c for c in raw_df.columns if "keyword" in c.lower())
            vol_col = next(
                c for c in raw_df.columns if "search" in c.lower() or "vol" in c.lower()
            )
            comp_col = next(c for c in raw_df.columns if "comp" in c.lower())
            cpc_col = next(
                c for c in raw_df.columns if "cpc" in c.lower() or "click" in c.lower()
            )

            working_df = pd.DataFrame(
                {
                    "Keyword": raw_df[kw_col],
                    "Searches": pd.to_numeric(raw_df[vol_col], errors="coerce"),
                    "Competition": raw_df[comp_col],
                    "CPC": pd.to_numeric(
                        raw_df[cpc_col]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True),
                        errors="coerce",
                    ),
                }
            ).dropna()

        # Profile 5 Mapping Check (Multi-Branch Sales Ranking)
        elif any("branch" in c or "loc" in c or "state" in c for c in cols) and any(
            "rev" in c or "sale" in c for c in cols
        ):
            detected_module = "Idea 5: Regional Branch Strategic Ranking Engine"
            branch_col = next(
                c
                for c in raw_df.columns
                if "branch" in c.lower() or "loc" in c.lower() or "state" in c.lower()
            )
            rev_col = next(
                c for c in raw_df.columns if "rev" in c.lower() or "sale" in c.lower()
            )

            working_df = pd.DataFrame(
                {
                    "Branch": raw_df[branch_col],
                    "Revenue": pd.to_numeric(
                        raw_df[rev_col]
                        .astype(str)
                        .str.replace(r"[^\d.]", "", regex=True),
                        errors="coerce",
                    ),
                }
            ).dropna()

        # Execute Engine Dashboard Display based on what was found
        if detected_module:
            st.info(
                f"Data Profile Decoded Successfully: Connected to **{detected_module}**"
            )
            st.write("---")
            st.write("### Step 2: Automated Analysis Dashboard")

            # ────────────────────────────────────────────────────────
            # RENDER DASHBOARD 1: SEARCH TERM CLEANER
            # ────────────────────────────────────────────────────────
            if "Search-Term" in detected_module:
                negative_keywords = run_search_term_cleaner_dc(working_df)

                # Business Values Computations
                wasted_rows = working_df[
                    (working_df["Clicks"] > 10) & (working_df["Conversions"] == 0)
                ]
                total_waste_cost = wasted_rows["Cost"].sum()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Identified Wasted Capital Outflows",
                        value=f"RM {total_waste_cost:,.2f}",
                    )
                with col2:
                    st.metric(
                        label="Generated Negative Keyword Directives",
                        value=f"{len(negative_keywords)} Core Phrases",
                    )

                st.write("#### Action System Directives")
                st.write(
                    "Add these phrases into your campaign settings to prevent your ads from triggering for non-buying queries:"
                )
                st.code(", ".join(list(negative_keywords)), language="text")

                st.write("#### Evaluated Raw System Inputs")
                st.dataframe(working_df, use_container_width=True, hide_index=True)

            # ────────────────────────────────────────────────────────
            # RENDER DASHBOARD 2: KEYWORD OPPORTUNITY FINDER
            # ────────────────────────────────────────────────────────
            elif "Keyword" in detected_module:
                sorted_records = run_keyword_opportunity_dc(working_df)
                results_df = pd.DataFrame(sorted_records)

                st.write("#### Top Arbitrage Opportunities Discovered")
                st.caption(
                    "These items display high consumer volume metrics relative to low unit click costs."
                )

                # Display Top 5 in standard metrics metrics blocks
                top_3 = results_df.head(3)
                m_cols = st.columns(3)
                for index, row in top_3.iterrows():
                    with m_cols[index]:
                        st.metric(
                            label=f"Rank {index+1}: {row['Keyword']}",
                            value=f"CPC: RM {row['CPC']:.2f}",
                            delta=f"Vol: {int(row['Searches'])}",
                        )

                # Visual Bar Chart Generation
                fig, ax = plt.subplots(figsize=(10, 3.5))
                chart_data = results_df.head(10)
                ax.barh(
                    chart_data["Keyword"][::-1],
                    chart_data["Opportunity_Score"][::-1],
                    color="#10B981",
                )
                ax.set_xlabel("Relative Arbitrage Value Score")
                ax.set_title(
                    "Top 10 Most Undervalued Keyword Properties", fontweight="bold"
                )
                st.pyplot(fig)

                st.write("#### Full Optimized Keyword Matrix Layout")
                st.dataframe(
                    results_df[["Keyword", "Searches", "Competition", "CPC"]],
                    use_container_width=True,
                    hide_index=True,
                )

            # ────────────────────────────────────────────────────────
            # RENDER DASHBOARD 5: MULTI-BRANCH SALES RANKING
            # ────────────────────────────────────────────────────────
            elif "Branch" in detected_module:
                records = working_df.to_dict("records")
                sorted_records = run_merge_sort_branches(records)
                sorted_df = pd.DataFrame(sorted_records)

                # Performance KPIs Calculations
                highest_branch = sorted_df.iloc[0]["Branch"]
                highest_revenue = sorted_df.iloc[0]["Revenue"]
                lowest_branch = sorted_df.iloc[-1]["Branch"]
                lowest_revenue = sorted_df.iloc[-1]["Revenue"]

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Top Regional Anchor Unit",
                        value=highest_branch,
                        delta=f"RM {highest_revenue:,.2f}",
                    )
                with col2:
                    st.metric(
                        label="Underperforming Operational Unit",
                        value=lowest_branch,
                        delta=f"- RM {lowest_revenue:,.2f}",
                        delta_color="inverse",
                    )

                # Visual Plot Execution
                fig, ax = plt.subplots(figsize=(10, 3.5))
                ax.bar(sorted_df["Branch"], sorted_df["Revenue"], color="#3B82F6")
                ax.set_ylabel("Revenue Value Matrix (RM)")
                ax.set_title(
                    "Ranked Divisional Branch Contribution Architecture",
                    fontweight="bold",
                )
                plt.xticks(rotation=45)
                st.pyplot(fig)

                st.write("#### Priority Resource Allocation Ledger")
                st.dataframe(sorted_df, use_container_width=True)

        else:
            st.error(
                "Validation Error: System structural profile could not match the dataset columns. Please review your metrics matrix headers."
            )

    except Exception as e:
        st.error(f"System Pipeline Execution Halt: {str(e)}")
else:
    st.info(
        "System operational standby state. Drag-and-drop any of your corporate metrics CSV files here to build your analytics layout."
    )
