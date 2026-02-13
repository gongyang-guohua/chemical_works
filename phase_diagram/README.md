# Phase Diagram Generator

这是一个二元/三元相图生成应用，能够根据化学物质名称自动生成相图。

## 功能特性

- ✅ 中英文物质名称识别
- ✅ 自动物化性质获取/预测
- ✅ NRTL活度系数模型计算
- ✅ T-x-y 二元相图绘制
- ✅ Streamlit Web交互界面
- 🚧 三元相图（开发中）

## 快速开始

### 安装依赖

```bash
uv pip install -r requirements_phase.txt
```

### 运行应用

```bash
streamlit run app.py
```

应用将在默认浏览器中打开（通常是 http://localhost:8501）

## 使用示例

### 二元体系

1. 选择"二元体系"
2. 输入组分名称，如：
   - 组分1: 乙醇
   - 组分2: 水
3. 设置压力（默认1.013 bar）
4. 点击"生成相图"

### 支持的物质

已内置常见物质数据库：
- 水、乙醇、甲醇
- 乙腈、四氢呋喃、丙酮
- 苯、甲苯
- 硫酸钠、氯化钠

其他物质会尝试从PubChem在线查询。

## 模块说明

- `molecule_identifier.py`: 物质识别与SMILES转换
- `property_predictor.py`: 物化性质获取/预测
- `thermodynamics.py`: 热力学模型与相平衡计算
- `phase_plotter.py`: 相图可视化
- `app.py`: Streamlit Web应用

## 注意事项

- 某些物质的热力学参数可能缺失，会使用估算值（精度较低）
- 二元交互参数数据库有限，未录入的体系使用默认参数
- 三元相图功能仍在开发中
