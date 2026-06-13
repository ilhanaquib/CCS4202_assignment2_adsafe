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
            if row["Clicks"] > 5 and row["Conversions"] == 0:
                words = str(row["Search Term"]).lower().split()
                for word in words:
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

    mid = len(df) // 2
    left_half = df.iloc[:mid]
    right_half = df.iloc[mid:]

    left_waste = run_search_term_cleaner_dc(left_half)
    right_waste = run_search_term_cleaner_dc(right_half)

    return left_waste.union(right_waste)


def run_keyword_opportunity_dc(df):
    """
    Idea 2: Keyword Opportunity Finder
    Uses a Divide and Conquer ranking filter to discover undervalued keyword
    arbitrage segments by recursively filtering out high-cost, low-volume traps.
    """

    def clean_comp(val):
        val_str = str(val).lower()
        if "high" in val_str or "3" in val_str:
            return 3
        if "med" in val_str or "2" in val_str:
            return 2
        return 1

    df["Comp_Value"] = df["Competition"].apply(clean_comp)
    df["Opportunity_Score"] = df["Searches"] / (
        df["Comp_Value"] * df["CPC"].replace(0, 0.01)
    )

    if len(df) <= 1:
        return df.to_dict("records")

    mid = len(df) // 2
    left_sorted = run_keyword_opportunity_dc(df.iloc[:mid])
    right_sorted = run_keyword_opportunity_dc(df.iloc[mid:])

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


def run_merge_sort_ranking(records_list, Metric_Key):
    """
    Idea 5: Strategic Performance Ranking Engine
    Classic implementation of the Merge Sort Divide and Conquer algorithm
    to sort and rank items (branches or campaigns) descending by their performance metric.
    """
    if len(records_list) <= 1:
        return records_list

    # Divide: Split the list of records in half
    mid = len(records_list) // 2
    left_half = run_merge_sort_ranking(records_list[:mid], Metric_Key)
    right_half = run_merge_sort_ranking(records_list[mid:], Metric_Key)

    # Conquer & Merge: Linear assembly by metric descending
    sorted_list = []
    i = j = 0
    while i < len(left_half) and j < len(right_half):
        if left_half[i][Metric_Key] > right_half[j][Metric_Key]:
            sorted_list.append(left_half[i])
            i += 1
        else:
            sorted_list.append(right_half[j])
            j += 1

    sorted_list.extend(left_half[i:])
    sorted_list.extend(right_half[j:])
    return sorted_list


# ─── ROBUST PLATFORM RAW CSV CLEANER PIPELINE ───


def parse_and_standardize_marketing_csv(uploaded_file):
    """
    Advanced Data Profiler: Safely reads unedited Google Ads/Meta Ads exports.
    Handles metadata rows, cleans currency strings, and paths files to the right engine.
    """
    try:
        preview = [
            uploaded_file.readline().decode("utf-8", errors="ignore") for _ in range(5)
        ]
        uploaded_file.seek(0)

        skip_rows = 0
        for idx, line in enumerate(preview):
            if any(
                term in line.lower()
                for term in [
                    "campaign",
                    "search term",
                    "keyword",
                    "ad set",
                    "branch",
                    "location",
                ]
            ):
                skip_rows = idx
                break

        df = pd.read_csv(uploaded_file, skiprows=skip_rows)
    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)

    if len(df) > 0:
        last_row_str = str(df.iloc[-1].values).lower()
        if any(
            term in last_row_str
            for term in ["total", "summary", "grand total", "unfiltered"]
        ):
            df = df.iloc[:-1]

    cols_clean = [str(c).strip().lower() for c in df.columns]

    # Define Column Identifier Maps
    search_term_triggers = ["search term", "search_term", "queries", "user query"]
    keyword_triggers = ["keyword", "keyword text", "target phrase"]
    campaign_triggers = [
        "campaign",
        "ad set",
        "placement",
        "target name",
        "branch",
        "location",
        "state",
    ]

    clicks_triggers = ["clicks", "clicks (all)", "link clicks", "inline link clicks"]
    cost_triggers = ["cost", "spend", "amount expended", "amount spent"]
    conv_triggers = ["conversions", "results", "all conv.", "actions"]
    cvr_triggers = ["cvr", "conv. rate", "conversion rate", "result rate"]

    vol_triggers = ["searches", "avg. monthly searches", "search volume", "volume"]
    comp_triggers = ["competition", "competition (indexed value)", "market rivalry"]
    cpc_triggers = ["cpc", "avg. cpc", "average cpc", "cost per click"]
    rev_triggers = ["revenue", "revenue (rm)", "sales", "turnover"]

    matched_type = None
    final_df = pd.DataFrame()

    # ENGINE PROFILE 1 PASS: SEARCH TERM CLEANER
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
        final_df["Cost"] = pd.to_numeric(
            df.iloc[:, cost_idx].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        )
        final_df["Conversions"] = pd.to_numeric(df.iloc[:, conv_idx], errors="coerce")
        return matched_type, final_df.dropna().reset_index(drop=True)

    # ENGINE PROFILE 2 PASS: KEYWORD OPPORTUNITY ARBITRAGE
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

    if kw_idx is not None and cpc_idx is not None:
        matched_type = "Idea 2: Keyword Opportunity Arbitrage Engine"
        final_df["Keyword"] = df.iloc[:, kw_idx]
        final_df["Searches"] = pd.to_numeric(
            df.iloc[:, vol_idx], errors="coerce"
        ).fillna(100)
        final_df["Competition"] = df.iloc[:, comp_idx].fillna("medium")
        final_df["CPC"] = pd.to_numeric(
            df.iloc[:, cpc_idx].astype(str).str.replace(r"[^\d.]", "", regex=True),
            errors="coerce",
        )
        return matched_type, final_df.dropna().reset_index(drop=True)

    # ENGINE PROFILE 5 PASS: CAMPAIGN / REGIONAL BRANCH RANKING
    camp_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in campaign_triggers)),
        None,
    )
    rev_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in rev_triggers)), None
    )
    cvr_idx = next(
        (i for i, c in enumerate(cols_clean) if any(t in c for t in cvr_triggers)), None
    )

    if camp_idx is not None:
        matched_type = "Idea 5: Operational Performance Ranking Engine"
        final_df["Entity Name"] = df.iloc[:, camp_idx]

        # If the file has Revenue, rank by Revenue. If it has CVR (like ad.csv), rank by CVR!
        if rev_idx is not None:
            final_df["Sorting_Metric"] = pd.to_numeric(
                df.iloc[:, rev_idx].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors="coerce",
            )
            st.session_state["metric_label"] = "Revenue (RM)"
        elif cvr_idx is not None:
            final_df["Sorting_Metric"] = pd.to_numeric(
                df.iloc[:, cvr_idx].astype(str).str.replace(r"[^\d.]", "", regex=True),
                errors="coerce",
            )
            st.session_state["metric_label"] = "Conversion Rate (CVR %)"
        else:
            final_df["Sorting_Metric"] = np.arange(len(df))
            st.session_state["metric_label"] = "Index Order"

        return matched_type, final_df.dropna().reset_index(drop=True)

    return None, None


