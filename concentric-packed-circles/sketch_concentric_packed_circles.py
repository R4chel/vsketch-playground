import vsketch
from shapely.geometry import Point, box
import math


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

    def draw(self, vsk: vsketch.Vsketch, draw_mode, ring_ratio, step_size):
        return draw_mode_options[draw_mode](self, vsk, ring_ratio, step_size)

    def to_arcs(self, vsk: vsketch.Vsketch, ring_ratio, step_size):
        shape = vsk.createShape()
        shape.arc(self.center.x, self.center.y, self.r, self.r, vsk.random(0, 360), vsk.random(0, 360), degrees=True,
                  mode="radius")

        levels = math.floor(abs(vsk.randomGaussian()) * self.r / ring_ratio)
        for i in range(levels):
            r = self.r * vsk.random(0, 1)
            r = step_size * round(r / step_size)
            shape.arc(self.center.x, self.center.y, r, r, vsk.random(0, 360), vsk.random(0, 360), degrees=True,
                      mode="radius")

        return [shape]

    def to_circles(self, vsk: vsketch.Vsketch, _ring_ratio, _step_size):
        return [self.to_circle(vsk)]

    def to_circle(self, vsk: vsketch.Vsketch):
        shape = vsk.createShape()
        shape.circle(self.center.x, self.center.y, radius=self.r)
        return shape

    def to_tangents(self, vsk: vsketch.Vsketch, _ring_ratio, _step_size):
        # choose a point uniformly inside the circle
        angle = vsk.random(0, 360)
        offset = self.r * math.sqrt(vsk.random(0., 1.))
        new_center = to_cartesian(offset, angle)

        new_shape = MyShape(Point(self.center.x + new_center.x, self.center.y + new_center.y), self.r - offset)
        my_shapes = [self, new_shape]
        return [my_shape.to_circle(vsk) for my_shape in my_shapes]


draw_mode_options = {"arcs": MyShape.to_arcs, "circles": MyShape.to_circles, "tangents": MyShape.to_tangents}


class ConcentricPackedCirclesSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(100.0)

    ring_ratio = vsketch.Param(5, step=1)
    step_size = vsketch.Param(5, step=1)
    target_percent_filled = vsketch.Param(0.75, step=0.5)
    max_attempts = vsketch.Param(100, step=100)
    draw_mode = vsketch.Param("tangents", choices=draw_mode_options.keys())

    def draw(self, vsk: vsketch.Vsketch) -> None:

        vsk.size("a3", landscape=True)
        vsk.scale("px")
        # vsk.ellipseMode("radius")

        shapes = []
        total_area = vsk.width * vsk.height
        target_area_filled = total_area * self.target_percent_filled
        area_filled = 0
        attempt = 0
        while area_filled < target_area_filled and attempt < self.max_attempts:
            point = Point(vsk.random(0, vsk.width), vsk.random(0, vsk.height))
            distances = [point.distance(shape.shapely) for shape in shapes]
            min_distance = min(distances + [distance_to_edge(vsk, point), self.max_radius])
            if min_distance > self.min_radius:
                shape = MyShape(point, min_distance)
                area_filled += shape.area
                shapes.append(shape)
            attempt += 1

        for shape in shapes:
            inner_shapes = shape.draw(vsk, self.draw_mode, self.ring_ratio, self.step_size)
            for i, inner_shape in enumerate(inner_shapes):
                vsk.stroke(i + 1)
                vsk.shape(inner_shape)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ConcentricPackedCirclesSketch.display()
