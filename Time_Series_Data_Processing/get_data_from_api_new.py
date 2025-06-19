import os
import requests
import pandas as pd
from datetime import datetime
import json
import sys
from tagCodes.tagcode_generator import generate_tagcodes

# 设置请求的 URL
url = 'http://10.86.6.3:8081/japrojecttag/timeseries'

# 设置时间范围
start_time = "2025-03-28 00:00:00"
end_time = "2025-03-28 01:01:00"
batch_size = 30
tagCodes = generate_tagcodes()  # 从tagcode_generator.py 导入的函数，生成tagCodes列表

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

        # 检查 'data' 是否存在且是列表
        if json_data and 'data' in json_data and isinstance(json_data['data'], list):
            # 遍历数据列表
            for item in json_data['data']:
                timeseries_data = item.get('timeseries')
                # 确保 timeseries_data 不是 None
                if timeseries_data is not None:
                    # 将数据转换为 DataFrame
                    df = pd.DataFrame(timeseries_data)

                    # 获取当前时间戳
                    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    # 定义输出文件的路径
                    output_file_path = f"{item['tagCode']}_{current_timestamp}.xlsx"

                    # 保存DataFrame到Excel文件
                    df.to_excel(output_file_path, index=False)
                    print(f"结果已保存到: {output_file_path}")
                else:
                    print(f"警告: tagCode {item['tagCode']} 的 timeseries 数据为空。")
        else:
            print(f"警告: 响应格式不正确或数据为空。")
    else:
        print(f"请求失败，状态码: {response.status_code}, 响应：{response.text}")
