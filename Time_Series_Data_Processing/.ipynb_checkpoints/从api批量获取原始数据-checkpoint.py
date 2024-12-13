
import os
import requests
import pandas as pd
from datetime import datetime

# 设置请求的 URL
url = 'http://10.86.6.3:8081/japrojecttag/timeseries'

tagCodes = [
    "SJ-T-23-1-Efp-0001_AE01_F",
    "SJ-T-23-1-Efp-0002_AE01_F",
    "SJ-T-23-1-Efp-0003_AE01_F",
    "SJ-T-23-1-Efp-0004_AE01_F",
    "SJ-T-23-1-Efp-0005_AE01_F",
    "SJ-T-23-1-Efp-0006_AE01_F",
    "SJ-T-23-1-Efp-0007_AE01_F",
    "SJ-B-23-1-Efp-0001_AE01_F",
    "SJ-B-23-1-Efp-0002_AE01_F",
    "SJ-B-23-1-Efp-0003_AE01_F",
    "SJ-B-23-1-Efp-0004_AE01_F",
    "SJ-B-23-1-Efp-0005_AE01_F",
    "SJ-B-23-1-Efp-0006_AE01_F",
    "SJ-B-23-1-Efp-0007_AE01_F",
    "SJ-B-23-1-Efp-0008_AE01_F",
    "SJ-B-23-1-Efp-0009_AE01_F",
    "SJ-B-23-1-Efp-0010_AE01_F",
    "SJ-B-23-1-Efp-0011_AE01_F",
    "SJ-B-23-1-Efp-0012_AE01_F",
    "SJ-B-23-1-Efp-0013_AE01_F",
    "SJ-B-23-1-Efp-0014_AE01_F",
    "SJ-A-23-1-Efp-0001_AE01_F",
    "SJ-A-23-1-Efp-0002_AE01_F",
    "SJ-A-23-1-Efp-0003_AE01_F",
    "SJ-T-23-1-Efp-0001_AE01_F",
    "SJ-T-23-1-Efp-0002_AE01_F",
    "SJ-T-23-1-Efp-0003_AE01_F",
    "SJ-T-23-1-Efp-0004_AE01_F",
    "SJ-T-23-1-Efp-0005_AE01_F",
    "SJ-T-23-1-Efp-0006_AE01_F",
    "SJ-T-23-1-Efp-0007_AE01_F",
]
# 设置时间范围
start_time = "2024-11-10 00:00:00"
end_time = "2024-11-13 00:00:00"
granularity_minutes = 5
# 用于存储所有 DataFrame 的列表
all_data_frames = []


# 处理 tagValue 列的转换函数，将布尔值转换为 1 或 0，将数值转换为浮点数
def convert_tag_value(value):
    if isinstance(value, str):
        # 尝试将字符串转换为浮点数，如果成功则返回该浮点数
        try:
            return float(value)
        except ValueError:
            # 如果转换失败，继续判断是否为布尔值
            if value.lower() == 'true':
                return 1
            elif value.lower() == 'false':
                return 0
            else:
                return None  # 或者可以返回一个默认值，如 0

    elif isinstance(value, bool):
        return 1 if value else 0

    return float(value)  # 默认将其他情况转换为 float


# 遍历每个 tagCode
for tagCode in tagCodes:
    # 设置请求的数据
    data = {
        "tagCode": tagCode,
        "startTime": start_time,
        "endTime": end_time
    }

    # 发送 POST 请求
    response = requests.post(url, json=data)
    print(response)
    # 检查请求是否成功
    if response.status_code == 200:
        # 解析 JSON 数据
        json_data = response.json()

        # 检查 'data' 和 'timeseries' 是否存在
        if json_data and 'data' in json_data and json_data['data'] is not None:
            timeseries_data = json_data['data'].get('timeseries')

            # 确保 timeseries_data 不是 None
            if timeseries_data is not None:
                # 将数据转换为 DataFrame
                df = pd.DataFrame(timeseries_data)
                # 使用转换函数处理 tagValue 列（如果是布尔值，则转换为 1 或 0，如果是数值，则转换为浮点数）
                df['tagValue'] = df['tagValue'].apply(convert_tag_value)  # 使用自定义函数处理 tagValue
                # 转换 time 列为 datetime
                df['time'] = pd.to_datetime(df['time'])
                # 添加 tagCode 列
                df['tagCode'] = tagCode

                # 如果有时间列，进行拆分
                if 'time' in df.columns:
                    df['time'] = pd.to_datetime(df['time'])  # 转换时间为时间格式
                    df['年'] = df['time'].dt.year
                    df['月'] = df['time'].dt.month
                    df['日'] = df['time'].dt.day
                    df['时'] = df['time'].dt.hour
                    df['分'] = df['time'].dt.minute

                # 转换 tagvalue 为数字类型
                if 'tagvalue' in df.columns:
                    df['tagvalue'] = pd.to_numeric(df['tagvalue'], errors='coerce')  # 转换为数值类型

                # 添加到总的 DataFrame 列表中
                all_data_frames.append(df)
            else:
                print(f"警告: tagCode {tagCode} 的 timeseries 数据为空。")
        else:
            print(f"警告: tagCode {tagCode} 的响应格式不正确或数据为空。")
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应：{response.text}")

