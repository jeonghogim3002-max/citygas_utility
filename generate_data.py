import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 난수 시드 설정
np.random.seed(42)

# 기본 정보
regions = ['서울', '경기', '인천', '강원', '충청', '전라', '경상']
branches = [f'{region}지사' for region in regions]
months = pd.date_range('2023-01-01', '2024-12-31', freq='MS')

# ===== 1. 사업장관리.csv =====
data_facility = []
for branch in branches:
    for month in months:
        data_facility.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '인원수': np.random.randint(30, 120),
            '유지보수비(만원)': np.random.randint(500, 2000),
            '전기료(만원)': np.random.randint(800, 3000),
            '수도료(만원)': np.random.randint(100, 500),
            '가스료(만원)': np.random.randint(200, 1000),
            '통신비(만원)': np.random.randint(50, 200),
            '청소비(만원)': np.random.randint(100, 400),
            '차량유지비(만원)': np.random.randint(300, 1200),
        })

df_facility = pd.DataFrame(data_facility)
df_facility.to_csv('data/사업장관리.csv', index=False, encoding='utf-8-sig')
print(f"✓ 사업장관리.csv 생성 ({len(df_facility)} 행)")

# ===== 2. 산업안전보건.csv =====
data_safety = []
for branch in branches:
    for month in months:
        data_safety.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '사고건수': np.random.randint(0, 5),
            '부상자수': np.random.randint(0, 4),
            '질병자수': np.random.randint(0, 3),
            '안전교육이수율(%)': np.random.randint(80, 100),
            '근골격계질환예방교육': np.random.choice(['O', 'X'], p=[0.9, 0.1]),
            '화학물질안전교육': np.random.choice(['O', 'X'], p=[0.85, 0.15]),
            '산업보건의료기관방문': np.random.randint(1, 6),
            '보유된위험요소수': np.random.randint(3, 15),
            '개선조치완료건수': np.random.randint(0, 8),
        })

df_safety = pd.DataFrame(data_safety)
df_safety.to_csv('data/산업안전보건.csv', index=False, encoding='utf-8-sig')
print(f"✓ 산업안전보건.csv 생성 ({len(df_safety)} 행)")

# ===== 3. 노무.csv =====
data_labor = []
for branch in branches:
    for month in months:
        total_employees = np.random.randint(30, 120)
        data_labor.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '총인원': total_employees,
            '정규직': int(total_employees * 0.85),
            '계약직': int(total_employees * 0.15),
            '신규채용': np.random.randint(0, 8),
            '퇴사자': np.random.randint(0, 6),
            '평균급여(만원)': np.random.randint(300, 500),
            '초과근무시간': np.random.randint(100, 400),
            '휴가사용률(%)': np.random.randint(50, 95),
            '산재보험료(만원)': np.random.randint(50, 200),
            '고용보험료(만원)': np.random.randint(50, 150),
            '건강검진수검률(%)': np.random.randint(70, 100),
        })

df_labor = pd.DataFrame(data_labor)
df_labor.to_csv('data/노무.csv', index=False, encoding='utf-8-sig')
print(f"✓ 노무.csv 생성 ({len(df_labor)} 행)")

# ===== 4. 에너지관리.csv (추가) =====
data_energy = []
for branch in branches:
    for month in months:
        data_energy.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '도시가스사용량(천m³)': np.random.randint(500, 3000),
            '도시가스요금(만원)': np.random.randint(1000, 5000),
            '전력사용량(kWh)': np.random.randint(10000, 50000),
            '전기요금(만원)': np.random.randint(1000, 5000),
            '수도사용량(톤)': np.random.randint(100, 500),
            '수도요금(만원)': np.random.randint(100, 500),
            '에너지효율등급': np.random.choice(['1등급', '2등급', '3등급', '4등급', '5등급']),
            '절감목표달성률(%)': np.random.randint(80, 120),
        })

df_energy = pd.DataFrame(data_energy)
df_energy.to_csv('data/에너지관리.csv', index=False, encoding='utf-8-sig')
print(f"✓ 에너지관리.csv 생성 ({len(df_energy)} 행)")

# ===== 5. 시설점검.csv (추가) =====
data_inspection = []
for branch in branches:
    for month in months:
        data_inspection.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '정기점검': np.random.choice(['완료', '진행중', '미시행']),
            '긴급점검': np.random.randint(0, 5),
            '발견결함건': np.random.randint(0, 20),
            '결함조치율(%)': np.random.randint(60, 100),
            '설비고장': np.random.randint(0, 10),
            '고장복구시간(시간)': np.random.randint(0, 48),
            '일일점검수행': np.random.choice(['예', '아니오']),
            '환경설비점검': np.random.choice(['우수', '양호', '보통', '미흡']),
        })

df_inspection = pd.DataFrame(data_inspection)
df_inspection.to_csv('data/시설점검.csv', index=False, encoding='utf-8-sig')
print(f"✓ 시설점검.csv 생성 ({len(df_inspection)} 행)")

# ===== 6. 환경&지속가능성.csv (추가) =====
data_env = []
for branch in branches:
    for month in months:
        data_env.append({
            '월': month.strftime('%Y-%m'),
            '사업장': branch,
            '지역': branch.replace('지사', ''),
            '폐기물배출량(톤)': np.random.randint(5, 50),
            '재활용률(%)': np.random.randint(30, 90),
            '수질배출검사': np.random.choice(['적합', '부적합']),
            '대기배출검사': np.random.choice(['적합', '부적합']),
            '소음진동검사': np.random.choice(['적합', '부적합']),
            '환경법위반': np.random.randint(0, 3),
            '환경개선비(만원)': np.random.randint(0, 500),
            'ISO14001인증': np.random.choice(['보유', '미보유']),
        })

df_env = pd.DataFrame(data_env)
df_env.to_csv('data/환경지속가능성.csv', index=False, encoding='utf-8-sig')
print(f"✓ 환경지속가능성.csv 생성 ({len(df_env)} 행)")

print("\n✅ 모든 데이터 생성 완료!")
print("\n생성된 파일:")
print("  - data/사업장관리.csv")
print("  - data/산업안전보건.csv")
print("  - data/노무.csv")
print("  - data/에너지관리.csv")
print("  - data/시설점검.csv")
print("  - data/환경지속가능성.csv")
