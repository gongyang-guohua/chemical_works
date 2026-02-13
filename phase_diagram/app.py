"""
相图生成应用 - Streamlit Web界面

输入物质名称，自动生成二元或三元相图
"""

import streamlit as st
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from molecule_identifier import MoleculeIdentifier
from property_predictor import PropertyPredictor
from thermodynamics import ThermodynamicsCalculator
from phase_plotter import PhasePlotter
from interactive_plotter import InteractivePhasePlotter
import matplotlib.pyplot as plt


def main():
    st.set_page_config(
        page_title="相图生成器",
        page_icon="🧪",
        layout="wide"
    )
    
    st.title("🧪 二元/三元相图生成应用")
    st.markdown("---")
    
    # 侧边栏 - 系统选择
    with st.sidebar:
        st.header("系统配置")
        
        system_type = st.radio(
            "选择体系类型",
            ["二元体系", "三元体系"],
            index=0
        )
        
        diagram_type = st.selectbox(
            "相图类型",
            ["T-x-y (汽液平衡)", "P-x-y (汽液平衡)", "三角坐标图 (仅三元)"],
            index=0
        )
        
        st.markdown("---")
        st.subheader("操作压力/温度")
        
        if "T-x-y" in diagram_type:
            pressure = st.number_input("压力 (bar)", value=1.013, min_value=0.1, max_value=10.0, step=0.1)
            temperature = None
        else:
            temperature = st.number_input("温度 (°C)", value=25.0, min_value=-50.0, max_value=200.0, step=1.0)
            pressure = None
    
    # 主界面 - 物质输入
    st.header("📝 输入物质")
    
    if system_type == "二元体系":
        col1, col2 = st.columns(2)
        
        with col1:
            comp1 = st.text_input("组分1名称", value="乙醇", help="输入化学物质名称（中文或英文）")
        
        with col2:
            comp2 = st.text_input("组分2名称", value="水", help="输入化学物质名称（中文或英文）")
        
        components = [comp1, comp2]
    
    else:  # 三元体系
        col1, col2, col3 = st.columns(3)
        
        with col1:
            comp1 = st.text_input("组分1名称", value="乙腈")
        
        with col2:
            comp2 = st.text_input("组分2名称", value="水")
        
        with col3:
            comp3 = st.text_input("组分3名称", value="四氢呋喃")
        
        components = [comp1, comp2, comp3]
    
    # 生成按钮
    if st.button("🚀 生成相图", type="primary", use_container_width=True):
        with st.spinner("正在生成相图..."):
            try:
                if system_type == "二元体系":
                    generate_binary_diagram(components, pressure, temperature, diagram_type)
                else:
                    generate_ternary_diagram(components)
            except Exception as e:
                st.error(f"❌ 生成相图时出错: {str(e)}")
                st.exception(e)


