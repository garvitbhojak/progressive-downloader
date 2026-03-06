import streamlit as st
import requests

st.set_page_config(page_title='Moviez Downloader', page_icon='🍿', layout='centered')

st.title("Moviez Downloader")
st.divider()

url = st.text_input("Enter Video URL:", placeholder="https://example.com/video.mp4")

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
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Content-Type", content_type)
            with col2:
                st.metric("Size", size_mb)
            with col3:
                st.metric("Accept-Ranges", "Yes" if supports_ranges else "No")
                
            if 'video' in content_type.lower():
                st.video(url)
            else:
                st.warning(f"The URL points to a resource of type '{content_type}', not a video.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error analyzing the URL: {e}")
    else:
        st.warning("Please enter a valid URL.")
