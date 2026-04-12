import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Formula HD", layout="wide")
st.title("📊 MAYA AI: Excel Formula Generator (HD Layout)")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    # 1. Sabhi sheets read karna
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    first_sheet = list(all_sheets.keys())[0]
    df = all_sheets[first_sheet].copy()
    df.columns = [str(c).strip() for c in df.columns]
    
    # Date column pehchanna
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    
    # 2. Excel Writer with Formulas
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Original Data save karein
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # --- HD Design Styles ---
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1, 'align': 'center'})
        data_fmt = workbook.add_format({'border': 1, 'align': 'center'})
        dash_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFC000', 'border': 2, 'align': 'center'})
        
        # --- 1. DASHBOARD SHEET ---
        dash = workbook.add_worksheet('Dashboard')
        dash.set_column('A:B', 25)
        dash.write('A1', '⚙️ SELECT BASE SHIFT:', dash_fmt)
        dash.write('B1', 'DS')  # Default Value
        dash.write('A2', '📅 SELECT BASE DATE:', dash_fmt)
        dash.write('B2', str(df[date_col].iloc[0])) # Default First Date
        
        # Base Calculation Formulas (Hidden or Summary)
        dash.write('A4', '✅ Base Number:', header_fmt)
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$I$1, 0)), "00")')
        dash.write('A5', '🔢 Dahai (Base T):', header_fmt)
        dash.write_formula('B5', '=LEFT(B4, 1)')
        dash.write('A6', '🔢 Ikai (Base U):', header_fmt)
        dash.write_formula('B6', '=RIGHT(B4, 1)')

        # --- 2. LOGIC SHEETS (Dahai & Ikai) ---
        shifts = [c for c in df.columns if c not in ['S.No', 'S.no', 'S. NUMBER', 'Serial No', date_col]]
        
        for sheet_name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(sheet_name)
            ws.set_column('A:O', 15)
            ws.write(0, 0, 'Date', header_fmt)
            
            for i, shift in enumerate(shifts):
                col_pos = 1 + (i * 2)
                ws.write(0, col_pos, f'{shift}_Comb1', header_fmt)
                ws.write(0, col_pos + 1, f'{shift}_Comb2', header_fmt)
                
                # Formula implementation for 6000 rows
                for row in range(1, 6001):
                    # Date Link
                    ws.write_formula(row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
                    
                    # Original Data Column (C=67, D=68...)
                    col_letter = chr(67 + i)
                    base_cell = '$B$5' if sheet_name == 'Dahai_Logic' else '$B$6'
                    
                    if sheet_name == 'Dahai_Logic':
                        # Dahai Logic: Base-D + Other-D | Base-D + Other-I
                        ws.write_formula(row, col_pos, f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                        ws.write_formula(row, col_pos + 1, f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                    else:
                        # Ikai Logic: Base-I + Other-I | Base-I + Other-D
                        ws.write_formula(row, col_pos, f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                        ws.write_formula(row, col_pos + 1, f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')

    st.success("✅ HD Formula Sheet Taiyaar Hai!")
    st.download_button("📥 Download Formula-Linked HD Excel", output.getvalue(), "MAYA_HD_Automated.xlsx")
else:
    st.info("Kripya apni Excel file upload karein jisme S.No, Date aur Shifts hon.")
    
