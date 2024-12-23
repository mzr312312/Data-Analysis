import pandas as pd
import numpy as np
from datetime import datetime

# 读取数据
file_path = '../../../PY/Time_Series_Data_Processing/02.一列数据所处区间的计数.xlsx'
df = pd.read_excel(file_path, sheet_name=0)

# 假设数据在第一列，第一行为标题
data = df.iloc[:, 0]

# 定义区间
bins = np.arange(-10, 11, 1)  # [-10, -9), [-9, -8), ..., [9, 10)
labels = [f"[{i},{i+1})" for i in range(-10, 10)]

# 统计在每个区间内的数据
count, bin_edges = np.histogram(data, bins=bins)
interval_counts = pd.Series(count, index=labels)

# 收集每个区间内的值
interval_values = {label: data[(data >= bin_edges[i]) & (data < bin_edges[i + 1])].tolist()
                             for i, label in enumerate(labels)}

# 创建结果DataFrame
result_df = pd.DataFrame({
    '区间': labels,
    '数量': interval_counts,
})

# 将每个区间对应的值添加到DataFrame
for i, label in enumerate(labels):
    values = pd.Series(interval_values[label], name=label)
    # 将当前的值与结果DataFrame合并
    result_df = pd.concat([result_df, values], axis=1)

# 生成输出文件名
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"../../PY/Time_Series_Data_Processing/区间数量统计_{timestamp}.xlsx"

# 写入Excel文件
result_df.to_excel(output_file, index=False)

print(f"区间统计已写入文件: {output_file}")
