import struct
import sys
from GC_Shared import *

def Main(binPath, dolPath, sectionAddress):    
    dolFile = open(dolPath, "rb")
    dolData = bytearray(dolFile.read())
    dolFile.close()

    dol = GetDolSections(dolData)

    # Get our bin data...
    binFile = open(binPath, "rb")
    binData = binFile.read()
    binFile.close()

    # Add our own section
    newSection = Section()
    newSection.sectionAddress = sectionAddress
    newSection.sectionOffset = len(dolData)
    newSection.sectionSize = len(binData)
    dol.textSections.insert(len(dol.textSections), newSection)
    #dol.textSections[len(dol.textSections) - 1] = newSection

    # Append the section's data to the end of the file
    dolData[len(dolData) : len(dolData) + len(binData)] = binData[:]

    # Save our file
    WriteDolSection(dol, dolData)

    dolFile = open(dolPath, "wb")
    dolFile.write(dolData)
    dolFile.close()


#Main("Final.bin", "Start.dol", 0x80550000)
Main(sys.argv[1], sys.argv[2], int(sys.argv[3], 16))
