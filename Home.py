import streamlit as st

# Set wide display, if not done before
try:
    st.set_page_config(layout="wide", page_title="uPlanner's Streamlit Demo")
except:
    pass

st.title("Home")

mkd = """
This web app is a demo of streamlit capabilities to easily put a 
frontend to multiple types of python scripts.

This web app has been developped to accompany the blog post: 
[uPlanner uses Streamlit to boost teams’ autonomy and foster innovation in data processing tasks ](https://blog.streamlit.io/). It contains a simplified version of some  
functionalities used at uPlanner. 
 
Please notice the app and code is provided as a starting point for your own projects, 
and no warranty is provided. 

We hope you find it useful!
"""
st.markdown(mkd)

st.image("images/uplanner.png", width=400)
