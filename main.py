import streamlit as st


# Page configuration
st.set_page_config(
    page_title="Operating Systems Dashboard",
    page_icon="computer",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for styling
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 40px;
    }
    .module-card {
        padding: 30px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 20px 0;
        transition: transform 0.3s;
    }
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .module-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 15px;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #666;
        border-top: 1px solid #ddd;
    }
    </style>
""", unsafe_allow_html=True)


# Main Dashboard Header
st.markdown('<h1 class="main-title">Operating Systems Dashboard</h1>', unsafe_allow_html=True)


# Introduction
st.markdown("---")


# Module Cards
col1, col2, col3 = st.columns(3)


with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">CPU Scheduling</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Open CPU Scheduling", use_container_width=True, type="primary"):
        st.switch_page("pages/cpu_scheduling_final.py")


with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">Deadlock Resolving</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Open Deadlock Resolving", use_container_width=True, type="primary"):
        st.switch_page("pages/deadlock_resolver.py")


with col3:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">Memory and Segmentation</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Open Memory and Segmentation", use_container_width=True, type="primary"):
        st.switch_page("pages/paging_segmentation_final.py")



# Quick Links Section
st.markdown("---")
st.markdown("## Quick Access")


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.page_link("pages/cpu_scheduling_final.py", label="CPU Scheduling")
    
with col2:
    st.page_link("pages/deadlock_resolver.py", label="Deadlock Resolving")
    
with col3:
    st.page_link("pages/paging_segmentation_final.py", label="Memory and Segmentation")


with col4:
    st.page_link("main.py", label="Home")
