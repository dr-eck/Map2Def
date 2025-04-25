import os
import re

def extract_runtimeclass_functions(proj_path):
    runtimeclass_functions = {}
    runtimeclass_pattern = re.compile(r'^\s*runtimeclass\s+([a-zA-Z_][a-zA-Z0-9_]*)')
    #function_pattern = re.compile(r'^\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(')
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

def find_decorated_function_names(map_file_path, runtimeclass_functions, runtimeclass_name, sln_name):
    """
    Finds the decorated function names for each function in the list from the .map file.

    Args:
        map_file_path (str): The path to the .map file.
        runtimeclass_functions (list): A list of function names to search for.
        runtimeclass_name (str): The name of the runtimeclass.
        sln_name (str): The solution name.

    Returns:
        dict: A dictionary mapping function names to a list of their decorated names.
    """
    decorated_names = {}
    try:
        with open(map_file_path, 'r') as file:
            lines = file.readlines()
            line_index = 0

            for func_name in runtimeclass_functions:
                # Debug: Print the function name being processed
                print(f"Searching for function: {func_name}")
                # Create the regex pattern for the current function
                pattern_template = (
                    r'\?' + re.escape(func_name) + r'@' + re.escape(runtimeclass_name) +
                    r'@implementation@' + re.escape(sln_name) + r'@winrt@@.*?Z '
                )
                pattern = re.compile(pattern_template)

                # Debug: Print the regex pattern being used
                # print(f"Searching for pattern: {pattern.pattern}")

                # Start scanning from the current position in the file
                decorated_list = []
                for i in range(line_index, len(lines)):
                    line = lines[i]
                    match = pattern.search(line)
                    if match:
                        # Debug: Print the match found
                        print(f"Match found: {match.group()}")
                        # Store the decorated name
                        decorated_list.append(match.group())
                        line_index = i + 1  # Move to the next line for subsequent matches
                    elif decorated_list:
                        # Stop scanning once we've moved past the adjacent matches
                        break

                # Add the list of decorated names to the dictionary
                if decorated_list:
                    decorated_names[func_name] = decorated_list
    except FileNotFoundError:
        print(f"Error: File not found at {map_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return decorated_names

# Example usage
if __name__ == "__main__":
    # # Define the path to the .idl file
    # idl_file_path = "C:/Users/dreck/Source/Repos/ImgUtilsX/ImgUtilsX/IMan.idl"

    # # Extract runtimeclass functions
    # runtimeclass_functions = extract_runtimeclass_functions(idl_file_path)

    # print(f"Extracted functions from {idl_file_path}:")

    # # print the number of runtimeclasses found
    # print(f"Number of runtimeclasses found: {len(runtimeclass_functions)}")

    # # Print the extracted functions
    # for runtimeclass, functions in runtimeclass_functions.items():
    #     print(f"Runtimeclass: {runtimeclass}")
    #     for func in functions:
    #         print(f"  {func}")

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

    # Create the map file name
    map_fname = sln_name + ".map"

    # Create the full path to the .map file
    map_file_path = sln_path + "x64\\Debug\\" + sln_name + "\\" + map_fname

    # Print the filename for confirmation
    print(f"Processing map file: {map_fname}")

    # Create the .def file content
    def_file_content = []
    def_file_content.append(f"LIBRARY   {sln_name.upper()}")
    def_file_content.append("EXPORTS")

    # Process each .idl file
    for idl_file in idl_files:
        print(f"Processing idl file: {idl_file}")
        runtimeclass_functions = extract_runtimeclass_functions(proj_path + idl_file)

        for runtimeclass_name, functions in runtimeclass_functions.items():
            decorated_functions = find_decorated_function_names(map_file_path, functions, runtimeclass_name, sln_name)

            # Add decorated function names grouped by runtimeclass
            def_file_content.append(f"; Functions from runtimeclass {runtimeclass_name}")
            unique_decorated_names = set()
            for func, decorated in decorated_functions.items():
                unique_decorated_names.update(decorated)
            for name in sorted(unique_decorated_names):
                def_file_content.append(f"  {name}")

    # Save the .def file in the proj_path
    def_file_path = proj_path + proj_name + ".def"
    with open(def_file_path, "w") as def_file:
        def_file.write("\n".join(def_file_content))

    # Print confirmation of the saved file
    print(f".def file saved at: {def_file_path}")
