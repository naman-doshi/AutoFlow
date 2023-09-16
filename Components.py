"""
This script contains all of the object definitions required for the simulation.

Environmental component hierarchy:
- Landscape
    - Landplots
    - Intersections (including traffic lights)
    - Roads

An algorithm for generating random landscapes is included.
"""

from collections import defaultdict
from random import randint


class LandPlot:

    """
    A land plot is a rectangular area where no roads can spawn.
    The size of a land plot is (number of cells taken in x axis) * (number of cells taken in y axis).
    """

    def __init__(self, xSize: int, ySize: int) -> None:

        # Set size of the land plot in number of cells
        self.xSize = xSize
        self.ySize = ySize

    def set_coordinate(self, xPos: int, yPos: int) -> None:

        # Set lower left coordinates of the land plot
        self.xPos = xPos
        self.yPos = yPos

    def area(self) -> int:
        return self.xSize * self.ySize


class Intersection:

    """
    A intersection is a point where two or more roads cross.
    An intersection is spawned at all four corners of a land plot.
    The coordinate (xPos, yPos) must be unique for each intersection.

    Each intersection also contains a neighbours list that points to all its adjacent neighbours (up to four)
    """

    def __init__(self, xPos: float, yPos: float) -> None:

        # Set coordinates of the intersection
        self.xPos = xPos
        self.yPos = yPos

        # Initiate neighbour references
        self.neighbours: list[Intersection] = []

    def __hash__(self) -> int:
        return hash((self.xPos, self.yPos))


class Road:

    """
    A road is one way lane between two intersections.
    Therefore, two roads going opposite directions need to be constructed for every pair of intersections. 

    Each road has the following properties:
    - Starting intersection and ending intersection
    - Length in metres
    - Speed limit in km/h

    Roads never need to be merged because there will always be a way to turn at an intersection.
    """

    def __init__(self, start: Intersection, end: Intersection) -> None:

        # Set starting intersection and ending intersection of the road
        self.start = start
        self.end = end

        self.set_length()
        self.set_speed_limit()

    def set_length(self, length = randint(50, 200)):
        self.length = length

    # this method should be overwritten by subclasses of road, e.g. highway => 120km/h
    def set_speed_limit(self, speedlimit: float = randint(40, 60)): 
        self.speedLimit = speedlimit


class LandPlotDescriptor:

    """
    Used to describe desirable "features" of a virtual landscape.
    Features e.g. residental rows are described through their corresponding land plot sizes.
    A list of LandPlotDescriptor will be passed to the landscape generator algorithm for virtual landscape generation.

    Assuming that the generated landscape faces North:
    xRange is the horizontal width (west to east) of the land plot
    yRange is the verticle length (south to north) of the land plot
    randomOrientation indicates whether x and y can be swapped when generating the specified landplot
    """

    def __init__(self, xRange: tuple[int, int], yRange: tuple[int, int], randomOrientation: bool = True) -> None:

        # Set size range of x and size range of y in number of cells
        self.xRange = xRange
        self.yRange = yRange

        # Whether x and y can be swapped (randomly) when generating landscape
        self.randomOrientation = randomOrientation