# ─── CORE USER STREAMLIT INTERFACE RENDERING ───

st.write("### Step 1: Drop Your Operations Spreadsheet")
st.caption(
    "Supports unedited CSV reports from Google Ads, Meta Ads, or Regional Corporate Sales sheets."
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
                st.code(", ".join(list(negative_keywords)), language="text")
                st.dataframe(working_df, use_container_width=True, hide_index=True)

            # ────────────────────────────────────────────────────────
            # RENDER ENGINE 2 UI LAYOUT: KEYWORD OPPORTUNITY FINDER
            # ────────────────────────────────────────────────────────
            elif "Keyword" in detected_module:
                sorted_records = run_keyword_opportunity_dc(working_df)
                results_df = pd.DataFrame(sorted_records)

                st.write("#### Top Arbitrage Value Targets Discovered")
                top_3 = results_df.head(3)
                m_cols = st.columns(3)
                for index, row in top_3.iterrows():
                    with m_cols[index]:
                        st.metric(
                            label=f"Rank {index+1}: {row['Keyword']}",
                            value=f"Avg CPC: RM {row['CPC']:.2f}",
                            delta=f"Vol: {int(row['Searches'])}",
                        )

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
                st.pyplot(fig)
                st.dataframe(
                    results_df[["Keyword", "Searches", "Competition", "CPC"]],
                    use_container_width=True,
                    hide_index=True,
                )

            # ────────────────────────────────────────────────────────
            # RENDER ENGINE 5 UI LAYOUT: OPERATIONAL STRATEGIC RANKING
            # ────────────────────────────────────────────────────────
            elif "Operational Performance" in detected_module:
                records = working_df.to_dict("records")
                sorted_records = run_merge_sort_ranking(records, "Sorting_Metric")
                sorted_df = pd.DataFrame(sorted_records)

                metric_label = st.session_state.get(
                    "metric_label", "Performance Metric"
                )

                highest_entity = sorted_df.iloc[0]["Entity Name"]
                highest_val = sorted_df.iloc[0]["Sorting_Metric"]
                lowest_entity = sorted_df.iloc[-1]["Entity Name"]
                lowest_val = sorted_df.iloc[-1]["Sorting_Metric"]

                col1, col2 = st.columns(2)
                with col1:
                    st.metric(
                        label="Top Performing Asset / Segment",
                        value=highest_entity,
                        delta=f"{highest_val:.2f} ({metric_label})",
                    )
                with col2:
                    st.metric(
                        label="Underperforming Asset (Needs Review)",
                        value=lowest_entity,
                        delta=f"{lowest_val:.2f} ({metric_label})",
                        delta_color="inverse",
                    )

                # Render Bar Chart of Ranked Contributions
                fig, ax = plt.subplots(figsize=(10, 4))
                chart_data = sorted_df.head(15)  # Show top 15 for clean visualization
                ax.bar(
                    chart_data["Entity Name"],
                    chart_data["Sorting_Metric"],
                    color="#3B82F6",
                )
                ax.set_ylabel(metric_label)
                ax.set_title(
                    f"Ranked Asset Analysis Frontier (Top 15 Segments via Merge Sort)",
                    fontweight="bold",
                )
                plt.xticks(rotation=45, ha="right")
                st.tight_layout()
                st.pyplot(fig)

                st.write("#### Full Ranked Optimization Ledger")
                # Clean columns names for user presentation
                display_df = sorted_df.rename(
                    columns={
                        "Entity Name": "Campaign / Branch Name",
                        "Sorting_Metric": metric_label,
                    }
                )
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        else:
            st.error(
                "Validation Error: System could not match your data configuration layout. Please ensure your file headers contain standard Campaign, Keyword, or Regional Branch performance variables."
            )

    except Exception as e:
        st.error(f"System Pipeline Execution Halt: {str(e)}")
else:
    st.info(
        "System operational standby state. Drag-and-drop any unedited Google Ads, Meta Ads, or Branch Sales metrics spreadsheet here to launch the automated interface ecosystem."
    )
