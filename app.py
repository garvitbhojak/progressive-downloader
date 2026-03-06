import streamlit as st
import requests

st.set_page_config(page_title='Moviez Downloader', page_icon='🍿', layout='centered')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🍿 Moviez")
    st.subheader("About the Developer")
    st.markdown("Hi, I'm the developer. 👋")
    st.markdown("I'm a software developer. I built this tool to solve a specific problem: streaming remote videos directly without downloading the whole file first.")
    st.markdown("This bot uses standard HTTP Range requests to fetch public video chunks and do the streaming for you.")
    
    st.divider()
    
    st.markdown("🔗 **Connect**")
    st.markdown("[GitHub Profile](#)")
    st.markdown("[Instagram: @developer](#)")

# --- MAIN PAGE ICON ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<h1 style='text-align: center; font-size: 120px; margin-bottom: 0;'>🍿</h1>", unsafe_allow_html=True)

# --- TABS ---
tab_download, tab_bulk = st.tabs(["🚀 Video Downloader", "📁 Bulk Link Extractor"])

with tab_download:
    st.title("Moviez Downloader")
    
    st.markdown("Stream your video instantly. Paste the **link** of a specific video, and this tool will analyze the headers to allow progressive streaming.")
    
    with st.expander("ℹ️ How does this work?"):
        st.markdown(
            "When you paste a video URL, we send a lightweight request to grab the video's content length and type. "
            "If the server supports byte ranges, we load the URL directly into a custom video player!"
        )
    
    url = st.text_input("Enter Video URL:", placeholder="https://example.com/video.mp4", label_visibility="collapsed")
    
    if st.button("Analyze & Watch"):
        if url:
            try:
                response = requests.head(url, allow_redirects=True, timeout=10)
                response.raise_for_status()
                
                headers = response.headers
                content_length = headers.get('Content-Length')
                content_type = headers.get('Content-Type', 'Unknown')
                accept_ranges = headers.get('Accept-Ranges')
                
                size_mb = "Unknown"
                if content_length and content_length.isdigit():
                    size_mb = f"{int(content_length) / (1024 * 1024):.2f} MB"
                    
                supports_ranges = (accept_ranges == 'bytes')
                
                st.subheader("Metadata")
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("Content-Type", content_type)
                with m_col2:
                    st.metric("Size", size_mb)
                with m_col3:
                    st.metric("Accept-Ranges", "Yes" if supports_ranges else "No")
                    
                if 'video' in content_type.lower():
                    st.divider()
                    st.video(url)
                else:
                    st.warning(f"The URL points to a resource of type '{content_type}', not a video.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Error analyzing the URL: {e}")
        else:
            st.warning("Please enter a valid URL.")

with tab_bulk:
    st.title("Bulk Link Extractor")
    st.info("Bulk feature coming soon!")
