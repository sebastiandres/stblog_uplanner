import streamlit as st
try:
    st.set_page_config(layout="wide")
except:
    pass
#import streamlit_book as stb

from datetime import datetime
import os

from helpers.export_to_excel_helpers import export_to_excel         

st.title("Exportar CSV a Excel")

mkd = """
* **Inputs**: Archivos csv. Pueden tener distintos encodings, pero deben tener el mismo separador.
    * Archivos csv a exportar a excel.
    * Separador de los archivos csv.
* **Outputs**: Archivo excel, donde cada archivo csv será una pestaña. Todas las celdas serán consideradas de tipo string para evitar conversiones innecesarias.
"""
st.markdown(mkd)

# Dynamic date generation
aaaammdd = datetime.now().strftime("%Y%m%d")

# Main - first file
c1, c2, c3 = st.columns([3,3,2])
uploaded_files = c1.file_uploader("Archivos [csv]", type="csv", accept_multiple_files=True)
separator_str = c2.selectbox("Separador - Output:", options=[";", ",", "\\t", "-"]).replace("\\t","\t")
# Generate download section
all_files_correct = len(uploaded_files)>0

st.markdown("---")
# The file processing
c1, c2, c3, c4 = st.columns([5,3,3,5])
c1.subheader("Outputs")
message_ph = st.empty()
if not all_files_correct:
    # If something is not working, stop here...
    message_ph.error("Primero debes subir todos los archivos correctamente.")
    # If previously set up, delete the download path
    if "executed_outputs" in st.session_state:
        del st.session_state.executed_outputs
else:
    create_button = c2.button("Crear archivo de layouts concatenados (zip)")
    if create_button:
        # Information
        message_ph.info("¡Trabajando en ello, jefe!")
        # Execute here
        executed_outputs = export_to_excel(uploaded_files, aaaammdd, separator_str)
        st.session_state.executed_outputs = executed_outputs
        message_ph.info("¡El archivo de trabajo está listo!")

if "executed_outputs" in st.session_state:
    download_filepath, stats_dict = st.session_state.executed_outputs
    with open(download_filepath, "rb") as file_handler: 
        c3.download_button(label="Descargar archivo de layouts concatenados (zip)", 
                            data=file_handler,
                            file_name=os.path.basename(download_filepath))
        st.markdown("Para mayor detalle del estado de la concatenación, expandir el archivo en análisis:")
        for expander_header, expander_content_list in stats_dict.items():
            with st.expander(expander_header):
                for expander_content in expander_content_list:
                    st.write(expander_content)