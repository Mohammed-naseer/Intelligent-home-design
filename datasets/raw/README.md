# Architectural Dataset Raw Input Directory

This folder is the **input interface** for external architectural floor-plan datasets.

The AI House Architect preprocessing pipeline reads from this folder and converts
any supported format into the canonical internal representation before training.

---

## How to Add a Public Dataset

### Option 1 — RPLAN (Recommended for Research)

RPLAN is a large-scale residential floor-plan dataset with ~80,000 annotated plans.

1. Request access at: https://github.com/zzilch/RPLAN
2. Download and extract the dataset.
3. Place the JSON or image annotation files in:

```
datasets/raw/rplan/
```

4. The preprocessing pipeline will detect and load RPLAN format automatically.

---

### Option 2 — CubiCasa5k

CubiCasa5k contains 5,000 Finnish floor plans with semantic annotations.

1. Download from: https://github.com/CubiCasa/CubiCasa5k
2. Place SVG/JSON files in:

```
datasets/raw/cubicasa5k/
```

---

### Option 3 — Custom JSON Dataset

You can also provide your own dataset in the **canonical internal format**.

Place a single `.json` file containing a list of samples:

```
datasets/raw/my_dataset.json
```

Each sample must follow this structure:

```json
{
  "sample_id": "sample_0001",
  "requirements": {
    "plot_width": 60.0,
    "plot_length": 50.0,
    "floors": 2,
    "bedrooms": 3,
    "bathrooms": 2,
    "style": "modern"
  },
  "rooms": [
    {
      "type": "living_room",
      "x": 2.0,
      "y": 2.0,
      "width": 18.0,
      "height": 14.0,
      "floor": 1
    }
  ]
}
```

Accepted room types:

```
living_room, bedroom, master_bedroom, bathroom, kitchen,
dining_room, corridor, entrance, staircase, balcony,
parking, storage, study, utility, garden
```

Many common aliases are also accepted (e.g., "foyer" → "entrance", "garage" → "parking").
See `datasets/room_vocabulary.py` for the full alias list.

---

## Without a Real Dataset

If no dataset is placed here, the system will automatically generate a **synthetic
dataset** using the rule-based `datasets/synthetic_generator.py`. This synthetic
data is sufficient to verify the full training pipeline.

To regenerate the synthetic dataset:

```powershell
python -c "from datasets.synthetic_generator import generate_dataset; generate_dataset('datasets/processed', 1000)"
```

---

## Preprocessing

After placing data here, run:

```powershell
python training/preprocess_dataset.py
python training/split_dataset.py
python training/dataset_statistics.py
```
