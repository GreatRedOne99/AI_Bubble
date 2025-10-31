"""
AI Bubble Simulation
Streamlit app to experiment when the AI bubble might pop
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SPY AI Bubble Simulator",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("📈 Streamlit SPY Valuation Simulator: AI Bubble 2029")
st.markdown("""
This simulator projects SPY's trajectory through an **AI-driven bubble** scenario by 2029.
Adjust the parameters below to explore different scenarios.
""")

# Baseline parameters
baseline_year = 2022
baseline_eps = 220
baseline_spy = 407
years_forward = 7
target_year = baseline_year + years_forward
spy_multiplier = 1 / 8.9  # SPY ≈ SPX / 8.9

# Load historical data
@st.cache_data
def load_data():
    try:
        spy = pd.read_csv('spy_historical_data.csv', index_col='Date', parse_dates=True)
        return spy
    except Exception as e:
        st.warning(f"Could not load historical data: {e}")
        return None

spy_data = load_data()

# Sidebar for baseline information
st.sidebar.header("📍 Baseline (as of 11/30/2022)")
st.sidebar.write(f"- SPY Price: ${baseline_spy}")
st.sidebar.write(f"- S&P 500 EPS: ${baseline_eps}")
st.sidebar.write(f"- Implied P/E: ~{baseline_spy / (baseline_eps * spy_multiplier):.1f}×")

# Load README content
@st.cache_data
def load_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Could not load README.md: {e}"

readme_content = load_readme()

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Projections", "📈 Valuation Scenarios", "🎲 Monte Carlo Simulation", "📖 About"])

with tab1:
    st.header("SPY Price Projection with Adjustable Parameters")

    col1, col2 = st.columns(2)

    with col1:
        eps_cagr = st.slider(
            "EPS CAGR (Compound Annual Growth Rate)",
            min_value=0.03,
            max_value=0.10,
            value=0.064,
            step=0.005,
            format="%.3f",
            help="Expected annual growth rate for earnings per share"
        )

    with col2:
        pe_ratio = st.slider(
            "P/E Ratio (Price-to-Earnings Multiple)",
            min_value=10,
            max_value=35,
            value=25,
            step=1,
            help="Valuation multiple applied to earnings"
        )

    # Calculate projection
    years = np.arange(baseline_year, target_year + 1)
    eps_projection = baseline_eps * (1 + eps_cagr) ** (years - baseline_year)
    spx_projection = eps_projection * pe_ratio
    spy_projection = spx_projection * spy_multiplier

    # Create plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(years, spy_projection, marker='o', linewidth=2, markersize=8, label=f'P/E {pe_ratio}×')
    ax.axhline(y=baseline_spy, color='gray', linestyle='--', linewidth=2, label='2022 SPY Baseline')
    ax.set_title('SPY Price Projection with Adjustable EPS CAGR and P/E', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('SPY Price ($)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    st.pyplot(fig)

    # Display final price
    final_price = spy_projection[-1]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Projected SPY Price (2029)", f"${final_price:.2f}")
    with col2:
        st.metric("Total Return", f"{((final_price / baseline_spy) - 1) * 100:.1f}%")
    with col3:
        st.metric("Annualized Return", f"{((final_price / baseline_spy) ** (1/years_forward) - 1) * 100:.1f}%")

    # EPS projection table
    st.subheader("📈 Projected EPS Growth")
    eps_df = pd.DataFrame({
        'Year': years,
        'Projected EPS': eps_projection,
        'SPX Price': spx_projection,
        'SPY Price': spy_projection
    })
    eps_df['Projected EPS'] = eps_df['Projected EPS'].map('${:.2f}'.format)
    eps_df['SPX Price'] = eps_df['SPX Price'].map('${:.2f}'.format)
    eps_df['SPY Price'] = eps_df['SPY Price'].map('${:.2f}'.format)
    st.dataframe(eps_df, use_container_width=True)

with tab2:
    st.header("🔁 Valuation Expansion Scenarios")

    # Multiple scenarios comparison
    pe_multiples = [15, 20, 25, 30]

    # Calculate projections for all P/E multiples
    years = np.arange(baseline_year, target_year + 1)
    eps_projection_base = baseline_eps * (1 + eps_cagr) ** (years - baseline_year)

    fig, ax = plt.subplots(figsize=(12, 6))

    for pe in pe_multiples:
        spx_vals = eps_projection_base * pe
        spy_vals = spx_vals * spy_multiplier
        ax.plot(years, spy_vals, marker='o', linewidth=2, markersize=6, label=f'P/E {pe}×')

    ax.axhline(y=baseline_spy, color='gray', linestyle='--', linewidth=2, label='2022 SPY Baseline')
    ax.set_title('SPY Price Projection: AI Bubble vs. Valuation Compression', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('SPY Price ($)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    st.pyplot(fig)

    # Valuation table
    st.subheader("2029 Price Targets by P/E Multiple")
    final_eps = eps_projection_base[-1]

    valuation_data = []
    for pe in pe_multiples:
        spx_price = final_eps * pe
        spy_price = spx_price * spy_multiplier
        total_return = ((spy_price / baseline_spy) - 1) * 100
        annualized_return = ((spy_price / baseline_spy) ** (1/years_forward) - 1) * 100

        scenario = ""
        if pe == 15:
            scenario = "Post-Burst Correction"
        elif pe == 20:
            scenario = "Fair Value"
        elif pe == 25:
            scenario = "Moderate Expansion"
        elif pe == 30:
            scenario = "Bubble Peak"

        valuation_data.append({
            'P/E Multiple': f'{pe}×',
            'Scenario': scenario,
            'SPX Price': f'${spx_price:.0f}',
            'SPY Price': f'${spy_price:.2f}',
            'Total Return': f'{total_return:.1f}%',
            'Annualized Return': f'{annualized_return:.1f}%'
        })

    valuation_df = pd.DataFrame(valuation_data)
    st.dataframe(valuation_df, use_container_width=True)

    # Key insights
    st.info("""
    **💥 Bubble vs. Correction Scenarios:**

    - **Bubble Peak (2029):** P/E = 30×, SPY ≈ $1,075+
    - **Post-Burst (2030-2031):** P/E compresses to 15×, SPY ≈ $550
    - **Historical Analogs:**
        - Dot-com peak (2000): P/E ~30×
        - Post-crash (2002): P/E ~15×
        - COVID rebound (2021): P/E ~22-23×
    """)

with tab3:
    st.header("🎲 Monte Carlo Simulation")
    st.markdown("Simulate probabilistic EPS paths to understand the distribution of potential outcomes.")

    col1, col2, col3 = st.columns(3)

    with col1:
        mean_growth = st.slider(
            "Mean EPS Growth Rate",
            min_value=0.03,
            max_value=0.10,
            value=0.064,
            step=0.005,
            format="%.3f",
            help="Average expected EPS growth rate"
        )

    with col2:
        std_dev = st.slider(
            "Volatility (Std Dev)",
            min_value=0.005,
            max_value=0.05,
            value=0.02,
            step=0.005,
            format="%.3f",
            help="Standard deviation of EPS growth rate"
        )

    with col3:
        pe_ratio_mc = st.slider(
            "Target P/E Ratio",
            min_value=10,
            max_value=35,
            value=30,
            step=1,
            help="P/E multiple for final valuation",
            key="pe_mc"
        )

    n_simulations = st.select_slider(
        "Number of Simulations",
        options=[100, 500, 1000, 2000, 5000],
        value=1000,
        help="More simulations = more accurate distribution"
    )

    # Run simulation
    @st.cache_data
    def simulate_eps_paths(baseline_eps, years, n_simulations, mean_growth, std_dev):
        np.random.seed(42)
        eps_paths = np.zeros((n_simulations, years + 1))
        eps_paths[:, 0] = baseline_eps

        for t in range(1, years + 1):
            growth_rates = np.random.normal(mean_growth, std_dev, n_simulations)
            eps_paths[:, t] = eps_paths[:, t - 1] * (1 + growth_rates)

        return eps_paths

    eps_paths = simulate_eps_paths(baseline_eps, years_forward, n_simulations, mean_growth, std_dev)

    # Calculate final SPY prices
    final_eps_sims = eps_paths[:, -1]
    final_spx_sims = final_eps_sims * pe_ratio_mc
    final_spy_sims = final_spx_sims * spy_multiplier

    # Create distribution plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(final_spy_sims, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    ax.axvline(x=np.mean(final_spy_sims), color='red', linestyle='--', linewidth=2,
               label=f'Mean: ${np.mean(final_spy_sims):.2f}')
    ax.axvline(x=np.median(final_spy_sims), color='orange', linestyle='--', linewidth=2,
               label=f'Median: ${np.median(final_spy_sims):.2f}')
    ax.set_title(f'SPY Price Distribution in {target_year} (P/E {pe_ratio_mc}×, {n_simulations:,} Simulations)',
                 fontsize=16, fontweight='bold')
    ax.set_xlabel('SPY Price ($)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    st.pyplot(fig)

    # Summary statistics
    st.subheader("📊 Distribution Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Mean Price", f"${np.mean(final_spy_sims):.2f}")
    with col2:
        st.metric("Median Price", f"${np.median(final_spy_sims):.2f}")
    with col3:
        st.metric("Std Deviation", f"${np.std(final_spy_sims):.2f}")
    with col4:
        st.metric("Coefficient of Variation", f"{(np.std(final_spy_sims)/np.mean(final_spy_sims)*100):.1f}%")

    # Confidence intervals
    st.subheader("Confidence Intervals")

    percentiles = [5, 25, 50, 75, 95]
    percentile_values = [np.percentile(final_spy_sims, p) for p in percentiles]

    ci_data = pd.DataFrame({
        'Percentile': [f'{p}th' for p in percentiles],
        'SPY Price': [f'${v:.2f}' for v in percentile_values],
        'Return from Baseline': [f'{((v/baseline_spy - 1)*100):.1f}%' for v in percentile_values]
    })

    st.dataframe(ci_data, use_container_width=True)

    st.success(f"""
               **95% Confidence Interval:** ${np.percentile(final_spy_sims, 2.5):.2f} – ${np.percentile(final_spy_sims, 97.5):.2f}

    This means there's a 95% probability that SPY will be within this range by {target_year},
    given the specified parameters.
    """)

with tab4:
    st.header("📖 About This Project")
    st.markdown(readme_content)

# Footer
st.markdown("---")
st.markdown("""
**🧠 Notes:**
- This framework assumes no dividend reinvestment
- Historical analogs provided for context
- Adjust parameters to simulate different macro regimes
- Monte Carlo simulation uses random sampling for probabilistic outcomes
""")
