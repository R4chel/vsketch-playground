import vsketch
from shapely.geometry import Point, box
import math

def flatten(xss):
    return [x for xs in xss for x in xs]

def rand_int(vsk:vsketch.Vsketch, low, high):
    return math.floor(vsk.random(low, high+1))

def distance_to_edge(vsk: vsketch.Vsketch, point):
    xmin = 0
    xmax = vsk.width
    ymin = 0
    ymax = vsk.height
    return min([point.x - xmin, xmax - point.x, point.y - ymin, ymax - point.y])


def to_cartesian(r, theta):
    return Point(r * math.cos(theta), r * math.sin(theta))


class MyShape:
    def __init__(self, point, r):
        self.center = point
        self.r = r
        self.shapely = point.buffer(self.r)
        self.area = self.shapely.area
        self.children = []

    def draw(self, vsk: vsketch.Vsketch, draw_mode, *args):
        return  draw_mode_options[draw_mode](self, vsk, *args)

    def to_arcs(self, vsk: vsketch.Vsketch, ring_ratio, step_size, min_radius):
        shape = vsk.createShape()
        shape.arc(self.center.x, self.center.y, self.r, self.r, vsk.random(0, 360), vsk.random(0, 360), degrees=True,
                  mode="radius")

        levels = math.floor(abs(vsk.randomGaussian()) * self.r / ring_ratio)
        for i in range(levels):
            r = self.r * vsk.random(0.5, 0.95)
            if r > min_radius:
                r = step_size * round(r / step_size)
                shape.arc(self.center.x, self.center.y, r, r, vsk.random(0, 360), vsk.random(0, 360), degrees=True,
                        mode="radius")
        return [shape]

    def to_circles(self, vsk: vsketch.Vsketch, _ring_ratio, _step_size, _min_radius):
        return [self.to_circle(vsk)]

    def to_circle(self, vsk: vsketch.Vsketch):
        shape = vsk.createShape()
        shape.circle(self.center.x, self.center.y, radius=self.r)
        return shape

    def to_tangents(self, vsk: vsketch.Vsketch, *args):
        circle = self.to_circle(vsk)
        children = flatten([ child.to_tangents(vsk, *args) for child in self.children ])
        return [circle] + children

    def maybe_add_child(self, vsk: vsketch.Vsketch, min_radius):
        angle = vsk.random(0, 360)
        offset = self.r * math.sqrt(vsk.random(0.05, 0.95))
        new_center = to_cartesian(offset, angle)
        point = Point(self.center.x + new_center.x, self.center.y + new_center.y)
        new_radius = max_possible_radius(vsk, self.children, self.r, self.r - offset, point)
        if new_radius >= min_radius:
            new_shape = MyShape(point, new_radius)
            self.children.append(new_shape)


    def maybe_add_children(self, vsk, min_radius, probability, attempts):
        angle = vsk.random(0, 360)
        offset = self.r * math.sqrt(vsk.random(0.05, 0.95))
        new_center = to_cartesian(offset, angle)
        point = Point(self.center.x + new_center.x, self.center.y + new_center.y)
        new_radius = max_possible_radius(vsk, self.children, self.r, self.r - offset, point)
        if new_radius >= min_radius:
            new_shape = MyShape(point, new_radius)
            self.children.append(new_shape)
            for i in range(attempts):
                if vsk.random(0,1 ) < probability:
                    new_shape.maybe_add_children(vsk, min_radius, probability , attempts -1 )

draw_mode_options = {"arcs": MyShape.to_arcs, "circles": MyShape.to_circles, "tangents": MyShape.to_tangents}

def max_possible_radius(vsk: vsketch.Vsketch, existing_circles, max_allowed_radius, distance_to_edge, point):
    distances = [point.distance(shape.shapely) for shape in existing_circles]
    min_distance = min(distances + [distance_to_edge, max_allowed_radius])
    return min_distance

class ConcentricPackedCirclesSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(5.0)
    max_radius = vsketch.Param(100.0)

    ring_ratio = vsketch.Param(5, step=1)
    step_size = vsketch.Param(5, step=1)
    target_percent_filled = vsketch.Param(0.75, step=0.5)
    max_attempts = vsketch.Param(100, step=100)
    draw_mode = vsketch.Param("tangents", choices=draw_mode_options.keys())
    max_child_attempts = vsketch.Param(5, step = 1)
    num_layers= vsketch.Param(1, step=1)
    recursive_probability= vsketch.Param(0.75, step=0.5)

    def draw(self, vsk: vsketch.Vsketch) -> None:

        vsk.size("a5", landscape=False)
        vsk.scale("px")
        # vsk.ellipseMode("radius")

        shapes = []
        total_area = vsk.width * vsk.height
        target_area_filled = total_area * self.target_percent_filled
        area_filled = 0
        attempt = 0
        while area_filled < target_area_filled and attempt < self.max_attempts:
            point = Point(vsk.random(0, vsk.width), vsk.random(0, vsk.height))
            proposed_radius = max_possible_radius(vsk, shapes, self.max_radius, distance_to_edge(vsk, point), point)
            if proposed_radius > self.min_radius:
                shape = MyShape(point, proposed_radius)
                area_filled += shape.area
                shapes.append(shape)
            attempt += 1
        
        for shape in shapes:

            for i in range(self.max_child_attempts):
                shape.maybe_add_children(vsk, self.min_radius, self.recursive_probability, self.max_child_attempts)
                
            inner_shapes = shape.draw(vsk, self.draw_mode, self.ring_ratio, self.step_size, self.min_radius)
            for inner_shape in inner_shapes:
                layer = rand_int(vsk, 1, self.num_layers)
                vsk.stroke(layer)
                vsk.shape(inner_shape)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ConcentricPackedCirclesSketch.display()
