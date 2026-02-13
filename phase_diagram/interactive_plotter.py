"""
交互式相图绘制模块（Plotly版本）

使用Plotly实现交互式二元和三元相图，支持：
- 鼠标悬停显示数据
- 缩放和平移
- 框选功能
- 多格式导出
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional


class InteractivePhasePlotter:
    """交互式相图绘制器（基于Plotly）"""
    
    def __init__(self):
        # Plotly 配置
        self.config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
            'modeBarButtonsToRemove': ['autoScale2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'phase_diagram',
                'height': 1200,
                'width': 1600,
                'scale': 2
            }
        }
    
    def plot_binary_txy_interactive(self, data: Dict, comp1_name: str, comp2_name: str) -> go.Figure:
        """
        绘制交互式二元T-x-y相图（Plotly版本）
        
        T-x-y相图展示了二元混合物在恒定压力下的汽液平衡关系：
        - 横轴: 组分1的摩尔分数 (0到1)
        - 纵轴: 温度 (°C)
        - 液相线: 泡点曲线，表示液相开始汽化的温度
        - 气相线: 露点曲线，表示气相开始冷凝的温度
        - 两相区: 液相线和气相线之间的区域，气液两相共存
        
        Args:
            data: 相图数据字典，包含:
                - x1: 液相中组分1的摩尔分数数组
                - y1: 气相中组分1的摩尔分数数组
                - T_bubble: 泡点温度数组 (K)
                - P: 系统压力 (bar)
            comp1_name: 组分1的名称（用于标签）
            comp2_name: 组分2的名称（用于标签）
            
        Returns:
            fig: Plotly交互式图形对象，支持缩放、悬停、导出等功能
        """
        # 提取数据
        x1 = data["x1"]  # 液相组成
        y1 = data["y1"]  # 气相组成
        T_bubble = data["T_bubble"] - 273.15  # 转换为摄氏度以便于阅读
        P = data.get("P", 1.013)  # 系统压力，默认1.013 bar (1 atm)
        
        # 步骤1: 创建Plotly图形对象
        fig = go.Figure()
        
        # 步骤2: 添加液相线（泡点线，蓝色）
        # 这条线表示在不同液相组成下液体开始沸腾的温度
        fig.add_trace(go.Scatter(
            x=x1,
            y=T_bubble,
            mode='lines+markers',
            name='液相线 (泡点)',
            line=dict(color='blue', width=3),
            marker=dict(size=6),
            hovertemplate=(
                f'<b>{comp1_name} 摩尔分数</b>: %{{x:.4f}}<br>' +
                '<b>温度</b>: %{y:.2f} °C<br>' +
                '<b>相态</b>: 液相<br>' +
                '<extra></extra>'
            )
        ))
        
        # 添加气相线（露点线）
        fig.add_trace(go.Scatter(
            x=y1,
            y=T_bubble,
            mode='lines+markers',
            name='气相线 (露点)',
            line=dict(color='red', width=3),
            marker=dict(size=6),
            hovertemplate=(
                f'<b>{comp1_name} 摩尔分数</b>: %{{x:.4f}}<br>' +
                '<b>温度</b>: %{y:.2f} °C<br>' +
                '<b>相态</b>: 气相<br>' +
                '<extra></extra>'
            )
        ))
        
        # 填充两相区
        fig.add_trace(go.Scatter(
            x=list(x1) + list(y1[::-1]),
            y=list(T_bubble) + list(T_bubble[::-1]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(width=0),
            name='两相区',
            hoverinfo='skip',
            showlegend=True
        ))
        
        # 更新布局
        fig.update_layout(
            title={
                'text': f'{comp1_name}-{comp2_name} T-x-y 相图 (P = {P:.3f} bar)',
                'font': {'size': 20, 'family': 'SimHei, Arial'},
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis={
                'title': {
                    'text': f'{comp1_name} 摩尔分数',
                    'font': {'size': 14, 'family': 'SimHei, Arial'}
                },
                'tickfont': {'size': 12},
                'range': [0, 1],
                'gridcolor': 'lightgray',
                'gridwidth': 0.5,
            },
            yaxis={
                'title': {
                    'text': '温度 (°C)',
                    'font': {'size': 14, 'family': 'SimHei, Arial'}
                },
                'tickfont': {'size': 12},
                'gridcolor': 'lightgray',
                'gridwidth': 0.5,
            },
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'family': 'SimHei, Arial'},
            legend={
                'font': {'size': 12},
                'x': 0.02,
                'y': 0.98,
                'bgcolor': 'rgba(255, 255, 255, 0.8)',
                'bordercolor': 'gray',
                'borderwidth': 1
            },
            width=1000,
            height=700,
            margin=dict(l=80, r=50, t=100, b=80)
        )
        
        # 添加网格
        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
        
        return fig
    
    def plot_binary_pxy_interactive(self, data: Dict, comp1_name: str, comp2_name: str) -> go.Figure:
        """
        绘制交互式二元P-x-y相图
        
        Args:
            data: 包含x1, y1, P的字典
            comp1_name, comp2_name: 组分名称
            
        Returns:
            Plotly图形对象
        """
        x1 = data["x1"]
        y1 = data["y1"]
        P = data["P"]
        T = data.get("T", 298.15)
        
        # 创建图形
        fig = go.Figure()
        
        # 添加液相线
        fig.add_trace(go.Scatter(
            x=x1,
            y=P,
            mode='lines+markers',
            name='液相线',
            line=dict(color='blue', width=3),
            marker=dict(size=6),
            hovertemplate=(
                f'<b>{comp1_name} 摩尔分数</b>: %{{x:.4f}}<br>' +
                '<b>压力</b>: %{y:.4f} bar<br>' +
                '<extra></extra>'
            )
        ))
        
        # 添加气相线
        fig.add_trace(go.Scatter(
            x=y1,
            y=P,
            mode='lines+markers',
            name='气相线',
            line=dict(color='red', width=3),
            marker=dict(size=6),
            hovertemplate=(
                f'<b>{comp1_name} 摩尔分数</b>: %{{x:.4f}}<br>' +
                '<b>压力</b>: %{y:.4f} bar<br>' +
                '<extra></extra>'
            )
        ))
        
        # 填充两相区
        fig.add_trace(go.Scatter(
            x=list(x1) + list(y1[::-1]),
            y=list(P) + list(P[::-1]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(width=0),
            name='两相区',
            hoverinfo='skip'
        ))
        
        # 更新布局
        fig.update_layout(
            title=f'{comp1_name}-{comp2_name} P-x-y 相图 (T = {T-273.15:.1f} °C)',
            xaxis_title=f'{comp1_name} 摩尔分数',
            yaxis_title='压力 (bar)',
            hovermode='closest',
            plot_bgcolor='white',
            font={'family': 'SimHei, Arial'},
            width=1000,
            height=700
        )
        
        return fig
    
    def plot_ternary_interactive(self, data: Dict, comp_names: List[str]) -> go.Figure:
        """
        绘制交互式三元相图
        
        Args:
            data: 三元组成数据
            comp_names: 三个组分的名称列表
            
        Returns:
            Plotly图形对象
        """
        # 使用Plotly的三元图
        fig = go.Figure()
        
        # 示例：添加相界线（如果有数据）
        if 'phase_boundary' in data:
            points = data['phase_boundary']
            # 转换为Plotly三元坐标
            a = [p[0] for p in points]
            b = [p[1] for p in points]
            c = [p[2] for p in points]
            
            fig.add_trace(go.Scatterternary(
                a=a, b=b, c=c,
                mode='lines+markers',
                name='相界线',
                line=dict(color='blue', width=2),
                marker=dict(size=4)
            ))
        
        # 更新三元图布局
        fig.update_layout(
            title=f'{comp_names[0]}-{comp_names[1]}-{comp_names[2]} 三元相图',
            ternary=dict(
                aaxis=dict(title=comp_names[0]),
                baxis=dict(title=comp_names[1]),
                caxis=dict(title=comp_names[2])
            ),
            font={'family': 'SimHei, Arial'},
            width=800,
            height=800
        )
        
        return fig


if __name__ == "__main__":
    # 测试交互式相图
    plotter = InteractivePhasePlotter()
    
    # 示例数据
    x1 = np.linspace(0, 1, 30)
    T_bubble = 373.15 - 21.71 * x1
    y1 = x1 * 1.2
    y1[y1 > 1] = 1
    
    data = {
        "x1": x1,
        "y1": y1,
        "T_bubble": T_bubble,
        "P": 1.013
    }
    
    fig = plotter.plot_binary_txy_interactive(data, "乙醇", "水")
    
    # 保存为HTML（可在浏览器中查看）
    fig.write_html("test_interactive_phase_diagram.html")
    print("交互式相图已生成: test_interactive_phase_diagram.html")
    
    # 也可以显示
    # fig.show()
