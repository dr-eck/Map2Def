# Python script to create a .def file from .idl files so C++/WinRT can use the DLL
# This script automates the process of:
# 1. Extract function names from .idl files
# 2. Run dumpbin on the corresponding .obj files to get decorated names
# 3. Find decorated function names in the dumpbin output
# 4. Create a .def file with the extracted function names

import os
import re
import subprocess   # for running external commands

def extract_runtimeclass_functions(proj_path):
    runtimeclass_functions = {}
    runtimeclass_pattern = re.compile(r'^\s*(?:unsealed\s+)?runtimeclass\s+([a-zA-Z_][a-zA-Z0-9_]*)')
    function_pattern = re.compile(r'^\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(.*?\)\s*;')

    try:
        with open(proj_path, 'r') as file:
            current_runtimeclass = None
            inside_runtimeclass = False
            for line in file:
                # print(f"Processing line: {line.strip()}")  # Debugging output

                # Check for the start of a runtimeclass block
                runtimeclass_match = runtimeclass_pattern.match(line)
                if runtimeclass_match:
                    current_runtimeclass = runtimeclass_match.group(1)
                    runtimeclass_functions[current_runtimeclass] = []
                    inside_runtimeclass = True
                    print(f"Found runtimeclass: {current_runtimeclass}")  # Debugging output
                    continue

                # Check for the end of a runtimeclass block
                if inside_runtimeclass and re.match(r'^\s*}\s*$', line):
                    inside_runtimeclass = False
                    current_runtimeclass = None
                    print("End of runtimeclass block")  # Debugging output
                    continue

                # If inside a runtimeclass block, look for function definitions
                if inside_runtimeclass and current_runtimeclass:
                    function_match = function_pattern.match(line)
                    if function_match:
                        function_name = function_match.group(1)
                        runtimeclass_functions[current_runtimeclass].append(function_name)
                        print(f"Found function: {function_name}")  # Debugging output

            # Sort the functions for each runtimeclass
        for runtimeclass in runtimeclass_functions:
            runtimeclass_functions[runtimeclass].sort()

    except FileNotFoundError:
        print(f"Error: File not found at {proj_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return runtimeclass_functions

def run_dumpbin_on_obj(obj_path, dumpbin_path="dumpbin.exe"):
    """
    Runs dumpbin /symbols on the specified .obj file and returns the output.

    Args:
        obj_path (str): Path to the .obj file.
        dumpbin_path (str): Path to dumpbin.exe (default assumes it's in PATH).

    Returns:
        str: The output from dumpbin, or an error message.
    """
    if not os.path.exists(obj_file_path):
        print(f"ERROR: .obj file does not exist: {obj_file_path}")
    try:
        result = subprocess.run(
            [dumpbin_path, "/symbols", obj_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"dumpbin failed: {e.stderr}")
        return f"Error running dumpbin: {e.stderr}"
    except FileNotFoundError:
        return "dumpbin.exe not found. Please ensure it is in your PATH or specify the full path."

def find_decorated_function_names(dumpbin_output, runtimeclass_functions, runtimeclass_name, sln_name):
    decorated_names = {}
    for func_name in runtimeclass_functions:
        # Build a regex to match the decorated name for this function
        pattern = re.compile(
            r'(\?' + re.escape(func_name) + r'@' + re.escape(runtimeclass_name) +
            r'@implementation@' + re.escape(sln_name) + r'@winrt@@.*?Z\s)'
        )
        decorated_list = []
        for line in dumpbin_output.splitlines():
            # if '?' in line and "implementation" in line and func_name in line:
            #     print(f"LINE: {line}")
            match = pattern.search(line)
            if match:
                decorated_list.append(match.group(1))
        if decorated_list:
            decorated_names[func_name] = decorated_list
        else:
            print(f"No decorated names found for function: {func_name}")  # Debugging output
    return decorated_names

if __name__ == "__main__":
    # Prompt the user for the Solution name
    sln_name = input("Enter the Solution name (without .sln extension): ").strip()
    # Ensure the solution name does not end with .sln
    if sln_name.endswith(".sln"):
        sln_name = sln_name[:-4]

    # Prompt the user for the Project name
    project_name = input("Enter the Project name (press Enter to use the Solution name): ").strip()
    # Default the project name to the solution name if the user hits Enter
    if not project_name:
        proj_name = sln_name
    else:
        proj_name = project_name

    # Define the path to the solution file
    sln_path = "C:\\Users\\dreck\\Source\\Repos\\" + sln_name + "\\"

    # Create the full path to the project files
    proj_path = sln_path + proj_name + "\\"

    # Scan the proj_path for .idl files
    idl_files = [f for f in os.listdir(proj_path) if f.endswith(".idl")]

    if not idl_files:
        print(f"No .idl files found in {proj_path}")
        exit(1)

    # Create the .def file content
    def_file_content = []
    def_file_content.append(f"LIBRARY   {sln_name.upper()}")
    def_file_content.append("EXPORTS")

    # Process each .idl file
    for idl_file in idl_files:
        print(f"Processing idl file: {idl_file}")
        runtimeclass_functions = extract_runtimeclass_functions(proj_path + idl_file)

        # Create the full path to the .obj file
        obj_file_path = proj_path + "x64\\Debug\\" + idl_file[:-4] + ".obj"
        print(f"Looking for .obj file: {obj_file_path}")

        # Run dumpbin on the .obj file
        dumpbin_output = run_dumpbin_on_obj(obj_file_path)
        # print(f"Number of lines in dumpbin_output: {len(dumpbin_output.splitlines())}")
        # print(f"Number of characters in dumpbin_output: {len(dumpbin_output)}")
        # print(dumpbin_output[:80])

        for runtimeclass_name, functions in runtimeclass_functions.items():
            decorated_functions = find_decorated_function_names(dumpbin_output, functions, runtimeclass_name, sln_name)

            # Add decorated function names grouped by runtimeclass
            def_file_content.append(f"; Functions from runtimeclass {runtimeclass_name}")
            unique_decorated_names = set()
            for func, decorated in decorated_functions.items():
                unique_decorated_names.update(decorated)
            for name in sorted(unique_decorated_names):
                print(f" adding {name} to .def file")  # Debugging output
                def_file_content.append(f"  {name}")

    # Save the .def file in the proj_path
    def_file_path = proj_path + proj_name + ".def"
    with open(def_file_path, "w") as def_file:
        def_file.write("\n".join(def_file_content))

    # Print confirmation of the saved file
    print(f".def file saved at: {def_file_path}")
