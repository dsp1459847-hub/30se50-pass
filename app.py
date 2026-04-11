import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title="MAYA AI - Advanced Dashboard", layout="wide")
st.title("📊 MAYA AI: Dual Date & All-Shift Logic")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    first_sheet_name = list(all_sheets.keys())[0]
    df = all_sheets[first_sheet_name].copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # Shift identification (S.No etc. ko ignore karke)
        ignore = ['s. number', 's.no', 'serial', 'sno', 'unnamed', date_col.lower()]
        shift_columns = [c for c in df.columns if not any(k in c.lower() for k in ignore) and not str(c).startswith('ï')]

        # --- Control Panel (Alag-Alag Dates) ---
        st.subheader("🛠️ Control Panel")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            base_shift = st.selectbox("🎯 Base Shift Chunein:", shift_columns)
        
        with col2:
            st.write("📅 **Base Shift ki Date:**")
            b_min, b_max = df[date_col].min().date(), df[date_col].max().date()
            base_date_range = st.date_input("Base Date Selection", [b_min, b_max], key="base_date")

        with col3:
            st.write("📅 **Baaki Shifts ki Date:**")
            o_min, o_max = df[date_col].min().date(), df[date_col].max().date()
            other_date_range = st.date_input("Other Date Selection", [o_min, o_max], key="other_date")

        if len(base_date_range) == 2 and len(other_date_range) == 2:
            # Base Shift ka data filter
            base_mask = (df[date_col].dt.date >= base_date_range[0]) & (df[date_col].dt.date <= base_date_range[1])
            df_base = df.loc[base_mask].copy()

            # Other Shifts ka data filter
            other_mask = (df[date_col].dt.date >= other_date_range[0]) & (df[date_col].dt.date <= other_date_range[1])
            df_others = df.loc[other_mask].copy()

            def process_pro_logic(df_b, df_o, b_col, all_cols):
                s1_rows, s2_rows = [], []
                # Dono dataframes ka size alag ho sakta hai, isliye minimum size tak loop chalega
                min_len = min(len(df_b), len(df_o))
                
                for i in range(min_len):
                    row_b = df_b.iloc[i]
                    row_o = df_o.iloc[i]
                    
                    if pd.isna(row_b[b_col]): continue
                    
                    b_val = str(row_b[b_col]).split('.')[0].zfill(2)
                    b_d, b_i = b_val[-2], b_val[-1]
                    
                    # Entry Header
                    r1 = {"Base_Date": row_b[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    r2 = {"Base_Date": row_b[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    
                    for col in all_cols: # Yahan Base Shift bhi included hai
                        if pd.isna(row_o[col]):
                            r1[f"{col}_C1"], r1[f"{col}_C2"] = "", ""
                            r2[f"{col}_C1"], r2[f"{col}_C2"] = "", ""
                        else:
                            o_val = str(row_o[col]).split('.')[0].zfill(2)
                            o_d, o_i = o_val[-2], o_val[-1]
                            # Logic 1: Dahai Base + (Other Dahai & Other Ikai)
                            r1[f"{col}_C1"], r1[f"{col}_C2"] = f"{b_d}{o_d}", f"{b_d}{o_i}"
                            # Logic 2: Ikai Base + (Other Ikai & Other Dahai)
                            r2[f"{col}_C1"], r2[f"{col}_C2"] = f"{b_i}{o_i}", f"{b_i}{o_d}"
                    
                    s1_rows.append(r1); s2_rows.append(r2)
                return pd.DataFrame(s1_rows), pd.DataFrame(s2_rows)

            # Ab 'other_shifts' mein Base Shift ko bhi rakha gaya hai
            df_s1, df_s2 = process_pro_logic(df_base, df_others, base_shift, shift_columns)

            st.divider()
            st.success(f"Result Taiyaar Hai! Base: {base_shift}")
            t1, t2 = st.tabs(["📑 Sheet 1 (Dahai Base)", "📑 Sheet 2 (Ikai Base)"])
            with t1: st.dataframe(df_s1)
            with t2: st.dataframe(df_s2)

            # Excel save logic
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                for sheet_name, sheet_df in all_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                df_s1.to_excel(writer, sheet_name=f'DAHAI_{base_shift}', index=False)
                df_s2.to_excel(writer, sheet_name=f'IKAI_{base_shift}', index=False)
            
            st.download_button("📥 Final Excel Download Karein", output.getvalue(), f"MAYA_DualDate_{base_shift}.xlsx")
    else:
        st.error("Date column nahi mila!")
else:
    st.info("Kripya Excel file upload karein.")
    