class Landscape:

    """
    A landscape is a grid structure that contains straight roads and rectangular land plots.
    The size of the landscape is (number of cells fittable in x axis) * (number of cells fittable in y axis).
    The real distance covered by each (square) cell on either axes is defined by cellSize in metres.
    This object represents an entire virtual landscape, storing references to all components.
    """

    def __init__(self, xSize: int, ySize: int, cellSize: int = 100) -> None:

        # Set size of the generated landscape in cell count, e.g. 10 x 10 cells with a cellSize of 100 => 1km^2 area
        self.xSize = xSize
        self.ySize = ySize
        cellSize = cellSize

        # Initiate component references
        self.reset_landscape()

    def reset_landscape(self):

        # Boolean 2D matrix used to indicate available plots of land, x and y are cell coordinates
        self.gridMatrix = [[False for i in range(self.xSize)] for i in range(self.ySize)]
        self.availableArea = self.xSize * self.ySize

        # Component references
        self.landPlots: list[LandPlot] = []
        self.roads: list[Road] = []
        self.intersections: dict[tuple[int, int]] = defaultdict(lambda: None)

        # Hashmap for accessing roads via intersection coordinates, e.g. self.roadmap[intersection1][intersection2]
        self.roadmap: dict[Intersection: dict[Intersection: Road]] = defaultdict(dict)

    @staticmethod
    def generate_features(desiredFeatures: list[tuple[LandPlotDescriptor, int]]) -> list[LandPlot]:
        """
        Generates and returns a list of feature groups from a list of LandPlotDescriptor and max occurrence counts.
        Each feature group represents a desired feature.
        """

        generatedFeatures: list[LandPlot] = []

        for desiredFeature, maxOccurrenceCount in desiredFeatures:

            if maxOccurrenceCount <= 0: # must be positive
                continue

            for i in range(maxOccurrenceCount):

                # Generate land plot feature
                if desiredFeature.randomOrientation == True:
                    # Randomly swap the x and y sizes
                    if randint(0, 1):
                        feature = LandPlot(
                            randint(*desiredFeature.xRange), 
                            randint(*desiredFeature.yRange)
                        )
                    else:
                        feature = LandPlot(
                            randint(*desiredFeature.yRange), 
                            randint(*desiredFeature.xRange)
                        )
                else:
                    feature = LandPlot(
                        randint(*desiredFeature.xRange), 
                        randint(*desiredFeature.yRange)
                    )

                # Add feature to generatedFeatures list
                generatedFeatures.append(feature)

        return generatedFeatures
    
    def get_valid_placements(self, feature: LandPlot) -> list[tuple[int, int]]:
        """
        Returns a list of all possible bottom_left coordinates where the feature land plot can fit.
        NOTE: x is the horizontal (west to east) coordinate, y is the vertical (south to north) coordinate,
        therefore y is indexed first (row in gridMatrix), then x (column in gridMatrix)
        """

        valid_coordinates: list[tuple[int, int]] = []

        # Check every possibly valid placement coordinate
        for ycoord in range(self.ySize - feature.ySize + 1):
            for xcoord in range(self.xSize - feature.xSize + 1):

                # Assume current placement coordinate is valid
                valid = True

                # Check every cell covered by the feature land plot                
                for y in range(ycoord, ycoord + feature.ySize):
                    for x in range(xcoord, xcoord + feature.xSize):

                        # cell has already been taken by another land plot
                        if self.gridMatrix[y][x] == True: 
                            valid = False
                            break

                    if not valid:
                        break
                
                # Append valid coordinates to list
                if valid:
                    valid_coordinates.append((xcoord, ycoord))

        return valid_coordinates
    
    def place_feature(self, feature: LandPlot, xPos: int, yPos: int):
        """
        Places a feature land plot within the landscape.
        """

        feature.set_coordinate(xPos, yPos)

        # Mark every cell covered by the feature land plot as taken
        for y in range(yPos, yPos + feature.ySize):
            for x in range(xPos, xPos + feature.xSize):
                self.gridMatrix[y][x] = True
                self.availableArea -= 1

        # Add feature land plot to component references
        self.landPlots.append(feature)

    def connect_intersections(self, intersection1: Intersection, intersection2: Intersection):
        """
        Connects two intersections by creating two roads that go in opposite directions
        """

        # Create road from intersection 1 to intersection 2
        intersection1.neighbours.append(intersection2)
        road1 = Road(intersection1, intersection2)
        self.roadmap[intersection1][intersection2] = road1
        self.roads.append(road1)

        # Create road from intersection 2 to intersection 1
        intersection2.neighbours.append(intersection1)
        road2 = Road(intersection2, intersection1)
        self.roadmap[intersection2][intersection1] = road2
        self.roads.append(road2)

    def generate_new_landscape(
            self, 
            desiredFeatures: list[tuple[LandPlotDescriptor, int]] = [], 
            filler: LandPlotDescriptor = LandPlotDescriptor((1, 1), (1, 1), False)
        ):
        """
        Algorithm for generating a random new landscape based on a list of desired features.

        The following optional parameters may be passed:
        - desiredFeatures: a list of (LandPlotDescriptor, maxCount) describing desired features and maximum occurrence
        - filler: a land plot used to populate the landscape, may occur indefinitely

        If the list of desired features is empty, or when no more desired features can fit, 
        filler land plot will be used to populate the landscape.
        """

        # Reset component references
        self.reset_landscape()

        # Generate feature land plots from desired features, then sort by decreasing area (place larger features first)
        featuresToAdd = Landscape.generate_features(desiredFeatures=desiredFeatures)
        featuresToAdd.sort(key = lambda feature: feature.area(), reverse = True)

        # Skip impossible placements quickly via temporary optimisation hashmap
        isUnplaceable: dict[tuple[int, int]: bool] = defaultdict(lambda: False)

        # Fit feature land plots into the landscape
        for feature in featuresToAdd:
            if isUnplaceable[(feature.xSize, feature.ySize)]:
                continue
            valid_coordinates = self.get_valid_placements(feature)
            if not valid_coordinates:
                isUnplaceable[(feature.xSize, feature.ySize)] = True
                continue
            self.place_feature(feature, *valid_coordinates[randint(0, len(valid_coordinates)-1)])

        # Generate filler land plots, then sort by decreasing area (place larger features first)
        fillerFeatures = Landscape.generate_features(desiredFeatures=[(filler, self.availableArea)])
        fillerFeatures.sort(key = lambda feature: feature.area(), reverse = True)

        # Fill in remaining area with filler, remaining area may not be completely filled if filler isn't 1 by 1
        for feature in fillerFeatures:
            if isUnplaceable[(feature.xSize, feature.ySize)]:
                continue
            valid_coordinates = self.get_valid_placements(feature)
            if not valid_coordinates:
                isUnplaceable[(feature.xSize, feature.ySize)] = True
                continue
            self.place_feature(feature, *valid_coordinates[randint(0, len(valid_coordinates)-1)])

        # Spawn intersections at all four corners of every land plot
        for landPlot in self.landPlots:

            # Create intersections
            corners = [
                (landPlot.xPos, landPlot.yPos), 
                (landPlot.xPos + landPlot.xSize, landPlot.yPos),
                (landPlot.xPos, landPlot.yPos + landPlot.ySize),
                (landPlot.xPos + landPlot.xSize, landPlot.yPos + landPlot.ySize)
            ]
            bottomLeft, bottomRight, topLeft, topRight = [
                Intersection(*corner) if self.intersections[(corner[0], corner[1])] == None 
                else self.intersections[corner[0]][corner[1]]
                for corner in corners
            ]

            # Connect intersections
            self.connect_intersections(bottomLeft, bottomRight)
            self.connect_intersections(bottomLeft, topLeft)
            self.connect_intersections(topRight, bottomRight)
            self.connect_intersections(topRight, topLeft)