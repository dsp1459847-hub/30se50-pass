import streamlit as st
import pandas as pd
from io import BytesIO

st.title("MAYA AI: Final Error-Free Excel")

uploaded_file = st.file_uploader("Apni file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Date column ko text format mein convert karna taaki MATCH function fail na ho
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    df[date_col] = df[date_col].dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_any_dtype(df[date_col]) else df[date_col].astype(str)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # Styles
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        text_fmt = workbook.add_format({'num_format': '@'}) # Text format important hai

        # --- DASHBOARD ---
        dash = workbook.add_worksheet('Dashboard')
        dash.write('A1', 'BASE SHIFT NAME:', header_fmt)
        dash.write('B1', 'DS', text_fmt) # Type manually: DS, FD etc.
        
        dash.write('A2', 'BASE DATE:', header_fmt)
        # Yahan Date ko Text ki tarah likhein taaki MATCH error na de
        dash.write('B2', str(df[date_col].iloc[0]), text_fmt) 

        # Base Number Finder (MATCH function ko update kiya hai)
        dash.write('A4', 'Base Number:', header_fmt)
        # Formula explanation: Original_Data ki B column mein B2 date dhoondho
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(B2&"", Original_Data!$B$2:$B$6000&"", 0), MATCH(B1&"", Original_Data!$C$1:$O$1, 0)), "00")')
        
        dash.write('A5', 'Dahai (Tens):', header_fmt)
        dash.write_formula('B5', '=LEFT(B4, 1)')
        dash.write('A6', 'Ikai (Units):', header_fmt)
        dash.write_formula('B6', '=RIGHT(B4, 1)')

        # --- LOGIC SHEETS ---
        # Aapke paas ye shifts hain: DS, FD, GD, GL, DB, SG, ZA
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        
        for name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(name)
            ws.write(0, 0, 'Date', header_fmt)
            
            for i, shift in enumerate(shifts):
                ws.write(0, 1 + (i*2), f'{shift}_C1', header_fmt)
                ws.write(0, 2 + (i*2), f'{shift}_C2', header_fmt)
                
                for row in range(1, 6001):
                    # Date copy logic
                    ws.write_formula(row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
                    
                    col_letter = chr(67 + i) # C, D, E...
                    base_val = '$B$5' if name == 'Dahai_Logic' else '$B$6'
                    
                    # Combination Logic
                    ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_val} & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                    ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_val} & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')

    st.success("File Ready!")
    st.download_button("Download MAYA_Final.xlsx", output.getvalue(), "MAYA_Final.xlsx")
    
