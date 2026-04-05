import m2cgen as m2c
import joblib
import os

# List of your models
models = ["USD", "GBP", "EUR", "CNY", "JPY"]

# Define where your pkl files are located
assets_dir = "assets" 

for name in models:
    model_file = os.path.join(assets_dir, f"{name}_model.pkl")
    
    if os.path.exists(model_file):
        print(f"Converting {model_file}...")
        # 1. Load the model
        model = joblib.load(model_file)
        
        # 2. Convert to pure Python code
        model_code = m2c.export_to_python(model)
        
        # 3. Save as a Python file in the root directory
        with open(f"{name}_logic.py", "w") as f:
            f.write(model_code)
        print(f"Done! {name}_logic.py created.")
    else:
        # Debugging print to show exactly where it looked
        print(f"Skipping {name}: Could not find {model_file}")

print("\nFinished! If successful, you should see .py files in your folder.")