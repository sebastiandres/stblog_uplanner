import streamlit as st
try:
    st.set_page_config(layout="wide", page_title="uPlanner's Streamlit Demo")
except:
    pass
#import streamlit_book as stb

from datetime import datetime
import os

from helpers.concatenate_layouts_helpers import concatenate_layouts         

st.title("Concatenate Files")

mkd = """
* **Inputs**: On both input files, encoding will be infered.
    * File 1: 
    * Layouts adicionales a concatenar.
    * Opcionalmente, puedes indicar la fecha, el encoding y el Separator deseado en los archivos de salida, aunque se aconseja dejar los valores por defecto.
* **Output**: A zip file containing a single file with the concatenation of files 1 and 2. Concatenated file will be saved with desired encoding and separator. Zip filename will have today's date. 
"""
#st.markdown(mkd)

# Main - first file
#c1, c2, _ = st.columns([3,2,5])
yyyymmdd = datetime.now().strftime("%Y%m%d")
# First batch of files
st.subheader("First set of files")
c1, c2, c3 = st.columns([3,3,2])
uploaded_files_1 = c1.file_uploader("Files 1 [csv]", type="csv", accept_multiple_files=True)
encoding_str = c2.selectbox("Encoding 1:", options=["utf-8-sig", "utf8", "latin1", "ascii", ""])
separator_str = c3.selectbox("Separator 1:", options=[";", ",", "\\t", "-"]).replace("\\t","\t")
st.subheader("Second set of files")
c1, c2, c3 = st.columns([3,3,2])
uploaded_files_2 = c1.file_uploader("Files 2 [csv]", type="csv", accept_multiple_files=True)
encoding_str = c2.selectbox("Encoding 2:", options=["utf-8-sig", "utf8", "latin1", "ascii", ""])
separator_str = c3.selectbox("Separator 2:", options=[";", ",", "\\t", "-"]).replace("\\t","\t")
st.subheader("Output properties")
c1, c2, c3 = st.columns([3,3,2])
date_str = c1.text_input("Date for output file (yyyymmdd)", value=yyyymmdd, max_chars=8)
encoding_str = c2.selectbox("Encoding Output:", options=["utf-8-sig", "utf8", "latin1", "ascii", ""])
separator_str = c3.selectbox("Separator Output:", options=[";", ",", "\\t", "-"]).replace("\\t","\t")
# Generate download section
all_files_correct = len(uploaded_files_1)>0 and len(uploaded_files_2)>0

st.markdown("---")
# The file processing
c1, c2, c3, c4 = st.columns([5,3,3,5])
c1.subheader("Outputs")
message_ph = st.empty()
if not all_files_correct:
    # If something is not working, stop here...
    message_ph.error("Upload files to continue")
    # If previously set up, delete the download path
    if "executed_outputs" in st.session_state:
        del st.session_state.executed_outputs
else:
    create_button = c2.button("Create output file (zip)")
    if create_button:
        # Information
        message_ph.info("Working on it, boss!")
        # Execute here
        executed_outputs = concatenate_layouts(uploaded_files_1, uploaded_files_2, 
                                                date_str, encoding_str, separator_str)
        st.session_state.executed_outputs = executed_outputs
        message_ph.info("Ready boss!")

if "executed_outputs" in st.session_state:
    download_filepath, stats_dict = st.session_state.executed_outputs
    with open(download_filepath, "rb") as file_handler: 
        c3.download_button(label="Download zipped files", 
                            data=file_handler,
                            file_name=os.path.basename(download_filepath))
        st.markdown("To know more, use the expanders:")
        for expander_header, expander_content_list in stats_dict.items():
            with st.expander(expander_header):
                for expander_content in expander_content_list:
                    st.write(expander_content)