# 合并所有 DataFrame
if all_data_frames:
    combined_df = pd.concat(all_data_frames, ignore_index=True)
    # combined_df.to_excel("conmbined1.xlsx")
    # 验证 tagValue 列的每个值是否为 float
    is_float = combined_df['tagValue'].apply(lambda x: isinstance(x, float))
    # 把combined_df保存到excel文件
    # combined_df.to_excel("combined.xlsx")
    # 打印非 float 的值
    not_float_values = combined_df.loc[~is_float, 'tagValue']
    print("不是 float 的值有：")
    print(not_float_values)
else:
    print("没有可合并的数据。")
    combined_df = pd.DataFrame()  # 为了后续代码安全，初始化为空的DataFrame



# 1）按照 tagCode 列和 time 列升序排列
combined_df.sort_values(by=['tagCode', 'time'], inplace=True)
# combined_df.to_excel("conmbined2.xlsx")

# 2）使用 floor 方法，精确到分钟
if not combined_df.empty:
    combined_df['time'] = combined_df['time'].dt.floor('min')

# 3）创建一个combined_df的独立副本，用于后续存储删除行后的表格
combined_cut_df = combined_df.copy()
# print("combined_df=\n", combined_df)

# 4）按照时间间隔，删除指定时间间隔内的重复数据的行
# 遍历每一行，计算其与前一行的时间差
print("len(combined_cut_df))=",len(combined_cut_df))

# 初始化一个新的 DataFrame 用于保存保留的行
result_df = pd.DataFrame(columns=combined_cut_df.columns)

# 将第一行直接加入到结果 DataFrame 中
if not combined_cut_df.empty:
    result_df = pd.concat([result_df, combined_cut_df.iloc[[0]]], ignore_index=True)
    print("result_df=\n",result_df)
# 使用while循环，遍历所有行，把符合时间间隔的行加入结果 DataFrame
i = 1
print("i=",i)
while i < len(combined_cut_df):
    if 0 < i < len(combined_cut_df):
        time_diff = (combined_cut_df.iloc[i]['time'] - combined_cut_df.iloc[i-1]['time']).total_seconds() / 60

    if abs(time_diff) >= granularity_minutes:
        result_df = pd.concat([result_df, combined_cut_df.iloc[[i]]], ignore_index=True)
        i += 1
    else:
        found = False

        for j in range(i + 1, len(combined_cut_df)):
            time_diff_next = (combined_cut_df.iloc[j]['time'] - combined_cut_df.iloc[i]['time']).total_seconds() / 60
            print(f"第 {j} 行与第 {i} 行时间差为 {time_diff_next} 分钟")
            print("i,j=",i,j)
            if abs(time_diff_next) >= granularity_minutes:
                result_df = pd.concat([result_df, combined_cut_df.iloc[[j]]], ignore_index=True)
                print(f"把第{j}行加入结果")
                i = j  # 更新 i 位置到下一个要检查的行
                print(f"从第{i+1}行开始继续遍历")
                found = True
                break

        if not found:
            i += 1

# # 打印结果
# print("\n保留的时间戳：")
# for _, row in result_df.iterrows():
#     print(row['time'].strftime("%Y-%m-%d %H:%M:%S"))


# 获取当前时间戳
current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 定义输出文件的路径
output_file_path = f"../../PY/时序数据处理/按颗粒度{granularity_minutes}min筛选的原始数据_{current_timestamp}.xlsx"
# 保存DataFrame
result_df.to_pickle('result_df.pkl') # 暂时不再更新这个pkl文件
# 打印结果
# print("result_df=\n", result_df)
# 保存结果到 Excel 文件
result_df.to_excel(output_file_path)
print(f"结果已保存到: {output_file_path}")