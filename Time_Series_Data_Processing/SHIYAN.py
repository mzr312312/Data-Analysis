import pandas as pd

# 定义Excel文件路径
excel_path = rf'../Time_Series_Data_Processing/data_inputs/节点父节点映射.xlsx'

# 读取Excel文件
df = pd.read_excel(excel_path)

# 打印 DataFrame 以检查数据
print("读取的Excel数据：")
print(df)

# 创建一个字典来存储树状结构
tree = {}

# 填充字典
for index, row in df.iterrows():
    node = row['node_name']
    parent = row['parent_node_name']
    if parent not in tree:
        tree[parent] = []
    tree[parent].append(node)

# 定义一个递归打印树的函数
def print_tree(node, level=0):
    indent = " " * (level * 4)  # 每层缩进4个空格
    print(f"{indent}- {node}")
    if node in tree:  # 如果当前节点有子节点，则继续打印
        for child in tree[node]:
            print_tree(child, level + 1)

# 打印树
root_nodes = [key for key in tree.keys() if key not in df['node_name'].values]
for root in root_nodes:
    print_tree(root)
