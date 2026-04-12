import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Dual Date HD", layout="wide")
st.title("📊 MAYA AI: Dual Date Range & Formula Logic")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    
    # Date ko standard format mein convert karna
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%d-%m-%Y')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # Styles
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1, 'align': 'center'})
        dash_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFC000', 'border': 2, 'align': 'center'})
        date_fmt = workbook.add_format({'num_format': 'dd-mm-yyyy', 'align': 'center', 'border': 1})

        # --- DASHBOARD SHEET (Range Settings) ---
        dash = workbook.add_worksheet('Dashboard')
        dash.set_column('A:D', 25)
        
        dash.write('A1', '⚙️ BASE SHIFT SETTINGS', dash_fmt)
        dash.write('A2', 'Select Base Shift Name:', header_fmt)
        dash.write('B2', 'DS') # B2: Shift Name
        
        dash.write('A3', 'Select Base Date (Single):', header_fmt)
        dash.write('B3', df[date_col].iloc[0]) # B3: Base Date
        
        dash.write('A5', '📅 DATE RANGE CONTROLLERS', dash_fmt)
        dash.write('A6', 'Base Data Start Date:', header_fmt)
        dash.write('B6', df[date_col].iloc[0]) # Start Date Range
        dash.write('A7', 'Base Data End Date:', header_fmt)
        dash.write('B7', df[date_col].iloc[-1]) # End Date Range

        # Hidden Logic for Base Digits
        dash.write('D1', 'LOGIC CALCULATION', header_fmt)
        dash.write_formula('D2', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(B3, Original_Data!$B$2:$B$6000, 0), MATCH(B2, Original_Data!$C$1:$O$1, 0)), "00")')
        dash.write('D3', 'Base Dahai:')
        dash.write_formula('E3', '=LEFT(D2, 1)')
        dash.write('D4', 'Base Ikai:')
        dash.write_formula('E4', '=RIGHT(D2, 1)')

        # --- LOGIC SHEETS ---
        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
        
        for name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(name)
            ws.set_column('A:O', 15)
            ws.write(0, 0, 'Date', header_fmt)
            
            base_digit_cell = 'Dashboard!$E$3' if name == 'Dahai_Logic' else 'Dashboard!$E$4'
            
            for i, shift in enumerate(shifts):
                col_idx = 1 + (i * 2)
                ws.write(0, col_idx, f'{shift}_Comb1', header_fmt)
                ws.write(0, col_idx + 1, f'{shift}_Comb2', header_fmt)
                
                for row in range(1, 6001):
                    # Filter Logic: Agar Date Range ke beech mein hai toh hi dikhaye
                    ws.write_formula(row, 0, f'=IF(AND(Original_Data!B{row+1}<>"", Original_Data!B{row+1}>=Dashboard!$B$6, Original_Data!B{row+1}<=Dashboard!$B$7), Original_Data!B{row+1}, "")')
                    
                    orig_col = chr(67 + i)
                    # Combination logic based on Date Filter
                    if name == 'Dahai_Logic':
                        # Dahai + Dahai | Dahai + Ikai
                        f1 = f'=IF($A{row+1}="","",{base_digit_cell} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{row+1}="","",{base_digit_cell} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    else:
                        # Ikai + Ikai | Ikai + Dahai
                        f1 = f'=IF($A{row+1}="","",{base_digit_cell} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{row+1}="","",{base_digit_cell} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    
                    ws.write_formula(row, col_idx, f1)
                    ws.write_formula(row, col_idx + 1, f2)

    st.success("✅ Dual Date Range HD File Taiyaar Hai!")
    st.download_button("📥 Download MAYA_DualRange_HD.xlsx", output.getvalue(), "MAYA_DualRange_HD.xlsx")
    
