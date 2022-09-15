import streamlit as st

# Set page properties, if not made before
try:
    st.set_page_config(layout="wide", page_title="uPlanner's Streamlit Demo")
except:
    pass

from datetime import datetime
import os

from helpers.concatenate_helpers import concatenate_files

st.title("Concatenate")
st.caption("Concatenate CSV files that share the same rootname")

input1_tab, input2_tab, output_tab, help_tab = st.tabs(["Input Set 1", "Input Set 2", "Output", "Help"])

yyyymmdd = datetime.now().strftime("%Y%m%d")
sep_options = ["infer", ";", ",", "\\t", "-"]
enc_options = ["infer", "utf-8-sig", "utf8", "latin1", "ascii", ""]

with input1_tab:
    # First batch of files
    st.caption("Properties of the first set of files")
    c1, c2, c3 = st.columns([3,2,2])
    uploaded_files_1 = c1.file_uploader("Files 1 [csv]", type="csv", accept_multiple_files=True)
    encoding_str_1 = c2.selectbox("Encoding 1:", options=enc_options)
    separator_str_1 = c3.selectbox("Separator 1:", options=sep_options).replace("\\t","\t")

with input2_tab:
    st.caption("Second set of files")
    c1, c2, c3 = st.columns([3,2,2])
    uploaded_files_2 = c1.file_uploader("Files 2 [csv]", type="csv", accept_multiple_files=True)
    encoding_str_2 = c2.selectbox("Encoding 2:", options=enc_options)
    separator_str_2 = c3.selectbox("Separator 2:", options=sep_options).replace("\\t","\t")

with output_tab:
    st.caption("Output properties")
    c1, c2, c3 = st.columns([3,2,2])
    date_str = c1.text_input("Date for output file (yyyymmdd)", value=yyyymmdd, max_chars=8)
    encoding_str_3 = c2.selectbox("Encoding Output:", options=enc_options[1:])
    separator_str_3 = c3.selectbox("Separator Output:", options=sep_options[1:]).replace("\\t","\t")

with help_tab:
    # Help section
    mkd = """
    This page allows you to concatenate CSV files of the same rootname. It will respect the column order of the first file,
    and remove any duplicate rows.
    For example, if you provide:
    * Set 1: `name1_20220909.csv`, `name2_20220910.csv`, `name3_20220909.csv`
    * Set 2: `name1_20220809.csv`, `name2_20220812.csv`
    You will get the following files on the output:
    * `name1_yyyymmdd.csv` =  `name1_20220809.csv` concatenated with `name1_20220809.csv`
    * `name2_yyyymmdd.csv` =  `name2_20220910.csv` concatenated with `name2_20220812.csv`
    The file `name3_20220909.csv` will be ignored, as it does not have a counterpart in the second set.
    You can set specific encodings and separators for inputs and outputs (or infer them for the inputs).
    * **Inputs 1**: 
        * CSV file(s): upload the CSV files you want to merge. You can upload multiple files at once. 
        * Encoding: select the encoding of the CSV files. If you don't know, leave it as it is.
        * Separator: select the separator of the CSV files. If you don't know, leave it as it is.
    * **Inputs 2**: 
        * CSV file(s): upload the CSV files you want to merge. You can upload multiple files at once.
        * Encoding: select the encoding of the CSV files. If you don't know, leave it as it is.
        * Separator: select the separator of the CSV files. If you don't know, leave it as it is.
    * **Output Configuration**: 
        * Date: Select the date you want to use for the output files (as `yyyymmdd`).
        * Encoding: select the encoding for the csv files.
        * Separator: select the separator for the csv files. 
    * **Outputs**: 
        * A zip file containing all the csv files.
    """
    st.markdown(mkd)

# Generate download section
all_files_correct = len(uploaded_files_1)>0 and len(uploaded_files_2)>0

st.markdown("---")
# The file processing
#c1, c2, c3, c4 = st.columns([5,3,3,5])
c1, c2, c3 = st.columns([3,2,2])
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
        executed_outputs = concatenate_files(uploaded_files_1, uploaded_files_2, 
                                                date_str, 
                                                encoding_str_1, separator_str_1,
                                                encoding_str_2, separator_str_2,
                                                encoding_str_3, separator_str_3
                                                )
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