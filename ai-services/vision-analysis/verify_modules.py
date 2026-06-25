import sys
import os
import importlib.util

def load_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load spec from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def verify_modules():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    modules = {
        "gaze_tracking": "GazeTracker",
        "posture_detection": "PostureDetector", 
        "micro_expressions": "MicroExpressionDetector"
    }
    
    print(f"Checking modules in {current_dir}...")
    
    for filename, class_name in modules.items():
        file_path = os.path.join(current_dir, f"{filename}.py")
        print(f"\n--- Verifying {class_name} ({filename}.py) ---")
        
        try:
            # Load module
            mod = load_module(filename, file_path)
            print(f"[success] Module loaded")
            
            # Get class
            cls = getattr(mod, class_name)
            print(f"[success] Class {class_name} found")
            
            # Instantiate
            print(f"Attempting initialization...")
            instance = cls()
            print(f"[success] Initialized successfully")
            
            # Close
            if hasattr(instance, 'close'):
                instance.close()
                print(f"[success] Closed successfully")
                
        except Exception as e:
            print(f"[FAIL] Error verifying {filename}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_modules()
