import struct
import sys

class DolFile:
    def __init__(self):
        self.textSections = list()
        self.dataSections = list()
        self.bssAddress = 0
        self.bssSize = 0
        self.entryPoint = 0

class Section:
    def __init__(self):
        self.sectionOffset = 0
        self.sectionAddress = 0
        self.sectionSize = 0

def GetDolSections(dolData):
    dol = DolFile()

    textSectionOffset = []
    dataSectionOffset = []
    
    for i in range(7):
        textSectionOffset.insert(len(textSectionOffset), int(struct.unpack(">I", dolData[(i * 0x04):(i * 0x04) + 0x04])[0]))
        #print("Text Section Offset: " + hex(textSectionOffset[i]))
    
    for i in range(11):
        dataSectionOffset.insert(len(dataSectionOffset), int(struct.unpack(">I", dolData[0x1C + (i * 0x04) : 0x1C + (i * 0x04) + 0x04])[0]))

    textLoadingAddress = []
    dataLoadingAddress = []

    for i in range(7):
        textLoadingAddress.append(int(struct.unpack(">I", dolData[0x48 + (i * 0x04):0x48 + (i * 0x04) + 0x04])[0]))
        #print("Text Loading Address: " + hex(textLoadingAddress[i]))
    
    for i in range(11):
        dataLoadingAddress.append(int(struct.unpack(">I", dolData[0x64 + (i * 0x04):0x64 + (i * 0x04) + 0x04])[0]))

    textSectionSize = []
    dataSectionSize = []

    for i in range(7):
        textSectionSize.append(int(struct.unpack(">I", dolData[0x90 + (i * 0x04):0x90 + (i * 0x04) + 0x04])[0]))
    
    for i in range(11):
        dataSectionSize.append(int(struct.unpack(">I", dolData[0xAC + (i * 0x04):0xAC + (i * 0x04) + 0x04])[0]))

    dol.bssAddress = int(struct.unpack(">I", dolData[0xD8:0xDC])[0])
    dol.bssSize = int(struct.unpack(">I", dolData[0xDC:0xE0])[0])
    dol.entryPoint = int(struct.unpack(">I", dolData[0xE0:0xE4])[0])

    #print("ENTRY POINT: " + hex(dol.entryPoint))

    #print(hex(dol.entryPoint))

    for i in range(7):
        if (textSectionOffset[i] != 0):
            section = Section()
            section.sectionAddress = textLoadingAddress[i]
            section.sectionOffset = textSectionOffset[i]
            section.sectionSize = textSectionSize[i]

            dol.textSections.append(section)
            
    for i in range(11):
        if (dataSectionOffset[i] != 0):
            section = Section()
            section.sectionAddress = dataLoadingAddress[i]
            section.sectionOffset = dataSectionOffset[i]
            section.sectionSize = dataSectionSize[i]

            dol.dataSections.append(section)

    return dol

def WriteDolSection(dol, dolData):

    # Write text section
    for i in range(len(dol.textSections)):
         dolData[(i * 0x04):(i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.textSections[i].sectionOffset))[:]
         dolData[0x48 + (i * 0x04) : 0x48 + (i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.textSections[i].sectionAddress))[:]
         dolData[0x90 + (i * 0x04) : 0x90 + (i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.textSections[i].sectionSize))[:]

    # Write data section
    for i in range(len(dol.dataSections)):
         dolData[0x1C + (i * 0x04) : 0x1C + (i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.dataSections[i].sectionOffset))[:]
         dolData[0x64 + (i * 0x04) : 0x64 + (i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.dataSections[i].sectionAddress))[:]
         dolData[0xAC + (i * 0x04) : 0xAC + (i * 0x04) + 0x04] = bytearray(struct.pack('>I', dol.dataSections[i].sectionSize))[:]

    # Write BSS and Entry Point
    dolData[0xD8:0xDC] = bytearray(struct.pack('>I', dol.bssAddress))[:]
    dolData[0xDC:0xE0] = bytearray(struct.pack('>I', dol.bssSize))[:]
    dolData[0xE0:0xE4] = bytearray(struct.pack('>I', dol.entryPoint))[:]