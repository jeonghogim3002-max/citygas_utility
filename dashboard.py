# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types

load_dotenv()
_gemini_key = os.getenv("GEMINI_API_KEY", "")
_gemini_client = genai.Client(api_key=_gemini_key) if _gemini_key else None

st.set_page_config(
    page_title="도시가스본부 고객지원팀 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
.main { background-color: #F4F6FB; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a237e 0%,#283593 100%); }
section[data-testid="stSidebar"] * { color: #E8EAF6 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label { color: #C5CAE9 !important; font-weight:600; }
.kpi-card { border-radius:16px; padding:22px 24px; color:white; box-shadow:0 4px 20px rgba(0,0,0,0.15); margin-bottom:4px; }
.kpi-label { font-size:12px; font-weight:600; letter-spacing:1px; opacity:0.88; }
.kpi-value { font-size:32px; font-weight:800; margin-top:6px; line-height:1; }
.kpi-delta { font-size:12px; margin-top:6px; opacity:0.78; }
.section-title { color:#3949AB; font-weight:700; font-size:15px; margin:16px 0 6px 0; }
hr.div { border:none; border-top:1.5px solid #E8EAF6; margin:20px 0; }
.chat-user { background:#3949AB; color:white; border-radius:18px 18px 4px 18px; padding:10px 16px; margin:4px 0; display:inline-block; max-width:80%; float:right; clear:both; font-size:14px; }
.chat-ai { background:#F0F4FF; color:#1a237e; border-radius:18px 18px 18px 4px; padding:10px 16px; margin:4px 0; display:inline-block; max-width:85%; float:left; clear:both; font-size:14px; }
.chat-label-user { text-align:right; font-size:11px; color:#9FA8DA; margin-bottom:2px; clear:both; }
.chat-label-ai { text-align:left; font-size:11px; color:#9FA8DA; margin-bottom:2px; clear:both; }
.chat-wrap { overflow:hidden; margin-bottom:6px; }
</style>
""", unsafe_allow_html=True)

BRANCH_COLORS = {
    '수원사업장':'#5C6BC0','남부사업장':'#EF5350','중부사업장':'#26A69A','안산사업장':'#AB47BC',
    '용인사업장':'#FF7043','오산사업장':'#29B6F6','부천사업장':'#EC407A','인천사업장':'#66BB6A'
}

@st.cache_data(ttl=0)
def load():
    fac  = pd.read_csv('data/사업장관리.csv',   encoding='utf-8-sig')
    lab  = pd.read_csv('data/노무관리.csv',      encoding='utf-8-sig')
    saf  = pd.read_csv('data/산업안전보건.csv',  encoding='utf-8-sig')
    eng  = pd.read_csv('data/에너지관리.csv',    encoding='utf-8-sig')
    ins  = pd.read_csv('data/시설점검.csv',      encoding='utf-8-sig')
    return fac, lab, saf, eng, ins

fac_df, lab_df, saf_df, eng_df, ins_df = load()
all_months = sorted(fac_df['기준월'].unique())

# ── 사이드바 ──────────────────────────────────────────────
st.sidebar.markdown("## 조회 조건")
start_m = st.sidebar.selectbox("시작월", all_months, index=0)
end_m   = st.sidebar.selectbox("종료월", all_months, index=len(all_months)-1)
all_br  = sorted(fac_df['사업장'].unique())
sel_br  = st.sidebar.multiselect("사업장 선택", all_br, default=all_br)

def filt(df):
    return df[(df['기준월']>=start_m)&(df['기준월']<=end_m)&(df['사업장'].isin(sel_br))]

fac = filt(fac_df); lab = filt(lab_df); saf = filt(saf_df)
eng = filt(eng_df); ins = filt(ins_df)
last_m  = fac['기준월'].max()
fac_l   = fac[fac['기준월']==last_m]
lab_l   = lab[lab['기준월']==last_m]
saf_l   = saf[saf['기준월']==last_m]
eng_l   = eng[eng['기준월']==last_m]

# ── 헬퍼 ──────────────────────────────────────────────────
def kpi(col, label, value, delta="", grad="linear-gradient(135deg,#667eea,#764ba2)"):
    col.markdown(f"""<div class="kpi-card" style="background:{grad}">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-delta">{delta}&nbsp;</div>
    </div>""", unsafe_allow_html=True)

def sec(title):
    st.markdown(f'<div class="section-title">▍ {title}</div>', unsafe_allow_html=True)

def line(df, x, y, color, title, ylab="", goal=None):
    cmap = {b: BRANCH_COLORS.get(b,'#888') for b in df[color].unique()}
    fig  = px.line(df, x=x, y=y, color=color, title=title, markers=True,
                   color_discrete_map=cmap, template="plotly_white")
    fig.update_traces(line_width=2.5, marker_size=6)
    fig.update_layout(title_font_size=14, title_font_color="#3949AB", height=330,
                      margin=dict(l=10,r=10,t=38,b=10), legend_title_text="사업장",
                      xaxis=dict(showgrid=True,gridcolor="#F0F0F0"),
                      yaxis=dict(showgrid=True,gridcolor="#F0F0F0",title=ylab))
    if goal:
        fig.add_hline(y=goal, line_dash="dot", line_color="#FF6B6B", line_width=1.5,
                      annotation_text=f"목표 {goal}", annotation_font_color="#FF6B6B",
                      annotation_position="bottom right")
    st.plotly_chart(fig, use_container_width=True)

def bar(df, x, y, color, title):
    cmap = {b: BRANCH_COLORS.get(b,'#888') for b in df[color].unique()}
    fig  = px.bar(df, x=x, y=y, color=color, title=title, barmode='group',
                  color_discrete_map=cmap, template="plotly_white", text_auto='.0f')
    fig.update_layout(title_font_size=14, title_font_color="#3949AB", height=310,
                      margin=dict(l=10,r=10,t=38,b=10), legend_title_text="사업장")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def yoy_df(df, val_col, agg='sum'):
    d = df.copy()
    d['연도'] = d['기준월'].str[:4]
    d['월']   = d['기준월'].str[5:]
    piv = d.groupby(['연도','월'])[val_col].agg(agg).unstack('연도').reset_index()
    piv.columns.name = None
    yr_cols = [c for c in piv.columns if c != '월']
    if len(yr_cols) >= 2:
        y1, y2 = yr_cols[0], yr_cols[1]
        piv['증감률(%)'] = ((piv[y2]-piv[y1])/piv[y1].replace(0,1)*100).round(1)
    return piv

def styled(df):
    def hl(v):
        if isinstance(v,(int,float)):
            if v>0:  return 'background-color:#FFEBEE;color:#C62828;font-weight:700'
            if v<0:  return 'background-color:#E8F5E9;color:#2E7D32;font-weight:700'
        return ''
    if '증감률(%)' in df.columns:
        try:
            return df.style.map(hl, subset=['증감률(%)'])
        except AttributeError:
            return df.style.applymap(hl, subset=['증감률(%)'])
    return df.style

def divider(): st.markdown('<hr class="div">', unsafe_allow_html=True)

# ── 헤더 ──────────────────────────────────────────────────
st.markdown("# 도시가스본부")
st.markdown(f"<p style='color:#7986CB;font-weight:600;margin-top:-12px'>고객지원팀 실적 분석 대시보드 &nbsp;|&nbsp; {start_m} ~ {end_m}</p>", unsafe_allow_html=True)
divider()

# ── 탭 ────────────────────────────────────────────────────
t0,t1,t2,t3,t4,t5,t6 = st.tabs(["📋 종합 요약","🏢 사업장 관리","👷 노무 관리","⚡ 에너지 관리","🛡️ 산업안전보건","🔧 시설 점검","🤖 AI 분석"])

# ══ 탭0: 종합 요약 ════════════════════════════════════════
with t0:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"총 재직인원", f"{int(lab_l['총인원'].sum()):,} 명", f"기준: {last_m}",
        "linear-gradient(135deg,#667eea,#764ba2)")
    kpi(c2,"이달 재해건수", f"{int(saf_l['재해건수'].sum())} 건", f"부상자 {int(saf_l['부상자수'].sum())}명",
        "linear-gradient(135deg,#f093fb,#f5576c)")
    util = int(fac_l[['전기료(천원)','수도료(천원)','가스료(천원)']].sum().sum())
    kpi(c3,"이달 유틸리티비", f"{util:,} 천원", "전기+수도+가스",
        "linear-gradient(135deg,#4facfe,#00f2fe)")
    kpi(c4,"에너지 절감달성률", f"{eng_l['절감목표달성률(%)'].mean():.1f} %", "평균",
        "linear-gradient(135deg,#43e97b,#38f9d7)")
    divider()

    c1,c2 = st.columns(2)
    with c1:
        sec("월별 사업장 총비용 추이")
        tmp = fac.copy()
        tmp['총비용(천원)'] = tmp[['유지보수비(천원)','전기료(천원)','수도료(천원)','가스료(천원)','임차료(천원)']].sum(axis=1)
        line(tmp.groupby(['기준월','사업장'])['총비용(천원)'].sum().reset_index(),
             '기준월','총비용(천원)','사업장','사업장별 월별 총비용','천원')
    with c2:
        sec("월별 재해건수 추이")
        line(saf.groupby(['기준월','사업장'])['재해건수'].sum().reset_index(),
             '기준월','재해건수','사업장','사업장별 월별 재해건수','건')

    c1,c2 = st.columns(2)
    with c1:
        sec("월별 도시가스 사용량 추이")
        line(eng.groupby(['기준월','사업장'])['도시가스사용량(천m3)'].sum().reset_index(),
             '기준월','도시가스사용량(천m3)','사업장','도시가스 사용량 추이','천m³')
    with c2:
        sec("재해건수 전년 동월 비교")
        d = yoy_df(saf.groupby('기준월')['재해건수'].sum().reset_index(),'재해건수')
        st.dataframe(styled(d), use_container_width=True, hide_index=True)

# ══ 탭1: 사업장 관리 ══════════════════════════════════════
with t1:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"재직인원 합계", f"{int(fac['재직인원'].sum()):,} 명", "조회기간",
        "linear-gradient(135deg,#a18cd1,#fbc2eb)")
    kpi(c2,"유지보수비 합계", f"{int(fac['유지보수비(천원)'].sum()):,} 천원", "",
        "linear-gradient(135deg,#667eea,#764ba2)")
    kpi(c3,"전기료 합계", f"{int(fac['전기료(천원)'].sum()):,} 천원", "",
        "linear-gradient(135deg,#f7971e,#ffd200)")
    kpi(c4,"임차료 합계", f"{int(fac['임차료(천원)'].sum()):,} 천원", "",
        "linear-gradient(135deg,#11998e,#38ef7d)")
    divider()

    cost_list = ['유지보수비(천원)','전기료(천원)','수도료(천원)','가스료(천원)','통신비(천원)','청소용역비(천원)','차량유지비(천원)','임차료(천원)']
    sel_cost  = st.selectbox("비용 항목 선택", cost_list)
    sec(f"{sel_cost} 월별 추이")
    line(fac.groupby(['기준월','사업장'])[sel_cost].sum().reset_index(),
         '기준월', sel_cost, '사업장', f'{sel_cost} 월별 추이', '천원')

    c1,c2 = st.columns(2)
    with c1:
        sec("재직인원 월별 추이")
        line(fac.groupby(['기준월','사업장'])['재직인원'].sum().reset_index(),
             '기준월','재직인원','사업장','재직인원 추이','명')
    with c2:
        sec("사업장별 총비용 비교 (조회기간 합계)")
        tmp = fac.copy()
        tmp['총비용(천원)'] = tmp[cost_list].sum(axis=1)
        bc = tmp.groupby('사업장')['총비용(천원)'].sum().reset_index()
        bar(bc,'사업장','총비용(천원)','사업장','사업장별 총비용')

    sec("유지보수비 전년 동월 비교")
    d = yoy_df(fac.groupby('기준월')['유지보수비(천원)'].sum().reset_index(),'유지보수비(천원)')
    st.dataframe(styled(d), use_container_width=True, hide_index=True)

# ══ 탭2: 노무 관리 ════════════════════════════════════════
with t2:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"총인원", f"{int(lab_l['총인원'].sum()):,} 명",
        f"정규 {int(lab_l['정규직'].sum())} / 계약 {int(lab_l['계약직'].sum())}",
        "linear-gradient(135deg,#4facfe,#00f2fe)")
    kpi(c2,"신규채용", f"{int(lab['신규채용'].sum())} 명", "조회기간 합계",
        "linear-gradient(135deg,#43e97b,#38f9d7)")
    kpi(c3,"퇴직자", f"{int(lab['퇴직자'].sum())} 명", "조회기간 합계",
        "linear-gradient(135deg,#f093fb,#f5576c)")
    kpi(c4,"평균급여", f"{int(lab_l['평균급여(천원)'].mean()):,} 천원", f"기준: {last_m}",
        "linear-gradient(135deg,#f7971e,#ffd200)")
    divider()

    c1,c2 = st.columns(2)
    with c1:
        sec("총인원 월별 추이")
        line(lab.groupby(['기준월','사업장'])['총인원'].sum().reset_index(),
             '기준월','총인원','사업장','사업장별 총인원 추이','명')
    with c2:
        sec("신규채용 vs 퇴직자 추이 (전체)")
        d2 = lab.groupby('기준월')[['신규채용','퇴직자']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['신규채용'],name='신규채용',
                                  line=dict(color='#43e97b',width=2.5),mode='lines+markers'))
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['퇴직자'],name='퇴직자',
                                  line=dict(color='#f5576c',width=2.5),mode='lines+markers'))
        fig.update_layout(template="plotly_white",height=330,title='신규채용 vs 퇴직자',
                          title_font_color="#3949AB",title_font_size=14,
                          margin=dict(l=10,r=10,t=38,b=10))
        st.plotly_chart(fig, use_container_width=True)

    c1,c2 = st.columns(2)
    with c1:
        sec("연차사용률 월별 추이")
        line(lab.groupby(['기준월','사업장'])['연차사용률(%)'].mean().reset_index(),
             '기준월','연차사용률(%)','사업장','연차사용률 추이','%',goal=80)
    with c2:
        sec("사업장별 이직률 (조회기간)")
        tr = lab.groupby('사업장').agg(퇴직자=('퇴직자','sum'),총인원=('총인원','mean')).reset_index()
        tr['이직률(%)'] = (tr['퇴직자']/tr['총인원']*100).round(1)
        bar(tr,'사업장','이직률(%)','사업장','사업장별 이직률')

    sec("총인원 전년 동월 비교")
    st.dataframe(styled(yoy_df(lab.groupby('기준월')['총인원'].sum().reset_index(),'총인원')),
                 use_container_width=True, hide_index=True)

# ══ 탭3: 에너지 관리 ══════════════════════════════════════
with t3:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"도시가스 사용량", f"{int(eng['도시가스사용량(천m3)'].sum()):,} 천m³", "조회기간",
        "linear-gradient(135deg,#f7971e,#ffd200)")
    kpi(c2,"전력 사용량", f"{int(eng['전력사용량(kWh)'].sum()):,} kWh", "조회기간",
        "linear-gradient(135deg,#4facfe,#00f2fe)")
    kpi(c3,"탄소배출량", f"{int(eng['탄소배출량(tCO2)'].sum()):,} tCO₂", "조회기간",
        "linear-gradient(135deg,#a8edea,#fed6e3)")
    kpi(c4,"절감목표달성률", f"{eng['절감목표달성률(%)'].mean():.1f} %", "평균",
        "linear-gradient(135deg,#43e97b,#38f9d7)")
    divider()

    c1,c2 = st.columns(2)
    with c1:
        sec("도시가스 사용량 월별 추이")
        line(eng.groupby(['기준월','사업장'])['도시가스사용량(천m3)'].sum().reset_index(),
             '기준월','도시가스사용량(천m3)','사업장','도시가스 사용량','천m³')
    with c2:
        sec("전력 사용량 월별 추이")
        line(eng.groupby(['기준월','사업장'])['전력사용량(kWh)'].sum().reset_index(),
             '기준월','전력사용량(kWh)','사업장','전력 사용량','kWh')

    c1,c2 = st.columns(2)
    with c1:
        sec("탄소배출량 월별 추이")
        line(eng.groupby(['기준월','사업장'])['탄소배출량(tCO2)'].sum().reset_index(),
             '기준월','탄소배출량(tCO2)','사업장','탄소배출량','tCO₂')
    with c2:
        sec("절감목표달성률 월별 추이")
        line(eng.groupby(['기준월','사업장'])['절감목표달성률(%)'].mean().reset_index(),
             '기준월','절감목표달성률(%)','사업장','절감목표달성률','%',goal=100)

    sec("도시가스 사용량 전년 동월 비교")
    st.dataframe(styled(yoy_df(eng.groupby('기준월')['도시가스사용량(천m3)'].sum().reset_index(),'도시가스사용량(천m3)')),
                 use_container_width=True, hide_index=True)

# ══ 탭4: 산업안전보건 ════════════════════════════════════════
with t4:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"재해건수", f"{int(saf['재해건수'].sum())} 건", "조회기간",
        "linear-gradient(135deg,#f093fb,#f5576c)")
    kpi(c2,"부상자수", f"{int(saf['부상자수'].sum())} 명", "조회기간",
        "linear-gradient(135deg,#ff9966,#ff5e62)")
    kpi(c3,"안전교육이수율", f"{saf['안전교육이수율(%)'].mean():.1f} %", "평균",
        "linear-gradient(135deg,#43e97b,#38f9d7)")
    kpi(c4,"위험요소 발굴", f"{int(saf['위험요소발굴건수'].sum())} 건", "조회기간",
        "linear-gradient(135deg,#4facfe,#00f2fe)")
    divider()

    c1,c2 = st.columns(2)
    with c1:
        sec("재해건수 / 부상자수 추이 (전체)")
        d2 = saf.groupby('기준월')[['재해건수','부상자수']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=d2['기준월'],y=d2['재해건수'],name='재해건수',marker_color='#f5576c',opacity=0.85))
        fig.add_trace(go.Bar(x=d2['기준월'],y=d2['부상자수'],name='부상자수',marker_color='#ff9966',opacity=0.85))
        fig.update_layout(template="plotly_white",barmode='group',height=330,
                          title='재해·부상 추이',title_font_color="#3949AB",title_font_size=14,
                          margin=dict(l=10,r=10,t=38,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sec("안전교육이수율 월별 추이")
        line(saf.groupby(['기준월','사업장'])['안전교육이수율(%)'].mean().reset_index(),
             '기준월','안전교육이수율(%)','사업장','안전교육이수율','%',goal=100)

    c1,c2 = st.columns(2)
    with c1:
        sec("위험요소 발굴 vs 개선조치 완료 추이")
        d2 = saf.groupby('기준월')[['위험요소발굴건수','개선조치완료건수']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['위험요소발굴건수'],name='발굴',
                                  line=dict(color='#FF7043',width=2.5),mode='lines+markers'))
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['개선조치완료건수'],name='완료',
                                  line=dict(color='#43e97b',width=2.5),mode='lines+markers'))
        fig.update_layout(template="plotly_white",height=330,
                          title='위험요소 발굴 vs 개선조치',title_font_color="#3949AB",title_font_size=14,
                          margin=dict(l=10,r=10,t=38,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sec("사업장별 누적 재해건수")
        bc = saf.groupby('사업장')['재해건수'].sum().reset_index()
        bar(bc,'사업장','재해건수','사업장','사업장별 누적 재해건수')

    sec("재해건수 전년 동월 비교")
    st.dataframe(styled(yoy_df(saf.groupby('기준월')['재해건수'].sum().reset_index(),'재해건수')),
                 use_container_width=True, hide_index=True)

# ══ 탭5: 시설 점검 ════════════════════════════════════════
with t5:
    c1,c2,c3,c4 = st.columns(4)
    kpi(c1,"발견결함 건수", f"{int(ins['발견결함건수'].sum())} 건", "조회기간",
        "linear-gradient(135deg,#11998e,#38ef7d)")
    kpi(c2,"결함조치율", f"{ins['결함조치율(%)'].mean():.1f} %", "평균",
        "linear-gradient(135deg,#43e97b,#38f9d7)")
    kpi(c3,"설비고장 건수", f"{int(ins['설비고장건수'].sum())} 건", "조회기간",
        "linear-gradient(135deg,#f7971e,#ffd200)")
    kpi(c4,"평균 복구시간", f"{ins['고장복구시간(시간)'].mean():.1f} 시간", "평균",
        "linear-gradient(135deg,#4facfe,#00f2fe)")
    divider()

    c1,c2 = st.columns(2)
    with c1:
        sec("발견결함 / 설비고장 추이")
        d2 = ins.groupby('기준월')[['발견결함건수','설비고장건수']].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['발견결함건수'],name='발견결함',
                                  line=dict(color='#FF7043',width=2.5),mode='lines+markers'))
        fig.add_trace(go.Scatter(x=d2['기준월'],y=d2['설비고장건수'],name='설비고장',
                                  line=dict(color='#EF5350',width=2.5,dash='dash'),mode='lines+markers'))
        fig.update_layout(template="plotly_white",height=330,
                          title='결함·고장 추이',title_font_color="#3949AB",title_font_size=14,
                          margin=dict(l=10,r=10,t=38,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sec("결함조치율 월별 추이")
        line(ins.groupby(['기준월','사업장'])['결함조치율(%)'].mean().reset_index(),
             '기준월','결함조치율(%)','사업장','결함조치율','%',goal=95)

    c1,c2 = st.columns(2)
    with c1:
        sec("고장복구시간 월별 추이")
        line(ins.groupby(['기준월','사업장'])['고장복구시간(시간)'].mean().reset_index(),
             '기준월','고장복구시간(시간)','사업장','평균 고장복구시간','시간')
    with c2:
        sec("사업장별 정기점검 이행률")
        cr = ins.groupby('사업장').apply(
            lambda x: round((x['정기점검']=='완료').sum()/len(x)*100, 1)
        ).reset_index()
        cr.columns = ['사업장','정기점검이행률(%)']
        bar(cr,'사업장','정기점검이행률(%)','사업장','정기점검 이행률')

    sec("발견결함건수 전년 동월 비교")
    st.dataframe(styled(yoy_df(ins.groupby('기준월')['발견결함건수'].sum().reset_index(),'발견결함건수')),
                 use_container_width=True, hide_index=True)

# ══ 탭6: AI 분석 ════════════════════════════════════════
with t6:
    if not _gemini_client:
        st.warning(".env 파일에 GEMINI_API_KEY가 설정되지 않았습니다.")
    else:
        def build_data_context():
            lines = [
                f"[조회 조건] 기간: {start_m} ~ {end_m}, 사업장: {', '.join(sel_br)}",
                "",
                "=== 사업장 관리 요약 ===",
                f"- 재직인원 합계: {int(fac['재직인원'].sum()):,}명",
                f"- 유지보수비: {int(fac['유지보수비(천원)'].sum()):,}천원",
                f"- 전기료: {int(fac['전기료(천원)'].sum()):,}천원",
                f"- 수도료: {int(fac['수도료(천원)'].sum()):,}천원",
                f"- 가스료: {int(fac['가스료(천원)'].sum()):,}천원",
                f"- 임차료: {int(fac['임차료(천원)'].sum()):,}천원",
                "",
                "=== 노무 관리 요약 ===",
                f"- 최근월({last_m}) 총인원: {int(lab_l['총인원'].sum()):,}명 (정규직 {int(lab_l['정규직'].sum())}, 계약직 {int(lab_l['계약직'].sum())})",
                f"- 조회기간 신규채용: {int(lab['신규채용'].sum())}명",
                f"- 조회기간 퇴직자: {int(lab['퇴직자'].sum())}명",
                f"- 최근월 평균급여: {int(lab_l['평균급여(천원)'].mean()):,}천원",
                f"- 평균 연차사용률: {lab['연차사용률(%)'].mean():.1f}%",
                "",
                "=== 에너지 관리 요약 ===",
                f"- 도시가스 사용량: {int(eng['도시가스사용량(천m3)'].sum()):,}천m³",
                f"- 전력 사용량: {int(eng['전력사용량(kWh)'].sum()):,}kWh",
                f"- 탄소배출량: {int(eng['탄소배출량(tCO2)'].sum()):,}tCO₂",
                f"- 평균 절감목표달성률: {eng['절감목표달성률(%)'].mean():.1f}%",
                "",
                "=== 산업안전보건 요약 ===",
                f"- 재해건수: {int(saf['재해건수'].sum())}건",
                f"- 부상자수: {int(saf['부상자수'].sum())}명",
                f"- 평균 안전교육이수율: {saf['안전교육이수율(%)'].mean():.1f}%",
                f"- 위험요소 발굴: {int(saf['위험요소발굴건수'].sum())}건",
                f"- 개선조치 완료: {int(saf['개선조치완료건수'].sum())}건",
                "",
                "=== 시설 점검 요약 ===",
                f"- 발견결함: {int(ins['발견결함건수'].sum())}건",
                f"- 평균 결함조치율: {ins['결함조치율(%)'].mean():.1f}%",
                f"- 설비고장: {int(ins['설비고장건수'].sum())}건",
                f"- 평균 고장복구시간: {ins['고장복구시간(시간)'].mean():.1f}시간",
            ]
            br_safety = saf.groupby('사업장')['재해건수'].sum().sort_values(ascending=False)
            lines.append("\n사업장별 재해건수: " + ", ".join(f"{k}({v}건)" for k, v in br_safety.items()))
            br_energy = eng.groupby('사업장')['도시가스사용량(천m3)'].sum().sort_values(ascending=False)
            lines.append("사업장별 도시가스사용량: " + ", ".join(f"{k}({v:.0f}천m³)" for k, v in br_energy.items()))
            return "\n".join(lines)

        SYSTEM_PROMPT = """당신은 도시가스본부 고객지원팀 대시보드 데이터 분석 전문 AI입니다.
아래 데이터 요약을 바탕으로 사용자의 질문에 친절하고 정확하게 한국어로 답변하세요.
숫자를 언급할 때는 단위를 함께 표기하고, 필요 시 인사이트나 개선 방향도 제안하세요.

{data_context}"""

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        st.markdown("### 🤖 데이터 분석 AI 어시스턴트")
        st.markdown("<p style='color:#7986CB;font-size:13px'>현재 조회 조건의 데이터를 기반으로 질문하세요.</p>", unsafe_allow_html=True)

        col_chat, col_info = st.columns([3, 1])

        with col_info:
            st.markdown("**추천 질문 예시**")
            examples = [
                "어느 사업장의 재해건수가 가장 많나요?",
                "에너지 절감 목표 달성 현황은?",
                "인원 변화 추이를 분석해줘",
                "유지보수비가 가장 높은 사업장는?",
                "안전교육이수율이 낮은 사업장는?",
                "전체 비용 구조를 분석해줘",
            ]
            for ex in examples:
                if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                    st.session_state["ai_input_prefill"] = ex

            if st.button("대화 초기화", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        with col_chat:
            chat_container = st.container(height=480)
            with chat_container:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="chat-label-user">나</div><div class="chat-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-label-ai">AI</div><div class="chat-wrap"><div class="chat-ai">{msg["content"]}</div></div>', unsafe_allow_html=True)

            prefill = st.session_state.pop("ai_input_prefill", "")
            user_input = st.chat_input("데이터에 대해 무엇이든 물어보세요...", key="ai_chat_input")

            if prefill and not user_input:
                user_input = prefill

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})

                with st.spinner("AI가 분석 중..."):
                    try:
                        data_ctx = build_data_context()
                        system_with_data = SYSTEM_PROMPT.format(data_context=data_ctx)

                        history_for_gemini = []
                        for m in st.session_state.chat_history[:-1]:
                            role = "user" if m["role"] == "user" else "model"
                            history_for_gemini.append(
                                genai_types.Content(role=role, parts=[genai_types.Part(text=m["content"])])
                            )
                        history_for_gemini.append(
                            genai_types.Content(role="user", parts=[genai_types.Part(text=user_input)])
                        )

                        response = _gemini_client.models.generate_content(
                            model="gemini-flash-latest",
                            contents=history_for_gemini,
                            config=genai_types.GenerateContentConfig(
                                system_instruction=system_with_data,
                            )
                        )
                        answer = response.text
                    except Exception as e:
                        err = str(e)
                        if "429" in err or "RESOURCE_EXHAUSTED" in err:
                            import re
                            delay = re.search(r'retry in (\d+)', err)
                            wait = f" ({delay.group(1)}초 후 재시도)" if delay else ""
                            answer = f"⚠️ Gemini API 무료 쿼터를 초과했습니다{wait}.\n\n**해결 방법:**\n- 잠시 기다렸다가 다시 질문해 주세요 (분당 제한)\n- 오늘 일일 쿼터가 소진된 경우 내일 자정 이후 초기화됩니다\n- [Google AI Studio](https://aistudio.google.com)에서 결제 수단을 등록하면 즉시 사용 가능합니다"
                        elif "API_KEY" in err or "invalid" in err.lower():
                            answer = "⚠️ API 키가 유효하지 않습니다. .env 파일의 GEMINI_API_KEY를 확인해 주세요."
                        else:
                            answer = f"⚠️ 오류가 발생했습니다: {err}"

                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                st.rerun()

divider()
st.markdown("<p style='text-align:center;color:#9FA8DA;font-size:12px'>도시가스본부 고객지원팀 내부 관리 시스템</p>", unsafe_allow_html=True)
