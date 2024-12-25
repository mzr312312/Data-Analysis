import os
import requests
import pandas as pd
from datetime import datetime
import json
import sys
from tagCodes.tagcode_generator import generate_tagcodes

"""
功能说明：
该脚本用于从指定的 API 获取时间序列数据，然后对数据进行处理和分析，最后将结果保存为 Excel 文件和 JSON 格式。主要功能如下：
1. 从 API 获取时间序列数据：通过指定的起始时间和结束时间，以及 tagCodes，向 API 发送请求以获取数据。
2. 数据转换：对获取的数据进行转换，包括将布尔值转换为 1 或 0，将数值转换为浮点数，确保数据格式的一致性。
3. 数据合并：将多个 tagCodes 的数据合并为一个 DataFrame，方便后续分析。
4. 数据处理：
   - 按照 tagCode 和时间升序排列数据。
   - 使用 pandas 的 resample 方法，按照指定的粒度（以分钟为单位）对数据进行重采样，删除多余的数据行。
   - 计算每个粒度时间窗口的 tagValue 差值，并将结果添加到新的列中。
5. 数据保存：将处理后的数据保存为 Excel 文件和 pickle 文件，以便后续使用和分析。
6. diff 值的提取：将每个 tagCode 在时间序列中的 diff 值提取到一个字典中，并转换为 JSON 格式，便于进一步使用或传递给其他模块。
使用说明：
- 确保安装所需的库，主要包括 requests、pandas 和 json。
- 根据需求修改请求的 URL、时间范围、粒度（granularity_minutes）和批量请求大小（batch_size）等配置项。
注意事项：
- 在运行脚本之前，请确保网络连接正常（如不在内网，需要配置代理），以便能够成功访问 API。
- 输出文件的路径可以根据实际需要进行调整。
"""


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


# 设置请求的 URL
url = 'http://10.86.6.3:8081/japrojecttag/timeseries'

# 设置时间范围
start_time = "2024-11-22 00:00:00"
end_time = "2024-11-23 00:03:00"
granularity_minutes = 10
tagCodes = generate_tagcodes()  # 从tagcode_generator.py 导入的函数，生成tagCodes列表
# 用于存储所有 DataFrame 的列表
all_data_frames = []
# 设置每次批量请求的数据点数量
batch_size = 25

# 循环遍历 tagCodes，分批请求数据
for i in range(0, len(tagCodes), batch_size):
    batch_tagCodes = tagCodes[i:i + batch_size]
    # 创建请求体
    data = {
        "tagCodes": batch_tagCodes,
        "startTime": start_time,
        "endTime": end_time
    }
    # 发送 POST 请求
    response = requests.post(url, json=data)
    print(response)
    # 检查请求是否成功，如果不成功，打印错误信息并继续下一次循环
    if response.status_code == 200:
        # 解析 JSON 数据
        json_data = response.json()
        print(f"请求成功，响应：{json_data}")
        # print(json_data)
        # 检查 'data' 是否存在且是列表
        if json_data and 'data' in json_data and isinstance(json_data['data'], list):
            # 遍历数据列表
            for item in json_data['data']:
                timeseries_data = item.get('timeseries')
                # 确保 timeseries_data 不是 None
                if timeseries_data is not None:
                    # 将数据转换为 DataFrame
                    df = pd.DataFrame(timeseries_data)
                    # 使用转换函数处理 tagValue 列（如果是布尔值，则转换为 1 或 0，如果是数值，则转换为浮点数）
                    df['tagValue'] = df['tagValue'].apply(convert_tag_value)  # 使用自定义函数处理 tagValue
                    # 转换 time 列为 datetime
                    df['time'] = pd.to_datetime(df['time'])
                    # 添加 tagCode 列
                    df['tagCode'] = item['tagCode']  # 使用当前 item 的 tagCode

                    # 添加到总的 DataFrame 列表中
                    all_data_frames.append(df)
                else:
                    print(f"警告: tagCode {item['tagCode']} 的 timeseries 数据为空。")
        else:
            print(f"警告: 响应格式不正确或数据为空。")
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应：{response.text}")

# 合并所有 DataFrame
if all_data_frames:
    combined_df = pd.concat(all_data_frames, ignore_index=True)
    # filepath_combined_df = r"../Time_Series_Data_Processing/data_outputs/combined1.xlsx"
    # combined_df.to_excel(filepath_combined_df)
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

# 2）使用 floor 方法，精确到分钟（删掉秒）
if not combined_df.empty:
    combined_df['time'] = combined_df['time'].dt.floor('min')

# 3) 使用pandas的groupby和resample方法，按照每个tagCode的granularity_minutes的分钟粒度，删除多余的行
if not combined_df.empty:
    # 设置时间列为索引
    combined_df.set_index('time', inplace=True)

    # 按tagCode分组并重新采样
    combined_cut_df = (combined_df.groupby('tagCode')
                       .resample(f'{granularity_minutes}min')
                       .first()
                       .droplevel(0))  # 移除最外层的索引（即tagCode），仅保留时间索引

    # 重置索引，将'time'转回列
    combined_cut_df.reset_index(inplace=True)

    print("combined_cut_df=\n", combined_cut_df)

# 4) 在combined_cut_df的基础上，计算每granularity_minutes分钟的差值diff，并添加到combined_cut_df的新列diff
combined_cut_df['diff'] = combined_cut_df.groupby('tagCode')['tagValue'].diff()

# print("combined_cut_df after diff calculation=\n", combined_cut_df)

# 5）利用fillna方法填充第一行的NaN值
combined_cut_df.bfill(inplace=True)
# print("final combined_cut_df=\n", combined_cut_df)

# 获取当前时间戳
current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 定义输出文件的路径
output_file_path = f"../Time_Series_Data_Processing/data_outputs/按颗粒度{granularity_minutes}min筛选的原始数据_{current_timestamp}.xlsx"
filepath_combined_cut_df = f"../Time_Series_Data_Processing/data_outputs/combined_cut_df.pkl"
# 保存DataFrame
combined_cut_df.to_pickle(filepath_combined_cut_df)

# 保存结果到 Excel 文件
combined_cut_df.to_excel(output_file_path)
print(f"结果已保存到: {output_file_path}")

# 在计算diff值之后，定义diff_values字典
diff_values = {}

# 遍历combined_cut_df，填充diff_values字典
for index, row in combined_cut_df.iterrows():
    tag_code = row['tagCode']
    timestamp = row['time'].strftime('%Y-%m-%d %H:%M:%S')  # 将时间转换为字符串
    diff_value = row['diff']

    # 确保tagCode在字典中
    if tag_code not in diff_values:
        diff_values[tag_code] = {}

    # 将diff值添加到时间戳的字典中
    diff_values[tag_code][timestamp] = diff_value

# 转换为JSON格式
diff_values_json = json.dumps(diff_values, ensure_ascii=False)
# 保存为txt文件
# with open('diff_values.txt', 'w', encoding='utf-8') as f:
#     f.write(diff_values_json)
# 输出JSON格式的diff_values
# print("diff_values (JSON格式):", diff_values_json)

# 下面可以将diff_values_json作为接口传递给其他模块
