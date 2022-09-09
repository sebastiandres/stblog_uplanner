import pandas as pd
import numpy as np

def get_missing_rows(df):
    """
    Returns the missing rows in the dataframe.
    """
    row_col = df["NumeroFila"].astype(int)
    max_rows = row_col.max()
    missing_rows = sorted(list(set(range(1,max_rows+1)) - set(list(row_col))))
    return missing_rows

def get_duplicated_rows(df):
    """
    Returns the duplicated rows in the dataframe.
    """
    check_cols = list(df.columns)
    check_cols.remove("NumeroFila")
    df_aux = df[check_cols]
    m = df_aux.duplicated(keep=False)
    duplicated_rows = df_aux[m]
    return duplicated_rows

def get_duplicated_rows_time(df):
    """
    Returns the duplicated rows in a subset of the dataframe
    Considers different data from columns ["Seccion", "Dia", "Modulo", "Sala", "Semanas"]
    Calculates duplicates from ["Dia", "Modulo", "Sala", "Semanas"]
    """
    # Construct the dataframe
    assignation_cols = ["Seccion", "Dia", "Modulo", "Sala", "Semanas"]
    m = np.logical_and(df.Dia!="", df.Modulo!="")
    m = np.logical_and(m, df.Sala!="")
    df_assignation = df[m].drop_duplicates(subset=assignation_cols)
    # Check duplicity
    check_cols = ["Dia", "Modulo", "Sala", "Semanas"]
    m = df_assignation.duplicated(subset=check_cols, keep=False)
    duplicated_rows = df_assignation[m]
    N_duplicated = duplicated_rows.duplicated(subset=check_cols).sum()
    return N_duplicated, duplicated_rows

def room_but_no_time(df):
    room_col = df["Sala"].astype(str)
    m = room_col!=""
    df_m = df[m]
    m_error = np.logical_or(df_m["Dia"]=="", df_m["Modulo"]=="")
    return df_m[m_error]

def incorrect_number_of_time_blocks(df):
    # Filter for the assigned time blocks, iterate through the sections and compare
    time_col = df["Dia"].astype(str)
    m = time_col!=""
    df_m = df[m]
    # iterate over the sessions
    section_with_errors_list = []
    for seccion, g in df_m.groupby("Seccion"):
        # Get the number of blocks
        time_blocks = list(g["TotalBloquesSemanales"].unique())
        n_programs = g["Programa"].nunique()
        n_time_blocks = int(time_blocks[0]) # Casting is important or the equality will be false
        if len(g)!=n_time_blocks*n_programs:
            section_with_errors_list.append(seccion)
    # Create dataframe
    df_error = df[df.Seccion.isin(section_with_errors_list)]
    return df_error

def sections_to_fix(df):
    """
    Returns a dataframe of Seccion/Grupos that are not assigned
    """
    m = df["Dia"]==""
    df_sections_todo = df.loc[m, ["Seccion", "GrupoCompatible"]].drop_duplicates()
    df_sections_todo = df_sections_todo.reset_index(drop=True)
    return df_sections_todo

def groups_to_fix(df_final):
    """
    Returns a dataframe of combined groups that need to be fixed
    """
    df_aux = df_final[["GrupoCompatible", "Dia"]]
    df_aux.loc[:,"Grupo"] = df_aux["GrupoCompatible"].apply(lambda x: tuple(sorted(list(set(x.split(","))))))
    df_aux.loc[:,"fixing"] = df_aux["Dia"]==""
    df_aux2 = df_aux[["Grupo", "fixing"]].drop_duplicates()
    groups = list(zip(df_aux2["Grupo"], df_aux2["fixing"]))
    unmerged_groups, merged_groups = groups[1:], groups[:1]
    for k1,v1 in unmerged_groups:
        k1_set = set(k1) # k1_set, v1 = set(g1[0]), g1[1]
        already_included = False
        for k2,v2 in merged_groups:
            k2_set = set(k2)
            #print( k1_set, ":", v1, k2_set, ":", v2, "->", merged_groups)
            # See if it should be merged to existant group
            if len(k1_set.intersection(k2_set))>0:
                #print("Cambiazo!")
                k = tuple(sorted(list(k1_set.union(k2_set))))
                v = v1 or v2
                merged_groups.remove((k2,v2))
                merged_groups.append((k,v))
                already_included = True
        # If it couldnt be found elsewhere, include by itself
        if not already_included:
            merged_groups.append((k1,v1))

    df_groups = pd.DataFrame(columns=["GrupoAux","Fix?"], data=merged_groups)
    df_groups_tofix = df_groups[df_groups["Fix?"]] # Select the ones to fix
    df_groups_tofix.loc[:, "len"] = df_groups_tofix["GrupoAux"].apply(lambda x: len(x))
    df_groups_tofix.loc[:, "min"] = df_groups_tofix["GrupoAux"].apply(lambda x: min([int(_)for _ in x]))
    df_groups_tofix.loc[:, "group"] = df_groups_tofix["GrupoAux"].apply(lambda x: ",".join(x))
    df_groups_tofix = df_groups_tofix.sort_values(["len", "min"])
    df_groups_tofix_save = df_groups_tofix[["group"]].reset_index(drop=True)
    return df_groups_tofix_save

