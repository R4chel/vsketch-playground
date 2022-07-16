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

    target_percent_filled = vsketch.Param(0.75, step=0.5)
    max_attempts = vsketch.Param(10000, step=100)


    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a3", landscape=True)
        vsk.scale("px")

        circles = []
        total_area = vsk.width * vsk.height
        target_area_filled = total_area * self.target_percent_filled
        area_filled = 0
        attempt = 0
        while area_filled < target_area_filled and attempt < self.max_attempts:
            point = Point(vsk.random(0, vsk.width), vsk.random(0, vsk.height))
            distances = [point.distance(s) for s in circles]
            min_distance = min(distances + [distance_to_edge(vsk, point), self.max_radius])
            if min_distance > self.min_radius:
                circle = point.buffer(min_distance)
                area_filled += circle.area
                circles.append(circle)
            attempt += 1

        for circle in circles:
            vsk.fill(1)
            vsk.geometry(circle)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FirstProjectSketch.display()
