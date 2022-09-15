import streamlit as st
import pandas as pd
import chardet
import os 

def create_expander(expander_header, expander_content_list):
    with st.expander(expander_header):
        for expander_content in expander_content_list:
            st.write(expander_content)


def file_uploader_wrapper(file_description, expected_extensions, expected_columns, 
                            validation_function=None, sheet_name=None):
    """
    This is a very smart wrapper to upload files.
    It first checks the file extension and the columns.
    If OK, it calls the (provided) validation_function and returns a dict with errors.
    """
    c1, c2 = st.columns(2)
    uploaded_file = c1.file_uploader(file_description + f" ({'/'.join(expected_extensions)})")
    c2.markdown("") # Empty for alignment
    c2.markdown("") # Empty for alignment
    # Run a basic validation, mostly for extension and columns
    expander_header, expander_content, is_file_ok = file_basic_validation(uploaded_file, expected_extensions, 
                                                                expected_columns, sheet_name)
    # Display the result in the second column
    with c2.expander(expander_header):
        st.markdown(expander_content)
    # Run the optional validation funcion, only if the file is OK
    if is_file_ok and validation_function is not None:
        validation_function(uploaded_file)                                                                            
    return uploaded_file, is_file_ok

def file_basic_validation(uploaded_file, expected_extensions, expected_columns, sheet_name):
    """
    Basic verification of provided file
    """
    # Shared variables
    error_dict = {True:"OK", False:"Error"}
    # Analisis
    if uploaded_file is None:
        expander_header = "Seleccionar archivo"
        expander_content = "Seleccionar archivo usando boton 'Browse Content'"
        is_file_ok = False
    else:
        extension = uploaded_file.name.split(".")[-1]
        correct_extension = extension in expected_extensions
        if not correct_extension:
            expander_header = f"ERROR: Archivo con extensión incorrecta."
            expander_content = f"Se requiere un archivo con extensión {'/'.join(expected_extensions)}"
            is_file_ok = False
        else:
            expander_header = ": " + uploaded_file.name
            if "csv" in expected_extensions:
                df, guessed_encoding = read_uploaded_csv(uploaded_file)
                missing_columns = list(set(expected_columns) - set(df.columns))
                count_missing_columns = len(missing_columns)
                missing_columns_str = ", ".join(missing_columns)
                if count_missing_columns > 0:
                    st.error(f"""El archivo no tiene las siguientes columnas: \n{missing_columns_str}. \n\nEl archivo tiene las siguientes columnas:\n{", ".join(df.columns)}""")
                correct_columns = count_missing_columns==0 # No missing columns
                Nrows, Ncols = df.shape
                expander_content = f"""
                * **File extension**: OK
                * **CSV Encoding**: {guessed_encoding}
                * **Columns**: {error_dict[correct_columns]}
                * **Number of Columns**: {Ncols:,}
                * **Number of Rows**: {Nrows:,}
                """
                is_file_ok = correct_extension and correct_columns
                expander_header = error_dict[is_file_ok] + expander_header
            elif "xlsx" in expected_extensions:
                if sheet_name:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                else:
                    df = pd.read_excel(uploaded_file)
                missing_columns = list(set(expected_columns) - set(df.columns))
                count_missing_columns = len(missing_columns)
                missing_columns_str = ", ".join(missing_columns)
                if count_missing_columns > 0:
                    st.error(f"""El archivo no tiene las siguientes columnas: \n{missing_columns_str}. \n\nEl archivo tiene las siguientes columnas:\n{", ".join(df.columns)}""")
                correct_columns = count_missing_columns==0 # No missing columns
                Nrows, Ncols = df.shape
                expander_content = f"""
                * **File extension**: {error_dict[correct_extension]}
                * **Columns**: {correct_columns}
                * **Number of Columns**: {Ncols:,}
                * **Number of Rows**: {Nrows:,}
                """
                is_file_ok = correct_extension and correct_columns
                expander_header = error_dict[is_file_ok] + expander_header
            else:
                expander_header = f"ERROR: No se leer archivos de extensión {'/'.join(expected_extensions)}"
                expander_content = "Contacte al administrador."
                is_file_ok = False
    return expander_header, expander_content, is_file_ok

def read_uploaded_csv(uploaded_csv_file, encoding="infer", separator="infer", dtype=None):
    """
    Reads an uploaded csv
    """
    # Get the data
    if type(uploaded_csv_file)!=str:
        uploaded_csv_file.seek(0)
        data = uploaded_csv_file.getvalue()
        filename = uploaded_csv_file.name
    else:
        with open(uploaded_csv_file, "rb") as file_handler:
            data = file_handler.read()
        filename = uploaded_csv_file
    # Save the properties for reading the file
    read_csv_params = {}
    # Guess the encoding
    if encoding=="infer":
        read_csv_params["encoding"] = infer_encoding(data[:10000])
    else:
        read_csv_params["encoding"] = encoding
    # Guess the separator
    if separator=="infer":
        read_csv_params["sep"] = infer_separator(data[:10000])
    else:
        read_csv_params["sep"] = separator
    # Match the dtype
    if dtype:
        read_csv_params["dtype"] = dype
    # Read the file
    df = pd.read_csv(uploaded_csv_file, **read_csv_params)
    return df, read_csv_params

def infer_separator(data):
    """
    Guesses the separator of a csv file
    """
    data = str(data)
    # Get the count of each character
    sep_options = [",", ";", "\t"]
    sep_count = {}
    for sep in sep_options:
        sep_count[sep] = data.count(sep)
    print("sep_count", sep_count)
    # Get the highest count
    infer_sep = max(sep_count, key=sep_count.get)
    # Guess the separator
    return infer_sep

def infer_encoding(data):
    """
    Guesses the encoding of a csv file
    """
    # Guess the separator
    analysis = chardet.detect(data)
    infer_enc = analysis["encoding"]
    return infer_enc