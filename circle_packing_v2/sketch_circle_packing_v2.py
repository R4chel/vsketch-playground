import vsketch
from shapely.geometry import Point, box

class Connector:
    def __init__(p1, p2):
        self.p1 = p1
        self.p2 = p2

    def line(self, vsk : vsketch.Vsketch):
        vsk.line(p1.x,p1.y,p2.x,p2.y)



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
        points = [Point(vsk.random(xmin,xmax), vsk.random(ymin,ymax)) for _ in range(self.num_shapes)]

        shapes = []
        for i, point in enumerate(points):
            distances = [ point.distance(p) / 2 for (index, p) in enumerate(points) if index != i ]
            r = min(distances + [self.max_radius, point.x - xmin, xmax - point.x, point.y - ymin, ymax - point.y])



            circle = point.buffer(r)
            shapes.append(circle)

        for shape in shapes:
            vsk.geometry(shape)
    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    CirclePackingV2Sketch.display()
