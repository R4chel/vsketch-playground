import vsketch
from shapely.geometry import Point, box


def distance_to_edge(vsk: vsketch.Vsketch, point):
    xmin = 0
    xmax = vsk.width
    ymin = 0
    ymax = vsk.height
    return min([point.x - xmin, xmax - point.x, point.y - ymin, ymax - point.y])


class FirstProjectSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(100.0)
    num_attempts = vsketch.Param(500, step=1)
    percent_filled = vsketch.Param(0.75,step=0.5)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=True)
        vsk.scale("px")

        shapes = []

        for i in range(self.num_attempts):
            point = Point(vsk.random(0,vsk.width), vsk.random(0,vsk.height))
            distances = [point.distance(s) for s in shapes]
            min_distance = min(distances+[distance_to_edge(vsk, point), self.max_radius])
            if min_distance > self.min_radius:
                circle = point.buffer(min_distance)
                shapes.append(circle)

        for shape in shapes:
            vsk.geometry(shape)



    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FirstProjectSketch.display()
