# Chemical Works

这个工作区包含了化学工程、合成、CFD (流体力学) 和 FEA (有限元分析) 相关的 AI 模型与脚本。

## 目录结构
- `scripts/`: 包含加载模型和演示功能的 Python 脚本。
    - `load_chem_models.py`: 演示 DeepChem 和 AiZynthFinder。
    - `load_cfd_fea_models.py`: 演示 DeepXDE (PINN) 和 PhiFlow。
- `models/`: 用于存放下载的模型权重 (如 DeepChem 权重)。
- `skills/`: (预留) 包含相关的 AI 技能文件。

## 环境配置

请使用 `uv` 安装以下依赖：

```bash
pip install uv
uv pip install -r requirements.txt --system
```

## 依赖列表
- rdkit
- deepchem
- deepxde
- phiflow
- aizynthfinder
- torch
- llvmlite
- numba
