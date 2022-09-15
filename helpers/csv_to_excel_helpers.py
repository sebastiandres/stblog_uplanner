def export_to_excel(uploaded_files, date_str, encoding_str, separator_str):
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
    LAYOUT_POSTFIX = ".csv"
    LAYOUT_TAIL = len(LAYOUT_POSTFIX)
    # Create the filename and folder
    now_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    folder_to_zip = f"tmp/exported_to_excel_{now_str}"
    os.mkdir(folder_to_zip)
    # Read the files
    expander_dict = {}
    df_dict = {}
    for csv_file in sorted(uploaded_files, key=lambda x: x.name):
        try:
            basename = csv_file.name[:-LAYOUT_TAIL]
            df, read_csv_params = read_uploaded_csv(csv_file)
            expander_content_list = []                
            n = 5
            expander_content_list.append(f"* Encoding: {read_csv_params['encoding']}")
            expander_content_list.append(f"* Separator: {read_csv_params['sep']}")
            expander_content_list.append(f"* Rows: {df.shape[0]}")
            expander_content_list.append(f"* Columns: {df.shape[1]}")
            expander_content_list.append(df.head(n))
            expander_content_list.append(f"First {n} rows:")
            expander_dict[basename] = expander_content_list
            df_dict[basename[:30]] = df
        except Exception as e:
            expander_dict["ERROR!!!:" + basename] = ["Could not read the file", "File skipped", f"ERROR: {e}"]
    # Create the excel file
    excel_filepath = folder_to_zip + f"/excel_from_csv_{date_str}.xlsx"
    with pd.ExcelWriter(excel_filepath) as ew:
        for sheet_name, df in df_dict.items():
            df.to_excel(ew, sheet_name=sheet_name, index=False)

    # Zip the folder
    executed_outputs = f"tmp/exported_to_excel_{date_str}.zip"
    filename_without_extension = executed_outputs.split(".")[0]
    shutil.make_archive(filename_without_extension, "zip", folder_to_zip)
    return executed_outputs, expander_dict  