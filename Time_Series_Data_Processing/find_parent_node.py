import pandas as pd

# 读取Excel文件
excel_path = rf'../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx'
df = pd.read_excel(excel_path)

# 初始化结果字典
result = []

# 从LEVEL5开始，从右向左逐列遍历
columns = ['LEVEL5', 'LEVEL4', 'LEVEL3', 'LEVEL2', 'LEVEL1']

for col in columns:
    for idx, value in enumerate(df[col]):
        if pd.isna(value):
            continue

        child_node = value
        parent_node = None

        # 从当前列的左侧列中寻找parent_node
        for left_col in df.columns[df.columns.get_loc(col) - 1::-1]:
            parent_candidates = df.loc[:idx, left_col]
            parent_candidate = parent_candidates.dropna().iloc[-1:].values
            if len(parent_candidate) > 0:
                parent_node = parent_candidate[0]
                break

        result.append({'Child Node': child_node, 'Parent Node': parent_node})

# 将结果写入到新的Excel文件中
result_df = pd.DataFrame(result)
output_path = rf'../Time_Series_Data_Processing/data_outputs/节点父节点映射.xlsx'
result_df.to_excel(output_path, index=False)

