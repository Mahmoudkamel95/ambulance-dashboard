import streamlit as st

# بيانات الدخول (تقدر تغيرها)
USERNAME = "drahmed"
PASSWORD = "12345"

# session لحفظ حالة الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# لو مش عامل login
if not st.session_state.logged_in:
    st.title("🔐 تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول ✅")
            st.rerun()
        else:
            st.error("بيانات غلط ❌")

    st.stop()  # يمنع باقي الكود يشتغل

# ---------------- بعد تسجيل الدخول ---------------- #
st.sidebar.success("✅ Logged in")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()



import pandas as pd

st.set_page_config(
    page_title="تقرير التمام اليومي",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🚑 تقرير التمام اليومي")


# ---------------- تحميل الداتا ---------------- #
url = "https://docs.google.com/spreadsheets/d/1Mmy2PYghA1nhG6DnTtNgy2RnBABByjaCPjU8vPa6Kgs/export?format=csv&gid=1682970187"
@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv(url)

df = load_data()
if st.sidebar.button("🔄 تحديث البيانات"):
    st.cache_data.clear()
    st.rerun()
# ---------------- تنظيف البيانات ---------------- #
df.columns = df.columns.str.strip()

# تحويل أعمدة لأرقام
cols_to_numeric = [
    "اجمالي سيارات المنطقه",
    "اجمالي سيارات التشغيل",
    "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل",
    "اجمالي السيارات بالتوكيل",
    "اجمالي السيارات المعطله"
]

for col in cols_to_numeric:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# تحويل التاريخ
df["التاريخ"] = pd.to_datetime(df["التاريخ"], dayfirst=True)

# ---------------- Sidebar ---------------- #
st.sidebar.image("Annotation 2026-03-11 213816.png")

# فلتر التاريخ
min_date = df["التاريخ"].min()
max_date = df["التاريخ"].max()

start_date, end_date = st.sidebar.date_input(
    "📅 اختر الفترة",
    [min_date, max_date]
)

# الأقاليم
regions_data = {
    "شمال": ["الفيوم", "المنيا", "بني سويف"],
    "جنوب": ["الأقصر", "قنا", "أسوان", "البحر الاحمر"],
    "وسط": ["أسيوط", "سوهاج", "الوادي الجديد"]
}

# فلتر الإقليم
region = st.sidebar.selectbox(
    "🌍 اختر الإقليم",
    ["الكل"] + list(regions_data.keys())
)

# فلتر المحافظة (ديناميك)
if region == "الكل":
    governorates = df["المحافظه"].dropna().unique()
else:
    governorates = regions_data[region]

governorate = st.sidebar.selectbox(
    "🏙️ اختر المحافظة",
    ["الكل"] + list(governorates)
)

# ---------------- تطبيق الفلترة ---------------- #
filtered_df = df.copy()

# فلتر التاريخ
filtered_df = filtered_df[
    (filtered_df["التاريخ"] >= pd.to_datetime(start_date)) &
    (filtered_df["التاريخ"] <= pd.to_datetime(end_date))
]

# فلتر الإقليم
if region != "الكل":
    filtered_df = filtered_df[filtered_df["الاقليم"] == region]

# فلتر المحافظة
if governorate != "الكل":
    filtered_df = filtered_df[filtered_df["المحافظه"] == governorate]

# عدد السجلات
st.write(f"📊 عدد السجلات بعد الفلترة: {len(filtered_df)}")
st.sidebar.write("")
st.sidebar.markdown("Made With Dr.Mahmoud Kamel")


# ---------------- تجهيز الداتا حسب التاريخ ---------------- #
sorted_df = filtered_df.sort_values("التاريخ")

dates = sorted_df["التاريخ"].dropna().unique()

# لو عندك يوم واحد بس
if len(dates) == 1:
    last_day = dates[-1]
    prev_day = dates[-1]
else:
    last_day = dates[-1]
    prev_day = dates[-2]

last_df = sorted_df[sorted_df["التاريخ"] == last_day]
prev_df = sorted_df[sorted_df["التاريخ"] == prev_day]

# ---------------- الحسابات (آخر يوم) ---------------- #
total_cars = last_df["اجمالي سيارات المنطقه"].sum()
total_operation = last_df["اجمالي سيارات التشغيل"].sum()
outside_operation = last_df["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"].sum()

inside_operation = total_operation - outside_operation

agency_cars = last_df["اجمالي السيارات بالتوكيل"].sum()
broken_cars = last_df["اجمالي السيارات المعطله"].sum()

# ---------------- الحسابات (اليوم السابق) ---------------- #
prev_operation = prev_df["اجمالي سيارات التشغيل"].sum()
prev_inside = prev_df["اجمالي سيارات التشغيل"].sum() - prev_df["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"].sum()

# ---------------- النسب ---------------- #
operation_ratio = (inside_operation / total_operation) * 100 if total_operation else 0
prev_ratio = (prev_inside / prev_operation) * 100 if prev_operation else 0

working_ratio = (inside_operation / total_cars) * 100 if total_cars else 0
agency_ratio = (agency_cars / total_cars) * 100 if total_cars else 0
broken_ratio = (broken_cars / total_cars) * 100 if total_cars else 0

# ---------------- KPI ---------------- #
st.markdown(f"## 📊 المؤشرات الحالية (📅 {last_day.date()})")
st.info("📌 المؤشرات تمثل آخر يوم داخل الفترة المختارة وليس الوقت الحالي")
col1, col2= st.columns(2)

col1.metric("🚑 إجمالي السيارات", int(total_cars),border=True)
col2.metric(
    "⚙️ إجمالي التشغيل",
    int(total_operation),
    border=True
)

# تحديد اللون حسب القيمة
color = "#ff4d4d" if outside_operation > 0 else "#28a745"  # أحمر لو فيه مشكلة / أخضر لو 0

st.markdown(f"""
<div style="
    background-color:{color};
    padding:20px;
    border-radius:15px;
    text-align:center;
    color:white;
    font-size:20px;
    font-weight:bold;">
    ❌ خارج التشغيل <br> {int(outside_operation)}
</div>
""", unsafe_allow_html=True)
    
    
    
col5, col6, col7 = st.columns(3)  
    
col5.metric(
    "✅ داخل التشغيل",
    int(inside_operation),
    delta=int(inside_operation - prev_inside),border=True
)




col6.metric("📈 نسبة السيارات العاملة", f"{working_ratio:.1f}%",
    delta=f"{operation_ratio - prev_ratio:.1f}%",border=True)
col7.metric(
    "⚡ نسبة التشغيل",
    f"{operation_ratio:.1f}%",
    delta=f"{operation_ratio - prev_ratio:.1f}%",border=True
)

col8, col9 = st.columns(2)

col8.metric("🏭 سيارات التوكيل", f"{int(agency_cars)} ({agency_ratio:.1f}%)",border=True)
col9.metric("🚫 السيارات المعطلة", f"{int(broken_cars)} ({broken_ratio:.1f}%)",border=True)

# ---------------- Alerts ---------------- #
if operation_ratio < 90:
    st.error("🚨 نسبة التشغيل ضعيفة - محتاج تدخل فوري")
elif operation_ratio < 97:
    st.warning("⚠️ نسبة التشغيل متوسطة")
else:
    st.success("✅ التشغيل ممتاز")
    
 
   

# ---------------- Charts ---------------- #

st.markdown("## 📈 تحليل البيانات")

# حسب الإقليم

# حسب الإقليم (نسبة التشغيل)
# st.markdown("### 📊 نسبة التشغيل حسب الإقليم")
region_grouped = filtered_df.groupby("الاقليم").agg({
    "اجمالي سيارات التشغيل": "sum",
    "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل": "sum"
})

region_grouped["نسبة التشغيل"] = region_grouped.apply(
    lambda x: ((x["اجمالي سيارات التشغيل"] - x["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"])
               / x["اجمالي سيارات التشغيل"]) * 100
    if x["اجمالي سيارات التشغيل"] else 0,
    axis=1
)


import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display


# حسب المحافظة

gov_grouped = filtered_df.groupby("المحافظه").agg({
    "اجمالي سيارات التشغيل": "sum",
    "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل": "sum"
})

gov_grouped["نسبة التشغيل"] = gov_grouped.apply(
    lambda x: ((x["اجمالي سيارات التشغيل"] - x["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"])
               / x["اجمالي سيارات التشغيل"]) * 100
    if x["اجمالي سيارات التشغيل"] else 0,
    axis=1
)


import plotly.express as px

st.markdown("### 📊 نسبة التشغيل حسب الإقليم")

fig1 = px.bar(
    region_grouped.reset_index(),
    x="الاقليم",
    y="نسبة التشغيل",
    color="نسبة التشغيل",
    color_continuous_scale=["red", "green"],
    text=region_grouped["نسبة التشغيل"].apply(lambda x: f"{x:.1f}%")
)

fig1.add_hline(y=97, line_dash="dash", line_color="orange")

fig1.update_layout(
    xaxis_title="الإقليم",
    yaxis_title="نسبة التشغيل %",
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("### 📊 نسبة التشغيل حسب المحافظة")

fig2 = px.bar(
    gov_grouped.reset_index(),
    x="المحافظه",
    y="نسبة التشغيل",
    color="نسبة التشغيل",
    color_continuous_scale=["red", "green"],
    text=gov_grouped["نسبة التشغيل"].apply(lambda x: f"{x:.1f}%")
)

fig2.add_hline(y=97, line_dash="dash", line_color="orange")

fig2.update_layout(
    xaxis_title="المحافظة",
    yaxis_title="نسبة التشغيل %",
    yaxis=dict(range=[0, 100])
)

st.plotly_chart(fig2, use_container_width=True)


# ---------------- 🏆 أفضل وأسوأ المحافظات ---------------- #
st.markdown("## 🏆 تحليل أداء المحافظات")

low_perf_count = (gov_grouped["نسبة التشغيل"] < 97).sum()
total_govs = len(gov_grouped)

st.metric(
    "🚨 محافظات تحت الهدف",
    f"{low_perf_count}/{total_govs}",
    delta=f"{(low_perf_count/total_govs)*100:.1f}%"
)

low_perf = gov_grouped[gov_grouped["نسبة التشغيل"] < 97]

if not low_perf.empty:
    gov_list = " - ".join(low_perf.index.tolist())

    st.error(f"""
    🚨 المحافظات تحت الهدف:

    {gov_list}
    """)
    
# ترتيب البيانات
gov_grouped_sorted = gov_grouped.sort_values("نسبة التشغيل", ascending=False)

# أفضل 5
best = gov_grouped_sorted.head(10).copy()

# Threshold للأداء الضعيف
threshold = 97

# أسوأ (بس اللي أقل من 97)
worst = gov_grouped[gov_grouped["نسبة التشغيل"] < threshold] \
            .sort_values("نسبة التشغيل") \
            .head(5) \
            .copy()

# إضافة Ranking
best["🏅 الترتيب"] = range(1, len(best) + 1)
if not worst.empty:
    worst["⚠️ الترتيب"] = range(1, len(worst) + 1)

# تقسيم الشاشة
col1, col2 = st.columns(2)

# ---------------- أفضل محافظات ---------------- #
with col1:
    st.markdown("### 🟢 أداء المحافظات")

    st.dataframe(
    best.style.format({
        "اجمالي سيارات التشغيل": "{:.0f}",
        "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل": "{:.0f}",
        "نسبة التشغيل": "{:.1f}%"
    }),
    use_container_width=True
)

    # Insight
    top_gov = best.index[0]
    top_val = best["نسبة التشغيل"].iloc[0]

    st.success(f"""
    🏆 أفضل محافظة: **{top_gov}**  
    📈 بنسبة تشغيل: **{top_val:.1f}%**
    """)

# ---------------- أسوأ محافظات ---------------- #
with col2:
    st.markdown("### 🔴 المحافظات التي تحتاج تدخل")

    if worst.empty:
        st.success("✅ كل المحافظات تعمل بكفاءة عالية (≥ 97%)")
    else:
        st.dataframe(
            worst.style.format({"نسبة التشغيل": "{:.1f}%"}),
            use_container_width=True
        )

        # Insight
        worst_gov = worst.index[0]
        worst_val = worst["نسبة التشغيل"].iloc[0]

        st.error(f"""
        🚨 تحتاج تدخل: **{worst_gov}**  
        📉 بنسبة تشغيل: **{worst_val:.1f}%**
        """)
        
# Trend يومي
trend_grouped = filtered_df.groupby("التاريخ").agg({
    "اجمالي سيارات التشغيل": "sum",
    "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل": "sum"
})

trend_grouped["نسبة التشغيل"] = trend_grouped.apply(
    lambda x: ((x["اجمالي سيارات التشغيل"] - x["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"])
               / x["اجمالي سيارات التشغيل"]) * 100
    if x["اجمالي سيارات التشغيل"] else 0,
    axis=1
)

trend = trend_grouped["نسبة التشغيل"]

import plotly.express as px

st.markdown("### 📈 اتجاه التشغيل عبر الوقت")

trend_df = trend_grouped.reset_index()

fig = px.line(
    trend_df,
    x="التاريخ",
    y="نسبة التشغيل",
    markers=True
)

# إضافة القيم كنص
fig.update_traces(
    text=trend_df["نسبة التشغيل"].apply(lambda x: f"{x:.1f}%"),
    textposition="top center"
)

# خط الهدف
fig.add_hline(y=97, line_dash="dash", line_color="orange")

# تنسيق الشكل
fig.update_layout(
    xaxis_title="التاريخ",
    yaxis_title="نسبة التشغيل %",
    yaxis=dict(range=[0, 100])
)

trend_df["الحالة"] = trend_df["نسبة التشغيل"].apply(
    lambda x: "جيد" if x >= 97 else "ضعيف"
)

fig = px.line(
    trend_df,
    x="التاريخ",
    y="نسبة التشغيل",
    color="الحالة",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)


# ---------------- عرض البيانات ---------------- #

# دالة لتلوين الصف
def highlight_row(row):
    try:
        total_operation = row["اجمالي سيارات التشغيل"]
        outside_operation = row["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"]

        if total_operation:
            ratio = ((total_operation - outside_operation) / total_operation) * 100
        else:
            ratio = 0

        if ratio < 97:
            return ['background-color: red'] * len(row)
        else:
            return [''] * len(row)
    except:
        return [''] * len(row)

worst_day = trend.idxmin()
worst_value = trend.min()

bad_days = trend[trend < 97]

if bad_days.empty:
    st.success("✅ لا توجد أيام تشغيل ضعيفة")
else:
    st.warning(f"""
    ⚠️ عدد الأيام الضعيفة: {len(bad_days)} يوم  
    📉 متوسط الأداء فيهم: {bad_days.mean():.1f}%
    """)
    
st.markdown(f"""
### 🧠 الاداء العام


🔻 أقل يوم تشغيل كان: **{worst_day.date()}**  
📉 بنسبة تشغيل: **{worst_value:.1f}%**

""")

worst_gov = gov_grouped.sort_values("نسبة التشغيل").head(1)
gov_name = worst_gov.index[0]
gov_value = worst_gov["نسبة التشغيل"].values[0]

st.markdown(f"""
### 🔍 تحليل السبب

🔴 أقل محافظة: **{gov_name}**  
📉 بنسبة: **{gov_value:.1f}%**

""")

threshold_good = 97
threshold_warning = 95

min_val = trend.min()

if min_val >= threshold_good:
    st.success("✅ التشغيل ممتاز في جميع الأيام")
elif min_val >= threshold_warning:
    st.warning(f"⚠️ الأداء جيد لكن أقل قيمة {min_val:.1f}%")
else:
    worst_day = trend.idxmin()
    st.error(f"🚨 أسوأ يوم: {worst_day.date()} بنسبة {min_val:.1f}%")


st.markdown("## 📋 البيانات بعد الفلترة")

green_cols = [
    "سيارات بالراحة",
    "سيارات بدون طاقم (عجز )",
    "سيارات  اجازة مسبقة",
    "سيارات غياب بدون اذن",
    "اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل",
    "نسبه التشغيل"
]

# ---------------- تلوين الصفوف بالأحمر ---------------- #
def highlight_row(row):
    try:
        total_operation = row["اجمالي سيارات التشغيل"]
        outside_operation = row["اجمالي سيارات المنطقه العامله  ولكن خارج التشغيل"]

        ratio = ((total_operation - outside_operation) / total_operation) * 100 if total_operation else 0

        if ratio < 97:
            return ['background-color: #ffcccc; color: black; font-weight: bold;'] * len(row)
        else:
            return [''] * len(row)
    except:
        return [''] * len(row)


# ---------------- Styling ---------------- #
styled_df = filtered_df.style.apply(highlight_row, axis=1)

# تلوين الأعمدة الخضراء
for col in green_cols:
    if col in filtered_df.columns:
        styled_df = styled_df.set_properties(
            subset=[col],
            **{
                "background-color": "lightgreen",
                "color": "black",
                "font-weight": "bold"
            }
        )

# تنسيق الأرقام
styled_df = styled_df.format({
    "نسبه التشغيل": "{:.1f}%"
})

styled_df = styled_df.format(
    lambda x: f"{int(x)}" if isinstance(x, (int, float)) and not pd.isna(x) else x
)

# عرض الجدول
st.dataframe(styled_df, use_container_width=True)


# ---------------- Excel Export ---------------- #
from io import BytesIO

output = BytesIO()

with pd.ExcelWriter(output, engine='openpyxl') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='Data')

st.download_button(
    "📥 Download Excel",
    data=output.getvalue(),
    file_name="Data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)







