"""
生成演示相图的脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from molecule_identifier import MoleculeIdentifier
from property_predictor import PropertyPredictor
from thermodynamics import ThermodynamicsCalculator
from phase_plotter import PhasePlotter


def main():
    print("=" * 60)
    print("相图生成应用 - 演示")
    print("=" * 60)
    
    # 测试体系：乙醇-水
    comp1_name = "乙醇"
    comp2_name = "水"
    
    print(f"\n测试体系: {comp1_name}-{comp2_name}")
    
    # 1. 识别物质
    print("\n[1/4] 识别物质...")
    identifier = MoleculeIdentifier()
    
    info1 = identifier.get_molecule_info(comp1_name)
    info2 = identifier.get_molecule_info(comp2_name)
    
    if not info1 or not info2:
        print("ERROR: 物质识别失败")
        return
    
    print(f"  {comp1_name}: {info1['smiles']}")
    print(f"  {comp2_name}: {info2['smiles']}")
    
    # 2. 获取物化性质
    print("\n[2/4] 获取物化性质...")
    predictor = PropertyPredictor()
    
    props1 = predictor.get_properties(info1['smiles'], comp1_name)
    props2 = predictor.get_properties(info2['smiles'], comp2_name)
    
    print(f"  {comp1_name} - 沸点: {props1.get('Tb', 'N/A')} K")
    print(f"  {comp2_name} - 沸点: {props2.get('Tb', 'N/A')} K")
    
    # 3. 热力学计算
    print("\n[3/4] 计算相平衡...")
    calc = ThermodynamicsCalculator()
    
    params = calc.get_binary_parameters(info1['smiles'], info2['smiles'], "NRTL")
    print(f"  NRTL参数: τ₁₂={params['tau12']:.4f}, τ₂₁={params['tau21']:.4f}")
    
    data = calc.generate_txy_diagram(props1, props2, params, P=1.013, n_points=30)
    
    # 4. 绘制相图
    print("\n[4/4] 绘制相图...")
    plotter = PhasePlotter()
    
    save_path = os.path.join(os.path.dirname(__file__), f"{comp1_name}_{comp2_name}_相图.png")
    fig = plotter.plot_binary_txy(data, comp1_name, comp2_name, save_path)
    
    print(f"\n✓ 相图已生成: {save_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
