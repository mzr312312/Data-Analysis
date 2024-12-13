import datetime

"""
tagcode_generator.py

此脚本用于处理特定格式的标签代码。标签代码示例为：
'SJ-B-23-1-Efp-0001_AE01_F'
'SJ-B-23-9-Hvm-0056_AE01_F'
'SJ-B-23-9-Etf-0003_AE01_F'

'SJ-B-24-9-Edc-0036_AE01_F'

使用方法：
1. 将标签代码数据存储在变量 `input_data` 中，格式如示例所示，每行一个代码。
2. 运行 `tagcode_generator.py` 生成标签代码字典。
3. 在 `get_data_from_api.py` 中导入并使用生成的标签代码字典。
"""

# 当前文件内容
input_data = """
SJ-B-23-1-Efp-0001_AE01_F
SJ-B-23-9-Hvm-0056_AE01_F
"""

def generate_tagcodes(input_data=input_data):
    # 将输入数据按行分割
    input_codes = input_data.strip().split('\n')

    # 过滤掉空行
    input_codes = [code for code in input_codes if code]

    return input_codes

# 生成标签代码字典
tagCodes = generate_tagcodes()

# 获取当前时间戳，并生成文件名
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'tagCodes_{timestamp}.txt'

# print (generate_tagcodes())

# # 写入带时间戳的文件
# with open(filename, 'w') as file:
#     file.write("tagCodes = [\n")
#     for code in tagCodes:
#         file.write(f'    "{code}",\n')
#     file.write("]\n")
#
# print(f"内容已写入 {filename} 文件。")
