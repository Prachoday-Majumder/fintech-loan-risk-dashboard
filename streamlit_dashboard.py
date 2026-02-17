import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Fintech Loan Analysis Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        max-width: 100%;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2em;
        color: #667eea;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('fintech_competition_40k.csv')
    return df

# Main app
def main():
    st.title("🚀 Fintech Loan Analysis Dashboard")
    st.markdown("### Complete dataset: 40,000 loan records with advanced filtering and analytics")
    
    # Load data
    df = load_data()
    
    # Calculate metrics
    total_loans = len(df)
    defaulters = len(df[df['loan_status'].isin(['Charged Off', 'Late (31-120 days)', 'Late (16-30 days)'])])
    avg_loan = df['loan_amnt'].mean()
    avg_rate = df['int_rate'].mean()
    total_volume = df['loan_amnt'].sum()
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Loans", f"{total_loans:,}")
    with col2:
        st.metric("Defaulters", f"{defaulters:,}", f"{defaulters/total_loans*100:.1f}%")
    with col3:
        st.metric("Avg Loan", f"${avg_loan:,.0f}")
    with col4:
        st.metric("Avg Rate", f"{avg_rate:.1f}%")
    with col5:
        st.metric("Total Volume", f"${total_volume/1e6:.1f}M")
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Loan Status Distribution")
        status_counts = df['loan_status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=['#667eea', '#48bb78', '#f56565', '#ed8936', '#ecc94b', '#fc8181']
        )
        fig.update_traces(textinfo='label+percent')
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Interest Rate Distribution")
        fig = px.histogram(
            df,
            x='int_rate',
            nbins=30,
            labels={'int_rate': 'Interest Rate (%)'},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Data explorer tabs
    st.subheader("📋 Complete Dataset Explorer")
    
    st.info("💡 **Features:** Search, sort, and filter through all records. Use the tabs to view different loan categories.")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        f"All Loans ({total_loans:,})",
        f"Defaulters ({defaulters:,})",
        f"Current ({len(df[df['loan_status']=='Current']):,})",
        f"Fully Paid ({len(df[df['loan_status']=='Fully Paid']):,})",
        "High Risk"
    ])
    
    with tab1:
        st.markdown("### All Loan Records")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search_job = st.text_input("Search by Job Title", "")
        with col2:
            status_filter = st.multiselect("Filter by Status", df['loan_status'].unique())
        with col3:
            state_filter = st.multiselect("Filter by State", sorted(df['addr_state'].unique()))
        
        # Filter data
        filtered_df = df.copy()
        if search_job:
            filtered_df = filtered_df[filtered_df['emp_title'].str.contains(search_job, case=False, na=False)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['loan_status'].isin(status_filter)]
        if state_filter:
            filtered_df = filtered_df[filtered_df['addr_state'].isin(state_filter)]
        
        st.write(f"Showing {len(filtered_df):,} of {total_loans:,} records")
        
        # Display data
        display_cols = ['loan_amnt', 'loan_term', 'int_rate', 'monthly_payment', 'sub_grade', 
                       'emp_title', 'emp_length', 'home_ownership', 'annual_inc', 'total_dti',
                       'loan_purpose', 'addr_state', 'loan_status', 'delinq_2yrs', 'credit_limit']
        
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            height=600
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            csv,
            "filtered_loans.csv",
            "text/csv",
            key='download-all'
        )
    
    with tab2:
        st.markdown("### Defaulter Records")
        defaulter_df = df[df['loan_status'].isin(['Charged Off', 'Late (31-120 days)', 'Late (16-30 days)'])]
        
        st.warning(f"⚠️ **{len(defaulter_df):,}** loans are in default status (Charged Off or Late)")
        
        display_cols = ['loan_amnt', 'int_rate', 'monthly_payment', 'emp_title', 'annual_inc', 
                       'total_dti', 'home_ownership', 'loan_purpose', 'addr_state', 'loan_status',
                       'delinq_2yrs', 'emp_length']
        
        st.dataframe(
            defaulter_df[display_cols].sort_values('loan_amnt', ascending=False),
            use_container_width=True,
            height=600
        )
        
        csv = defaulter_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Defaulters (CSV)",
            csv,
            "defaulters.csv",
            "text/csv",
            key='download-defaulters'
        )
    
    with tab3:
        st.markdown("### Current Loans")
        current_df = df[df['loan_status'] == 'Current']
        
        st.success(f"✅ **{len(current_df):,}** loans are current and performing")
        
        display_cols = ['loan_amnt', 'int_rate', 'monthly_payment', 'emp_title', 'annual_inc',
                       'total_dti', 'home_ownership', 'loan_purpose', 'addr_state', 'emp_length']
        
        st.dataframe(
            current_df[display_cols].sort_values('loan_amnt', ascending=False),
            use_container_width=True,
            height=600
        )
        
        csv = current_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Current Loans (CSV)",
            csv,
            "current_loans.csv",
            "text/csv",
            key='download-current'
        )
    
    with tab4:
        st.markdown("### Fully Paid Loans")
        paid_df = df[df['loan_status'] == 'Fully Paid']
        
        st.success(f"✅ **{len(paid_df):,}** loans have been fully paid off")
        
        display_cols = ['loan_amnt', 'int_rate', 'monthly_payment', 'emp_title', 'annual_inc',
                       'total_dti', 'home_ownership', 'loan_purpose', 'addr_state']
        
        st.dataframe(
            paid_df[display_cols].sort_values('loan_amnt', ascending=False),
            use_container_width=True,
            height=600
        )
        
        csv = paid_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Paid Loans (CSV)",
            csv,
            "paid_loans.csv",
            "text/csv",
            key='download-paid'
        )
    
    with tab5:
        st.markdown("### High Risk Loans")
        st.warning("⚠️ **High Risk Criteria:** Interest Rate > 15% OR DTI > 25 OR Past Delinquencies > 0")
        
        high_risk_df = df[
            (df['int_rate'] > 15) | 
            (df['total_dti'] > 25) | 
            (df['delinq_2yrs'] > 0)
        ]
        
        st.error(f"🎯 **{len(high_risk_df):,}** loans meet high-risk criteria")
        
        display_cols = ['loan_amnt', 'int_rate', 'total_dti', 'emp_title', 'annual_inc',
                       'home_ownership', 'loan_status', 'delinq_2yrs', 'loan_purpose', 'emp_length']
        
        st.dataframe(
            high_risk_df[display_cols].sort_values('int_rate', ascending=False),
            use_container_width=True,
            height=600
        )
        
        csv = high_risk_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download High Risk Loans (CSV)",
            csv,
            "high_risk_loans.csv",
            "text/csv",
            key='download-highrisk'
        )

if __name__ == "__main__":
    main()
