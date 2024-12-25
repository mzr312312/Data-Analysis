import sys
import pandas as pd
from PyQt5.QtWidgets import QHBoxLayout, QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QPushButton, \
    QVBoxLayout, QWidget, QLabel
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget


# 读取 combined_cut_df.pkl 文件并计算 diff 的聚合值
def calculate_diff_values(file_path):
    df = pd.read_pickle(file_path)
    diff_sum = df.groupby('tagCode')['diff'].sum().round(2)  # 保留两位小数
    return diff_sum.to_dict()
# 计算出的diff_values是一个字典，key为tagCode（数据点编码），value为diff的聚合值（也就是某一个数据点在整个时间段内的总耗电量）
diff_values = calculate_diff_values(rf'../Time_Series_Data_Processing/data_outputs/combined_cut_df.pkl')
print("diff_values:", diff_values)
# 读取时间范围
def calculate_time_range(file_path):
    df = pd.read_pickle(file_path)
    start_time = df['time'].min()
    end_time = df['time'].max()
    return {'start_time': start_time, 'end_time': end_time}


# 读取数据
def load_data(file_path, diff_values):
    df = pd.read_excel(file_path, engine='openpyxl')
    nodes = df.to_dict(orient='records')
    for node in nodes:
        node['current_diff'] = diff_values.get(node['node_name'], None)
    return nodes





def collect_tree_data(tree_widget, parent_item=None, level=0):
    items = []
    for i in range(tree_widget.topLevelItemCount()):
        item = tree_widget.topLevelItem(i) if parent_item is None else parent_item.child(i)
        text = item.text(0)
        parts = text.split(':')
        node_name = parts[0].strip()
        diff_text = parts[1].strip() if len(parts) > 1 else '无'
        # 假设我们用level表示层级，可以作为额外的一列保存在Excel中
        items.append([node_name, diff_text, level])

        # 如果有子节点，递归处理
        if item.childCount() > 0:
            items.extend(collect_tree_data(tree_widget, item, level + 1))

    return items


def save_to_excel(tree_widget, file_path):
    data = collect_tree_data(tree_widget)
    df = pd.DataFrame(data, columns=['Node Name', 'Diff Value', 'Level'])
    df.to_excel(file_path, index=False)


