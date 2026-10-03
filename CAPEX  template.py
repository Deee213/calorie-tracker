import os
import re
import pandas as pd

# Paths
folder_path = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\Project 1 Rehabilitation of Distribution Lines\2023"
excel_file1 = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\CAPEX_ED - 1.xlsx"
excel_file2 = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\MCT REPORT FOR TSD 04082026.xlsx"
output_file = r"C:\Users\SMS1\Documents\Ed Files\CAPEX\Final_Matched_Materials312.xlsx"

# Extract IDs from filenames
def extract_id(filename):
    matches = re.findall(r'\d+', filename)
    if matches:
        candidate = max(matches, key=len)
        return int(candidate.lstrip("0") or candidate)
    return None

files = os.listdir(folder_path)
file_id_map = {extract_id(f): f for f in files if extract_id(f) is not None}
file_ids = list(file_id_map.keys())

def search_excel_for_ids(excel_file, ids, label, prefix=None, column_index=0):
    xl = pd.ExcelFile(excel_file)
    output_rows = []
    matched_ids = set()
    unmatched_ids = set(ids)

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)

        # Forward-fill Column A (MCT No.)
        df.iloc[:,0] = df.iloc[:,0].fillna(method="ffill")

        if prefix:  # MCT REPORT file (search in column J)
            df["id_norm"] = df.iloc[:,column_index].astype(str).str.strip()
            search_keys = {f"{prefix}{str(fid).zfill(6)}": fid for fid in ids}
            mask = df["id_norm"].isin(search_keys.keys())
            matched_rows = df[mask]

            for _, row in matched_rows.iterrows():
                fid = search_keys[row["id_norm"]]
                matched_ids.add(fid)
                if fid in unmatched_ids:
                    unmatched_ids.remove(fid)

                # Drop the duplicate MCT No. column (column J)
                row_data = row.drop(["id_norm", df.columns[column_index]]).to_dict()
                row_data["MCT No."] = fid
                row_data["File Name"] = file_id_map.get(fid, "")
                row_data["Sheet Name"] = sheet
                row_data["Source File"] = label
                output_rows.append(row_data)

        else:  # CAPEX file (search in column A)
            df["id_norm"] = pd.to_numeric(df.iloc[:,column_index], errors="coerce").astype("Int64")
            mask = df["id_norm"].isin(ids)
            start_indices = df.index[mask].tolist()

            for start in start_indices:
                fid = int(df.loc[start, "id_norm"])
                matched_ids.add(fid)
                if fid in unmatched_ids:
                    unmatched_ids.remove(fid)

                next_idx_candidates = df.index[(df.index > start) & df["id_norm"].notna()]
                next_idx = next_idx_candidates.min() if not next_idx_candidates.empty else len(df)

                block = df.loc[start:next_idx-1].drop("id_norm", axis=1)
                block["MCT No."] = fid
                block["File Name"] = file_id_map.get(fid, "")
                block["Sheet Name"] = sheet
                block["Source File"] = label
                output_rows.extend(block.to_dict("records"))

    return pd.DataFrame(output_rows), matched_ids, unmatched_ids

# Step 1: Search in CAPEX_ED - 1.xlsx (column A)
df1, matched1, unmatched1 = search_excel_for_ids(excel_file1, file_ids, "CAPEX_ED - 1", column_index=0)

# Step 2: Search unmatched IDs in MCT REPORT using "MCTA" prefix (column J = index 9)
df2, matched2, unmatched2 = search_excel_for_ids(excel_file2, list(unmatched1), "MCT REPORT FOR TSD 04082026", prefix="MCTA", column_index=9)

# Step 3: Save results into 3 sheets
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df1.to_excel(writer, sheet_name="Matched CAPEX_ED", index=False)
    df2.to_excel(writer, sheet_name="Matched MCT REPORT", index=False)
    pd.DataFrame({"Still_Unmatched_IDs": sorted(unmatched2)}).to_excel(writer, sheet_name="Still Unmatched", index=False)

print("\n=== SUMMARY ===")
print(f"Matched in CAPEX_ED: {sorted(matched1)}")
print(f"Matched in MCT REPORT: {sorted(matched2)}")
print(f"Still Unmatched: {sorted(unmatched2)}")
print(f'Excel file has been created on "{output_file}"')