import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Pro Data Splitter", layout="wide")

st.title("📊 MAYA AI: Smart Shift Automator")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    # Data load karna
    df = pd.read_excel(uploaded_file)
    
    # Columns ke naam se faltu spaces hatana
    df.columns = [str(c).strip() for c in df.columns]
    
    # 1. Date Column ko handle karna (Flexible Search)
    date_col = None
    for col in df.columns:
        if 'date' in col.lower():
            date_col = col
            break
            
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        
        # 2. Shift Columns ko identify karna
        # Serial No aur Date ko nikaal kar baaki sab Shifts hain
        ignore_cols = ['Serial No', 'S.No', 'S.no', 'Sl No', 'Sno', date_col]
        shift_columns = [c for c in df.columns if c not in ignore_cols]
        
        st.sidebar.header("Calculation Settings")
        
        if not shift_columns:
            st.error("Shifts ke columns nahi mile. Kripya Excel format check karein.")
        else:
            # Dropdown mein shifts ke asli naam dikhenge (e.g., DS, FD, GD)
            base_shift = st.sidebar.selectbox("Pehli (Base) Shift chunein", shift_columns)
            
            # Date Range Filter
            min_date = df[date_col].min()
            max_date = df[date_col].max()
            selected_dates = st.sidebar.date_input("Kab se kab tak ka data?", [min_date, max_date])

            if len(selected_dates) == 2:
                mask = (df[date_col] >= pd.Timestamp(selected_dates[0])) & (df[date_col] <= pd.Timestamp(selected_dates[1]))
                filtered_df = df.loc[mask].copy()

                def process_logic(data, b_col, other_cols):
                    s1_rows, s2_rows = [], []
                    for _, row in data.iterrows():
                        # Base Number logic
                        b_val = str(row[b_col]).split('.')[0].zfill(2) if pd.notnull(row[b_col]) else "00"
                        # Handle case where val might be single digit or empty
                        if len(b_val) < 2: b_val = b_val.zfill(2)
                        b_d, b_i = b_val[-2], b_val[-1]
                        
                        # Data entries
                        r1 = {date_col: row[date_col], "Base_Shift": b_col, "Base_Value": b_val}
                        r2 = {date_col: row[date_col], "Base_Shift": b_col, "Base_Value": b_val}
                        
                        for col in other_cols:
                            o_val = str(row[col]).split('.')[0].zfill(2) if pd.notnull(row[col]) else "00"
                            if len(o_val) < 2: o_val = o_val.zfill(2)
                            o_d, o_i = o_val[-2], o_val[-1]
                            
                            # Sheet 1: Dahai Base + (Other Dahai & Other Ikai)
                            r1[f"{col}_Comb1"] = f"{b_d}{o_d}"
                            r1[f"{col}_Comb2"] = f"{b_d}{o_i}"
                            
                            # Sheet 2: Ikai Base + (Other Ikai & Other Dahai)
                            r2[f"{col}_Comb1"] = f"{b_i}{o_i}"
                            r2[f"{col}_Comb2"] = f"{b_i}{o_d}"
                            
                        s1_rows.append(r1)
                        s2_rows.append(r2)
                    return pd.DataFrame(s1_rows), pd.DataFrame(s2_rows)

                other_shifts = [c for c in shift_columns if c != base_shift]
                df_s1, df_s2 = process_logic(filtered_df, base_shift, other_shifts)

                # Results Display
                st.subheader(f"✅ Processed: Base Shift '{base_shift}' ke hisaab se")
                t1, t2 = st.tabs(["Sheet 1 (Dahai Base)", "Sheet 2 (Ikai Base)"])
                with t1: st.dataframe(df_s1)
                with t2: st.dataframe(df_s2)

                # Excel Download
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_s1.to_excel(writer, sheet_name='Dahai_Base', index=False)
                    df_s2.to_excel(writer, sheet_name='Ikai_Base', index=False)
                
                st.download_button(label="📥 Download Result Excel", 
                                   data=output.getvalue(), 
                                   file_name=f"MAYA_Analysis_{base_shift}.xlsx")
    else:
        st.error("Excel mein 'Date' naam ka column nahi mila. Kripya check karein.")
else:
    st.info("Kripya Excel file upload karein. Pehle do columns 'S.No' aur 'Date' hone chahiye, uske baad Shifts.")
    
