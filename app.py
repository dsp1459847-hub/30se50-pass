import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Pro Data Splitter", layout="wide")
st.title("📊 MAYA AI: Smart Shift Automator")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    
    # 1. Date Column search
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # 2. Identify Shift Columns (S. NUMBER ko ignore karte hue)
        ignore_keywords = ['s. number', 's.no', 'serial', 'sl no', 'sno', 's number', date_col.lower()]
        shift_columns = [c for c in df.columns if not any(k in c.lower() for k in ignore_keywords)]
        
        # --- UI Options (Ab Main Screen Par) ---
        col1, col2 = st.columns(2)
        with col1:
            base_shift = st.selectbox("🎯 Pehli (Base) Shift chunein", shift_columns)
        with col2:
            min_d, max_d = df[date_col].min(), df[date_col].max()
            selected_dates = st.date_input("📅 Date Range", [min_d, max_d])

        if len(selected_dates) == 2:
            mask = (df[date_col] >= pd.Timestamp(selected_dates[0])) & (df[date_col] <= pd.Timestamp(selected_dates[1]))
            filtered_df = df.loc[mask].copy()

            def process_logic(data, b_col, other_cols):
                s1_rows, s2_rows = [], []
                for _, row in data.iterrows():
                    b_val = str(row[b_col]).split('.')[0].zfill(2) if pd.notnull(row[b_col]) else "00"
                    b_d, b_i = b_val[-2], b_val[-1]
                    
                    r1 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    r2 = {"Date": row[date_col].strftime('%d-%m-%Y'), "Base_Val": b_val}
                    
                    for col in other_cols:
                        o_val = str(row[col]).split('.')[0].zfill(2) if pd.notnull(row[col]) else "00"
                        o_d, o_i = o_val[-2], o_val[-1]
                        # Logic: Sheet 1 (Dahai Base), Sheet 2 (Ikai Base)
                        r1[f"{col}_C1"], r1[f"{col}_C2"] = f"{b_d}{o_d}", f"{b_d}{o_i}"
                        r2[f"{col}_C1"], r2[f"{col}_C2"] = f"{b_i}{o_i}", f"{b_i}{o_d}"
                    s1_rows.append(r1); s2_rows.append(r2)
                return pd.DataFrame(s1_rows), pd.DataFrame(s2_rows)

            other_shifts = [c for c in shift_columns if c != base_shift]
            df_s1, df_s2 = process_logic(filtered_df, base_shift, other_shifts)

            st.success(f"Processed: '{base_shift}' ko base maan kar")
            t1, t2 = st.tabs(["📑 Sheet 1 (Dahai)", "📑 Sheet 2 (Ikai)"])
            with t1: st.dataframe(df_s1)
            with t2: st.dataframe(df_s2)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_s1.to_excel(writer, sheet_name='Dahai_Base', index=False)
                df_s2.to_excel(writer, sheet_name='Ikai_Base', index=False)
            st.download_button("📥 Download Result Excel", output.getvalue(), f"MAYA_{base_shift}.xlsx")
    else:
        st.error("'Date' column nahi mila. Kripya check karein.")
else:
    st.info("Kripya Excel file upload karein.")
    
