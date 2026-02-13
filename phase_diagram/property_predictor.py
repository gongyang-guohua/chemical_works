"""
物化性质预测模块

从多个数据源获取或预测物质的物化性质
"""

import numpy as np
from typing import Dict, Optional, List
import logging
import pubchempy as pcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PropertyPredictor:
    """物化性质预测器"""
    
    def __init__(self):
        # 常见物质的物化性质数据库（用于快速查询）
        self.property_db = {
            "O": {  # 水
                "name": "水",
                "Tb": 373.15,  # 沸点 K
                "Tc": 647.1,   # 临界温度 K
                "Pc": 220.64,  # 临界压力 bar
                "w": 0.3443,   # 偏心因子
                "antoine_A": 8.07131,
                "antoine_B": 1730.63,
                "antoine_C": 233.426,
            },
            "CCO": {  # 乙醇
                "name": "乙醇",
                "Tb": 351.44,
                "Tc": 513.9,
                "Pc": 61.48,
                "w": 0.649,
                "antoine_A": 8.20417,
                "antoine_B": 1642.89,
                "antoine_C": 230.300,
            },
            "CC#N": {  # 乙腈
                "name": "乙腈",
                "Tb": 354.75,
                "Tc": 545.5,
                "Pc": 48.3,
                "w": 0.338,
                "antoine_A": 7.33542,
                "antoine_B": 1482.29,
                "antoine_C": 250.523,
            },
            "C1CCOC1": {  # 四氢呋喃
                "name": "四氢呋喃",
                "Tb": 339.15,
                "Tc": 540.1,
                "Pc": 51.9,
                "w": 0.225,
                "antoine_A": 6.99515,
                "antoine_B": 1202.29,
                "antoine_C": 226.254,
            },
            "CO": {  # 甲醇
                "name": "甲醇",
                "Tb": 337.85,
                "Tc": 512.6,
                "Pc": 80.97,
                "w": 0.565,
                "antoine_A": 8.08097,
                "antoine_B": 1582.27,
                "antoine_C": 239.726,
            },
        }
    
    def get_properties(self, smiles: str, substance_name: str = "") -> Optional[Dict]:
        """
        获取物质的物化性质
        
        Args:
            smiles: SMILES字符串
            substance_name: 物质名称（用于显示）
            
        Returns:
            包含物化性质的字典
        """
        # 1. 先从本地数据库查找
        if smiles in self.property_db:
            logger.info(f"从本地数据库获取 {substance_name} 的性质")
            return self.property_db[smiles].copy()
        
        # 2. 尝试从PubChem获取基本性质
        try:
            logger.info(f"正在从PubChem查询 {substance_name} 的性质")
            compounds = pcp.get_compounds(smiles, 'smiles')
            if compounds:
                comp = compounds[0]
                props = {
                    "name": substance_name,
                    "molecular_weight": comp.molecular_weight,
                }
                
                # 尝试获取更多性质（PubChem可能有些数据）
                # 注意：PubChem的热力学数据有限，这里只是示例
                return props
        except Exception as e:
            logger.warning(f"从PubChem获取性质失败: {e}")
        
        # 3. 使用估算方法（简化的基团贡献法）
        logger.warning(f"{substance_name} 缺少物化性质数据，将使用估算值（精度较低）")
        return self._estimate_properties(smiles, substance_name)
    
    def _estimate_properties(self, smiles: str, name: str) -> Dict:
        """
        使用简化方法估算性质（仅作为占位符）
        实际应用中应使用PhysChemBERT等模型
        """
        # 这里仅返回示例值，实际应该调用ML模型
        return {
            "name": name,
            "Tb": 350.0,  # 默认沸点
            "Tc": 500.0,  # 默认临界温度
            "Pc": 50.0,   # 默认临界压力
            "w": 0.3,     # 默认偏心因子
            "antoine_A": 7.0,
            "antoine_B": 1200.0,
            "antoine_C": 230.0,
            "_estimated": True  # 标记为估算值
        }
    
    def calculate_vapor_pressure(self, T: float, antoine_params: Dict) -> float:
        """
        使用Antoine方程计算纯组分的饱和蒸气压
        
        Antoine方程是描述温度与蒸气压关系的半经验公式：
        log₁₀(P) = A - B / (T + C)
        
        其中:
        - A, B, C 是物质特定的Antoine常数（通过实验数据回归得到）
        - T 是温度（本方法使用摄氏度）
        - P 是饱和蒸气压（mmHg）
        
        物理意义:
        饱和蒸气压是指在给定温度下，纯物质的液相和气相达到平衡时的压力。
        温度越高，蒸气压越大，物质越容易汽化。
        
        Args:
            T: 温度 (K)
            antoine_params: Antoine参数字典，包含:
                - antoine_A: 常数A
                - antoine_B: 常数B
                - antoine_C: 常数C
            
        Returns:
            蒸气压 (bar)
        """
        # 获取Antoine常数
        A = antoine_params.get("antoine_A", 0)
        B = antoine_params.get("antoine_B", 0)
        C = antoine_params.get("antoine_C", 0)
        
        # 步骤1: 将温度从开尔文转换为摄氏度
        # Antoine方程通常使用摄氏度
        T_celsius = T - 273.15
        
        # 步骤2: 应用Antoine方程计算蒸气压的对数值
        log_P = A - B / (T_celsius + C)
        
        # 步骤3: 计算蒸气压（mmHg）
        P_mmHg = 10 ** log_P
        
        # 步骤4: 单位转换：mmHg -> bar
        # 1 bar = 750.062 mmHg
        P_bar = P_mmHg / 750.062
        
        return P_bar


if __name__ == "__main__":
    # 测试
    predictor = PropertyPredictor()
    
    test_smiles = {
        "O": "水",
        "CCO": "乙醇",
        "CC#N": "乙腈",
    }
    
    for smiles, name in test_smiles.items():
        print(f"\n{name} ({smiles}):")
        props = predictor.get_properties(smiles, name)
        if props:
            print(f"  沸点: {props.get('Tb', 'N/A')} K")
            print(f"  临界温度: {props.get('Tc', 'N/A')} K")
            print(f"  临界压力: {props.get('Pc', 'N/A')} bar")
            
            # 测试蒸气压计算
            if 'antoine_A' in props:
                T = 298.15  # 25°C
                P = predictor.calculate_vapor_pressure(T, props)
                print(f"  蒸气压(25°C): {P:.4f} bar")
