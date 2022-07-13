import vsketch
from shapely.geometry import Point, box

class CirclePackingV2Sketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(100.0)
    num_shapes = vsketch.Param(500, step=1)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=True)
        vsk.scale("px")

        xmin = 0
        xmax = vsk.width
        ymin = 0
        ymax = vsk.height
        corners = [Point(xmin, ymin), Point(xmin, ymax), Point(xmax,ymin), Point(xmax,ymax)]
        points = [Point(vsk.random(xmin,xmax), vsk.random(ymin,ymax)) for _ in range(self.num_shapes)]

        shapes = []
        for i, point in enumerate(points):
            distances = [ point.distance(p) / 2 for (index, p) in enumerate(points) if index != i ]
            r = min(distances + [self.max_radius, point.x - xmin, xmax - point.x, point.y - ymin, ymax - point.y])

            #if r > self.min_radius:

            circle = point.buffer(r)
            shapes.append(circle)

        for shape in shapes:
            vsk.geometry(shape)
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CirclePackingV2Sketch.display()
