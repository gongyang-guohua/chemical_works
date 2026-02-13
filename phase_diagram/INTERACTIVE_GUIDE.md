# 相图应用使用演示

## 启动应用

```bash
cd f:\chemical_works\phase_diagram
streamlit run app.py
```

## 交互式相图功能

### 1. 生成相图

1. 输入物质名称（如：乙醇、水）
2. 设置压力（默认1.013 bar）
3. 选择 **"🎯 交互式图表 (推荐)"**
4. 点击"生成相图"

### 2. 交互操作

#### 🖱️ 鼠标悬停
将鼠标移动到图表上的任意点，会显示：
- 精确的摩尔分数
- 对应的温度
- 相态信息（液相/气相）

#### 🔍 缩放
- **方法1**: 使用鼠标滚轮
- **方法2**: 双击图表恢复原始视图
- **方法3**: 使用工具栏的放大/缩小按钮

#### ↔️ 平移
- 点击并拖动图表查看不同区域

#### 📦 框选放大
1. 点击工具栏的"Box Select"或"Lasso Select"
2. 在图表上框选感兴趣的区域
3. 松开鼠标自动放大到该区域

#### 📥 导出
- **PNG图片**: 点击工具栏的相机图标
- **交互式HTML**: 点击"下载交互式HTML文件"按钮

#### 🔄 重置视图
点击工具栏的"Home"图标恢复原始视图

## 命令行演示

也可以直接运行演示脚本：

```bash
python phase_diagram/demo.py
```

或生成交互式HTML：

```bash
python phase_diagram/interactive_plotter.py
```

这将生成 `test_interactive_phase_diagram.html`，可在任意浏览器中打开查看。
