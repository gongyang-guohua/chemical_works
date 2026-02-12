import deepchem as dc
import rdkit
from rdkit import Chem
from rdkit.Chem import Draw
import torch
import os
import numpy as np

print(f"DeepChem version: {dc.__version__}")
print(f"RDKit version: {rdkit.__version__}")
print(f"PyTorch version: {torch.__version__}")

# DeepChem Demo: Solubility Prediction
print("\n--- DeepChem Demo: Solubility Prediction ---")
try:
    print("Loading Delaney dataset...")
    # Load Delaney dataset (Solubility)
    tasks, datasets, transformers = dc.molnet.load_delaney(featurizer='GraphConv')
    train_dataset, valid_dataset, test_dataset = datasets

    # Initialize model
    print("Initializing GraphConvModel...")
    model = dc.models.GraphConvModel(n_tasks=1, mode='regression', dropout=0.2)
    
    # Train for a few epochs to demonstrate
    print("Training model (this may take a moment)...")
    model.fit(train_dataset, nb_epoch=5)
    
    # Evaluate
    metric = dc.metrics.Metric(dc.metrics.pearson_r2_score)
    print("Evaluating model...")
    train_scores = model.evaluate(train_dataset, [metric], transformers)
    print(f"Train scores: {train_scores}")
    
    # Predict for a sample molecule (Aspirin)
    smiles = ['CC(=O)Oc1ccccc1C(=O)O']
    print(f"Predicting solubility for Aspirin: {smiles[0]}")
    featurizer = dc.feat.ConvMolFeaturizer()
    mol_x = featurizer.featurize(smiles)
    dataset = dc.data.NumpyDataset(mol_x)
    prediction = model.predict(dataset)
    # The output is normalized, apply inverse transform if needed, 
    # but here we just show the raw model output for demonstration
    # Ideally use transformers[0].untransform(prediction) if available
    
    real_pred = transformers[0].untransform(prediction)
    print(f"Predicted Log Solubility (LogS): {real_pred[0][0]:.4f}")

except Exception as e:
    print(f"DeepChem demo failed: {e}")
    import traceback
    traceback.print_exc()

# AiZynthFinder Check
print("\n--- AiZynthFinder Check ---")
try:
    from aizynthfinder.aizynthfinder import AiZynthFinder
    print("AiZynthFinder imported successfully.")
    print("Note: AiZynthFinder requires a 'config.yml' and policy model weights to perform actual retrosynthesis.")
    print("To use it, you need to:")
    print("1. Download the config and weights (available from AiZynthFinder documentation/repo).")
    print("2. Set up the configuration file.")
    print("3. Run: finder = AiZynthFinder(configfile='config.yml')")
except ImportError:
    print("AiZynthFinder import failed.")
except Exception as e:
    print(f"AiZynthFinder check failed: {e}")
