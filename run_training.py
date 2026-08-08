"""
run_training.py - Quick bootstrap script for AI House Architect
Generates synthetic dataset, trains PyTorch layout model, and trains Scikit-Learn quality model.
Run this once before starting the application for first-time setup.
"""

import sys
import os
import io

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("AI House Architect -- Model Training Bootstrap")
    print("=" * 60)

    # Step 1: Generate synthetic dataset
    print("\n[1/3] Generating synthetic architectural dataset...")
    try:
        from datasets.synthetic_generator import generate_dataset
        base_dir = os.path.dirname(os.path.abspath(__file__))
        dataset_dir = os.path.join(base_dir, "datasets", "processed")
        dataset_path = generate_dataset(dataset_dir, num_samples=400)
        print(f"      ✓ Dataset generated: {dataset_path}")
    except Exception as e:
        print(f"      ✗ Dataset generation failed: {e}")
        return

    # Step 2: Train layout model
    print("\n[2/3] Training PyTorch Layout Neural Network...")
    try:
        from training.train_layout_model import train_layout_model
        saved = train_layout_model(epochs=25)
        print(f"      ✓ Layout model saved: {saved}")
    except Exception as e:
        print(f"      ✗ Layout model training failed: {e}")
        print("      → Falling back to procedural layout generation (no PyTorch required)")

    # Step 3: Train quality model
    print("\n[3/3] Training Scikit-Learn Quality Predictor...")
    try:
        from training.train_quality_model import train_quality_model
        saved = train_quality_model()
        print(f"      ✓ Quality model saved: {saved}")
    except Exception as e:
        print(f"      ✗ Quality model training failed: {e}")
        print("      → Falling back to heuristic quality scoring (no Scikit-Learn required)")

    print("\n" + "=" * 60)
    print("Training bootstrap complete.")
    print("Start the backend server with:  python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
