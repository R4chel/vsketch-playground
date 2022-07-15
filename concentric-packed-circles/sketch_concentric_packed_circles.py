import vsketch
from shapely.geometry import Point, box


def distance_to_edge(vsk: vsketch.Vsketch, point):
    xmin = 0
    xmax = vsk.width
    ymin = 0
    ymax = vsk.height
    return min([point.x - xmin, xmax - point.x, point.y - ymin, ymax - point.y])


class MyShape:
    def __init__(self, point, r):
        self.center = point
        self.r = r
        self.shapely = point.buffer(self.r)
        self.area = self.shapely.area

    def to_shape(self, vsk: vsketch.Vsketch):
        shape = vsk.createShape()
        shape.circle(self.center.x, self.center.y, radius=self.r)
        return shape


class ConcentricPackedCirclesSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(100.0)

    target_percent_filled = vsketch.Param(0.75, step=0.5)
    max_attempts = vsketch.Param(100, step=100)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=True)
        vsk.scale("px")

        shapes = []
        total_area = vsk.width * vsk.height
        target_area_filled = total_area * self.target_percent_filled
        area_filled = 0
        attempt = 0
        while area_filled < target_area_filled and attempt < self.max_attempts:
            point = Point(vsk.random(0, vsk.width), vsk.random(0, vsk.height))
            distances = [point.distance(shape.shapely) for shape in shapes]
            print(point, distances)
            min_distance = min(distances + [distance_to_edge(vsk, point), self.max_radius])
            if min_distance > self.min_radius:
                shape = MyShape(point, min_distance)
                area_filled += shape.area
                shapes.append(shape)
            attempt += 1

        shapes = [shape.to_shape(vsk) for shape in shapes]

        for shape in shapes:
            vsk.shape(shape)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    ConcentricPackedCirclesSketch.display()
