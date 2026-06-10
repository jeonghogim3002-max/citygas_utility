# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

np.random.seed(42)
os.makedirs('data', exist_ok=True)

# 사업소 목록 (경기남부)
BRANCHES = ['수원사업소','성남사업소','안양사업소','안산사업소',
            '용인사업소','화성사업소','평택사업소','시흥사업소']
REGIONS  = [b[:-4] for b in BRANCHES]
MONTHS   = pd.date_range('2023-01-01','2024-12-31',freq='MS')
DONE     = '완료'
NOT_DONE = '미완료'

def ri(lo, hi): return np.random.randint(lo, hi)
def rc(arr, p=None): return np.random.choice(arr, p=p)

# 단위 문자열을 변수로 분리해 인코딩 오류 방지
U_CHEONWON = '제원'  # 천원 (직접 유니코드)

# ─ 실제로는 아래처럼 직접 한글 문자열 사용 ─
C1 = '기준월'; C2 = '사업소'; C3 = '지역'


# ── 1. 사업장관리 ──────────────────────────────────────────
rows = []
for b, r in zip(BRANCHES, REGIONS):
    for m in MONTHS:
        rows.append([m.strftime('%Y-%m'), b, r,
                     ri(30,120), ri(5000,20000), ri(8000,30000), ri(1000,5000),
                     ri(2000,10000), ri(500,2000), ri(1000,4000), ri(3000,12000), ri(5000,20000)])

cols = ['기준월','사업소','지역','재직인원',
        '유지보수비(천원)','전기료(천원)','수도료(천원)','가스료(천원)',
        '통신비(천원)','청소용역비(천원)','차량유지비(천원)','임차료(천원)']
pd.DataFrame(rows, columns=cols).to_csv('data/사업장관리.csv', index=False, encoding='utf-8-sig')
print('1/5 사업장관리.csv OK')

# ── 2. 노무관리 ────────────────────────────────────────────
rows = []
for b, r in zip(BRANCHES, REGIONS):
    for m in MONTHS:
        total = ri(30,120)
        reg = int(total * np.random.uniform(0.80,0.90))
        rows.append([m.strftime('%Y-%m'), b, r,
                     total, reg, total-reg,
                     ri(0,8), ri(0,6), ri(3500,5500), ri(100,400), ri(50,95),
                     ri(500,2000), ri(500,1500), ri(70,100), ri(0,3)])

cols = ['기준월','사업소','지역','총인원','정규직','계약직',
        '신규채용','퇴직자','평균급여(천원)','연장근무시간','연차사용률(%)',
        '산재보험료(천원)','고용보험료(천원)','건강검진수검률(%)','노사분쟁건수']
pd.DataFrame(rows, columns=cols).to_csv('data/노무관리.csv', index=False, encoding='utf-8-sig')
print('2/5 노무관리.csv OK')

# ── 3. 산업안전보건 ────────────────────────────────────────
rows = []
for b, r in zip(BRANCHES, REGIONS):
    for m in MONTHS:
        rows.append([m.strftime('%Y-%m'), b, r,
                     ri(0,5), ri(0,4), ri(0,3), ri(80,100),
                     rc([DONE,NOT_DONE],[.9,.1]), rc([DONE,NOT_DONE],[.85,.15]),
                     ri(1,6), ri(3,15), ri(0,8),
                     rc([DONE,NOT_DONE],[.9,.1]), rc([DONE,NOT_DONE],[.95,.05])])

cols = ['기준월','사업소','지역','재해건수','부상자수','직업병자수','안전교육이수율(%)',
        '근골격계예방교육','화학물질안전교육','안전점검횟수',
        '위험요소발굴건수','개선조치완료건수','소방훈련실시','안전보호구지급']
pd.DataFrame(rows, columns=cols).to_csv('data/산업안전보건.csv', index=False, encoding='utf-8-sig')
print('3/5 산업안전보건.csv OK')

# ── 4. 에너지관리 ──────────────────────────────────────────
rows = []
for b, r in zip(BRANCHES, REGIONS):
    for m in MONTHS:
        rows.append([m.strftime('%Y-%m'), b, r,
                     ri(500,3000), ri(10000,50000), ri(10000,50000), ri(10000,50000),
                     ri(100,500), ri(1000,5000),
                     rc(['1등급','2등급','3등급','4등급','5등급']),
                     ri(80,120), ri(50,300)])

cols = ['기준월','사업소','지역',
        '도시가스사용량(천m3)','도시가스요금(천원)','전력사용량(kWh)','전기요금(천원)',
        '수도사용량(톤)','수도요금(천원)','에너지효율등급','절감목표달성률(%)','탄소배출량(tCO2)']
pd.DataFrame(rows, columns=cols).to_csv('data/에너지관리.csv', index=False, encoding='utf-8-sig')
print('4/5 에너지관리.csv OK')

# ── 5. 시설점검 ────────────────────────────────────────────
rows = []
for b, r in zip(BRANCHES, REGIONS):
    for m in MONTHS:
        rows.append([m.strftime('%Y-%m'), b, r,
                     rc(['완료','진행중','미실시']), ri(0,5), ri(0,20), ri(60,100),
                     ri(0,10), ri(0,48), rc([DONE,NOT_DONE]),
                     rc(['우수','양호','보통','미흡']), rc([DONE,NOT_DONE],[.9,.1])])

cols = ['기준월','사업소','지역','정기점검','긴급점검횟수','발견결함건수','결함조치율(%)',
        '설비고장건수','고장복구시간(시간)','일상점검실시','환경설비상태','소방시설점검']
pd.DataFrame(rows, columns=cols).to_csv('data/시설점검.csv', index=False, encoding='utf-8-sig')
print('5/5 시설점검.csv OK')

print('\n전체 완료! 각 192건 (8개 사업소 x 24개월)')
