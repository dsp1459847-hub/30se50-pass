import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import io

# --- 1. v57 मास्टर इंजन (Full Day Isolation) ---
def get_v57_fixed_logic(df, s_name, target_date):
    try:
        # डेटा क्लीनिंग
        df_clean = df.iloc[:, [1, df.columns.get_loc(s_name)]].copy()
        df_clean.columns = ['DATE', 'NUM']
        df_clean['DATE'] = pd.to_datetime(df_clean['DATE'], dayfirst=True, errors='coerce').dt.date
        df_clean['NUM'] = pd.to_numeric(df_clean['NUM'], errors='coerce')
        df_clean = df_clean.dropna(subset=['DATE', 'NUM'])

        # 🛑 असली फिक्स: आज की तारीख का कोई भी डेटा इस्तेमाल नहीं होगा।
        # सिर्फ कल (target_date - 1) तक का ही इतिहास देखा जाएगा।
        # इससे सुबह का रिजल्ट डालने पर शाम की प्रेडिक्शन नहीं बदलेगी।
        hist_limit = target_date - datetime.timedelta(days=1)
        hist_data = df_clean[df_clean['DATE'] <= hist_limit]
        
        if len(hist_data) < 10:
            return "इतिहास कम है", "N/A", []

        all_vals = hist_data['NUM'].astype(int).tolist()
        last_val = all_vals[-1] # कल का आखिरी नंबर

        # --- लॉजिक: वार + मिरर + जंप ---
        t_day_name = target_date.strftime('%A')
        day_hist = hist_data[hist_data['DATE'].apply(lambda x: x.strftime('%A')) == t_day_name]['NUM'].astype(int).tolist()
        top_3_day = [n for n, c in Counter(day_hist[-100:]).most_common(3)]

        mirror = (last_val + 50) % 100
        neighbors = [(last_val + 1) % 100, (last_val - 1) % 100]

        # मास्टर पुल
        combined_pool = list(set(top_3_day + [mirror] + neighbors))
        final_picks = combined_pool[:10]
        
        top_picks_str = " | ".join([f"{n:02d}" for n in sorted(final_picks)])
        analysis = f"कल का अंतिम: {last_val:02d} | वार: {t_day_name}"
        
        return analysis, top_picks_str, final_picks

    except Exception as e:
        return f"Error: {str(e)}", "N/A", []

# --- 2. UI सेटअप ---
st.set_page_config(page_title="MAYA AI v57 Full Lock", layout="wide")
st.title("🛡️ MAYA AI: v57 Zero-Leakage Engine")
st.info("💡 **FIXED:** अब आज का कोई भी रिजल्ट डालने पर आज की किसी भी शिफ्ट की प्रेडिक्शन नहीं बदलेगी।")

uploaded_file = st.file_uploader("📂 अपनी Excel फ़ाइल अपलोड करें", type=['xlsx'])

if uploaded_file:
    try:
        df = pd.read_excel(io.BytesIO(uploaded_file.getvalue()), engine='openpyxl')
        df_match = df.copy()
        df_match['DATE_COL'] = pd.to_datetime(df_match.iloc[:, 1], dayfirst=True, errors='coerce').dt.date
        
        # शिफ्ट्स की लिस्ट
        shift_cols = [c for c in ['DS', 'FD', 'GD', 'GL', 'DB', 'SG'] if c in df.columns]
        target_date = st.date_input("📅 प्रेडिक्शन की तारीख चुनें:", datetime.date.today())

        if st.button("🚀 100% फिक्स्ड स्कैन"):
            selected_row = df_match[df_match['DATE_COL'] == target_date]
            results = []

            for s in shift_cols:
                # यहाँ 'Day Isolation' लागू है
                info, picks_str, raw_list = get_v57_fixed_logic(df_match, s, target_date)
                
                actual = "--"
                res_emoji = "⚪"
                if not selected_row.empty:
                    val = selected_row[s].values[0]
                    if pd.notnull(val) and str(val).replace('.','',1).isdigit():
                        v_int = int(float(val))
                        actual = f"{v_int:02d}"
                        res_emoji = "✅ PASS" if v_int in raw_list else "❌"

                results.append({
                    "Shift": s, "Result": actual, "परिणाम": res_emoji, 
                    "📊 विश्लेषण": info, "🌟 टॉप 10": picks_str
                })

            st.table(pd.DataFrame(results))
            st.warning("🔒 **Full Day Lock Active:** आज का डेटा सिर्फ 'Result' कॉलम में दिखेगा, प्रेडिक्शन में उसका कोई हाथ नहीं होगा।")
            st.balloons()

    except Exception as e:
        st.error(f"Error: {e}")
                
