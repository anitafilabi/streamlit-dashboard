
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import jdatetime
import io

st.set_page_config(page_title="داشبورد محاسبه پورسانت", layout="wide")

st.markdown("""
    <style>
        @import url('https://cdn.fontcdn.ir/Font/Persian/Vazirmatn/Vazirmatn.css');
        html, body, .stApp, .block-container {
            background-color: #f9fafb !important;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
            overflow-y: auto !important;
            height: auto !important;
        }
        .main, .block-container, .stApp {
            text-align: center !important;
            align-items: center !important;
            justify-content: center !important;
        }
        .stMetric {
            background: #f1f5f9;
            border-radius: 10px;
            padding: 1rem 0.5rem;
            margin: 0.5rem 0;
            color: #1565c0;
            font-weight: bold;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
            box-shadow: 0 1px 4px #e0e7ef;
        }
        .stDataFrame, .stTable {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 4px #e0e7ef;
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
        }
        .stExpander {
            background: #e3eafc !important;
            border-radius: 8px !important;
            box-shadow: 0 1px 4px #e0e7ef;
            margin: 0.5rem 0;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
        }
        .stButton > button {
            background: linear-gradient(90deg, #1976d2 0%, #90caf9 100%);
            color: white;
            border-radius: 8px;
            font-weight: bold;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
            border: none;
            padding: 0.5rem 1.2rem;
        }
        .stSelectbox, .stNumberInput, .stFileUploader {
            margin-left: auto !important;
            margin-right: auto !important;
            text-align: center !important;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
        }
        .css-1v0mbdj, .css-1d391kg, .css-1cpxqw2 {
            text-align: center !important;
        }
        .stDownloadButton button[data-testid="baseButton-download_btn_week"],
        .stDownloadButton button[data-testid="baseButton-download_btn_month"] {
            background: linear-gradient(90deg, #43a047 0%, #66bb6a 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            box-shadow: 0 1px 4px #e0e7ef !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 داشبورد محاسبه پورسانت")

SALES_COEFFICIENTS_NUMERIC = {
    'لید_هات_اول_هفته': 1.3,
    'لید_کولد_اول_هفته': 3.0,
    'لید_گران_اول_هفته': 3.0,
    'لید_هات_آخر_هفته_تک_شب': 0.8,
    'لید_کولد_آخر_هفته_تک_شب': 1.0,
    'لید_گران_آخر_هفته_تک_شب': 0.5,
    'لید_هات_آخر_هفته_کامل': 1.0,
    'لید_کولد_آخر_هفته_کامل': 3.0,
    'لید_گران_آخر_هفته_کامل': 2.0,
    'مشاوره_هات_فروش': 0.5,
    'مشاوره_کولد_فروش': 1.0,
    'مشاوره_گران_فروش': 1.0,
    'تور_هات_اول_هفته': 0.5,
    'تور_کولد_اول_هفته': 0.0,
    'تور_گران_اول_هفته': 1.0,
    'تور_هات_آخر_هفته': 0.3,
    'تور_کولد_آخر_هفته': 0.0,
    'تور_گران_آخر_هفته': 2.0,
    'کنیبال_هات_آخر_هفته_نان_گارانت': 2.0,
    'کنیبال_کولد_آخر_هفته_نان_گارانت': 0.0,
    'کنیبال_گران_آخر_هفته_نان_گارانت': 2.0,
    'کنیبال_هات_اول_هفته_نان_گارانت': 4.0,
    'کنیبال_کولد_اول_هفته_نان_گارانت': 0.0,
    'کنیبال_گران_اول_هفته_نان_گارانت': 4.0,
    'کنیبال_هات_آخر_هفته_گارانت_کامل': 1.2,
    'کنیبال_کولد_آخر_هفته_گارانت_کامل': 0.0,
    'کنیبال_گران_آخر_هفته_گارانت_کامل': 1.5,
    'کنیبال_هات_آخر_هفته_گارانت_تک_شب': 1.0,
    'کنیبال_کولد_آخر_هفته_گارانت_تک_شب': 0.0,
    'کنیبال_گران_آخر_هفته_گارانت_تک_شب': 1.0,
    'کنیبال_هات_اول_هفته_گارانت': 1.4,
    'کنیبال_کولد_اول_هفته_گارانت': 0.0,
    'کنیبال_گران_اول_هفته_گارانت': 3.0
}

QC_WEIGHT = 0.3
OTHER_WEIGHT = 0.7

# تعریف پله‌های جدید با حداقل فرم
bonus_steps = [
    {"tfrn_min": 220, "kpi": 80_000_000, "form_min": 30},
    {"tfrn_min": 200, "kpi": 65_000_000, "form_min": 30},
    {"tfrn_min": 190, "kpi": 55_000_000, "form_min": 50},
    {"tfrn_min": 170, "kpi": 45_000_000, "form_min": 50},
    {"tfrn_min": 150, "kpi": 40_000_000, "form_min": 60},
    {"tfrn_min": 140, "kpi": 35_000_000, "form_min": 70},
    {"tfrn_min": 130, "kpi": 30_000_000, "form_min": 80},
    {"tfrn_min": 120,  "kpi": 25_000_000, "form_min": 80},
    {"tfrn_min": 110,  "kpi": 20_000_000, "form_min": 80},
]

def normalize_percent(value):
    try:
        value = str(value).replace('%', '').replace('None', '0')
        value = float(value)
    except:
        return 0
    if 0 <= value <= 1.5:
        value = value * 100
    if value >= 100:
        return 99
    return value

def calculate_tfrn(row):
    tfrn = 0
    for column, coefficient in SALES_COEFFICIENTS_NUMERIC.items():
        if column in row:
            tfrn += row[column] * coefficient
    return tfrn

def get_bonus_step(tfrn, form_completion):
    for step in bonus_steps:
        if tfrn >= step["tfrn_min"] and form_completion >= step["form_min"]:
            return step["kpi"]
    return 0

def calculate_bonus(tfrn, qc_score, form_completion, cr, login_violations, ignore_qc=False):
    qc_normalized = normalize_percent(qc_score)
    form_completion_normalized = normalize_percent(form_completion)
    cr_normalized = normalize_percent(cr)

    # شرط‌های اولیه برای ورود به مرحله محاسبه پورسانت
    if not ignore_qc:
        if qc_normalized < 85:
            return 0, "QC پایین"
    if cr_normalized < 20:
        return 0, "CR پایین"
    if login_violations > 3:
        return 0, "تعداد دیر/زود لاگین بیش از حد مجاز"

    # پیدا کردن پله مناسب
    base_bonus = get_bonus_step(tfrn, form_completion_normalized)
    if base_bonus == 0:
        if form_completion_normalized < min([step["form_min"] for step in bonus_steps]):
            return 0, "فرم ناقص"
        else:
            return 0, "TFRN پایین"

    # --- تغییر منطق محاسبه پورسانت ---
    # وزن فروش 60%
    max_tfrn = 221
    sales_score = min(tfrn / max_tfrn, 1.0)  # مقدار نرمالایز شده بین 0 و 1
    sales_factor = sales_score * 0.6  # سهم 60 درصدی فروش
    
    # وزن سایر معیارها (QC، فرم، CR و لاگین) 40%
    qc_score_norm = qc_normalized / 100  # تبدیل درصد به عدد بین 0 و 1
    form_score_norm = form_completion_normalized / 100  # تبدیل درصد به عدد بین 0 و 1
    cr_score_norm = cr_normalized / 100  # تبدیل درصد به عدد بین 0 و 1
    
    # محاسبه امتیاز لاگین (هرچه تخلفات کمتر باشد، امتیاز بیشتر)
    login_score_norm = max(0, 1 - (login_violations / 4))
    
    # اختصاص وزن‌های جدید به هر معیار از سهم 40 درصدی
    if ignore_qc:  # اگر QC نادیده گرفته شود
        form_weight = 0.16  # 16% برای فرم
        cr_weight = 0.16    # 16% برای CR
        login_weight = 0.08 # 8% برای لاگین
        
        other_factor = (form_score_norm * form_weight) + \
                     (cr_score_norm * cr_weight) + \
                     (login_score_norm * login_weight)
    else:  # اگر QC در محاسبات لحاظ شود
        qc_weight = 0.14    # 14% برای QC
        form_weight = 0.10  # 10% برای فرم
        cr_weight = 0.10    # 10% برای CR
        login_weight = 0.06 # 6% برای لاگین
        
        other_factor = (qc_score_norm * qc_weight) + \
                     (form_score_norm * form_weight) + \
                     (cr_score_norm * cr_weight) + \
                     (login_score_norm * login_weight)
    
    # محاسبه پورسانت نهایی با وزن‌های جدید
    final_factor = sales_factor + other_factor
    final_bonus = int(base_bonus * final_factor)
    
    return final_bonus, "واجد شرایط"

# --- تابع ساخت badge رنگی برای وضعیت ---
def status_badge(val):
    color = "#43a047" if val == "واجد شرایط" else ("#e53935" if val in ["QC پایین", "فرم ناقص", "CR پایین", "تعداد دیر/زود لاگین بیش از حد مجاز"] else "#fbc02d")
    return f'<span style="background-color:{color};color:white;padding:2px 8px;border-radius:8px;font-size:13px;box-shadow:0 1px 4px #bbb;">{val}</span>'

months = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]

with st.sidebar:
    st.header("📝 ورود اطلاعات")
    uploaded_file = st.file_uploader("فایل اکسل را آپلود کنید", type=['xlsx'])

    # اضافه کردن دکمه تایید
    confirm_upload = st.button("تایید و اضافه کردن فایل اکسل")

    # متغیرهای پیش‌فرض
    df = pd.DataFrame()
    bo_total = 0

    if uploaded_file is not None:
        # انتخاب ماه و هفته توسط کاربر (قبل از تایید)
        selected_month_name = st.selectbox("ماه اکسل را انتخاب کنید:", months)
        selected_month_num = months.index(selected_month_name) + 1
        selected_week = st.number_input("شماره هفته شمسی را وارد کنید:", min_value=1, max_value=53, value=1)

        if confirm_upload:
            # ذخیره فایل اکسل آپلود شده
            os.makedirs("uploads", exist_ok=True)
            with open(f"uploads/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getbuffer())

            # خواندن داده اصلی
            df = pd.read_excel(uploaded_file)
            df['ماه'] = selected_month_num
            df['نام ماه'] = selected_month_name
            df['هفته'] = selected_week

            # خواندن BO_total از شیت summary
            try:
                bo_total = pd.read_excel(uploaded_file, sheet_name='summary').iloc[0, 0]
                bo_total = float(bo_total)
            except Exception as e:
                bo_total = 0
            # پیام موفقیت بعد از آپلود
            st.success("فایل اکسل با موفقیت اضافه شد!.", icon="✅")
        else:
            st.info("پس از انتخاب فایل و وارد کردن ماه و هفته، دکمه تایید را بزنید تا داده‌ها اضافه شوند.")
    else:
        st.info("لطفاً یک فایل اکسل آپلود کنید و سپس دکمه تایید را بزنید.")

if not df.empty:
    for col in ['QC', 'تکمیل فرم', 'CR']:
        df[col] = df[col].apply(normalize_percent)

    df['دیر/زود لاگین'] = pd.to_numeric(df['دیر/زود لاگین'], errors='coerce').fillna(0).astype(int)

    if any(col in df.columns for col in SALES_COEFFICIENTS_NUMERIC.keys()):
        df['TFRN'] = df.apply(calculate_tfrn, axis=1)

    # بررسی وجود QC معتبر
    qc_missing = (df['QC'].isnull() | (df['QC'] == 0)).all()
    if qc_missing:
        st.warning("🔴 مبلغ پورسانت فعلی بدون نمره QC محاسبه شده و نهایی نیست. لطفاً در پایان ماه نمره QC را وارد کنید.")

    results = [
        calculate_bonus(row['TFRN'], row['QC'], row['تکمیل فرم'], row['CR'], row['دیر/زود لاگین'], ignore_qc=qc_missing)
        for _, row in df.iterrows()
    ]
    df['پورسانت'] = [r[0] for r in results]
    df['وضعیت'] = [r[1] for r in results]

    # ذخیره داده‌های هر هفته در فایل CSV
    save_path = "all_weeks_data.csv"
    if os.path.exists(save_path):
        old = pd.read_csv(save_path)
        # جلوگیری از تکرار داده‌های یک هفته
        old = old[~((old['هفته'] == selected_week) & (old['ماه'] == selected_month_num))]
        df_all = pd.concat([old, df], ignore_index=True)
    else:
        df_all = df.copy()
    df_all.to_csv(save_path, index=False)
else:
    save_path = "all_weeks_data.csv"
    if os.path.exists(save_path):
        df_all = pd.read_csv(save_path)
    else:
        df_all = pd.DataFrame()

# --- نمایش مجموع کل پورسانت و BO_total برای این هفته و کل ماه (همیشه نمایش داده شود) ---
if not df_all.empty:
    # آخرین ماه و هفته ثبت شده را پیدا کن
    last_month = df_all['ماه'].max()
    last_week = df_all[df_all['ماه'] == last_month]['هفته'].max()
    month_mask = (df_all['ماه'] == last_month)
    week_mask = (df_all['ماه'] == last_month) & (df_all['هفته'] == last_week)
    total_month_bonus = df_all[month_mask]['پورسانت'].sum()
    total_bonus = df_all[week_mask]['پورسانت'].sum()
    month_name = df_all[df_all['ماه'] == last_month]['نام ماه'].iloc[0]
    bo_total = 0
    if 'BO_total' in df_all.columns:
        bo_total = df_all[week_mask]['BO_total'].iloc[0]
else:
    total_month_bonus = 0
    total_bonus = 0
    month_name = ""
    bo_total = 0

col_exp1, col_exp2 = st.columns(2)
with col_exp1:
    with st.expander(f"💰 مجموع کل پورسانت پرداختی این هفته: {total_bonus:,.0f} ریال (کلیک کن برای جزئیات)"):
        st.write(f"مجموع کل فروش هفته (BO_total): {bo_total:,.0f} ریال")
        # فقط متریک‌های مهم را نمایش بده
        if not df_all.empty and total_bonus > 0:
            display_df = df_all[week_mask][['نام', 'TFRN', 'QC', 'تکمیل فرم', 'CR', 'دیر/زود لاگین', 'پورسانت', 'وضعیت', 'هفته', 'ماه', 'نام ماه']].copy()
            filter_name = st.text_input("جستجو بر اساس نام:", "", key="search_week_always")
            filter_status = st.selectbox("فیلتر بر اساس وضعیت:", ["همه"] + display_df['وضعیت'].unique().tolist(), key="status_week_always")
            filtered_df = display_df.copy()
            if filter_name:
                filtered_df = filtered_df[filtered_df['نام'].str.contains(filter_name, case=False, na=False)]
            if filter_status != "همه":
                filtered_df = filtered_df[filtered_df['وضعیت'] == filter_status]
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("میانگین TFRN", f"{filtered_df['TFRN'].mean():.1f}")
            with col2:
                st.metric("میانگین QC", f"{filtered_df['QC'].mean():.2f}%")
            with col3:
                st.metric("میانگین تکمیل فرم", f"{filtered_df['تکمیل فرم'].mean():.2f}%")
            with col4:
                st.metric("میانگین CR", f"{filtered_df['CR'].mean():.2f}%")
            with col5:
                st.metric("میانگین دیر/زود لاگین", f"{filtered_df['دیر/زود لاگین'].mean():.1f}")
        # جدول و نمودار حذف شد
with col_exp2:
    with st.expander(f"💰 مجموع کل پورسانت پرداختی ماه {month_name}: {total_month_bonus:,.0f} ریال (کلیک کن برای جزئیات)"):
        if not df_all.empty and total_month_bonus > 0:
            st.dataframe(
                df_all[month_mask][['نام', 'پورسانت']]
                .groupby(['نام'])
                .sum()
                .reset_index()
                .style.format({'پورسانت': '{:,.0f}'})
            )
        else:
            st.info("داده‌ای برای این ماه وجود ندارد.")

st.metric("مجموع پورسانت", f"{total_bonus:,.0f} ریال")

# نمایش گزارش ماهانه فقط با ماه‌های فارسی و جدول کارشناسان
if not df_all.empty:
    st.subheader("📅 گزارش ماهانه")
    months_in_data = [m for m in months[1:] if m in df_all['نام ماه'].unique()]
    if months_in_data:
        month_selected = st.selectbox("ماه مورد نظر را انتخاب کنید:", months_in_data)
        df_month = df_all[df_all['نام ماه'] == month_selected]
        weeks_in_month = sorted(df_month['هفته'].unique())
        week_selected = st.selectbox("هفته مورد نظر را انتخاب کنید:", weeks_in_month)
        df_week = df_month[df_month['هفته'] == week_selected]
        # نمایش اطلاعات کامل همان هفته انتخاب شده
        display_df = df_week[['نام', 'TFRN', 'QC', 'تکمیل فرم', 'CR', 'دیر/زود لاگین', 'پورسانت', 'وضعیت', 'هفته', 'ماه', 'نام ماه']].copy()
        # --- فیلتر و جستجو ---
        filter_name = st.text_input("جستجو بر اساس نام:", "", key="search_month")
        filter_status = st.selectbox("فیلتر بر اساس وضعیت:", ["همه"] + display_df['وضعیت'].unique().tolist(), key="status_month")
        filtered_df = display_df.copy()
        if filter_name:
            filtered_df = filtered_df[filtered_df['نام'].str.contains(filter_name, case=False, na=False)]
        if filter_status != "همه":
            filtered_df = filtered_df[filtered_df['وضعیت'] == filter_status]
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("میانگین TFRN", f"{filtered_df['TFRN'].mean():.1f}")
        with col2:
            st.metric("میانگین QC", f"{filtered_df['QC'].mean():.2f}%")
        with col3:
            st.metric("میانگین تکمیل فرم", f"{filtered_df['تکمیل فرم'].mean():.2f}%")
        with col4:
            st.metric("میانگین CR", f"{filtered_df['CR'].mean():.2f}%")
        with col5:
            st.metric("میانگین دیر/زود لاگین", f"{filtered_df['دیر/زود لاگین'].mean():.1f}")
        st.subheader("📊 نمودار TFRN")
        fig = px.bar(filtered_df, x='نام', y='TFRN', color='وضعیت', title='TFRN به تفکیک افراد')
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("📋 جدول اطلاعات کامل هفته")
        styled_df = filtered_df.style.format({
            'پورسانت': '{:,.0f}',
            'CR': '{:.2f}%','QC': '{:.2f}%','تکمیل فرم': '{:.2f}%','TFRN': '{:.1f}','دیر/زود لاگین': '{:.0f}'
        }).applymap(lambda v: '', subset=['وضعیت'])
        styled_df = styled_df.format({'وضعیت': status_badge}, escape="html")
        st.write(
            f'<div style="display: flex; justify-content: center;">{styled_df.to_html(escape=False)}</div>',
            unsafe_allow_html=True
        )
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Sheet1')
        output.seek(0)
        processed_data = output.getvalue()

        st.download_button(
            label="دانلود جدول به Excel",
            data=processed_data,
            file_name='week_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            type='primary',
            key='download_btn_month'
        )
    else:
        st.info("داده‌ای برای ماه‌های اردیبهشت به بعد وجود ندارد.")

# آپلود QC پایان ماه و آپدیت داده‌ها
st.subheader("آپلود نمره QC پایان ماه")
qc_file = st.file_uploader("فایل QC را آپلود کنید (ستون نام و QC)", type=['xlsx'], key="qc")
if qc_file is not None and not df_all.empty:
    df_qc = pd.read_excel(qc_file)
    # انتخاب ماه برای آپدیت QC
    months_in_data = [m for m in months[1:] if m in df_all['نام ماه'].unique()]
    month_selected_for_qc = st.selectbox("ماه مورد نظر برای آپدیت QC:", months_in_data, key="qc_month")
    for idx, row in df_qc.iterrows():
        mask = (df_all['نام'] == row['نام']) & (df_all['نام ماه'] == month_selected_for_qc)
        df_all.loc[mask, 'QC'] = row['QC']
    df_all.to_csv(save_path, index=False)
    st.success("نمره QC با موفقیت به داده‌های ماه اضافه شد. لطفاً صفحه را رفرش کنید.")

    with st.expander("🔍 راهنمای محاسبه پورسانت"):
        st.write("""
        شرایط دریافت پورسانت:
        - QC باید بالای 85% باشد (وزن 30%)
        - درصد تکمیل فرم باید بالای حداقل تعیین شده در پله پورسانتی باشد
        - نرخ تبدیل (CR) باید بالای 20% باشد
        - TFRN، فرم و CR مجموعاً وزن 70% دارند
        - تعداد دفعات دیر/زود لاگین نباید بیشتر از 3 بار باشد
        """)

        kpi_df = pd.DataFrame([
            {'حداقل TFRN': step["tfrn_min"], 'حداقل درصد فرم': f"{step['form_min']}%", 'پورسانت پایه': f"{step['kpi']:,} ریال"}
            for step in bonus_steps
        ])
        st.table(kpi_df)

        st.subheader("📊 جدول ضرایب فروش")
        coefficients_df = pd.DataFrame([
            {'نوع فروش': k.replace('_', ' '), 'ضریب': f"{v:.1f}"}
            for k, v in SALES_COEFFICIENTS_NUMERIC.items()
        ])
        st.table(coefficients_df)

# --- بخش مدیریت و حذف دستی داده‌های وارد شده ---
if not df_all.empty:
    with st.expander("🗑️ مدیریت و حذف داده‌های وارد شده"):
        # نمایش لیست یکتا از ماه‌ها و هفته‌ها
        unique_months = df_all['نام ماه'].unique().tolist()
        selected_month = st.selectbox("ماه مورد نظر برای حذف داده:", unique_months, key="delete_month")

        # بررسی اینکه داده‌ای برای ماه انتخاب شده وجود دارد
        weeks_in_month = sorted(df_all[df_all['نام ماه'] == selected_month]['هفته'].unique()) if selected_month else []
        
        # بررسی مقدار weeks_in_month برای جلوگیری از خطای خالی بودن لیست
        if weeks_in_month:
            selected_week = st.selectbox("هفته مورد نظر برای حذف داده:", weeks_in_month, key="delete_week")

            # نمایش داده‌های انتخاب شده
            df_selected = df_all[(df_all['نام ماه'] == selected_month) & (df_all['هفته'] == selected_week)]
            st.dataframe(df_selected, use_container_width=True)

            if st.button("حذف این هفته از داشبورد", key="delete_btn"):
                df_all = df_all[~((df_all['نام ماه'] == selected_month) & (df_all['هفته'] == selected_week))]
                df_all.to_csv(save_path, index=False)
                st.success(f"داده‌های هفته {selected_week} از ماه {selected_month} حذف شد! برای مشاهده تغییرات صفحه را رفرش کنید.", icon="🗑️")
        else:
            st.warning("هیچ داده‌ای برای این ماه ثبت نشده است!")

# --- تنظیمات نمایش دکمه‌های دانلود ---
st.markdown("""
    <style>
        .stDownloadButton button[data-testid='baseButton-download_btn_week'],
        .stDownloadButton button[data-testid='baseButton-download_btn_month'] {
            background: linear-gradient(90deg, #43a047 0%, #66bb6a 100%) !important;
            color: white !important;
            border-radius: 8px !important;
            font-weight: bold !important;
            font-family: 'Vazirmatn', IRANSans, Tahoma, sans-serif !important;
            border: none !important;
            padding: 0.5rem 1.2rem !important;
            box-shadow: 0 1px 4px #e0e7ef !important;
        }
    </style>
""", unsafe_allow_html=True)
