#!/usr/bin/env python

# Create pH array (with no compound) with symmetric "blanks"

# TODO
# * Stage dilution (manually?) of 10 mM stock into DMSO so that we are < 50 uM for final concentrations of erlotinib to avoid solubility problems.
# * Create blanks using DMSO instead of erlotinib stock.

# TODO: Replace this taable with a module that computes buffer recipes automatically.
filename = 'citric-phosphate.txt'
infile = open(filename, 'r')
lines = infile.readlines()
infile.close()
conditions = list()
for line in lines:
    # ignore comments
    if line[0] == '#': continue

    # processs data
    elements = line.split()
    entry = dict()
    entry['pH'] = float(elements[0])
    entry['citric acid'] = float(elements[1])
    entry['sodium phosphate'] = float(elements[2])

    # Adjust for 0.1M sodium phosphate.
    entry['sodium phosphate'] *= 2
    total = entry['citric acid'] + entry['sodium phosphate'] 
    entry['citric acid'] /= total
    entry['sodium phosphate'] /= total

    # Store entry.
    conditions.append(entry)

def aspirate(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    return 'A;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def dispense(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    return 'D;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def washtips():
    return 'W;\r\n' # queue wash tips

assay_volume = 100.0 # assay volume (uL)
compound_volume = 5.0 # compound volume (uL)
buffer_volume = assay_volume - compound_volume
assay_RackType = 'Corning 3651' # black with clear bottom
assay_RackType = 'Corning 3679' # uv-transparent half-area

volume_consumed = dict()
volume_consumed['citric acid'] = 0.0
volume_consumed['sodium phosphate'] = 0.0

# Build worklist.
worklist = ""
for (condition_index, condition) in enumerate(conditions):
    print "pH : %8.1f" % condition['pH']

    # destination well of assay plate
    destination_position = condition_index + 1

    # citric acid
    volume = condition['citric acid']*buffer_volume
    volume_consumed['citric acid'] += 2*volume
    worklist += aspirate('Source Plate', '4x3 Vial Holder', 2, 2*volume, 2)
    worklist += dispense('Assay Plate', assay_RackType, destination_position, volume, 2)
    worklist += dispense('Assay Plate', assay_RackType, 96-destination_position+1, volume, 2) # C2 rotation for blanks
    worklist += washtips()
    
    # sodium phosphate
    volume = condition['sodium phosphate']*buffer_volume
    volume_consumed['sodium phosphate'] += 2*volume
    worklist += aspirate('Source Plate', '4x3 Vial Holder', 3, 2*volume, 4)
    worklist += dispense('Assay Plate', assay_RackType, destination_position, volume, 4)
    worklist += dispense('Assay Plate', assay_RackType, 96-destination_position+1, volume, 4)
    worklist += washtips()
    
# Write worklist.
worklist_filename = 'ph-worklist.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes.
print "citric acid:      %8.3f uL" % volume_consumed['citric acid']
print "sodium phosphate: %8.3f uL" % volume_consumed['sodium phosphate']