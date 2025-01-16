import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QMenu, QAction, QLabel
)
import pyperclip  # 用于复制到剪贴板
from PyQt5.QtCore import Qt

# 读取 combined_cut_df.pkl 文件并计算 diff 的聚合值
def calculate_diff_values(pkl_file_path):
    df = pd.read_pickle(pkl_file_path)
    diff_sum = df.groupby('tagCode')['diff'].sum().round(2)  # 保留两位小数
    diff_sum.index = diff_sum.index.rename("node_id")  # 将索引名称改为 node_id
    return diff_sum.to_dict()  # 将计算结果转换为字典格式返回

# 读取时间范围
def calculate_time_range(file_path):
    df = pd.read_pickle(file_path)
    start_time = df['time'].min()
    end_time = df['time'].max()
    return {'start_time': start_time, 'end_time': end_time}

# 计算出的 diff_values 是一个字典，key 为 node_id，value 为 diff 的聚合值
diff_values = calculate_diff_values(rf'../Time_Series_Data_Processing/data_outputs/combined_cut_df-全部电表.pkl')
print("diff_values:", diff_values)

class TreeWidgetDemo(QWidget):
    def __init__(self, tree_data, node_mapping, diff_values):
        super().__init__()
        self.tree_data = tree_data
        self.node_mapping = node_mapping  # 添加节点映射关系
        self.diff_values = diff_values  # 添加 diff 值字典
        self.show_alias = False  # 默认不显示别名
        # 设置窗口默认大小为800x700
        self.resize(800, 700)
        self.initUI()

    def initUI(self):
        # 创建QTreeWidget并启用多选
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(['石家庄基地'])  # 修改标题为 "Node Name"
        self.tree.setSelectionMode(QTreeWidget.MultiSelection)  # 启用多选模式
        
        # 添加选中项变化监听
        self.tree.itemSelectionChanged.connect(self.update_selection_sum)
        
        # 创建时间显示标签
        self.start_time_label = QLabel("开始时间: ", self)
        self.start_time_label.setStyleSheet("font-weight: bold; color: black;")
        self.end_time_label = QLabel("结束时间: ", self)
        self.end_time_label.setStyleSheet("font-weight: bold; color: black;")
        self.update_time_labels()

        # 创建用于显示总和的标签
        self.sum_label = QLabel("总和: 0.00", self)
        self.sum_label.setStyleSheet("font-weight: bold; color: black;")

        # 递归构建树状结构
        self.build_tree(self.tree_data, self.tree)

        # 创建“全部展开”按钮
        self.expand_all_button = QPushButton("全部展开", self)
        self.expand_all_button.clicked.connect(self.expand_all_nodes)

        # 创建“全部收起”按钮
        self.collapse_all_button = QPushButton("全部收起", self)
        self.collapse_all_button.clicked.connect(self.collapse_all_nodes)

        # 创建“切换显示模式”按钮
        self.toggle_button = QPushButton("切换显示模式", self)
        self.toggle_button.clicked.connect(self.toggle_display_mode)

        # 创建主布局
        layout = QVBoxLayout()

        # 将时间标签和sum_label添加到左上角
        top_layout = QVBoxLayout()  # 使用垂直布局

        # 将时间标签和sum_label添加到左上角
        top_layout = QVBoxLayout()  # 使用垂直布局

        # 按顺序添加标签
        top_layout.addWidget(self.start_time_label)  # 第一行：开始时间
        top_layout.addWidget(self.end_time_label)  # 第二行：结束时间
        top_layout.addWidget(self.sum_label)  # 第三行：总和

        # 如果需要左对齐，可以设置对齐方式
        top_layout.setAlignment(Qt.AlignLeft)

        
        # 创建水平布局，用于放置其他按钮
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.expand_all_button)
        button_layout.addWidget(self.collapse_all_button)
        button_layout.addWidget(self.toggle_button)

        # 将各个布局添加到主布局
        layout.addLayout(top_layout)
        layout.addWidget(self.tree)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.setWindowTitle('TreeWidget Demo')
        self.show()

        # 连接右键菜单事件
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

    def update_time_labels(self):
        """更新时间显示标签"""
        time_range = calculate_time_range(rf'../Time_Series_Data_Processing/data_outputs/combined_cut_df-全部电表.pkl')
        start_time_str = time_range['start_time'].strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = time_range['end_time'].strftime('%Y-%m-%d %H:%M:%S')
        self.start_time_label.setText(f"开始时间: {start_time_str}")
        self.end_time_label.setText(f"结束时间: {end_time_str}")

    def build_tree(self, tree_data, parent_widget):
        """递归构建树状结构"""
        for row in tree_data:
            # 创建父节点
            parent_item = QTreeWidgetItem(parent_widget)
            node_name = row['name']
            node_id = self.node_mapping.get(node_name, '')  # 获取节点的别名

            # 根据当前显示模式设置节点文本
            if self.show_alias and node_id:
                node_text = f"{node_name} ({node_id})"  # 显示节点名称和别名
            else:
                node_text = node_name  # 只显示节点名称

            # 检查是否存在 diff 值
            if node_id in self.diff_values:
                diff_value = self.diff_values[node_id]
                node_text += f" (Diff: {diff_value})"  # 显示 diff 值

            parent_item.setText(0, node_text)

            # 递归添加子节点
            if 'children' in row:
                self.build_tree(row['children'], parent_item)

    def toggle_display_mode(self):
        """切换显示模式"""
        self.show_alias = not self.show_alias  # 切换显示别名的状态
        self.update_tree_display()  # 更新树状结构的显示内容

    def update_tree_display(self):
        """更新树状结构的显示内容，保留展开状态"""
        self.update_item_text(self.tree.invisibleRootItem())  # 从根节点开始更新

    def update_item_text(self, item):
        """递归更新节点的显示文本"""
        node_text = item.text(0)
        node_name = node_text.split(' (')[0]  # 提取节点名称
        node_id = self.node_mapping.get(node_name, '')  # 获取节点的别名

        # 根据当前显示模式设置节点文本
        if self.show_alias and node_id:
            new_text = f"{node_name} ({node_id})"  # 显示节点名称和别名
        else:
            new_text = node_name  # 只显示节点名称

        # 检查是否存在 diff 值
        if node_id in self.diff_values:
            diff_value = self.diff_values[node_id]
            new_text += f" (Diff: {diff_value})"  # 显示 diff 值

        item.setText(0, new_text)

        # 递归更新子节点的文本
        for i in range(item.childCount()):
            self.update_item_text(item.child(i))

    def expand_all_nodes(self):
        """展开树状结构中的所有节点"""
        self.tree.expandAll()

    def collapse_all_nodes(self):
        """收起树状结构中的所有节点"""
        self.tree.collapseAll()

    def update_selection_sum(self):
        """更新选中项的diff值总和"""
        selected_items = self.tree.selectedItems()
        total = 0.0
        
        for item in selected_items:
            node_text = item.text(0)
            if "(Diff:" in node_text:
                # 提取diff值
                diff_str = node_text.split("(Diff: ")[1].split(")")[0]
                total += float(diff_str)
        
        # 更新总和显示
        self.sum_label.setText(f"总和: {total:.2f} KWH")

    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree.currentItem()  # 获取当前选中的项
        if item:
            node_text = item.text(0)
            node_id = self.extract_node_id(node_text)  # 从节点文本中提取 node_id
            menu = QMenu(self.tree)
            
            if node_id:
                copy_action = QAction("复制数据点编码", self.tree)
                copy_action.triggered.connect(lambda: self.copy_to_clipboard(node_id))
                menu.addAction(copy_action)
            
            # 添加取消多选选项
            clear_action = QAction("取消多选", self.tree)
            clear_action.triggered.connect(self.clear_selection)
            menu.addAction(clear_action)
            
            menu.exec_(self.tree.viewport().mapToGlobal(position))

    def clear_selection(self):
        """清除所有选中项"""
        self.tree.clearSelection()
        self.sum_label.setText("总和: 0.00")

    def extract_node_id(self, node_text):
        """从节点文本中提取 node_id"""
        if "(" in node_text and ")" in node_text:
            return node_text.split("(")[1].split(")")[0]
        return None

    def copy_to_clipboard(self, node_id):
        """将 node_id 复制到剪贴板"""
        pyperclip.copy(node_id)
        print(f"已复制 node_id: {node_id}")

