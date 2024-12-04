import importlib
from pathlib import Path
import re

imports = set()
datas = []
print(f'inside hook-watertap')
# add all modules to watertap modules hidden imports

# for package in ["watertap", "pyomo", "scipy", "prommis"]:
for package in ["watertap"]:
    pkg = importlib.import_module(package)
    try:
        # base_folder = Path(pkg.__path__[0])
        pkg_path = Path(pkg.__file__).parent
        base_folder = pkg_path.parent
        print("------------------importing", package, base_folder, pkg_path)
    except TypeError:  # missing __init__.py perhaps
        print(
            f"---------------Cannot find package '{package}' directory, possibly "
            f"missing an '__init__.py' file"
        )
    if not pkg_path.is_dir():
        print(
            f"--------------------Cannot load from package '{package}': "
            f"path '{pkg_path}' not a directory"
        )

    skip_expr = re.compile(r"_test|test_|__")
    print("beginning python files")
    for python_file in pkg_path.glob("**/*.py"):
        if skip_expr.search(str(python_file)):
            continue
        # print(python_file)
        relative_path = python_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()[:-3].replace("/", ".")
        module_name = package + "." + dotted_name
        try:
            module = importlib.import_module(module_name)
            imports.add(module_name)
            # print(module_name)
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{python_file}' failed: {err}")
            continue

        # ensure all parent modules are imported (a lot of repeats here but it works)
        relative_path = relative_path.parent
        while relative_path != Path("."):
            dotted_name = relative_path.as_posix().replace("/", ".")
            module_name = package + "." + dotted_name
            try:
                module = importlib.import_module(module_name)
                imports.add(module_name)
                relative_path = relative_path.parent
            except:
                relative_path = relative_path.parent
                print("error on my part")
                continue

    # add all png files to pyinstaller data
    for png_file in pkg_path.glob("**/*.png"):
        file_name = "/" + png_file.as_posix().split("/")[-1]
        # print(file_name)
        if skip_expr.search(str(png_file)):
            continue
        relative_path = png_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()
        src_name = f"{base_folder}/" + package + "/" + dotted_name
        dst_name = package + "/" + dotted_name.replace(file_name, "")
        try:
            datas.append((src_name, dst_name))
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{png_file}' failed: {err}")
            continue

    # add all yaml files to pyinstaller data
    for yaml_file in pkg_path.glob("**/*.yaml"):
        file_name = "/" + yaml_file.as_posix().split("/")[-1]
        # print(file_name)
        if skip_expr.search(str(yaml_file)):
            continue
        relative_path = yaml_file.relative_to(pkg_path)
        dotted_name = relative_path.as_posix()
        src_name = f"{base_folder}/" + package + "/" + dotted_name
        dst_name = package + "/" + dotted_name.replace(file_name, "")
        try:
            datas.append((src_name, dst_name))
        except Exception as err:  # assume the import could do bad things
            print(f"Import of file '{yaml_file}' failed: {err}")
            continue

datas.append((src_name, "watertap/core"))
hiddenimports = list(imports)