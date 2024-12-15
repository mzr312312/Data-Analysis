import pandas as pd

# 读取Excel文件
file_path = r'../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx'
df = pd.read_excel(file_path)

# 定义一个函数来寻找父节点
def find_parent(df, level_name, row_index):
    parent_value = None
    current_value = df.at[row_index, level_name]
    if pd.notna(current_value):
        # 直接从当前节点的左边一列向上遍历找到第一个非空的值作为父节点
        if level_name != '0级':
            left_level_name = f'{int(level_name[0]) - 1}级'
            for i in range(row_index - 1, -1, -1):
                if pd.notna(df.at[i, left_level_name]):
                    parent_value = df.at[i, left_level_name]
                    break
    return parent_value

# 初始化一个字典来存储父子关系
parent_child_map = {}

# 从“5级”到“0级”逐列遍历
for level in range(5, -1, -1):
    level_name = f'{level}级'
    for row_index, value in df[level_name].items():
        if pd.notna(value):
            parent = find_parent(df, level_name, row_index)
            # 确保当前节点在字典中
            if value not in parent_child_map:
                parent_child_map[value] = {'parent': parent, 'children': []}
            # 如果父节点存在，确保父节点在字典中
            if parent is not None:
                if parent not in parent_child_map:
                    parent_child_map[parent] = {'parent': None, 'children': []}
            # 如果父节点存在，记录当前节点为父节点的子节点
            if parent is not None and value not in parent_child_map[parent]['children']:
                parent_child_map[parent]['children'].append(value)

# 找到根节点
root_nodes = [node for node, info in parent_child_map.items() if info['parent'] is None]

# 打印根节点和父子关系
print("根节点:", root_nodes)
for node, info in parent_child_map.items():
    print(f"节点: {node}, 父节点: {info['parent']}, 子节点: {info['children']}")
