"""
物质识别与SMILES转换模块

将化学物质名称转换为SMILES表示，用于后续性质预测
"""

import pubchempy as pcp
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoleculeIdentifier:
    """物质识别器，负责将化学名称转换为SMILES"""
    
    def __init__(self):
        # 常见物质的本地缓存（中英文名称映射）
        self.local_database = {
            "水": "O",
            "乙腈": "CC#N",
            "四氢呋喃": "C1CCOC1",
            "乙醇": "CCO",
            "甲醇": "CO",
            "丙酮": "CC(=O)C",
            "苯": "c1ccccc1",
            "甲苯": "Cc1ccccc1",
            "硫酸钠": "[Na+].[Na+].[O-]S(=O)(=O)[O-]",
            "氯化钠": "[Na+].[Cl-]",
            "acetonitrile": "CC#N",
            "water": "O",
            "tetrahydrofuran": "C1CCOC1",
            "ethanol": "CCO",
            "methanol": "CO",
            "sodium sulfate": "[Na+].[Na+].[O-]S(=O)(=O)[O-]",
            "sodium chloride": "[Na+].[Cl-]",
        }
    
    def get_smiles(self, substance_name: str) -> Optional[str]:
        """
        获取物质的SMILES表示
        
        Args:
            substance_name: 物质名称（中文或英文）
            
        Returns:
            SMILES字符串，如果无法识别则返回None
        """
        # 1. 先从本地缓存查找
        name_lower = substance_name.strip().lower()
        if name_lower in [k.lower() for k in self.local_database.keys()]:
            for k, v in self.local_database.items():
                if k.lower() == name_lower:
                    logger.info(f"从本地数据库找到 {substance_name}: {v}")
                    return v
        
        # 2. 从PubChem在线查询
        try:
            logger.info(f"正在从PubChem查询: {substance_name}")
            compounds = pcp.get_compounds(substance_name, 'name')
            if compounds:
                smiles = compounds[0].canonical_smiles
                logger.info(f"PubChem查询成功: {substance_name} -> {smiles}")
                return smiles
            else:
                logger.warning(f"PubChem未找到: {substance_name}")
                return None
        except Exception as e:
            logger.error(f"PubChem查询失败 {substance_name}: {e}")
            return None
    
    def get_molecule_info(self, substance_name: str) -> Optional[Dict]:
        """
        获取物质的详细信息
        
        Returns:
            包含SMILES、分子式、分子量等信息的字典
        """
        smiles = self.get_smiles(substance_name)
        if not smiles:
            return None
        
        try:
            compounds = pcp.get_compounds(smiles, 'smiles')
            if compounds:
                comp = compounds[0]
                return {
                    'name': substance_name,
                    'smiles': smiles,
                    'formula': comp.molecular_formula,
                    'molecular_weight': comp.molecular_weight,
                    'iupac_name': comp.iupac_name if hasattr(comp, 'iupac_name') else None
                }
        except Exception as e:
            logger.error(f"获取分子信息失败: {e}")
            return {'name': substance_name, 'smiles': smiles}


if __name__ == "__main__":
    # 测试
    identifier = MoleculeIdentifier()
    
    test_substances = ["水", "乙腈", "四氢呋喃", "ethanol", "硫酸钠"]
    
    for substance in test_substances:
        print(f"\n测试物质: {substance}")
        info = identifier.get_molecule_info(substance)
        if info:
            print(f"  SMILES: {info.get('smiles')}")
            print(f"  分子式: {info.get('formula')}")
            print(f"  分子量: {info.get('molecular_weight')}")
        else:
            print(f"  未找到")
