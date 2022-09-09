import streamlit as st
# Set wide display, if not done before
try:
    st.set_page_config(layout="wide", page_title="uPlanner's Streamlit Demo")
except:
    pass

st.title("Home")

mkd = """
This web app is a demo of streamlit capabilities to easily put a frontend to previously created python scripts.
We are sharing a simplified version of some of the shared functionalities we internally used at uPlanner. 

This web app has been developped to accompany the blog post: [uPlanner uses Streamlit to boost teams’ autonomy and foster innovation in data processing tasks ](https://blog.streamlit.io/).

Of course, this is provided as an example and no warranty is provided. We hope you find it useful as a starting point!
"""
st.markdown(mkd)

st.image("images/uplanner.png", width=400)
