import os
from huggingface_hub import snapshot_download

# 定义要下载的模型与数据库列表
models = [
    "hkqiu/PolyNC",                          # 高分子属性预测
    "ibm-research/MoLFormer-XL-both-10pct",        # 通用化学语言模型
    "dptech/Uni-Mol-Model-SMILES",             # 3D 分子表示框架
    "yisun/PhysChemBERT",                    # 物化性质预测模型
    "AI4Chem/ChemLLM-7B-Chat",               # 专业的化学大语言模型（知识库）
]

datasets = [
    "kms7530/chemeng",                       # 化工数据集集锦（包含 VLE 等）
]

def download_models():
    print("开始下载化学与化工相关大模型及数据库...")
    
    # 下载模型
    for model_id in models:
        try:
            print(f"正在下载模型: {model_id}...")
            path = snapshot_download(repo_id=model_id)
            print(f"模型下载成功! 本地路径: {path}")
        except Exception as e:
            print(f"模型下载失败: {model_id}. 错误信息: {e}")
            
    # 下载数据集
    from huggingface_hub import snapshot_download
    for dataset_id in datasets:
        try:
            print(f"正在下载数据集: {dataset_id}...")
            # 对于数据集，同样使用 snapshot_download，但 repo_type 指定为 dataset
            path = snapshot_download(repo_id=dataset_id, repo_type="dataset")
            print(f"数据集下载成功! 本地路径: {path}")
        except Exception as e:
            print(f"数据集下载失败: {dataset_id}. 错误信息: {e}")

if __name__ == "__main__":
    download_models()
