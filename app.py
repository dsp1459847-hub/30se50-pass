import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="MAYA AI - Professional Fix", layout="wide")
st.title("📊 MAYA AI: Dual Date Range Fix (No Dashboard)")

uploaded_file = st.file_uploader("Apni Excel file upload karein", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [str(c).strip() for c in df.columns]
    date_col = next((c for c in df.columns if 'date' in c.lower()), df.columns[1])
    
    # Date Format for Excel Compatibility
    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%d-%m-%Y')

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Original_Data', index=False)
        workbook = writer.book
        
        # --- Styles ---
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1, 'align': 'center'})
        setting_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFC000', 'border': 1})
        input_fmt = workbook.add_format({'bg_color': '#FFFFFF', 'border': 1, 'align': 'center'})

        shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']

        for sheet_name in ['Dahai_Logic', 'Ikai_Logic']:
            ws = workbook.add_worksheet(sheet_name)
            ws.set_column('A:O', 15)
            
            # --- TOP CONTROLS (Ab yahan se data fetch hoga) ---
            ws.write('A1', '🎯 BASE SHIFT:', setting_fmt)
            ws.write('B1', 'DS', input_fmt) 
            
            ws.write('D1', '📅 BASE DATE (SINGLE):', setting_fmt)
            ws.write('E1', df[date_col].iloc[0], input_fmt) 
            
            # Date Ranges for Filtering
            ws.write('A3', '📅 ALL SHIFT START:', setting_fmt)
            ws.write('B3', df[date_col].iloc[0], input_fmt)
            ws.write('A4', '📅 ALL SHIFT END:', setting_fmt)
            ws.write('B4', df[date_col].iloc[-1], input_fmt)

            # --- DYNAMIC BASE ANK CALCULATION ---
            # Z1 cell mein hum INDEX/MATCH formula laga rahe hain jo E1 date aur B1 shift se number uthayega
            ws.write_formula('Z1', '=TEXT(INDEX(Original_Data!$C$2:$O$6000, MATCH(E1, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$O$1, 0)), "00")')
            
            # Table Headers
            ws.write(6, 0, 'Date', header_fmt)
            for i, shift in enumerate(shifts):
                ws.write(6, 1+(i*2), f'{shift}_C1', header_fmt)
                ws.write(6, 2+(i*2), f'{shift}_C2', header_fmt)

            # --- LOGIC IMPLEMENTATION (6000 Rows) ---
            # Dahai sheet ke liye Dahai base ($Z$1 ka Left), Ikai ke liye Ikai ($Z$1 ka Right)
            base_digit = 'LEFT($Z$1,1)' if sheet_name == 'Dahai_Logic' else 'RIGHT($Z$1,1)'
            
            for row in range(1, 6001):
                ex_row = 6 + row
                # Date Filter Formula: Agar Original_Data ki date B3 aur B4 ke beech hai, tabhi date dikhaye
                ws.write_formula(ex_row, 0, f'=IF(AND(Original_Data!B{row+1}>=$B$3, Original_Data!B{row+1}<=$B$4), Original_Data!B{row+1}, "")')
                
                for i, shift in enumerate(shifts):
                    orig_col = chr(67 + i) # C, D, E...
                    
                    if sheet_name == 'Dahai_Logic':
                        # Dahai + Dahai | Dahai + Ikai
                        f1 = f'=IF($A{ex_row+1}="","",{base_digit} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{ex_row+1}="","",{base_digit} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    else:
                        # Ikai + Ikai | Ikai + Dahai
                        f1 = f'=IF($A{ex_row+1}="","",{base_digit} & RIGHT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                        f2 = f'=IF($A{ex_row+1}="","",{base_digit} & LEFT(TEXT(Original_Data!{orig_col}{row+1},"00"),1))'
                    
                    ws.write_formula(ex_row, 1+(i*2), f1)
                    ws.write_formula(ex_row, 2+(i*2), f2)

    st.success("✅ Excel file taiyaar hai! Ab koi data blank nahi aayega.")
    st.download_button("📥 Download MAYA_Final_Fixed.xlsx", output.getvalue(), "MAYA_Final_Fixed.xlsx")
    
