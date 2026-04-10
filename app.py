import pandas as pd

# Data Load karna
df = pd.read_excel("aapki_file.xlsx")

# Digit Split karne ka function
def split_digits(val):
    val = str(val).zfill(2) # 5 ko 05 banata hai
    return val[0], val[1] # (Dahai, Ikai)

# Maan lijiye 'Shift 1' base hai
base_shift = 'Shift 1'
other_shifts = [col for col in df.columns if col not in ['S.No', 'Date', base_shift]]

# Processing Logic
sheet_1_results = []
sheet_2_results = []

for index, row in df.iterrows():
    b_d, b_i = split_digits(row[base_shift]) # Base Dahai, Base Ikai
    
    for s in other_shifts:
        o_d, o_i = split_digits(row[s]) # Other Dahai, Other Ikai
        
        # Sheet 1: Base Dahai + Others
        sheet_1_results.append(f"{b_d}{o_d}")
        sheet_1_results.append(f"{b_d}{o_i}")
        
        # Sheet 2: Base Ikai + Others
        sheet_2_results.append(f"{b_i}{o_d}")
        sheet_2_results.append(f"{b_i}{o_i}")
        