def inconsistent_schedule_to_fix(df_final):
    """
    """
    rows = []
    for IdSeccionPadre, g in df_final.groupby("IdSeccionPadre"):
        error = ""
        g = g.sort_values(["Asignatura", "Actividad", "Dia", "Modulo"]).reset_index(drop=True)
        # Add UnidadTematica
        g["UnidadTematica"] = g["Actividad"].apply(lambda x: x.split(".")[0])

        # Count actividades por UnidadTematica
        NMaxUnidadTematica = g[["UnidadTematica","Actividad"]].groupby(["UnidadTematica"]).nunique().values.max()
        if NMaxUnidadTematica==1:
            rows.append([IdSeccionPadre, error])
            continue # No error will be found

        # Count unidadesTematicas por semanas-calendario
        NMaxUnidadTematica = g[["Semanas","UnidadTematica"]].groupby(["Semanas"]).nunique().values.max()
        if NMaxUnidadTematica==1:
            rows.append([IdSeccionPadre, error])
            continue # No error will be found
        # Get the number of weekly modules, if error skips IdSeccionPadre
        g["TotalBloquesSemanales"] = g["TotalBloquesSemanales"].astype("int")
        df_aux = g[["Actividad", "Semanas","TotalBloquesSemanales"]].drop_duplicates()
        df_aux2 = df_aux.groupby("Semanas").sum().reset_index()
        if df_aux2["TotalBloquesSemanales"].nunique()!=1:
            rows.append([IdSeccionPadre, "BloquesSemanales no me cuadra;"])
            continue # No error will be found
        Nblocks = df_aux2["TotalBloquesSemanales"].unique()[0]
        # Check only if everything has been assigned
        if any(g["Sala"]=="") or any(g["Dia"]=="") or any(g["Dia"]==""):
            rows.append([IdSeccionPadre, error]) # This is a different error, not for idPadre
            continue
        # Get the number of rows
        Nrows = g.shape[0]
        Npatterns = Nrows//Nblocks
        if Nblocks*Npatterns!=Nrows:
            rows.append([IdSeccionPadre, error])
            continue # Not the problem to be solved
        # We can compare properly
        error_list = []
        for i in range(Npatterns-1):
            m1 = range(i*Nblocks,(i+1)*Nblocks) 
            m2 = range((i+1)*Nblocks,(i+2)*Nblocks)
            error_dia = any(g.loc[m1, "Dia"].values!=g.loc[m2, "Dia"].values)
            error_modulo = any(g.loc[m1, "Modulo"].values!=g.loc[m2, "Modulo"].values)
            error_list.append(error_dia or error_modulo)
        if any(error_list):
            error += "Días y modulos asignados no respetan patrón para IdSeccionPadre"
        # Check the Room (sala)
        df_aux = g[["UnidadTematica", "Sala"]].drop_duplicates()
        df_aux2 = df_aux.groupby("UnidadTematica").nunique().reset_index()
        if df_aux2["Sala"].max()!=1:
            rows.append([IdSeccionPadre, "Más de una sala por unidad temática;"])
        # Append the information
        rows.append([IdSeccionPadre, error])

    # Create dataframe
    df_idpadre_tofix = pd.DataFrame(columns=["IdSeccionPadre", "Error"], data=rows)
    df_idpadre_tofix["aux"] = df_idpadre_tofix["IdSeccionPadre"].astype(int)
    df_idpadre_tofix = df_idpadre_tofix.sort_values("aux")
    df_idpadre_tofix_save = df_idpadre_tofix.loc[df_idpadre_tofix["Error"]!="", ["IdSeccionPadre", "Error"]]
    df_idpadre_tofix_save = df_idpadre_tofix_save.reset_index(drop=True)

    return df_idpadre_tofix_save

def dataframe_description(df_final):
    """
    Creates the described dataframe
    """
    df_count = df_final.describe(include="all").T.fillna("")
    df_count.loc[:,"Empty"] = (df_final=="").sum()
    return df_count
