"""
此脚本的主要功能是对时间序列数据进行处理和聚合。具体步骤如下：

1. 将时间戳（timestamp）精确到分钟，并生成一个新的列'minute'。
2. 提取出每个时间戳对应的小时段，并格式化为字符串，生成新的列'hour_period'。
3. 按照小时段对'diff'列进行聚合计算，计算每个小时段内'diff'的总和，并将其重命名为'聚合值'。
4. （可选）可以添加一个日期列，记录每个小时段的日期。
5. 最后，将处理后的数据输出到Excel文件中，文件名包含当前的日期和时间。

使用说明：
- 确保原始excel文件中包含'日期'、'时间'和'diff'这三列，且日期和时间格式为'YYYY-MM-DD" "HH:MM:SS'。
- 确保输入的DataFrame（df）包含'timestamp'和'diff'这两列。
- 运行该脚本后，会在指定的目录下生成一个Excel文件，保存了按小时聚合的结果。
"""

import pandas as pd
from datetime import datetime

# 读取Excel文件
file_path = '../../../PY/Time_Series_Data_Processing/01.时间戳标准化.xlsx'
df = pd.read_excel(file_path)

# 检查并填充缺失值
df['日期'] = df['日期'].ffill()  # 使用前一个有效值填充
df['时间'] = df['时间'].fillna('00:00:00')  # 默认时间填充为00:00:00

# 将日期和时间合并为一个datetime对象，并创建新列
df['timestamp'] = pd.to_datetime(df['日期'].astype(str) + ' ' + df['时间'].astype(str), errors='coerce')

# 检查是否有无法解析的日期时间
if df['timestamp'].isnull().any():
    print("有无法解析的日期时间，请检查数据！")

# 将时间精确到分钟
df['minute'] = df['timestamp'].dt.floor('min')

# 提取小时段
df['hour_period'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:00:00')

# 按小时聚合diff列
result = df.groupby(['hour_period'], as_index=False)['diff'].sum()
result.rename(columns={'diff': '聚合值'}, inplace=True)

# # 添加日期列
# result['日期'] = pd.to_datetime(result['hour_period']).dt.date

# 输出到Excel
output_file = f'../../PY/Time_Series_Data_Processing/分钟级聚合值_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
result.to_excel(output_file, index=False)

print(f"文件已保存到：{output_file}")