def parse_tree_structure(df):
    """解析树状结构"""
    tree = []
    current_nodes = {}

    for index, row in df.iterrows():
        # 初始化当前行的节点
        node = None

        # 从 LEVEL0 到 LEVEL5，逐层处理
        for level in range(6):  # 遍历 LEVEL0 到 LEVEL5
            level_name = f'LEVEL{level}'

            # 如果当前层级不为空
            if pd.notna(row[level_name]):
                # 创建当前层级的节点
                node = {
                    'name': row[level_name],
                    'children': []
                }

                # 如果当前层级是 LEVEL0，则将其作为根节点
                if level == 0:
                    tree.append(node)
                    current_nodes = {0: node}
                else:
                    # 如果当前层级不是 LEVEL0，则将其添加到父节点的 children 中
                    # 向上追溯到第一个不为空的父节点
                    for parent_level in range(level - 1, -1, -1):  # 从当前层级的上一级开始向上找
                        if parent_level in current_nodes:
                            current_nodes[parent_level]['children'].append(node)
                            break  # 找到父节点后跳出循环

                    # 更新当前层级的节点映射
                    current_nodes[level] = node

    return tree

def load_node_mapping(df):
    """加载节点映射关系"""
    node_mapping = {}
    for index, row in df.iterrows():
        node_name = row['node_name']
        node_id = row['node_id']

        # 将 NaN 替换为空字符串
        if pd.isna(node_id):
            node_id = ''

        node_mapping[node_name] = node_id  # 将 node_name 和 node_id 映射
    return node_mapping

if __name__ == '__main__':
    # 定义Excel文件路径
    excel_path = rf'../Time_Series_Data_Processing/data_inputs/电表结构化清单和名称映射.xlsx'

    # 读取Excel文件的"结构化清单"sheet页
    df_tree = pd.read_excel(excel_path, sheet_name='结构化清单')

    # 读取Excel文件的"映射关系"sheet页
    df_mapping = pd.read_excel(excel_path, sheet_name='映射关系')

    # 解析树状结构
    tree_data = parse_tree_structure(df_tree)

    # 加载节点映射关系
    node_mapping = load_node_mapping(df_mapping)

    # 启动PyQt应用程序
    app = QApplication(sys.argv)
    demo = TreeWidgetDemo(tree_data, node_mapping, diff_values)
    sys.exit(app.exec_())
