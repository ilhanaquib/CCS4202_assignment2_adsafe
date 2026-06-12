import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

# 1. Page Configuration (Using DaisyUI-like clean styling hints)
st.set_page_config(page_title="AdSpend SafeZones", layout="wide")

st.title("🎯 AdSpend SafeZones Engine")
st.subheader("Divide & Conquer Convex Hull Simulation Dashboard")
st.write("---")

# 2. Sidebar Controls (The Simulator Inputs)
st.sidebar.header("Campaign Simulation Settings")
total_budget = st.sidebar.slider(
    "Total Advertising Budget (RM)",
    min_value=1000,
    max_value=50000,
    value=10000,
    step=1000,
)
num_ad_sets = st.sidebar.slider(
    "Number of Target Audience Groups", min_value=20, max_value=100, value=50
)

# Generate Mock Data deterministically based on settings
np.random.seed(42)
# X-axis: Cost Per Click (CPC) from RM 0.50 to RM 4.50
cpc = np.random.uniform(0.5, 4.5, num_ad_sets)
# Y-axis: Conversion Rate (CVR) from 0.5% to 8.0%
cvr = np.random.uniform(0.5, 8.0, num_ad_sets)
points = np.column_stack((cpc, cvr))

# 3. Running the Simulation Logic
st.write(f"### 📊 Step 1: Visualizing Your {num_ad_sets} Target Groups")
st.write(
    f"Currently distributing your **RM {total_budget:,}** budget across the field..."
)

# Button to execute the Divide & Conquer Algorithm
if st.button("🚀 Run Convex Hull Optimizer", type="primary"):

    # Calculate the Convex Hull (The D&C Magic)
    hull = ConvexHull(points)

    # Check which points are inside vs outside the Hull
    # For a simple PoC, we classify points on the boundary/hull vertices as our "Champions"
    hull_indices = hull.vertices

    # Calculate simulated financial metrics
    total_points = len(points)
    champions_count = len(hull_indices)
    outliers_count = total_points - champions_count

    # Simulate that ~32% of budget is wasted on outliers (matches our RM3,200 example)
    wasted_percentage = (outliers_count / total_points) * 0.45
    cash_saved = total_budget * wasted_percentage
    optimized_spend = total_budget - cash_saved
    sales_increase = (cash_saved / optimized_spend) * 100

    # 4. The Profit & Savings Report (DaisyUI-style KPI Cards)
    st.write("---")
    st.write("### 💰 Step 2: The Profit & Savings Decision Report")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🔴 Wasteful Outliers Halted", value=f"{outliers_count} Groups")
    with col2:
        st.metric(
            label="💵 Cash Saved / Pocketed",
            value=f"RM {cash_saved:,.2f}",
            delta=f"-{wasted_percentage*100:.1f}% Ad Waste",
        )
    with col3:
        st.metric(
            label="📈 Potential Sales Boost",
            value=f"+{sales_increase:.1f}%",
            delta="If reinvested inside SafeZone",
        )

    # 5. Interactive Data Visualization Mapping
    st.write("---")
    st.write("### 🗺️ Step 3: Interactive SafeZone Map")

    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot all data points (Outliers)
    ax.scatter(
        points[:, 0],
        points[:, 1],
        color="red",
        alpha=0.6,
        label="Wasteful Outliers (Cut Spend)",
    )

    # Plot Champion points
    ax.scatter(
        points[hull_indices, 0],
        points[hull_indices, 1],
        color="green",
        s=100,
        zorder=5,
        label="Champion Benchmarks",
    )

    # Draw the Convex Hull "Digital Fence"
    for simplex in hull.simplices:
        ax.plot(points[simplex, 0], points[simplex, 1], "g-", linewidth=2)

    # Fill the inside of the fence with a soft green glow
    ax.fill(points[hull_indices, 0], points[hull_indices, 1], "g", alpha=0.1)

    ax.set_xlabel("Cost Per Click (CPC in RM) - LOWER IS BETTER")
    ax.set_ylabel("Conversion Rate (CVR in %) - HIGHER IS BETTER")
    ax.set_title("Convex Hull Boundary Setup")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

    st.pyplot(fig)

    # Decision Helper Text
    st.info(
        f"💡 **Investor Decision:** You can now choose to only spend **RM {optimized_spend:,.2f}** to get your baseline sales, "
        f"or reinvest the saved **RM {cash_saved:,.2f}** exclusively inside the green fence to skyrocket your revenue."
    )
else:
    # Before the button is clicked, show a static gray plot representing the unoptimized state
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(
        points[:, 0],
        points[:, 1],
        color="gray",
        alpha=0.7,
        label="Unoptimized Target Groups",
    )
    ax.set_xlabel("Cost Per Click (CPC in RM)")
    ax.set_ylabel("Conversion Rate (CVR in %)")
    ax.set_title("Awaiting Algorithmic Fencing...")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    st.pyplot(fig)
    st.caption(
        "Click the 'Run Convex Hull Optimizer' button above to see the Divide & Conquer framework isolate your data."
    )
