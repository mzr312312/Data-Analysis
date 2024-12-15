import pandas as pd

excel_path = rf'../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx'
node_tree = pd.read_excel (excel_path)
print(node_tree["LEVEL5"]) # test

node_tree = pd.DataFrame(data)
# print(node_tree)

for column in range(5, 0, -1):
    for index, node in node_tree[f'LEVEL{column}'].iteritems():
        # print(node)
        current_row = index
        current_column = f'LEVEL{column - 1}'
        if pd.notna(node):
            for i in range(current_row, -1, -1):
                node_parrent = node_tree.loc[current_row, current_column]
                if pd.na(node_parrent):

                elseif
                pd.notna(node_parrent):
                print(f"{node}'的父节点是'{node_parrent}")
                break
    else:
        continue