import numpy as np

class BenzeneKinetics:
    """
    苯加氢反应动力学模型 (Langmuir-Hinshelwood Mechanism)
    反应: C6H6 + 3H2 -> C6H12
    参考: Kehoe, J. P. G., & Butt, J. B. (1972). Interactions in the kinetics of benzene hydrogenation.
    """

    def __init__(self):
        # 气体常数 R (J/(mol*K))
        self.R = 8.314

        # 动力学参数 (示例值，需根据实际文献微调)
        # Pre-exponential factors
        self.k0 = 4.22e4  # mol/(g_cat * s * bar) - Adjusted for visible reaction in simulation
        self.KB0 = 1.2e-2  # 1/bar (Benzene adsorption)
        self.KH0 = 1.5e-2  # 1/bar (Hydrogen adsorption) - Note: L-H model often uses KH^0.5 or similar depending on dissociation

        # Activation Energies / Heats of Adsorption (J/mol)
        self.Ea = 55000     # Activation energy
        self.dH_B = -35000  # Heat of adsorption for Benzene (exothermic)
        self.dH_H = -40000  # Heat of adsorption for Hydrogen

    def get_rate_constant(self, T):
        """计算速率常数 k (Arrhenius Equation)"""
        return self.k0 * np.exp(-self.Ea / (self.R * T))

    def get_adsorption_constant_B(self, T):
        """计算苯的吸附平衡常数 KB (Van't Hoff Equation)"""
        # K = K0 * exp(-dH / RT)
        # 注意：吸附通常放热，dH < 0，所以 T 升高 K 降低
        return self.KB0 * np.exp(-self.dH_B / (self.R * T))

    def get_adsorption_constant_H(self, T):
        """计算氢气的吸附平衡常数 KH"""
        return self.KH0 * np.exp(-self.dH_H / (self.R * T))

    def calculate_rate(self, T, P_B, P_H, P_C=0):
        """
        计算反应速率 r
        T: 温度 (K)
        P_B: 苯分压 (bar)
        P_H: 氢气分压 (bar)
        P_C: 环己烷分压 (bar)
        
        Rate equation (Kehoe & Butt 简化形式):
        r = k * KB * P_B * (KH * P_H)^3 / (1 + KB * P_B)^{4} 
        (这里采用一种通用的 L-H 形式，假设竞争吸附主要由苯主导，或者分母项包含所有物种)
        
        修正后的常用形式 (假设 H2 解离吸附):
        r = (k * KB * P_B * (KH * P_H)^3) / (1 + KB * P_B + KH_sqrt * P_H^0.5)^4
        如果在高压下或特定催化剂，可能简化。
        在此演示中使用：
        r = k * P_B * P_H^3 / (1 + KB*P_B)^2 (示例简化 L-H)
        
        为了模拟真实性，我们使用一个较为完整的形式:
        Numerator = k * KB * P_B * KH * P_H
        Denominator = (1 + KB * P_B + KH * P_H)^2 (双位点机理示例)
        
        让我们使用一个经典的单位点模型形式:
        r = k * P_B * P_H / (1 + K_B * P_B)^2
        (注：通常苯吸附远强于氢)
        """
        k = self.get_rate_constant(T)
        KB = self.get_adsorption_constant_B(T)
        # 假设强吸附的苯主导表面位点
        
        # 速率方程: r = k * P_B * P_H / (1 + KB * P_B)^2
        # 注意单位: mol/(g_cat * s)
        rate = k * P_B * P_H**3 / (1 + KB * P_B)**2
        
        return rate
