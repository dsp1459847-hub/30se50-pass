import pandas as pd

# 1. Aapki file ka naam yahan likhein
input_file = '0DSP0.xlsx' 
output_file = 'MAYA_AI_Automated_Formulas.xlsx'

# 2. Data load karein
try:
    df = pd.read_excel(input_file)
except:
    # Agar Excel nahi milti toh sample data banayega testing ke liye
    df = pd.DataFrame({'S.No': [1], 'Date': ['10-04-2026'], 'DS':[70], 'FD':[72], 'GD':[71], 'GL':[75], 'DB':[70], 'SG':[70], 'ZA':[70]})

# 3. Excel Writer setup (with XlsxWriter engine)
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
df.to_excel(writer, sheet_name='Original_Data', index=False)
workbook = writer.book

# Formatting (Headers ke liye)
header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})

# --- DASHBOARD SHEET ---
dash = workbook.add_worksheet('Dashboard')
dash.write('A1', 'BASE SHIFT NAME:', header_fmt)
dash.write('B1', 'DS') # Dropdown value yahan aayegi
dash.write('A2', 'BASE DATE:', header_fmt)
dash.write('B2', df['Date'].iloc[0]) # Pehli date default

# Base Number Logic Formulas
dash.write('A4', 'Base Number Found:', header_fmt)
dash.write_formula('B4', '=TEXT(INDEX(Original_Data!$C$2:$I$6000, MATCH(B2, Original_Data!$B$2:$B$6000, 0), MATCH(B1, Original_Data!$C$1:$I$1, 0)), "00")')
dash.write('A5', 'Dahai (Tens):', header_fmt)
dash.write_formula('B5', '=LEFT(B4, 1)')
dash.write('A6', 'Ikai (Units):', header_fmt)
dash.write_formula('B6', '=RIGHT(B4, 1)')

# --- LOGIC SHEETS FUNCTION ---
def add_logic_sheet(sheet_name, base_cell_ref):
    ws = workbook.add_worksheet(sheet_name)
    ws.write(0, 0, 'Date', header_fmt)
    
    shifts = ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA']
    
    for i, shift in enumerate(shifts):
        ws.write(0, 1 + (i*2), f'{shift}_C1', header_fmt)
        ws.write(0, 2 + (i*2), f'{shift}_C2', header_fmt)
        
        # 6000 Rows tak formulas apply karna
        for row in range(1, 6001):
            # Date Link
            ws.write_formula(row, 0, f'=IF(Original_Data!B{row+1}="","",Original_Data!B{row+1})')
            
            col_letter = chr(67 + i) # C, D, E... (Shifts Columns)
            
            if sheet_name == 'Dahai_Logic':
                # Dahai Logic (Base Dahai + Other Digits)
                ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$5 & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$5 & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
            else:
                # Ikai Logic (Base Ikai + Other Digits)
                ws.write_formula(row, 1 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$6 & RIGHT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')
                ws.write_formula(row, 2 + (i*2), f'=IF(Original_Data!{col_letter}{row+1}="","",$Dashboard!$B$6 & LEFT(TEXT(Original_Data!{col_letter}{row+1},"00"),1))')

# Dono sheets create karein
add_logic_sheet('Dahai_Logic', '$B$5')
add_logic_sheet('Ikai_Logic', '$B$6')

writer.close()
print(f"Success! '{output_file}' taiyaar hai.")
