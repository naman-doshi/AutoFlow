from Components import *

landscape = Landscape(xSize=5, ySize=5)

#landscape.generate_new_landscape(desiredFeatures=[(LandPlotDescriptor((1, 1), (1, 1), False), 20)])
landscape.generate_new_landscape(filler=LandPlotDescriptor((2, 2), (2, 2), False))

#print(landscape.availableArea)

for i in range(len(landscape.gridMatrix)):
    print(landscape.gridMatrix[i])