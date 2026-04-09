import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. हाई-एक्यूरेसी इंजन (Safe & Static Fix) ---
def get_safe_high_accuracy_picks(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग: खाली या गलत डेटा को हटाना
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        
        # 🛑 NaN (खाली सेल) को यहीं हटा दिया ताकि एरर न आए
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        # 🛑 Static Vision: केवल चुनी गई तारीख से पहले का डेटा देखना
        hist_data = df_clean[df_clean['DATE'] < target_date]
        
        if len(hist_data) < 10:
            return "इतिहास कम है", "N/A", []

        # A. साल दर साल (Yearly Connection)
        t_day, t_month = target_date.day, target_date.month
        yearly = hist_data[(hist_data['DATE'].apply(lambda x: x.day == t_day and x.month == t_month))]['NUM'].astype(int).tolist()

        # B. वार की ताकत (Day-wise Power)
        t_day_name = target_date.strftime('%A')
        day_hist = hist_data[hist_data['DATE'].apply(lambda x: x.strftime('%A')) == t_day_name]['NUM'].astype(int).tolist()
        top_3_day = [n for n, c in Counter(day_hist[-100:]).most_common(3)]

        # C. कल की चाल (Last Valid Result)
        last_val = int(hist_data.iloc[-1]['NUM'])
        mirror = (last_val + 50) % 100
        neighbors = [(last_val + 1) % 100, (last_val - 1) % 100]

        # मास्टर पूल (8 नंबर)
        combined_pool = list(set(yearly + top_3_day + [mirror] + neighbors))
        final_picks_raw = combined_pool[:8]
        top_picks_str = " | ".join([f"{n:02d}" for n in final_picks_raw])
        
        analysis = f"वार: {t_day_name} | पिछला: {last_val:02d} | मिरर: {mirror:02d}"
        
        return analysis, top_picks_str, final_picks_raw

    except Exception as e:
        return f"विश्लेषण में त्रुटि", "N/A", []

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI v56 Fixed", layout="wide")
st.title("🛡️ MAYA AI: v56 Deep-Clean (No More Errors)")
st.info("💡 **Error Fixed:** अब खाली सेल होने पर भी 'NaN' एरर नहीं आएगा और प्रेडिक्शन फिक्स रहेगी।")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        # एक्सेल लोड करना (Error Handling के साथ)
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        
        df_match = df.copy()
        # तारीख कॉलम की पहचान (Index 1)
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG', 'ZA'] if c in df.columns]
        target_date = st.date_input("📅 विश्लेषण की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 सुरक्षित स्कैन शुरू करें"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results = []

            for s in shift_cols:
                info, picks_str, raw_picks = get_safe_high_accuracy_picks(df_match, s, target_date)
                
                actual_val = "--"
                res_emoji = "⚪"
                
                if not selected_row.empty:
                    # आज का असली रिजल्ट उठाना (NaN चेक के साथ)
                    val = selected_row[s].values[0]
                    if pd.notnull(val) and str(val).replace('.','',1).isdigit():
                        val_int = int(float(val))
                        actual_val = f"{val_int:02d}"
                        res_emoji = "✅ PASS" if val_int in raw_picks else "❌"

                results.append({
                    "Shift": s,
                    "📍 Result": actual_val,
                    "परिणाम": res_emoji,
                    "📊 विश्लेषण": info,
                    "🌟 टॉप सिलेक्शन": picks_str
                })

            st.table(pd.DataFrame(results))
            st.warning("🔒 **Security Mode Active:** खाली सेल्स और भविष्य के डेटा को हटा दिया गया है। प्रेडिक्शन अब नहीं बदलेगी।")
            st.balloons()

    except Exception as e:
        st.error(f"Excel पढ़ने में समस्या: {e}")
                
