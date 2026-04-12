import streamlit as st
import pandas as pd
from io import BytesIO

st.title("MAYA AI: 100% Accurate Logic Sheets")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    # Date format fix for Excel matching
    df[date_col] = df[date_col].dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_any_dtype(df[date_col]) else df[date_col].astype(str)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        text_fmt = workbook.add_format({'num_format': '@'})

        # --- DASHBOARD (Controls) ---
        dash = workbook.add_worksheet('Dashboard')
        dash.write('A1', 'SELECT BASE SHIFT:', header_fmt)
        dash.write('B1', 'DS', text_fmt)
        dash.write('A2', 'SELECT BASE DATE:', header_fmt)
        dash.write('B2', str(df[date_col].iloc[0]), text_fmt)

        # Base digit calculations
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$O$1, 0)), "00")')
        dash.write('A5', 'Dahai (T):')
        dash.write_formula('B5', '=LEFT(B4, 1)')
        dash.write('A6', 'Ikai (U):')
        dash.write_formula('B6', '=RIGHT(B4, 1)')

        # --- LOGIC SHEETS ---
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        
        for name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(name)
            ws.write(0, 0, 'Date', header_fmt)
            
            for i, shift in enumerate(shifts):
                ws.write(0, 1 + (i*2), f'{shift}_Comb1', header_fmt)
                ws.write(0, 2 + (i*2), f'{shift}_Comb2', header_fmt)
                
                for row in range(1, 6001):
                    ws.write_formula(row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
                    col_letter = chr(67 + i) # Column C, D, E...
                    
                    if name == 'Dahai_Logic':
                        # RULE: Base Dahai + Other Dahai | Base Dahai + Other Ikai
                        ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$5 & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                        ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$5 & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                    else:
                        # RULE: Base Ikai + Other Ikai | Base Ikai + Other Dahai
                        ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$6 & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                        ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$6 & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')

    st.success("Aapke logic ke hisaab se file taiyaar hai!")
    st.download_button("Download Accurate MAYA File", output.getvalue(), "MAYA_Accurate.xlsx")
    
