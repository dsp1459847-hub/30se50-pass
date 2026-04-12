import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Professional", layout="wide")
st.title("📊 MAYA AI: Multi-Range & Digit Sheet Logic")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    
    # Date Format Fix
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df[date_col] = df[date_col].dt.strftime('%d-%m-%Y')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # --- Styles ---
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1, 'align': 'center'})
        setting_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFC000', 'border': 1})
        input_fmt = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'center'})

        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']

        # --- NEW SHEET: ANK_SHEET (Digits Wise) ---
        ws_ank = workbook.add_worksheet('Ank_Sheet')
        ws_ank.write('A1', '🎯 BASE SHIFT:', setting_fmt)
        ws_ank.write('B1', 'DS', input_fmt)
        ws_ank.write('A2', '📅 SELECT BASE DATE:', setting_fmt)
        ws_ank.write('B2', df[date_col].iloc[0], input_fmt)
        
        ws_ank.write(4, 0, 'Date', header_fmt)
        for i, shift in enumerate(shifts):
            ws_ank.write(4, 1 + (i*2), f'{shift}_Dahai', header_fmt)
            ws_ank.write(4, 2 + (i*2), f'{shift}_Ikai', header_fmt)
        
        for row in range(1, 6001):
            ws_ank.write_formula(row+4, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
            for i, shift in enumerate(shifts):
                col_let = chr(67 + i)
                ws_ank.write_formula(row+4, 1+(i*2), f'=IF(Original_Data!{col_let}{row+1}="","",LEFT(TEXT(Original_Data!{col_let}{row+1},"00"),1))')
                ws_ank.write_formula(row+4, 2+(i*2), f'=IF(Original_Data!{col_let}{row+1}=""," ",RIGHT(TEXT(Original_Data!{col_let}{row+1},"00"),1))')

        # --- LOGIC SHEETS (Dahai & Ikai with Range) ---
        for sheet_name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(sheet_name)
            
            # Controls on Top
            ws.write('A1', '🎯 BASE SHIFT:', setting_fmt); ws.write('B1', 'DS', input_fmt)
            ws.write('D1', '📅 BASE DATE:', setting_fmt); ws.write('E1', df[date_col].iloc[0], input_fmt)
            
            ws.write('A3', '📅 BASE RANGE START:', setting_fmt); ws.write('B3', df[date_col].iloc[0], input_fmt)
            ws.write('A4', '📅 BASE RANGE END:', setting_fmt); ws.write('B4', df[date_col].iloc[-1], input_fmt)
            
            ws.write('D3', '📅 ALL SHIFT START:', setting_fmt); ws.write('E3', df[date_col].iloc[0], input_fmt)
            ws.write('D4', '📅 ALL SHIFT END:', setting_fmt); ws.write('E4', df[date_col].iloc[-1], input_fmt)

            # Calculation Anchor
            ws.write_formula('Z1', f'=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(E1, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$O$1, 0)), "00")')
            
            # Headers
            ws.write(6, 0, 'Date', header_fmt)
            for i, shift in enumerate(shifts):
                ws.write(6, 1+(i*2), f'{shift}_C1', header_fmt)
                ws.write(6, 2+(i*2), f'{shift}_C2', header_fmt)

            # Logic
            base_digit = 'LEFT($Z$1,1)' if sheet_name == 'Dahai_Logic' else 'RIGHT($Z$1,1)'
            for row in range(1, 6001):
                ex_row = 6 + row
                # Range Filter on Date
                ws.write_formula(ex_row, 0, f'=IF(AND(Original_Data!B{row+1}>=$D$3, Original_Data!B{row+1}<=$E$3), Original_Data!B{row+1}, "")')
                
                for i, shift in enumerate(shifts):
                    orig_col = chr(67 + i)
                    if sheet_name == 'Dahai_Logic':
                        f1 = f'=IF($A{ex_row+1}="","",{base_digit} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{ex_row+1}="","",{base_digit} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    else:
                        f1 = f'=IF($A{ex_row+1}="","",{base_digit} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{ex_row+1}="","",{base_digit} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    ws.write_formula(ex_row, 1+(i*2), f1)
                    ws.write_formula(ex_row, 2+(i*2), f2)

    st.success("✅ Sabhi sheets (Ank, Dahai, Ikai) HD layout mein taiyaar hain!")
    st.download_button("📥 Download MAYA_Pro_Logic.xlsx", output.getvalue(), "MAYA_Pro_Logic.xlsx")
    
