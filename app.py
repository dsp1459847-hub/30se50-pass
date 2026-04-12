import streamlit as st
import pandas as pd
from io import BytesIO

st.title("MAYA AI: Master Dashboard Control")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    # Date ko text banana taaki Excel MATCH function fail na ho
    df[date_col] = df[date_col].dt.strftime('%d-%m-%Y') if pd.api.types.is_datetime64_any_dtype(df[date_col]) else df[date_col].astype(str)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 1. Original Data Sheet (Safe side ke liye)
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        
        workbook = writer.book
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1, 'align': 'center'})
        text_fmt = workbook.add_format({'num_format': '@', 'align': 'center'})

        # --- MASTER DASHBOARD ---
        dash = workbook.add_worksheet('Dashboard')
        
        # Dashboard Control UI (Top Left)
        dash.write('A1', 'SELECT BASE SHIFT:', header_fmt)
        dash.write('B1', 'DS', text_fmt)
        dash.write('A2', 'SELECT BASE DATE:', header_fmt)
        dash.write('B2', str(df[date_col].iloc[0]), text_fmt)
        
        # Base Number Finder (Sirf hidden calculation ke liye)
        dash.write('A4', 'Base Digit Logic:', header_fmt)
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$I$1, 0)), "00")')
        dash.write_formula('C4', '=LEFT(B4,1)') # Base Dahai
        dash.write_formula('D4', '=RIGHT(B4,1)') # Base Ikai

        # Table Headings (Data yahan se shuru hoga)
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        dash.write('A6', 'DATE', header_fmt)
        
        for i, shift in enumerate(shifts):
            col_start = 1 + (i * 4)
            # Dahai Combinations
            dash.merge_range(5, col_start, 5, col_start + 1, f'{shift} (DAHAI BASE)', header_fmt)
            dash.write(6, col_start, 'D+D', header_fmt)
            dash.write(6, col_start + 1, 'D+I', header_fmt)
            # Ikai Combinations
            dash.merge_range(5, col_start + 2, 5, col_start + 3, f'{shift} (IKAI BASE)', header_fmt)
            dash.write(6, col_start + 2, 'I+I', header_fmt)
            dash.write(6, col_start + 3, 'I+D', header_fmt)

        # 5305 Rows ka Live Data
        for row in range(1, 5500):
            # Row index in Excel (Starts from 7 because of headers)
            excel_row = 6 + row
            # Date Link
            dash.write_formula(excel_row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
            
            for i, shift in enumerate(shifts):
                col_start = 1 + (i * 4)
                orig_col = chr(67 + i) # Column C, D, E...
                
                # Sheet 1 Logic (Dahai Base)
                dash.write_formula(excel_row, col_start, f'=IF(Original_Data!{orig_col}{row+1}="","",$C$4 & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))')
                dash.write_formula(excel_row, col_start + 1, f'=IF(Original_Data!{orig_col}{row+1}="","",$C$4 & RIGHT(TEXT(Original_Data!{row+1}{orig_col},"00"),1))')
                
                # Sheet 2 Logic (Ikai Base)
                dash.write_formula(excel_row, col_start + 2, f'=IF(Original_Data!{orig_col}{row+1}="","",$D$4 & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))')
                dash.write_formula(excel_row, col_start + 3, f'=IF(Original_Data!{orig_col}{row+1}="","",$D$4 & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))')

    st.success("Ab Dashboard par hi saara data dikhega!")
    st.download_button("Download Master Dashboard Excel", output.getvalue(), "MAYA_Master_Dashboard.xlsx")
    
