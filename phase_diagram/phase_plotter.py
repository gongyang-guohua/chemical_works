"""
相图绘制模块

绘制二元和三元相图
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 支持中文显示
matplotlib.rcParams['axes.unicode_minus'] = False


class PhasePlotter:
    """相图绘制器"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
    
    def plot_binary_txy(self, data: Dict, comp1_name: str, comp2_name: str, 
                       save_path: Optional[str] = None):
        """
        绘制二元T-x-y相图
        
        Args:
            data: 包含x1, y1, T_bubble的字典
            comp1_name, comp2_name: 组分名称
            save_path: 保存路径（可选）
        """
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        
        x1 = data["x1"]
        y1 = data["y1"]
        T_bubble = data["T_bubble"] - 273.15  # 转换为摄氏度
        
        # 绘制液相线和气相线
        self.ax.plot(x1, T_bubble, 'b-', linewidth=2, label='液相线 (泡点)')
        self.ax.plot(y1, T_bubble, 'r-', linewidth=2, label='气相线 (露点)')
        
        # 填充两相区
        self.ax.fill_betweenx(T_bubble, x1, y1, alpha=0.2, color='gray', label='两相区')
        
        # 设置标签和标题
        self.ax.set_xlabel(f'{comp1_name} 摩尔分数', fontsize=12)
        self.ax.set_ylabel('温度 (°C)', fontsize=12)
        self.ax.set_title(f'{comp1_name}-{comp2_name} T-x-y 相图 (P = {data.get("P", 1.013):.3f} bar)', 
                         fontsize=14, fontweight='bold')
        
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(fontsize=10)
        
        # 设置x轴范围
        self.ax.set_xlim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相图已保存至: {save_path}")
        
        return self.fig
    
    def plot_binary_pxy(self, data: Dict, comp1_name: str, comp2_name: str,
                       save_path: Optional[str] = None):
        """
        绘制二元P-x-y相图
        
        Args:
            data: 包含x1, y1, P的字典
            comp1_name, comp2_name: 组分名称
            save_path: 保存路径（可选）
        """
        self.fig, self.ax = plt.subplots(figsize=(10, 7))
        
        x1 = data["x1"]
        y1 = data["y1"]
        P = data["P"]
        
        # 绘制液相线和气相线
        self.ax.plot(x1, P, 'b-', linewidth=2, label='液相线')
        self.ax.plot(y1, P, 'r-', linewidth=2, label='气相线')
        
        # 填充两相区
        self.ax.fill_betweenx(P, x1, y1, alpha=0.2, color='gray', label='两相区')
        
        # 设置标签和标题
        self.ax.set_xlabel(f'{comp1_name} 摩尔分数', fontsize=12)
        self.ax.set_ylabel('压力 (bar)', fontsize=12)
        self.ax.set_title(f'{comp1_name}-{comp2_name} P-x-y 相图 (T = {data.get("T", 298.15)-273.15:.1f} °C)',
                         fontsize=14, fontweight='bold')
        
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(fontsize=10)
        
        # 设置x轴范围
        self.ax.set_xlim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相图已保存至: {save_path}")
        
        return self.fig
    
    def plot_ternary_diagram(self, data: Dict, comp_names: List[str],
                           save_path: Optional[str] = None):
        """
        绘制三元相图（需要python-ternary库）
        
        Args:
            data: 三元组成数据
            comp_names: 三个组分的名称列表
            save_path: 保存路径（可选）
        """
        try:
            import ternary
        except ImportError:
            print("需要安装 python-ternary 库来绘制三元相图")
            print("运行: uv pip install python-ternary")
            return None
        
        self.fig, self.ax = plt.subplots(figsize=(10, 9))
        
        # 创建三元图
        tax = ternary.TernaryAxesSubplot(ax=self.ax, scale=100)
        
        # 设置标签
        tax.set_title(f'{comp_names[0]}-{comp_names[1]}-{comp_names[2]} 三元相图',
                     fontsize=14, fontweight='bold')
        tax.left_axis_label(f'{comp_names[1]} (%)', fontsize=12)
        tax.right_axis_label(f'{comp_names[2]} (%)', fontsize=12)
        tax.bottom_axis_label(f'{comp_names[0]} (%)', fontsize=12)
        
        # 绘制相包络线（如果有液液分离数据）
        if 'phase_boundary' in data:
            points = data['phase_boundary']
            tax.plot(points, linewidth=2, color='blue', label='相界线')
        
        # 绘制连结线（如果有）
        if 'tie_lines' in data:
            for tie_line in data['tie_lines']:
                tax.plot(tie_line, linewidth=1, color='gray', linestyle='--')
        
        # 添加网格
        tax.gridlines(multiple=10, color="gray", alpha=0.3)
        tax.boundary(linewidth=1.5)
        tax.ticks(axis='lbr', linewidth=1, multiple=10)
        
        tax.legend()
        tax.clear_matplotlib_ticks()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"三元相图已保存至: {save_path}")
        
        return self.fig


if __name__ == "__main__":
    # 测试：生成示例相图
    plotter = PhasePlotter()
    
    # 示例数据（乙醇-水）
    x1 = np.linspace(0, 1, 20)
    T_bubble = 373.15 - 21.71 * x1  # 简化的线性关系
    y1 = x1 * 1.2  # 简化的气液平衡关系
    y1[y1 > 1] = 1
    
    data = {
        "x1": x1,
        "y1": y1,
        "T_bubble": T_bubble,
        "P": 1.013
    }
    
    fig = plotter.plot_binary_txy(data, "乙醇", "水", "test_txy.png")
    print("测试相图已生成")
    plt.show()
