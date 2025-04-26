Python script for creating a .def file so C++/WinRT projects will export functions (ctors soon!).
1. Scans the project folder for .idl files
2. Reads each one and creates a list of functions
3. Scans the .map file (which must exist!!!) for the decorated method names
4. Adds the decorated method names to a .def file
5. Saves the .def file over any that exists in the project folder

To create a .map file:
1. turn on the switch in the Linker | All options
2. enter a name for the .map file; <project name>.map is assumed