def generate_binary_diagram(components, pressure, temperature, diagram_type):
    """
    生成二元体系相图的主流程函数
    
    完整流程:
    1. 物质识别: 将化学名称转换为SMILES分子表示
    2. 性质获取: 查询或预测物化性质（沸点、临界参数等）
    3. 热力学计算: 应用NRTL模型计算汽液平衡
    4. 相图绘制: 生成交互式或静态相图
    
    Args:
        components: 组分名称列表 [comp1_name, comp2_name]
        pressure: 系统压力 (bar)
        temperature: 系统温度 (°C)
        diagram_type: 相图类型（T-x-y 或 P-x-y）
    """
    comp1_name, comp2_name = components
    
    # ========== 步骤1: 物质识别 ==========
    # 目标: 将化学名称（如"乙醇"）转换为标准的SMILES分子表示（如"CCO"）
    # SMILES是化学信息学中的通用分子表示法
    st.subheader("🔍 步骤1: 识别物质")
    identifier = MoleculeIdentifier()
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.status(f"正在识别 {comp1_name}...") as status:
            info1 = identifier.get_molecule_info(comp1_name)
            if info1:
                st.success(f"✅ {comp1_name}")
                st.code(f"SMILES: {info1['smiles']}", language="text")
                status.update(label=f"✅ 已识别 {comp1_name}", state="complete")
            else:
                st.error(f"❌ 无法识别 {comp1_name}")
                status.update(label=f"❌ 识别失败", state="error")
                return
    
    with col2:
        with st.status(f"正在识别 {comp2_name}...") as status:
            info2 = identifier.get_molecule_info(comp2_name)
            if info2:
                st.success(f"✅ {comp2_name}")
                st.code(f"SMILES: {info2['smiles']}", language="text")
                status.update(label=f"✅ 已识别 {comp2_name}", state="complete")
            else:
                st.error(f"❌ 无法识别 {comp2_name}")
                status.update(label=f"❌ 识别失败", state="error")
                return
    
    # ========== 步骤2: 获取物化性质 ==========
    # 目标: 获取热力学计算所需的关键物化性质
    # 包括: 沸点(Tb)、临界温度(Tc)、临界压力(Pc)、Antoine常数等
    st.subheader("📊 步骤2: 获取物化性质")
    predictor = PropertyPredictor()
    
    # 查询或预测两个组分的物化性质
    # 优先从本地数据库查找，如无数据则使用模型预测
    props1 = predictor.get_properties(info1['smiles'], comp1_name)
    props2 = predictor.get_properties(info2['smiles'], comp2_name)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{comp1_name}**")
        st.metric("沸点", f"{props1.get('Tb', 'N/A')} K")
        st.metric("临界温度", f"{props1.get('Tc', 'N/A')} K")
        if props1.get('_estimated'):
            st.warning("⚠️ 使用估算值")
    
    with col2:
        st.markdown(f"**{comp2_name}**")
        st.metric("沸点", f"{props2.get('Tb', 'N/A')} K")
        st.metric("临界温度", f"{props2.get('Tc', 'N/A')} K")
        if props2.get('_estimated'):
            st.warning("⚠️ 使用估算值")
    
    # ========== 步骤3: 热力学计算 ==========
    # 目标: 基于NRTL模型计算汽液平衡(VLE)关系
    # 计算原理: 改进的Raoult定律 + NRTL活度系数模型
    st.subheader("⚗️ 步骤3: 热力学计算")
    calc = ThermodynamicsCalculator()
    
    # 获取二元交互参数（τ12, τ21, α）
    # 这些参数描述了两个组分之间的分子间相互作用能
    params = calc.get_binary_parameters(info1['smiles'], info2['smiles'], "NRTL")
    
    st.info(f"NRTL参数: τ₁₂={params['tau12']:.4f}, τ₂₁={params['tau21']:.4f}, α={params['alpha']:.2f}")
    
    # 生成T-x-y相图数据
    # 在多个液相组成点(x1)上求解泡点温度(T)和对应的气相组成(y1)
    with st.spinner("正在计算相平衡..."):
        data = calc.generate_txy_diagram(props1, props2, params, P=pressure, n_points=30)
    
    # 步骤4: 绘制相图
    st.subheader("📈 步骤4: 相图结果")
    
    # 选择图表类型
    chart_type = st.radio(
        "选择图表类型",
        ["🎯 交互式图表 (推荐)", "📊 静态图表"],
        horizontal=True
    )
    
    if chart_type == "🎯 交互式图表 (推荐)":
        # 使用Plotly交互式图表
        interactive_plotter = InteractivePhasePlotter()
        fig = interactive_plotter.plot_binary_txy_interactive(data, comp1_name, comp2_name)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("✅ 交互式相图生成完成!")
        
        # 提供功能说明
        with st.expander("💡 交互功能说明"):
            st.markdown("""
            **交互式相图支持以下功能：**
            
            - 🖱️ **鼠标悬停**：显示精确的坐标和相态信息
            - 🔍 **缩放**：滚轮缩放或双击图表
            - ↔️ **平移**：拖动图表查看不同区域
            - 📦 **框选**：使用工具栏的框选工具放大特定区域
            - 📥 **导出**：点击相机图标下载高清PNG图片
            - 🔄 **重置**：点击"Home"图标恢复原始视图
            """)
        
        # 提供HTML下载
        html_str = fig.to_html(include_plotlyjs='cdn')
        st.download_button(
            label="📥 下载交互式HTML文件",
            data=html_str,
            file_name=f"{comp1_name}_{comp2_name}_interactive.html",
            mime="text/html"
        )
    
    else:
        # 使用静态matplotlib图表（保留原功能）
        plotter = PhasePlotter()
        fig = plotter.plot_binary_txy(data, comp1_name, comp2_name)
        
        st.pyplot(fig)
        
        # 提供下载
        st.download_button(
            label="📥 下载相图",
            data=save_figure_to_bytes(fig),
            file_name=f"{comp1_name}_{comp2_name}_phase_diagram.png",
            mime="image/png"
        )


def generate_ternary_diagram(components):
    """生成三元相图（简化版）"""
    st.info("三元相图功能正在开发中...")
    st.markdown("""
    三元相图需要更复杂的热力学计算，包括：
    - 多组分活度系数计算
    - 液液平衡求解
    - 连结线计算
    
    建议先使用二元体系功能。
    """)


def save_figure_to_bytes(fig):
    """将matplotlib图保存为字节流"""
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf


if __name__ == "__main__":
    main()
