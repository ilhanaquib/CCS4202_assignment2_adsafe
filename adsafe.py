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
    Idea 1: Search-Term Cleaner Engine
    Uses a Divide and Conquer approach to process search phrases,
    isolating low-performing terms to build an automated negative keyword list.
    """
    if len(df) <= 2:
        wasteful_words = set()
        for _, row in df.iterrows():
            # Condition: Has traffic cost/clicks, but completely generated ZERO conversions
            if row["Clicks"] > 5 and row["Conversions"] == 0:
                words = str(row["Search Term"]).lower().split()
                for word in words:
                    # Filter out common baseline search intents to preserve valid variations
                    if word not in [
                        "buy",
                        "purchase",
                        "shop",
                        "order",
                        "online",
                        "price",
                        "malaysia",
                    ]:
                        wasteful_words.add(word)
        return wasteful_words

    # Divide: Split data into structural halves
    mid = len(df) // 2
    left_half = df.iloc[:mid]
    right_half = df.iloc[mid:]

    # Conquer: Recursively process the partitions
    left_waste = run_search_term_cleaner_dc(left_half)
    right_waste = run_search_term_cleaner_dc(right_half)

    # Merge: Combine identified negative keyword configurations
    return left_waste.union(right_waste)


def run_keyword_opportunity_dc(df):
    """
    Idea 2: Keyword Opportunity Finder
    Uses a Divide and Conquer ranking filter to discover undervalued keyword
    arbitrage segments by recursively filtering out high-cost, low-volume traps.
    """

    # Standardize competition strings to numerical intensity values safely
    def clean_comp(val):
        val_str = str(val).lower()
        if "high" in val_str or "3" in val_str:
            return 3
        if "med" in val_str or "2" in val_str:
            return 2
        return 1  # Fallback defaults for low/unspecified competition vectors

    df["Comp_Value"] = df["Competition"].apply(clean_comp)
    # Opportunity Score Formula: Search Volume / (Competition Risk * Unit Cost)
    df["Opportunity_Score"] = df["Searches"] / (
        df["Comp_Value"] * df["CPC"].replace(0, 0.01)
    )

    if len(df) <= 1:
        return df.to_dict("records")

    # Divide: Split data matrix down the middle
    mid = len(df) // 2
    left_sorted = run_keyword_opportunity_dc(df.iloc[:mid])
    right_sorted = run_keyword_opportunity_dc(df.iloc[mid:])

    # Conquer & Merge: Combine sorted blocks back descending by opportunity value
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


# ─── ROBUST PLATFORM RAW CSV CLEANER PIPELINE ───


def parse_and_standardize_marketing_csv(uploaded_file):
    """
    Advanced Data Profiler: Safely reads unedited Google Ads/Meta Ads exports.
    Handles random metadata rows, cleans currency strings, and formats column headers.
    """
    # Step 1: Detect and bypass potential Google Ads empty metadata header spacing
    try:
        # Read first 5 lines to check for typical network report headers
        preview = [
            uploaded_file.readline().decode("utf-8", errors="ignore") for _ in range(5)
        ]
        uploaded_file.seek(0)  # Reset tracking pointer

        skip_rows = 0
        for idx, line in enumerate(preview):
            if any(
                term in line.lower()
                for term in [
                    "campaign",
                    "search term",
                    "keyword",
                    "ad set",
                    "ad set name",
                ]
            ):
                skip_rows = idx
                break

        df = pd.read_csv(uploaded_file, skiprows=skip_rows)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)

    # Drop known network platform aggregate summary total rows immediately
    if len(df) > 0:
        last_row_str = str(df.iloc[-1].values).lower()
        if any(
            term in last_row_str
            for term in ["total", "summary", "grand total", "unfiltered"]
        ):
            df = df.iloc[:-1]

    # Normalize raw target headers for tracking match passes
    cols_clean = [str(c).strip().lower() for c in df.columns]

    # Define mapping criteria arrays matching Google and Meta platform specifications
    search_term_triggers = ["search term", "search_term", "queries", "user query"]
    keyword_triggers = ["keyword", "keyword text", "target phrase"]

    clicks_triggers = ["clicks", "clicks (all)", "link clicks", "inline link clicks"]
    cost_triggers = ["cost", "spend", "amount expended", "amount spent"]
    conv_triggers = [
        "conversions",
        "results",
        "all conv.",
        "actions",
        "link click conversion rate",
        "conv. rate",
    ]

    vol_triggers = ["searches", "avg. monthly searches", "search volume", "volume"]
    comp_triggers = ["competition", "competition (indexed value)", "market rivalry"]
    cpc_triggers = [
        "cpc",
        "avg. cpc",
        "average cpc",
        "cost per inline link click (cpc)",
        "cost per click",
    ]

    # Master Identification Flag Maps
    matched_type = None
    final_df = pd.DataFrame()

    # ENGINE PROFILE 1 VERIFICATION PASS: SEARCH TERM CLEANER
    term_idx = next(
        (
            i
            for i, c in enumerate(cols_clean)
            if any(t in c for t in search_term_triggers)
        ),
        None,
    )
    clicks_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in clicks_triggers)),
        None,
    )
    cost_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in cost_triggers)),
        None,
    )
    conv_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in conv_triggers)),
        None,
    )

    if term_idx is not None and clicks_idx is not None:
        matched_type = "Idea 1: Search-Term Cleaner Engine"
        final_df["Search Term"] = df.iloc[:, term_idx]
        final_df["Clicks"] = pd.to_numeric(df.iloc[:, clicks_idx], errors="coerce")
        final_df["Cost"] = (
            df.iloc[:, cost_idx].astype(str).str.replace(r"[^\d.]", "", regex=True)
        )
        final_df["Cost"] = pd.to_numeric(final_df["Cost"], errors="coerce")
        # Check conversion values; convert conversion rates to absolute values if exported as percentages
        raw_conv = df.iloc[:, conv_idx].astype(str).str.replace("%", "", regex=False)
        final_df["Conversions"] = pd.to_numeric(raw_conv, errors="coerce")

    # ENGINE PROFILE 2 VERIFICATION PASS: KEYWORD OPPORTUNITY ARBITRAGE
    kw_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in keyword_triggers)),
        None,
    )
    vol_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in vol_triggers)), None
    )
    comp_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in comp_triggers)),
        None,
    )
    cpc_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in cpc_triggers)), None
    )

    # Fallback secondary routine routing to run Profile 2 optimization if no search terms match
    if matched_type is None and kw_idx is not None and cpc_idx is not None:
        matched_type = "Idea 2: Keyword Opportunity Arbitrage Engine"
        final_df["Keyword"] = df.iloc[:, kw_idx]
        final_df["Searches"] = pd.to_numeric(
            df.iloc[:, vol_idx], errors="coerce"
        ).fillna(100)
        final_df["Competition"] = df.iloc[:, comp_idx].fillna("medium")
        final_df["CPC"] = (
            df.iloc[:, cpc_idx].astype(str).str.replace(r"[^\d.]", "", regex=True)
        )
        final_df["CPC"] = pd.to_numeric(final_df["CPC"], errors="coerce")

    if matched_type and len(final_df) > 0:
        return matched_type, final_df.dropna().reset_index(drop=True)
    return None, None


# ─── CORE USER STREAMLIT INTERFACE RENDERING ───

st.write("### Step 1: Drop Your Google Ads or Meta Ads Export Spreadsheet")
st.caption(
    "Supports unedited CSV raw report file logs from Google Ads Keyword Planner, Search Term Reports, or Meta Ad Set breakdowns."
)
uploaded_file = st.file_uploader("Upload Network CSV File:", type=["csv"])

if uploaded_file is not None:
    try:
        detected_module, working_df = parse_and_standardize_marketing_csv(uploaded_file)

        if detected_module is not None and not working_df.empty:
            st.success(
                f"Network Format Parsed! Automatically Connected to: **{detected_module}**"
            )
            st.write("---")
            st.write("### Step 2: Automated Analysis Dashboard")

            # ────────────────────────────────────────────────────────
            # RENDER ENGINE 1 UI LAYOUT: GOOGLE SEARCH TERM CLEANER
            # ────────────────────────────────────────────────────────
            if "Search-Term" in detected_module:
                negative_keywords = run_search_term_cleaner_dc(working_df)

                # Math Analytics Calculations
                wasted_rows = working_df[
                    (working_df["Clicks"] > 5) & (working_df["Conversions"] == 0)
                ]
                total_waste_cost = wasted_rows["Cost"].sum()

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Identified Bleeding Capital Cost Outflows",
                        value=f"RM {total_waste_cost:,.2f}",
                    )
                with col2:
                    st.metric(
                        label="Generated Negative Keyword Filter Directives",
                        value=f"{len(negative_keywords)} Core Phrases",
                    )

                st.write("#### Action System Directives")
                st.write(
                    "Copy and paste these phrases directly into your Google Ads or Meta Account Negative Lists to block wasteful matching algorithms:"
                )
                if negative_keywords:
                    st.code(", ".join(list(negative_keywords)), language="text")
                else:
                    st.info(
                        "No major non-converting structural phrases detected inside the data partitions."
                    )

                st.write("#### Verified System Data Matrix Log View")
                st.dataframe(working_df, use_container_width=True, hide_index=True)

            # ────────────────────────────────────────────────────────
            # RENDER ENGINE 2 UI LAYOUT: KEYWORD OPPORTUNITY FINDER
            # ────────────────────────────────────────────────────────
            elif "Keyword" in detected_module:
                sorted_records = run_keyword_opportunity_dc(working_df)
                results_df = pd.DataFrame(sorted_records)

                st.write("#### Top Arbitrage Value Targets Discovered")
                st.caption(
                    "These keywords exhibit deep audience reach parameters coupled with highly efficient acquisition click costs."
                )

                top_3 = results_df.head(3)
                m_cols = st.columns(3)
                for index, row in top_3.iterrows():
                    with m_cols[index]:
                        st.metric(
                            label=f"Rank {index+1}: {row['Keyword']}",
                            value=f"Avg CPC: RM {row['CPC']:.2f}",
                            delta=f"Vol: {int(row['Searches'])}",
                        )

                # Plot Configuration Summary
                fig, ax = plt.subplots(figsize=(10, 3.5))
                chart_data = results_df.head(10)
                ax.barh(
                    chart_data["Keyword"][::-1],
                    chart_data["Opportunity_Score"][::-1],
                    color="#10B981",
                )
                ax.set_xlabel("Relative Arbitrage Value Score (Higher is Better)")
                ax.set_title(
                    "Top 10 Most Undervalued Ad Target Opportunities", fontweight="bold"
                )
                ax.grid(True, axis="x", linestyle="--", alpha=0.5)
                st.pyplot(fig)

                st.write("#### Comprehensive Optimization Keyword Placement Array")
                st.dataframe(
                    results_df[["Keyword", "Searches", "Competition", "CPC"]],
                    use_container_width=True,
                    hide_index=True,
                )

        else:
            st.error(
                "Validation Error: System could not match your data configuration layout. Please ensure you are uploading a valid export sheet containing Campaign/Keyword metrics matching standard Google or Meta headers."
            )

    except Exception as e:
        st.error(f"System Pipeline Execution Halt: {str(e)}")
else:
    st.info(
        "System operational standby state. Drag-and-drop any unedited Google Ads Search Term, Keyword Planner, or Meta Ad Set metrics spreadsheet here to launch the automated interface ecosystem."
    )
