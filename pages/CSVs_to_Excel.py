import streamlit as st

# Set page properties, if not made before
try:
    st.set_page_config(layout="wide", page_title="uPlanner's Streamlit Demo")
except:
    pass

from datetime import datetime
import os

from helpers.csv_to_excel_helpers import export_to_excel         

st.title("CSVs to Excel")
st.caption("Merge multiple CSV files into a single Excel file")

# Dynamic date generation
yyyymmdd = datetime.now().strftime("%Y%m%d")

main_tab, help_tab = st.tabs(["Inputs", "Help"])
with main_tab:
    c1, c2, c3 = st.columns([3,3,2])
    uploaded_files = c1.file_uploader("CSV file(s)", type="csv", accept_multiple_files=True)
    encoding_str = c2.selectbox("Encoding:", 
                                options=["infer","utf-8-sig", "utf8", "latin1", "ascii"])
    separator_str = c3.selectbox("Separator:", 
                                 options=["infer", ";", ",", "\\t"]).replace("\\t","\t")

with help_tab:
    # Help section
    mkd = """
    This page allows you to merge multiple CSV files into a single Excel file. 
    You can set specific encodings and separators, or infer them from the file.
    * **Inputs**: 
        * CSV file(s): upload the CSV files you want to merge. 
        You can upload multiple files at once.
        * Encoding: select the encoding of the CSV files. 
        If you don't know, leave it as it is.
        * Separator: select the separator of the CSV files. 
        If you don't know, leave it as it is.
    * **Outputs**: 
        * A zip file containing a single excel file, where each csv files has been saved as a sheet.
    """
    st.markdown(mkd)
st.markdown("---")


# The file processing
c1, c2, c3, c4 = st.columns([5,3,3,5])
c1.subheader("Outputs")
message_ph = st.empty()
all_files_correct = len(uploaded_files)>0
if not all_files_correct:
    # If something is not working, stop here...
    message_ph.error("Please upload at least one file")
    # If previously set up, delete the download path
    if "executed_outputs" in st.session_state:
        del st.session_state.executed_outputs
else:
    create_button = c2.button("Create zipped Excel file (zip)")
    if create_button:
        # Information
        message_ph.info("Bip bop bip... processing...")
        # Execute here
        executed_outputs = export_to_excel(uploaded_files, yyyymmdd, encoding_str, separator_str)
        st.session_state.executed_outputs = executed_outputs
        message_ph.info("Bop! Done!")

if "executed_outputs" in st.session_state:
    download_filepath, stats_dict = st.session_state.executed_outputs
    with open(download_filepath, "rb") as file_handler: 
        c3.download_button(label="Download output (zip)", 
                            data=file_handler,
                            file_name=os.path.basename(download_filepath))
        st.markdown("File Details:")
        for expander_header, expander_content_list in stats_dict.items():
            with st.expander(expander_header):
                for expander_content in expander_content_list:
                    st.write(expander_content)