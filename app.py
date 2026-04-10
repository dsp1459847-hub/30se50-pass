import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Pro Data Splitter", layout="wide")

st.title("📊 MAYA AI: Ikai-Dahai Shift Automator")

# 1. File Upload Section
uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    # Data load karna
    df = pd.read_excel(uploaded_file)
    
    # Date column ko datetime mein convert karna
    df['Date'] = pd.to_datetime(df['Date'])
    
    st.sidebar.header("Settings")
    
    # 2. Date Filter Option
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    selected_dates = st.sidebar.date_input("Date Range Chunein", [min_date, max_date])
    
    # 3. Shift Selection Option
    # C1 se aage ki shifts ko identify karna
    all_columns = df.columns.tolist()
    shift_columns = all_columns[2:] # Serial No aur Date ko chhod kar
    base_shift = st.sidebar.selectbox("Apni Base (Pehli) Shift chunein", shift_columns)
    
    if len(selected_dates) == 2:
        # Data Filter karna
        mask = (df['Date'] >= pd.Timestamp(selected_dates[0])) & (df['Date'] <= pd.Timestamp(selected_dates[1]))
        filtered_df = df.loc[mask].copy()
        
        st.write(f"Processing data from {selected_dates[0]} to {selected_dates[1]}")

        # Processing Logic Function
        def process_logic(data, base_col, other_cols):
            sheet1_data = [] # Dahai Base
            sheet2_data = [] # Ikai Base
            
            for _, row in data.iterrows():
                # Base number split
                base_val = str(row[base_col]).zfill(2)
                b_d, b_i = base_val[0], base_val[1]
                
                row_s1 = {"Date": row['Date'], "Base_Val": base_val}
                row_s2 = {"Date": row['Date'], "Base_Val": base_val}
                
                for col in other_cols:
                    other_val = str(row[col]).zfill(2)
                    o_d, o_i = other_val[0], other_val[1]
                    
                    # Sheet 1: Base Dahai + Others (Dahai & Ikai)
                    row_s1[f"{col}_Comb1"] = f"{b_d}{o_d}"
                    row_s1[f"{col}_Comb2"] = f"{b_d}{o_i}"
                    
                    # Sheet 2: Base Ikai + Others (Ikai & Dahai)
                    row_s2[f"{col}_Comb1"] = f"{b_i}{o_i}"
                    row_s2[f"{col}_Comb2"] = f"{b_i}{o_d}"
                
                sheet1_data.append(row_s1)
                sheet1_data.append(row_s2)
            
            return pd.DataFrame(sheet1_data), pd.DataFrame(sheet2_data)

        other_shifts = [c for c in shift_columns if c != base_shift]
        df_s1, df_s2 = process_logic(filtered_df, base_shift, other_shifts)

        # 4. Results Display & Download
        st.subheader("Generated Sheets Preview")
        tab1, tab2 = st.tabs(["Sheet 1 (Dahai Base)", "Sheet 2 (Ikai Base)"])
        
        with tab1:
            st.dataframe(df_s1)
        with tab2:
            st.dataframe(df_s2)

        # Excel Download Button
        def to_excel(df1, df2):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df1.to_excel(writer, sheet_name='Dahai_Base', index=False)
                df2.to_excel(writer, sheet_name='Ikai_Base', index=False)
            return output.getvalue()

        excel_data = to_excel(df_s1, df_s2)
        st.download_button(label="📥 Download Processed Excel", 
                           data=excel_data, 
                           file_name="MAYA_AI_Processed.xlsx")

else:
    st.info("Kripya Excel file upload karein jisme 'Serial No', 'Date' aur Shifts ke columns hon.")
    