class TreeViewApp(QMainWindow):
    def __init__(self, nodes):
        super().__init__()

        self.setWindowTitle("树状结构显示")
        self.setGeometry(500, 100, 800, 900)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # 新增3个按钮
        self.expand_all_button = QPushButton("全部展开", self)
        self.expand_all_button.clicked.connect(self.expand_all)

        self.collapse_all_button = QPushButton("全部收起", self)
        self.collapse_all_button.clicked.connect(self.collapse_all)

        self.toggle_button = QPushButton("切换显示格式", self)
        self.toggle_button.clicked.connect(self.toggle_display_format)

        # 在TreeViewApp类中添加一个方法来调用save_to_excel

        def export_to_excel(self, file_path_to_save):
            # 初始化一个空的DataFrame
            data = []

            # 定义一个递归函数来遍历树形结构
            def export_to_excel(self, file_path_to_save):
                # 初始化一个空的数据列表
                global data
                data = []

                # 开始遍历树形控件
                self.traverse_tree(self.tree_widget)

                # 创建一个DataFrame并填充数据
                df = pd.DataFrame(data, columns=[f'层级{i}' for i in range(max(len(row) for row in data))])

                # 导出到Excel
                df.to_excel(file_path_to_save, index=False)

            def traverse_tree(self, widget, level=0):
                # 遍历根节点
                for index in range(widget.topLevelItemCount()):
                    item = widget.topLevelItem(index)
                    row = [''] * (level + 1)  # 根据当前层级初始化空行
                    row[level] = item.text(0)  # 将当前项的文本放入对应的列
                    data.append(row)
                    # 递归处理子项
                    self.traverse_children(item, level + 1)

            def traverse_children(self, item, level):
                # 遍历子项
                for index in range(item.childCount()):
                    child_item = item.child(index)
                    row = [''] * (level + 1)  # 根据当前层级初始化空行
                    row[level] = child_item.text(0)  # 将子项的文本放入对应的列
                    data.append(row)
                    # 递归处理更深层级的子项
                    if child_item.childCount() > 0:
                        self.traverse_children(child_item, level + 1)

            def traverse_children(self, item, level):
                # 遍历子项
                for index in range(item.childCount()):
                    child_item = item.child(index)
                    row = [''] * (level + 1)  # 根据当前层级初始化空行
                    row[level] = child_item.text(0)  # 将子项的文本放入对应的列
                    data.append(row)
                    # 递归处理更深层级的子项
                    if child_item.childCount() > 0:
                        self.traverse_children(child_item, level + 1)

            # 开始遍历树形控件
            try:
                traverse_tree(self.tree_widget)
            except Exception as e:
                print(f"发生错误: {e}")

            # 创建一个DataFrame并填充数据
            # 使用适当的列名，如 "层级0", "层级1", "层级2", 等等
            df = pd.DataFrame(data, columns=[f'层级{i}' for i in range(max(len(row) for row in data))])

            # 导出到Excel
            df.to_excel(file_path_to_save, index=False)

        # 添加导出按钮
        self.export_button = QPushButton("导出到Excel", self)
        self.export_button.clicked.connect(lambda: export_to_excel(self, r'../../PY/Time_Series_Data_Processing/导出数据.xlsx'))
        # 添加时间显示标签
        self.start_time_label = QLabel(self)
        self.end_time_label = QLabel(self)
        self.update_time_labels()
        # 创建TreeWidget
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setHeaderLabel("节点")
        # 创建一个标签来显示选中节点的总 diff 值
        self.total_diff_label = QLabel("选中节点的总 diff 值: 0")

        # 设置为多选模式
        self.tree_widget.setSelectionMode(QTreeWidget.MultiSelection)

        # 默认显示为 node_name : diff值 的格式
        self.display_diff_format = True

        root_nodes = [node for node in nodes if pd.isna(node['parent_node_name'])]

        for root in root_nodes:
            tree = self.build_tree(nodes, root['node_name'])
            self.populate_tree_widget(tree, self.tree_widget)

        self.tree_widget.itemSelectionChanged.connect(self.update_diff_total)

        # 将时间标签添加到布局中
        self.layout.addWidget(self.start_time_label)
        self.layout.addWidget(self.end_time_label)
        # 将总 diff 值标签添加到布局中
        self.layout.addWidget(self.total_diff_label)
        # 将树状结构树添加到布局中
        self.layout.addWidget(self.tree_widget)

        # 创建一个水平布局
        h_layout_buttons = QHBoxLayout()
        # 将按钮添加到水平布局中
        h_layout_buttons.addWidget(self.expand_all_button)
        h_layout_buttons.addWidget(self.collapse_all_button)
        h_layout_buttons.addWidget(self.toggle_button)
        h_layout_buttons.addWidget(self.export_button)

        # 将水平布局添加到主布局中
        self.layout.addLayout(h_layout_buttons)

    def expand_all(self):
        self.tree_widget.expandAll()  # 展开所有节点

    def collapse_all(self):
        self.tree_widget.collapseAll()  # 收起所有节点

    def update_time_labels(self):
        time_range = calculate_time_range('data_outputs/combined_cut_df.pkl')
        start_time_str = time_range.get('start_time', '未知').strftime('%Y-%m-%d %H:%M:%S') if isinstance(
            time_range.get('start_time'), pd.Timestamp) else '未知'
        end_time_str = time_range.get('end_time', '未知').strftime('%Y-%m-%d %H:%M:%S') if isinstance(
            time_range.get('end_time'), pd.Timestamp) else '未知'
        self.start_time_label.setText(f"起始时间: {start_time_str}")
        self.end_time_label.setText(f"结束时间: {end_time_str}")

    def build_tree(self, nodes, node_name=None):
        current_node = next((node for node in nodes if node['node_name'] == node_name), None)
        if not current_node:
            return None

        # 通过 parent_node_name 来获取子节点
        children = [self.build_tree(nodes, child['node_name']) for child in nodes if
                    child['parent_node_name'] == current_node['node_name']]

        current_diff = diff_values.get(current_node['node_name'], None)  # 如果需要 diff 值，则需要进行相应修改

        return {
            'node_name': current_node['node_name'],
            'children': children,
            'diff': current_diff
        }


    def populate_tree_widget(self, tree, parent_widget):
        if tree is None:
            return

        if self.display_diff_format:
            display_text = f"{tree['node_name']} : {tree['diff'] if tree['diff'] is not None else '无'}"
        else:
            display_text = f"{tree['node_name']} (ID: {tree['node_name']}) : {tree['diff']:.2f}KWH" if tree['diff'] is not None else f"{tree['node_name']} (ID: {tree['node_name']}) : 无"

        item = QTreeWidgetItem(parent_widget, [display_text])
        for child in tree['children']:
            self.populate_tree_widget(child, item)

    def update_diff_total(self):
        total_diff = 0
        for item in self.tree_widget.selectedItems():
            text = item.text(0)
            parts = text.split(':')
            if len(parts) > 1:
                diff_text = parts[1].strip()
                if diff_text != '无':
                    total_diff += float(diff_text.split()[0])
        self.total_diff_label.setText(f"选中节点的总 diff 值: {total_diff:.2f}")

    def toggle_display_format(self):
        self.display_diff_format = not self.display_diff_format
        self.tree_widget.clear()
        root_nodes = [node for node in load_data('../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx') if
                      pd.isna(node['parent_node_name'])]
        for root in root_nodes:
            tree = self.build_tree(load_data('../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx'), root['node_name'])
            self.populate_tree_widget(tree, self.tree_widget)


def load_data(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    return df.to_dict(orient='records')


if __name__ == '__main__':
    file_path = 'data_inputs/节点父节点映射.xlsx'
    nodes = load_data(file_path)

    app = QApplication(sys.argv)
    window = TreeViewApp(nodes)
    window.show()
    sys.exit(app.exec_())
