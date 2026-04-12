import streamlit as st
import pandas as pd
from io import BytesIO

st.title("MAYA AI: Formula File Downloader")

# Yahan apni purani file upload karein
uploaded_file = st.file_uploader("Apni file 0DSP0.xlsx yahan upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Original Data
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # Dashboard with Formulas
        dash = workbook.add_worksheet('Dashboard')
        dash.write('A1', 'BASE SHIFT:'); dash.write('B1', 'DS')
        dash.write('A2', 'BASE DATE:'); dash.write('B2', str(df.iloc[0,1]))
        
        # Base Number Formula
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$I$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$I$1, 0)), "00")')
        dash.write_formula('B5', '=LEFT(B4, 1)') # Dahai
        dash.write_formula('B6', '=RIGHT(B4, 1)') # Ikai
        
        # Nayi Logic Sheet mein formula daalna
        logic_ws = workbook.add_worksheet('Logic_Result')
        logic_ws.write(0, 0, 'Formula Linked Date')
        logic_ws.write_formula(1, 1, '=$Dashboard!$B$5 & LEFT(TEXT(Original_Data!C2,"00"),1)')
        
    st.download_button("📥 Click Here to Download Your Formula File", output.getvalue(), "MAYA_FORMULA_FILE.xlsx")
        
