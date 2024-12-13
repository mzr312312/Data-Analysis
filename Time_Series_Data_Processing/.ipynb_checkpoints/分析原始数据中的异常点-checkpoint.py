import plotly.express as px
import numpy as np
import pandas as pd
from scipy import stats
import plotly.graph_objects as go
from plotly.subplots import make_subplots  # 导入 make_subplots

# 从.pkl文件读取原始数据
result_df = pd.read_pickle('result_df_electricity.pkl')
print(result_df)

# 获取不重复的tagCode并存储在列表中
tag_codes = result_df['tagCode'].unique().tolist()

# 创建一个ExcelWriter对象
with pd.ExcelWriter('tag_code_analysis.xlsx') as writer:
    # 针对每一个不重复的tagCode，生成一个dataframe，进行处理
    for tag_code in tag_codes:
        # 生成对应tagCode的数据框
        tag_df = result_df[result_df['tagCode'] == tag_code].copy()

        # 读取tagValue，新增一个diff列
        tag_df['diff'] = tag_df['tagValue'].diff().fillna(0).astype(float)

        # 计算z-score、平均值、中位数、标准差
        diff_without_first = tag_df['diff'][1:]
        z_scores = stats.zscore(diff_without_first)

        # 将Z-Score添加到DataFrame中
        tag_df['z_score'] = np.nan
        tag_df.loc[1:, 'z_score'] = z_scores

        mean_diff = np.mean(diff_without_first)
        median_diff = np.median(diff_without_first)
        std_dev_diff = np.std(diff_without_first)

        # 打印输出当前的dataframe及统计结果
        print(f"Tag Code: {tag_code}")
        print(tag_df)
        print(f"平均值: {mean_diff}, 中位数: {median_diff}, 标准差: {std_dev_diff}")
        print("=" * 50)

        # 将当前tag_df写入Excel的对应sheet
        tag_df.to_excel(writer, sheet_name=str(tag_code), index=False)

        # 使用 Plotly 绘制图表
        fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])  # 创建单个子图，带有副Y轴

        # 添加 tagValue 曲线到主坐标轴
        fig.add_trace(go.Scatter(x=tag_df['time'], y=tag_df['tagValue'], mode='lines', name='Tag Value',
                                 line=dict(color='blue')), secondary_y=False)

        # 添加 diff 曲线到副坐标轴
        fig.add_trace(go.Scatter(x=tag_df['time'], y=tag_df['diff'], mode='lines', name='Diff',
                                 line=dict(color='orange')), secondary_y=True)

        # 更新布局
        fig.update_layout(
            title=f'Tag Code: {tag_code} 变化趋势',
            xaxis_title='时间',
            legend_title='指标',
            template='plotly_white'
        )

        # 设置主坐标轴和副坐标轴的标题
        fig.update_yaxes(title_text="Tag Value", secondary_y=False)
        fig.update_yaxes(title_text="Diff", secondary_y=True)

        # 设置主坐标轴和副坐标轴的范围
        fig.update_yaxes(range=[tag_df['tagValue'].min(), tag_df['tagValue'].max()], secondary_y=False)
        fig.update_yaxes(range=[tag_df['diff'].min(), tag_df['diff'].max()], secondary_y=True)

        # 显示图表
        fig.show()
        # fig.write_image(f"{tag_code}.png")  # 保存图表为图片