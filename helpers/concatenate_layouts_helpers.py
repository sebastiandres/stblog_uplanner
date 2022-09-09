def concatenate_layouts(uploaded_files_1, uploaded_files_2, 
                        date_str, encoding_str, separator_str):
    """
    Create a folder where to put the created files.
    Creates all layouts that could be matched.
    Creates a zip file with the layouts.
    Return the zip filepath so it can be downloaded.
    """
    from datetime import datetime
    import pandas as pd
    import shutil
    import os
    from .helpers import read_uploaded_csv

    # Variables
    LAYOUT_POSTFIX = "_aaaammdd.csv"
    LAYOUT_TAIL = len(LAYOUT_POSTFIX)
    # Create the filename and folder
    now_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    folder_to_zip = f"tmp/Layouts_{now_str}"
    os.mkdir(folder_to_zip)
    # Create the files
    expander_dict = {}
    for file_1 in sorted(uploaded_files_1, key=lambda x: x.name[:-LAYOUT_TAIL]):
        basename_1 = file_1.name[:-LAYOUT_TAIL] # remove _20201010.csv
        for file_2 in sorted(uploaded_files_2, key=lambda x: x.name[:-LAYOUT_TAIL]):
            basename_2 = file_2.name[:-LAYOUT_TAIL] # remove _20201010.csv
            if basename_1 ==basename_2:
                # We need to join the files
                df_1, encoding_1 = read_uploaded_csv(file_1)
                df_2, encoding_2 = read_uploaded_csv(file_2)
                df_12 = pd.concat([df_1, df_2])
                df_12_dups = df_12[df_12.duplicated()]
                df_12 = df_12.drop_duplicates()
                # We save the file
                filename_12 = f"{basename_1}_{date_str}.csv" 
                filepath_12 = f"{folder_to_zip}/{filename_12}" 
                df_12.to_csv(filepath_12, index=False, sep=separator_str, encoding=encoding_str)
                # Do stats analysis on the files
                Nrows_1, Ncols_1 = df_1.shape
                Nrows_2, Ncols_2 = df_2.shape
                Nrows_12, Ncols_12 = df_12.shape
                analysis_status = "OK"
                expander_content_list = []                
                # Row analisis
                if (Nrows_12 == Nrows_1 + Nrows_2):
                    expander_content_list.append("[OK] Filas: Archivos no tienen filas duplicadas.")
                else:
                    expander_content_list.append(f"**[WARNING] Filas: Archivos poseen las siguientes {df_12_dups.shape[0]:,} filas duplicadas.**")
                    expander_content_list.append(df_12_dups)
                    analysis_status = "WARNING"
                # Column analisis
                if (Ncols_12 == Ncols_1 == Ncols_2):
                    expander_content_list.append("[OK] Columnas: Ambos archivos tienen las mismas columnas.")
                else:
                    expander_content_list.append("**[ERROR] Columnas: Archivos NO poseen las mismas columnas.**")
                    expander_content_list.append(f"Columnas de archivo 1: {', '.join(df_1.columns)}")
                    expander_content_list.append(f"Columnas de archivo 2: {', '.join(df_2.columns)}")
                    s1 = set(df_1.columns)
                    s2 = set(df_2.columns)
                    unknown_columns = list(s1.union(s2) - s1.intersection(s2))
                    expander_content_list.append(f"Columnas distintas: {', '.join(unknown_columns)}")
                    analysis_status = "ERROR"
                # Pack and go
                expander_header = f"{analysis_status}: {filename_12}" 
                expander_dict[expander_header] = expander_content_list

    # Zip the folder
    executed_outputs = f"tmp/Layouts_{date_str}.zip"
    filename_without_extension = executed_outputs.split(".")[0]
    shutil.make_archive(filename_without_extension, "zip", folder_to_zip)
    return executed_outputs, expander_dict  