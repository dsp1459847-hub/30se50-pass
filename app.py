import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title="MAYA AI - Multi-Sheet Pro", layout="wide")
st.title("📊 MAYA AI: New Sheet Generator")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    # Original file ko read karna taaki uski sheets save rahein
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    
    # Maan lete hain data pehli sheet mein hai
    first_sheet_name = list(all_sheets.keys())[0]
    df = all_sheets[first_sheet_name].copy()
    
    # Cleaning columns
    df.columns = [str(c).strip() for c in df.columns]
    
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        today = pd.Timestamp(date.today())
        # Filter: Sirf aaj tak ka data
        df = df[df[date_col] <= today] 
        
        ignore = ['s. number', 's.no', 'serial', 'sno', 'unnamed', date_col.lower()]
        shift_columns = [c for c in df.columns if not any(k in c.lower() for k in ignore) and not str(c).startswith('ï')]

        st.subheader("⚙️ Settings")
        c1, c2 = st.columns(2)
        with c1:
            base_shift = st.selectbox("🎯 Base Shift Chunein (e.g. DS/FD/GD)", shift_columns)
        with c2:
            min_d, max_d = df[date_col].min(), df[date_col].max()
            selected_dates = st.date_input("📅 Date Range", [min_d, max_d])

        if len(selected_dates) == 2:
            mask = (df[date_col] >= pd.Timestamp(selected_dates[0])) & (df[date_col] <= pd.Timestamp(selected_dates[1]))
            filtered_df = df.loc[mask].copy()

            def process_logic(data, b_col, other_cols):
                s1_rows, s2_rows = [], []
                for _, row in data.iterrows():
                    if pd.isna(row[b_col]): continue
                    
                    b_val = str(row[b_col]).split('.')[0].zfill(2)
                    b_d, b_i = b_val[-2], b_val[-1]
                    
                    r1 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    r2 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    
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

            st.success(f"Nayi Sheets taiyaar hain! Base: {base_shift}")
            
            # --- Excel Download Logic (Purani + Nayi Sheets) ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # 1. Purani saari sheets wapas likhna
                for sheet_name, sheet_df in all_sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 2. Nayi sheets add karna
                df_s1.to_excel(writer, sheet_name=f'DAHAI_{base_shift}', index=False)
                df_s2.to_excel(writer, sheet_name=f'IKAI_{base_shift}', index=False)
            
            st.download_button(
                label="📥 Download Updated Excel File", 
                data=output.getvalue(), 
                file_name=f"MAYA_Updated_{date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.info("💡 Note: Is file mein aapka 'Original Data' pehli sheet mein hai, aur naya data last ki 2 sheets mein.")
    else:
        st.error("Date column nahi mila!")
else:
    st.info("Kripya apni Excel file upload karein.")
    
