import re
import pandas as pd

summary_file = './changwoo/predict/results_summary.txt'  # 정확한 경로 지정
output_excel = './changwoo/predict/results_summary_accuracy.xlsx'

with open(summary_file, encoding='utf-8') as f:
    lines = f.readlines()

data = []
region = None
item = None
for line in lines:
    line = line.strip()
    m = re.match(r'^--- \[(.+?) / (.+?)\] ---$', line)
    if m:
        region = m.group(1)
        item = m.group(2)
        continue

    m2 = re.match(r'^분류 정확도.*:\s*([0-9.]+)', line)
    if m2 and region and item:
        acc = float(m2.group(1))
        data.append({'지역명': region, '변수명': item, '분류 정확도(accuracy)': acc})

df = pd.DataFrame(data)
df.to_excel(output_excel, index=False)
print(f'완료! 파일 저장: {output_excel}')
