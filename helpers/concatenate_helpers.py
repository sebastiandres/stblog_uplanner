def concatenate_files(uploaded_files_1, uploaded_files_2, 
                        date_str, 
                        encoding_str_1, separator_str_1,
                        encoding_str_2, separator_str_2,
                        encoding_str_3, separator_str_3
                        ):
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
                df_1, read_csv_params_1 = read_uploaded_csv(file_1, encoding=encoding_str_1, separator=separator_str_1)
                df_2, read_csv_params_2 = read_uploaded_csv(file_2, encoding=encoding_str_2, separator=separator_str_2)
                df_12 = pd.concat([df_1, df_2])
                df_12_dups = df_12[df_12.duplicated()]
                df_12 = df_12.drop_duplicates()
                # We save the file
                filename_12 = f"{basename_1}_{date_str}.csv" 
                filepath_12 = f"{folder_to_zip}/{filename_12}" 
                df_12.to_csv(filepath_12, index=False, sep=separator_str_3, encoding=encoding_str_3)
                # Do stats analysis on the files
                Nrows_1, Ncols_1 = df_1.shape
                Nrows_2, Ncols_2 = df_2.shape
                Nrows_12, Ncols_12 = df_12.shape
                analysis_status = "OK"
                expander_content_list = []                
                # File properties
                expander_content_list.append(f"* File 1: encoding = {read_csv_params_1['encoding']}, separator = {read_csv_params_1['sep']}")
                expander_content_list.append(f"* File 2: encoding = {read_csv_params_2['encoding']}, separator = {read_csv_params_2['sep']}")
                # Row analisis
                if (Nrows_12 == Nrows_1 + Nrows_2):
                    expander_content_list.append("* [OK] Rows: No duplicated rows.")
                else:
                    expander_content_list.append(f"* **[WARNING] Rows: There are {df_12_dups.shape[0]:,} duplicated rows.**")
                    expander_content_list.append(df_12_dups)
                    analysis_status = "WARNING"
                # Column analisis
                if (Ncols_12 == Ncols_1 == Ncols_2):
                    expander_content_list.append("* [OK] Columns: Both files have the same columns.")
                else:
                    expander_content_list.append("* **[ERROR] Columns: Files have different columns.**")
                    expander_content_list.append(f"* Columns on file 1: {', '.join(df_1.columns)}")
                    expander_content_list.append(f"* Columns on file 2: {', '.join(df_2.columns)}")
                    s1 = set(df_1.columns)
                    s2 = set(df_2.columns)
                    unknown_columns = list(s1.union(s2) - s1.intersection(s2))
                    expander_content_list.append(f"* Different columns: {', '.join(unknown_columns)}")
                    analysis_status = "ERROR"
                # Pack and go
                expander_header = f"{analysis_status}: {filename_12}" 
                expander_dict[expander_header] = expander_content_list

    # Zip the folder
    executed_outputs = f"tmp/Concatenation_{date_str}.zip"
    filename_without_extension = executed_outputs.split(".")[0]
    shutil.make_archive(filename_without_extension, "zip", folder_to_zip)
    return executed_outputs, expander_dict  