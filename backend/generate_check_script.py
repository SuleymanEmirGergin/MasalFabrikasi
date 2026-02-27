
import re
import os

source_file = "app/routers/story_advanced_features.py"
output_file = "check_advanced_deps.py"

with open(source_file, "r", encoding="utf-8") as f:
    content = f.read()

imports = re.findall(r"from (app\.services\.[\w_]+) import (\w+)", content)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("import sys\nimport os\nimport traceback\nimport importlib\n\n")
    f.write("sys.path.append(os.getcwd())\n\n")
    f.write("services = [\n")
    for module, cls in imports:
        f.write(f'    ("{module}", "{cls}"),\n')
    f.write("]\n\n")
    f.write('print("🔍 Checking Advanced Services Instantiation...")\n\n')
    f.write("for module_name, class_name in services:\n")
    f.write('    print(f"👉 Checking {class_name} ({module_name})...", end=" ", flush=True)\n')
    f.write("    try:\n")
    f.write("        module = importlib.import_module(module_name)\n")
    f.write("        cls = getattr(module, class_name)\n")
    f.write("        instance = cls()\n")
    f.write('        print("✅ OK")\n')
    f.write("    except Exception as e:\n")
    f.write('        print("❌ FAILED")\n')
    f.write('        print(f"\\nCRITICAL ERROR in {class_name}:")\n')
    f.write("        traceback.print_exc()\n")
    f.write("        break\n")

print(f"Generated {output_file} with {len(imports)} services.")
