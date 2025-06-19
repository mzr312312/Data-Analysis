import requests
import pandas as pd
from datetime import datetime

# 配置参数
batch_size = 20  # 每批次的 tagCodes 数量（可调整）
output_file_sjz = "shijiazhuang_data.xlsx"  # 石家庄基地的输出文件名
output_file_yz = "yangzhou_data.xlsx"  # 扬州基地的输出文件名

# 石家庄基地配置
sjz_url = 'http://10.86.6.3:8081/japrojecttag/timeseries'
sjz_start_time = "2025-03-28 00:00:00"
sjz_end_time = "2025-03-28 00:11:00"
sjz_tagCodes = [
    "SJ-T-99-9-Edc-0103_AE01_F",
    "SJ-T-99-9-Edc-0104_AE01_F",
    "SJ-T-99-9-Edc-0124_AE01_F",
    # 添加更多 tagCodes...
]

# 扬州基地配置
yz_url = "http://localhost:8081/japrojecttag/timeseries"
yz_start_time = "2025-03-28 00:00:00"
yz_end_time = "2025-03-28 00:11:00"
yz_tagCodes = [
    "SJ-T-99-9-Edc-0103_AE01_F",
    "SJ-T-99-9-Edc-0104_AE01_F",
    "SJ-T-99-9-Edc-0124_AE01_F",
    # 添加更多 tagCodes...
]


def fetch_data(url, start_time, end_time, tagCodes):
    """
    从 API 获取时序数据。
    :param url: API 的 URL
    :param start_time: 起始时间
    :param end_time: 结束时间
    :param tagCodes: tagCode 列表
    :return: 数据列表
    """
    data_list = []
    # 将 tagCodes 分成多个批次
    for i in range(0, len(tagCodes), batch_size):
        batch_tagCodes = tagCodes[i:i + batch_size]
        payload = {
            "start_time": start_time,
            "end_time": end_time,
            "tagCodes": batch_tagCodes
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()  # 检查请求是否成功
            batch_data = response.json()
            if isinstance(batch_data, list):  # 确保返回的是列表
                data_list.extend(batch_data)
            else:
                print(f"警告：API 返回的数据不是列表，跳过该批次。返回内容：{batch_data}")
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
    return data_list


def save_to_excel(data, filename):
    """
    将数据保存为 Excel 文件。
    :param data: 数据列表
    :param filename: 输出文件名
    """
    if not data:
        print(f"没有数据可保存到 {filename}")
        return

    # 检查数据格式
    valid_data = []
    for item in data:
        if isinstance(item, dict) and all(key in item for key in ["tagCode", "time", "tagValue"]):
            valid_data.append(item)
        else:
            print(f"警告：跳过无效数据项：{item}")

    if not valid_data:
        print(f"没有有效数据可保存到 {filename}")
        return

    # 将数据转换为 DataFrame
    df = pd.DataFrame(valid_data, columns=["tagCode", "time", "tagValue"])
    # 确保 time 列是 datetime 类型
    df['time'] = pd.to_datetime(df['time'])
    # 保存为 Excel 文件
    df.to_excel(filename, index=False)
    print(f"数据已保存到 {filename}")


def main():
    # 获取石家庄基地数据
    print("正在获取石家庄基地数据...")
    sjz_data = fetch_data(sjz_url, sjz_start_time, sjz_end_time, sjz_tagCodes)
    save_to_excel(sjz_data, output_file_sjz)

    # 获取扬州基地数据
    print("正在获取扬州基地数据...")
    yz_data = fetch_data(yz_url, yz_start_time, yz_end_time, yz_tagCodes)
    save_to_excel(yz_data, output_file_yz)


if __name__ == "__main__":
    main()