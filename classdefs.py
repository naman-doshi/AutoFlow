class Vertex:
    def __init__(self, name, neighbours=None):
        self.name = name
        self.neighbours = neighbours if neighbours else []
        self.visited = {}
        self.traffic_light = None

    def add_neighbour(self, neighbour):
        self.neighbours.append(neighbour)
        neighbour.neighbours.append(self)
    
    def add_traffic_light(self, traffic_light):
        self.traffic_light = traffic_light
    
    def number_of_neighbours(self):
        return len(self.neighbours)
    
class Road:
    def __init__(self, start : Vertex, end : Vertex, length, speed_limit, num_lanes):
        self.start = start
        self.end = end
        self.length = length
        self.speed_limit = speed_limit
        self.num_lanes = num_lanes
    
    @staticmethod
    def connect(vertex1 : Vertex, vertex2 : Vertex, length, speed_limit, num_lanes):
        road = Road(vertex1, vertex2, length, speed_limit, num_lanes)
        vertex1.add_neighbour(vertex2)
        return road

class Traffic_Light:
    def __init__(self, vertex : Vertex, type_of_light):
        self.vertex = vertex
        self.visited = {}
        self.type_of_light = type_of_light # Either pedestrian or intersection
    
    def add_attrs_intersection(self, road1 : list[Road], road2 : list[Road], on_time_road1, on_time_road2):
        self.road1 = road1
        self.road2 = road2
        self.on_time_road1 = on_time_road1
        self.on_time_road2 = on_time_road2
    
    def add_attrs_pedestrian(self, on_time, off_time):
        self.on_time = on_time
        self.off_time = off_time
    
    def is_on(self, time):
        '''
        If intersection, returns the road that is on
        If pedestrian, returns True if the light is on, False otherwise
        '''
        if self.type_of_light == "intersection":
            if time % (self.on_time_road1 + self.on_time_road2) < self.on_time_road1:
                return self.road1
            else:
                return self.road2
            
        elif self.type_of_light == "pedestrian":
            if time % (self.on_time + self.off_time) < self.on_time:
                return True
            else:
                return False

class Vehicle:
    def __init__(self, start : Vertex, end : Vertex, emissions_per_hour):
        self.start = start
        self.end = end
        self.emissions_per_hour = emissions_per_hour
        self.path = []
        self.current_vertex = start
        self.time = 0
        
            

