"""
热力学计算模块

实现VLE和LLE相平衡计算，使用NRTL、Wilson等活度系数模型
"""

import numpy as np
from scipy.optimize import fsolve, minimize
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThermodynamicsCalculator:
    """热力学计算器，用于相平衡计算"""
    
    def __init__(self):
        # 二元交互参数数据库（NRTL模型参数）
        # 格式: (comp1_smiles, comp2_smiles): {'tau12': value, 'tau21': value, 'alpha': value}
        self.nrtl_params = {
            ("CCO", "O"): {  # 乙醇-水
                "tau12": 0.8009,
                "tau21": -0.1771,
                "alpha": 0.3,
            },
            ("CC#N", "O"): {  # 乙腈-水
                "tau12": 0.5,
                "tau21": 0.3,
                "alpha": 0.3,
            },
        }
    
    def get_binary_parameters(self, smiles1: str, smiles2: str, model: str = "NRTL") -> Optional[Dict]:
        """
        获取二元交互参数
        
        Args:
            smiles1, smiles2: 两个组分的SMILES
            model: 模型类型 ("NRTL", "Wilson", 等)
            
        Returns:
            参数字典或None
        """
        if model == "NRTL":
            # 尝试正向和反向查找
            key1 = (smiles1, smiles2)
            key2 = (smiles2, smiles1)
            
            if key1 in self.nrtl_params:
                return self.nrtl_params[key1]
            elif key2 in self.nrtl_params:
                # 反向参数需要交换tau12和tau21
                params = self.nrtl_params[key2]
                return {
                    "tau12": params["tau21"],
                    "tau21": params["tau12"],
                    "alpha": params["alpha"]
                }
        
        # 如果没有找到，返回默认值
        logger.warning(f"未找到 {smiles1}-{smiles2} 的{model}参数，使用默认值")
        return {"tau12": 0.0, "tau21": 0.0, "alpha": 0.3}
    
    def nrtl_activity_coefficient(self, x: np.ndarray, tau12: float, tau21: float, alpha: float) -> Tuple[float, float]:
        """
        计算NRTL模型的活度系数（二元体系）
        
        NRTL (Non-Random Two-Liquid) 模型是用于描述非理想溶液中组分间相互作用的经典模型。
        活度系数γ反映了实际溶液与理想溶液的偏差程度。
        
        Args:
            x: 摩尔分数数组 [x1, x2]，其中 x1 + x2 = 1
            tau12, tau21: 二元交互参数，表示组分间能量相互作用
            alpha: 非随机性参数，通常取值0.2-0.47，描述分子的局部组成
            
        Returns:
            (gamma1, gamma2) 组分1和组分2的活度系数
        """
        # 提取摩尔分数
        x1, x2 = x[0], x[1]
        
        # 步骤1: 计算NRTL模型中的G参数
        # G_ij = exp(-alpha * tau_ij)
        # 这些参数反映了组分间的非随机性相互作用
        G12 = np.exp(-alpha * tau12)  # 组分1对组分2的影响因子
        G21 = np.exp(-alpha * tau21)  # 组分2对组分1的影响因子
        
        # 步骤2: 计算组分1的活度系数对数值 ln(γ1)
        # NRTL方程的完整形式，考虑了局部组成和能量参数
        ln_gamma1 = x2**2 * (tau21 * (G21 / (x1 + x2*G21))**2 + 
                             tau12 * G12 / (x2 + x1*G12)**2)
        
        # 步骤3: 计算组分2的活度系数对数值 ln(γ2)
        ln_gamma2 = x1**2 * (tau12 * (G12 / (x2 + x1*G12))**2 + 
                             tau21 * G21 / (x1 + x2*G21)**2)
        
        # 步骤4: 对数值取指数得到最终的活度系数
        # γ = exp(ln γ)
        gamma1 = np.exp(ln_gamma1)
        gamma2 = np.exp(ln_gamma2)
        
        return gamma1, gamma2
    
    def calculate_bubble_point(self, x1: float, P: float, 
                               props1: Dict, props2: Dict,
                               params: Dict) -> Tuple[float, float]:
        """
        计算泡点温度和气相组成（汽液平衡计算的核心）
        
        泡点是指在给定压力下，液相开始产生第一个气泡时的温度。
        此方法通过求解改进的Raoult定律来确定泡点温度。
        
        物理意义：
        - 泡点曲线是T-x-y相图中的液相线
        - 在泡点温度下，系统处于液相与气相的边界
        
        Args:
            x1: 液相中组分1的摩尔分数 (0 ≤ x1 ≤ 1)
            P: 系统总压力 (bar)
            props1, props2: 两个组分的物化性质字典（包含Antoine常数等）
            params: NRTL二元交互参数字典
            
        Returns:
            (T_bubble, y1) 返回泡点温度(K)和对应的气相组成
        """
        # 构建液相组成数组
        x = np.array([x1, 1-x1])
        
        def bubble_point_equation(T):
            """
            泡点方程的残差函数
            
            基于改进的Raoult定律:
            P_total = Σ(x_i * γ_i * P_i^sat)
            其中 γ_i 是活度系数，P_i^sat 是纯组分的饱和蒸气压
            """
            # 步骤1: 使用Antoine方程计算各组分在温度T下的饱和蒸气压
            P1_sat = self._antoine_pressure(T, props1)  # 组分1的饱和蒸气压
            P2_sat = self._antoine_pressure(T, props2)  # 组分2的饱和蒸气压
            
            # 步骤2: 计算NRTL活度系数
            # 活度系数反映了溶液的非理想性
            gamma1, gamma2 = self.nrtl_activity_coefficient(
                x, params["tau12"], params["tau21"], params["alpha"]
            )
            
            # 步骤3: 应用改进的Raoult定律计算理论总压
            # 理想溶液时 γ_i = 1，此时退化为经典Raoult定律
            P_calc = x[0] * gamma1 * P1_sat + x[1] * gamma2 * P2_sat
            
            # 返回残差: 理论压力与实际压力的差值
            # 求解器会寻找使残差为0的温度T
            return P_calc - P
        
        # 求解泡点温度（初始猜测：两个沸点的平均值）
        T_init = (props1.get("Tb", 350) + props2.get("Tb", 350)) / 2
        
        try:
            T_bubble = fsolve(bubble_point_equation, T_init)[0]
            
            # 计算气相组成
            P1_sat = self._antoine_pressure(T_bubble, props1)
            P2_sat = self._antoine_pressure(T_bubble, props2)
            gamma1, gamma2 = self.nrtl_activity_coefficient(
                x, params["tau12"], params["tau21"], params["alpha"]
            )
            
            y1 = x[0] * gamma1 * P1_sat / P
            
            return T_bubble, y1
        except Exception as e:
            logger.error(f"泡点计算失败: {e}")
            return T_init, x1
    
    def _antoine_pressure(self, T: float, props: Dict) -> float:
        """使用Antoine方程计算饱和蒸气压"""
        A = props.get("antoine_A", 0)
        B = props.get("antoine_B", 0)
        C = props.get("antoine_C", 0)
        
        T_celsius = T - 273.15
        log_P = A - B / (T_celsius + C)
        P_mmHg = 10 ** log_P
        P_bar = P_mmHg / 750.062
        
        return P_bar
    
    def generate_txy_diagram(self, props1: Dict, props2: Dict, 
                            params: Dict, P: float = 1.013,
                            n_points: int = 20) -> Dict:
        """
        生成T-x-y相图数据
        
        Args:
            props1, props2: 组分性质
            params: 二元交互参数
            P: 压力 (bar)
            n_points: 数据点数量
            
        Returns:
            包含x, y, T_bubble, T_dew的字典
        """
        x1_range = np.linspace(0, 1, n_points)
        
        T_bubble_list = []
        y1_list = []
        
        for x1 in x1_range:
            if x1 == 0:
                T_bubble = props2.get("Tb", 350)
                y1 = 0
            elif x1 == 1:
                T_bubble = props1.get("Tb", 350)
                y1 = 1
            else:
                T_bubble, y1 = self.calculate_bubble_point(x1, P, props1, props2, params)
            
            T_bubble_list.append(T_bubble)
            y1_list.append(y1)
        
        return {
            "x1": x1_range,
            "y1": np.array(y1_list),
            "T_bubble": np.array(T_bubble_list),
            "P": P
        }


if __name__ == "__main__":
    # 测试：计算乙醇-水体系的VLE
    calc = ThermodynamicsCalculator()
    
    # 简化的性质数据
    props_ethanol = {
        "Tb": 351.44,
        "antoine_A": 8.20417,
        "antoine_B": 1642.89,
        "antoine_C": 230.300,
    }
    
    props_water = {
        "Tb": 373.15,
        "antoine_A": 8.07131,
        "antoine_B": 1730.63,
        "antoine_C": 233.426,
    }
    
    params = calc.get_binary_parameters("CCO", "O", "NRTL")
    
    print("测试泡点计算:")
    T_b, y1 = calc.calculate_bubble_point(0.5, 1.013, props_ethanol, props_water, params)
    print(f"  x_ethanol = 0.5")
    print(f"  泡点温度: {T_b:.2f} K ({T_b-273.15:.2f} °C)")
    print(f"  y_ethanol: {y1:.4f}")
