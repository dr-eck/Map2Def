import re

def extract_function_names(idl_file_path):
    """
    Reads a .idl file and extracts function names.

    Args:
        idl_file_path (str): The path to the .idl file.

    Returns:
        list: A list of function names found in the .idl file.
    """
    function_names = []

    # Regular expression to match function definitions
    function_pattern = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(.*?\)\s*;')

    try:
        with open(idl_file_path, 'r') as file:
            for line in file:
                # Search for function definitions in the line
                match = function_pattern.search(line)
                if match:
                    # Extract the function name
                    function_signature = match.group()
                    function_name = function_signature.split('(')[0].split()[-1]
                    function_names.append(function_name)
    except FileNotFoundError:
        print(f"Error: File not found at {idl_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

        # Sort the function names alphabetically
    function_names.sort()

    return function_names

def find_decorated_function_names(map_file_path, function_names, fname, solution_name):
    """
    Finds the decorated function names for each function in the list from the .map file.

    Args:
        map_file_path (str): The path to the .map file.
        function_names (list): A list of function names to search for.
        fname (str): The file name without the .idl extension.
        solution_name (str): The solution name.

    Returns:
        dict: A dictionary mapping function names to a list of their decorated names.
    """
    decorated_names = {}
    try:
        with open(map_file_path, 'r') as file:
            lines = file.readlines()
            line_index = 0

            for func_name in function_names:
                # Create the regex pattern for the current function
                pattern_template = (
                    r'\?' + re.escape(func_name) + r'@' + re.escape(fname) +
                    r'@implementation@' + re.escape(solution_name) + r'@winrt@@.*?@Z'
                )
                pattern = re.compile(pattern_template)

                # Start scanning from the current position in the file
                decorated_list = []
                for i in range(line_index, len(lines)):
                    line = lines[i]
                    match = pattern.search(line)
                    if match:
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
    # Prompt the user for the Solution name (assuming it's the same as the project name)
    solution_name = input("Enter the Solution name (without .sln extension): ").strip()
    # Ensure the solution name does not end with .sln
    if solution_name.endswith(".sln"):
        solution_name = solution_name[:-4]
    # Define the path to the .idl file
    sln_path = "C:\\Users\\dreck\\Source\\Repos\\" + solution_name + "\\"

    # Prompt the user for the .idl file name
    idl_fname = input("Enter the .idl file name (with or without the .idl extension): ").strip()

    # Ensure the file name ends with .idl
    if not idl_fname.endswith(".idl"):
        idl_fname += ".idl"

    # Extract the file name without the .idl extension
    fname = idl_fname[:-4]

    # Create the full path to the .idl file
    idl_file_path = sln_path + solution_name + "\\" + idl_fname

    # Print the filename for confirmation
    print(f"Processing idl file: {idl_fname}")

    # Call the function to extract function names
    functions = extract_function_names(idl_file_path)
    print("Extracted function names:")
    for func in functions:
        print(func)

    # Create the map file name
    map_fname = solution_name + ".map"

    # Create the full path to the .map file
    map_file_path = sln_path + "x64\Debug\\" + solution_name + "\\" + map_fname

    # Print the filename for confirmation
    print(f"Processing map file: {map_fname}")

    decorated_functions = find_decorated_function_names(map_file_path, functions, fname, solution_name)
    print("Decorated function names:")
    for func, decorated in decorated_functions.items():
        print(f"{func}: {decorated}")