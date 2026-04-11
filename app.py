import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title="MAYA AI - Dashboard", layout="wide")

st.title("📊 MAYA AI: Interactive Data Controller")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    # 1. Excel Read karna
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    first_sheet_name = list(all_sheets.keys())[0]
    df = all_sheets[first_sheet_name].copy()
    
    # Column cleaning
    df.columns = [str(c).strip() for c in df.columns]
    
    # Date column check
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # --- UI Dashboard Section (Excel jaisa control) ---
        st.markdown("### 🛠️ Control Panel")
        col1, col2 = st.columns(2)
        
        # Shift Columns identify karna
        ignore = ['s. number', 's.no', 'serial', 'sno', 'unnamed', date_col.lower()]
        shift_columns = [c for c in df.columns if not any(k in c.lower() for k in ignore) and not str(c).startswith('ï')]

        with col1:
            # Base Shift badalne ka option seedha screen par
            base_shift = st.selectbox("👉 Pehli (Base) Shift Badlein:", shift_columns)
        
        with col2:
            # Date badalne ka option
            min_d, max_d = df[date_col].min().date(), df[date_col].max().date()
            selected_dates = st.date_input("📅 Data ki Date badlein:", [min_d, max_d])

        if len(selected_dates) == 2:
            mask = (df[date_col].dt.date >= selected_dates[0]) & (df[date_col].dt.date <= selected_dates[1])
            filtered_df = df.loc[mask].copy()

            # Logic for splitting digits
            def process_logic(data, b_col, other_cols):
                s1_rows, s2_rows = [], []
                for _, row in data.iterrows():
                    if pd.isna(row[b_col]): continue
                    
                    b_val = str(row[b_col]).split('.')[0].zfill(2)
                    b_d, b_i = b_val[-2], b_val[-1]
                    
                    r1 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base": b_val}
                    r2 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base": b_val}
                    
                    for col in other_cols:
                        if pd.isna(row[col]) or str(row[col]).strip() == "":
                            r1[f"{col}_C1"], r1[f"{col}_C2"] = "", ""
                            r2[f"{col}_C1"], r2[f"{col}_C2"] = "", ""
                        else:
                            o_val = str(row[col]).split('.')[0].zfill(2)
                            o_d, o_i = o_val[-2], o_val[-1]
                            r1[f"{col}_C1"], r1[f"{col}_C2"] = f"{b_d}{o_d}", f"{b_d}{o_i}"
                            r2[f"{col}_C1"], r2[f"{col}_C2"] = f"{b_i}{o_i}", f"{b_i}{o_d}"
                    s1_rows.append(r1); s2_rows.append(r2)
                return pd.DataFrame(s1_rows), pd.DataFrame(s2_rows)

            other_shifts = [c for c in shift_columns if c != base_shift]
            df_s1, df_s2 = process_logic(filtered_df, base_shift, other_shifts)

            # --- Live Preview ---
            st.divider()
            st.subheader(f"Results for: {base_shift}")
            t1, t2 = st.tabs(["Sheet 1 (Dahai)", "Sheet 2 (Ikai)"])
            with t1: st.dataframe(df_s1, use_container_width=True)
            with t2: st.dataframe(df_s2, use_container_width=True)

            # Excel download with new sheets
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, sheet_df in all_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                df_s1.to_excel(writer, sheet_name=f'DAHAI_{base_shift}', index=False)
                df_s2.to_excel(writer, sheet_name=f'IKAI_{base_shift}', index=False)
            
            st.download_button("📥 Nayi Excel File Download Karein", output.getvalue(), f"MAYA_{base_shift}.xlsx")
    else:
        st.error("Excel mein 'Date' column nahi mil raha.")
else:
    st.info("Kripya Excel file upload karein.")
                            
