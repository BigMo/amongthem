# AmongThem

## How to Update
1. Download and compile the latest version of  [Il2CppInspector](https://github.com/djkaty/Il2CppInspector)
2. Load the files `Among Us_Data\il2cpp_data\Metadata\global-metadata.dat` and `GameAssembly.dll` into Il2CppInspector 
3. Under "Namespaces", click "Select all"
4. Export C# prototypes:
    1. Select "C# prototypes"
    2. Select "Single file"
    3. Export to `types.cs`
5. Export Ghidra script:
    1. Select "Python script for disassemblers"
    2. Select latest Unity version
    3. Select Ghidra
    4. Export to `il2cpp.py`
6. Download [Ghidra](https://ghidra-sre.org/) and install [Java JDK 11](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html)

tbd