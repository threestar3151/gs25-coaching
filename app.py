import streamlit as st
import pandas as pd
import altair as alt

# 1. 페이지 설정
st.set_page_config(page_title="GS25 수익 코칭 대시보드", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Nanum Gothic', sans-serif !important; }
    .main { background-color: #f8f9fa; }
    h1 { font-size: 30px !important; color: #007aff; font-weight: 800; }
    .stMetric { background-color: white; border-radius: 12px; border: 1px solid #e1e4e8; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 기초 데이터
type_info = {
    "GS1": {"support": 184.0, "royalty": 0.71},
    "GS2": {"support": 205.8, "royalty": 0.65},
    "GS3": {"support": 240.4, "royalty": 0.46}
}

st.title("📊 GS25 경영주 수익 개선 시뮬레이터")
st.divider()

# 3. 사이드바 입력
with st.sidebar:
    st.header("⚙️ 데이터 입력")
    st.markdown("### 🏷️ [1. 현재 현황]")
    c_type = st.selectbox("현재 가맹 타입", ["GS1", "GS2", "GS3"], key="c_t")
    c_rent = 0
    if c_type == "GS2":
        c_rent = st.number_input("현재 임차료 (천원)", value=0, step=10)
    c_sales = st.number_input("현재 일매출 (천원)", value=1500, step=10, key="c_s")
    c_margin = st.slider("현재 매익률 (%)", 20.0, 45.0, 30.0, step=0.1, key="c_m")
    c_o4o = st.number_input("현재 O4O 매출 (천원)", value=0, step=10, key="c_o")
    
    st.divider()
    st.markdown("### 🚀 [2. 코칭 목표]")
    t_type = st.selectbox("목표 가맹 타입", ["GS1", "GS2", "GS3"], index=(["GS1", "GS2", "GS3"].index(c_type)), key="t_t")
    t_rent = 0
    if t_type == "GS2":
        t_rent = st.number_input("목표 임차료 (천원)", value=0, step=10)
    t_sales = st.number_input("목표 일매출 (천원)", value=c_sales + 200, step=10, key="t_s")
    t_margin = st.slider("목표 매익률 (%)", 20.0, 45.0, c_margin + 1.5, step=0.1, key="t_m")
    t_o4o = st.number_input("목표 O4O 매출 (천원)", value=500, step=10, key="t_o")

# 4. 계산 로직
def calc(sales, margin, utype, o4o, rent=0):
    m_sales = sales * 30.41
    m_profit = m_sales * (margin / 100)
    royalty = m_profit * type_info[utype]["royalty"]
    support = type_info[utype]["support"]
    o4o_p = o4o * 0.16
    total = (royalty + support + o4o_p) - rent
    return {"m_sales": m_sales, "royalty": royalty, "o4o": o4o_p, "total": total, "support": support, "rent": rent}

cur = calc(c_sales, c_margin, c_type, c_o4o, c_rent)
tar = calc(t_sales, t_margin, t_type, t_o4o, t_rent)
diff = tar["total"] - cur["total"]

# 5. 메인 화면 출력
m1, m2, m3 = st.columns(3)
m1.metric("현재 월 예상수익", f"{int(cur['total']):,} 천원")
m2.metric("목표 월 예상수익", f"{int(tar['total']):,} 천원", delta=f"{int(diff):,} 천원 상승")
m3.metric("수익 개선율", f"{round((diff/cur['total'])*100, 1) if cur['total'] != 0 else 0}%")

st.markdown("---")
col_l, col_r = st.columns([1.6, 1])
with col_l:
    st.subheader("📑 상세 항목 비교")
    df_data = {
        "항목": ["가맹 타입", "임차료", "매익률", "O4O 매출액", "최종 정산금액"],
        "현재(A)": [c_type, f"-{c_rent:,}원", f"{c_margin}%", f"{c_o4o:,}원", f"{int(cur['total']):,}원"],
        "목표(B)": [t_type, f"-{t_rent:,}원", f"{t_margin}%", f"{t_o4o:,}원", f"{int(tar['total']):,}원"],
        "증감": ["-", f"{-(t_rent-c_rent):,}", "-", "-", f"**{int(diff):,}**"]
    }
    st.table(pd.DataFrame(df_data))

with col_r:
    st.subheader("📈 수익 변화 비교")
    chart_df = pd.DataFrame({
        "상태": ["기존", "목표"],
        "수익": [cur["total"], tar["total"]],
        "색상": ["#ADB5BD", "#007AFF"]
    })
    chart = alt.Chart(chart_df).mark_bar(size=40).encode(
        x=alt.X('수익:Q', axis=None),
        y=alt.Y('상태:N', sort='-x'),
        color=alt.Color('색상:N', scale=None)
    ).properties(height=250)
    st.altair_chart(chart, use_container_width=True)
