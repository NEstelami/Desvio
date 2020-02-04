# NOTE: This has only been tested with the PowerPC version of GCC 8.2.0 packaged with devkitPPC

import struct
import sys
from GC_Shared import *

# Removes comments, and spaces at the beginning of a line, and returns the result.
def CleanupLine(inputLine):
    outputLine = ""

    for i in range(len(inputLine)):
        lineChar = inputLine[i]
        
        if (lineChar == "/"):
            if (i < len(inputLine) - 1):
                break
        
        outputLine += lineChar

    while (outputLine.startswith(" ")):
        outputLine = outputLine[1:]

    return outputLine

# Returns a dictionary of symbols from a GCC Linker Map File.
# Key = Symbol Name, Value = Symbol Address
def GetSymbols(mapFilePath):
    with open(mapFilePath) as f:
        lines = f.read().splitlines()

        output = dict()

        for line in lines:
            if (line.startswith("                0x") and line.find(". = ") == -1):
                parts = list(filter(None, line.split(' ')))

                if (len(parts) >= 2):
                    addr = int(parts[0].split("x")[1], 16)
                    varName = parts[1].replace("@", "_").replace("?", "_")

                    if (varName.startswith("0x")):
                        continue

                    output[varName] = addr

        return output

def GetSectionOffset(dolData, address):
    dol = GetDolSections(dolData)

    for i in range(len(dol.textSections)):
        if (address >= dol.textSections[i].sectionAddress and address <= dol.textSections[i].sectionAddress + dol.textSections[i].sectionSize):
            diff = address - dol.textSections[i].sectionAddress
            return dol.textSections[i].sectionOffset + diff

    return -1

def Main(sourceFilePath, mapFilePath, dolFilePath):
    lines = list()

    # Read in the symbols from our linker output file
    symbols = GetSymbols(mapFilePath)

    # Read in the ROM File
    dolFile = open(dolFilePath, "rb")
    dolData = bytearray(dolFile.read())
    dolFile.close()

    # Read in our source code.
    with open(sourceFilePath) as f:
        lines = f.read().splitlines()

    # Go through each line of our source code. Check for the DETOUR() macro and patch in a jump.
    for line in lines:
        cleanedLine = CleanupLine(line)

        if (cleanedLine.startswith("DETOUR(")):
            funcName = cleanedLine.split("DETOUR(")[1].split(",")[0]
            funcAddr = int(cleanedLine.split("DETOUR(")[1].split(")")[0].split(",")[1].split('0x')[1], 16)

            #print("Detour Function Name: " + funcName)
            #print("Detour Function Address: " + str(hex(funcAddr)))

            dolAddress = GetSectionOffset(dolData, funcAddr)

            # Patch a Jump Opcode
            newFuncAddr = symbols[funcName]

            addressDifference = newFuncAddr - funcAddr

            #print(hex(addressDifference))

            dolData[dolAddress : dolAddress + 4] = struct.pack(">I", 0x48000000 + (addressDifference))[:]
        elif (cleanedLine.startswith("DETOURLINK(")):
            funcName = cleanedLine.split("DETOURLINK(")[1].split(",")[0]
            funcAddr = int(cleanedLine.split("DETOURLINK(")[1].split(")")[0].split(",")[1].split('0x')[1], 16)

            print("Detour Link Function Name: " + funcName + ", Function Address: " + str(hex(funcAddr)))

            dolAddress = GetSectionOffset(dolData, funcAddr)

            # Patch a Jump Opcode
            newFuncAddr = symbols[funcName]

            addressDifference = newFuncAddr - funcAddr

            #print(hex(addressDifference))

            dolData[dolAddress : dolAddress + 4] = struct.pack(">I", 0x48000000 + (addressDifference+1))[:]

    # Write Patched DOL File
    dolFile = open(dolFilePath, "wb")
    dolFile.write(dolData)
    dolFile.close()

Main(sys.argv[1], sys.argv[2], sys.argv[3])
#print("Patched!")