import streamlit as st
import pandas as pd
from io import BytesIO

st.title("MAYA AI: Professional Formula File Generator")

# 1. File Upload
uploaded_file = st.file_uploader("Apni Original Excel file (0DSP0.xlsx) upload karein", type=["xlsx"])

if uploaded_file:
    # Data read karna
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    
    # Date column dhundhna
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    
    # Buffer taiyaar karna Excel ke liye
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Sheet 1: Original Data
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # Format styles
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFEB9C', 'border': 1})
        date_fmt = workbook.add_format({'num_format': 'dd-mm-yyyy'})

        # Sheet 2: Dashboard
        dash = workbook.add_worksheet('Dashboard')
        dash.write('A1', 'BASE SHIFT NAME:', header_fmt)
        dash.write('B1', 'DS')  # Default Value
        dash.write('A2', 'BASE DATE:', header_fmt)
        
        # Pehli date ko default likhna
        first_date = df[date_col].iloc[0]
        dash.write('B2', first_date, date_fmt)

        # Calculation Formulas
        dash.write('A4', 'Base Number Found:', header_fmt)
        # INDEX/MATCH Formula
        dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$I$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$I$1, 0)), "00")')
        
        dash.write('A5', 'Dahai (Tens):', header_fmt)
        dash.write_formula('B5', '=LEFT(B4, 1)')
        dash.write('A6', 'Ikai (Units):', header_fmt)
        dash.write_formula('B6', '=RIGHT(B4, 1)')

        # Sheet 3 & 4: Logic Sheets
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        
        for sheet_name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(sheet_name)
            ws.write(0, 0, 'Date', header_fmt)
            
            for i, shift in enumerate(shifts):
                ws.write(0, 1 + (i*2), f'{shift}_C1', header_fmt)
                ws.write(0, 2 + (i*2), f'{shift}_C2', header_fmt)
                
                # 6000 rows tak formula khinchna
                for row in range(1, 6001):
                    ws.write_formula(row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
                    col_letter = chr(67 + i) # C, D, E...
                    
                    base_cell = '$B$5' if sheet_name == 'Dahai_Logic' else '$B$6'
                    
                    # Logic: Dahai/Ikai Base + Current Row Digit
                    ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                    ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!{base_cell} & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')

    processed_data = output.getvalue()
    st.success("✅ Formula file taiyaar hai!")
    st.download_button(
        label="📥 Download MAYA_Formula_Pro.xlsx",
        data=processed_data,
        file_name="MAYA_Formula_Pro.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Kripya apni 0DSP0.xlsx file upload karein taaki main usmein formulas fit kar sakoon.")
    
