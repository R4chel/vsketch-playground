import vsketch
from shapely.geometry import Point
import math
import vpype as vp


class Connector:
    def __init__(p1, p2):
        self.p1 = p1
        self.p2 = p2

    def line(self, vsk : vsketch.Vsketch):
        vsk.line(p1.x,p1.y,p2.x,p2.y)


path_mode_options = {"line": Connector.line }

class TrianglesSketch(vsketch.SketchClass):
    # Sketch parameters:
    step_increment = vsketch.Param(5.0)
    angle_ish_N = vsketch.Param(1)
    angle_ish_D = vsketch.Param(3)
    steps = vsketch.Param(50)
    path_mode = vsketch.Param("path", choices=path_mode_options.keys())

    def connect(self, vsk:vsketch.Vsketch, p1 : Point, p2 : Point):
        return

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=True)
        scale = "mm"
        vsk.scale(scale)
        factor = 1 / vp.convert_length(scale)
        w, h = factor * vsk.width, factor * vsk.height

        
        # implement your sketch here
        xmin = 0
        xmax = w
        ymin = 0
        ymax = h

        p0 = Point(vsk.random(xmax), vsk.random(ymax))
        angle_delta = math.pi * (1.0 - self.angle_ish_N/self.angle_ish_D )
        angle = vsk.random(0, 2 * math.pi)
        step_size = self.step_increment

        for i in range(self.steps):
            p1 = Point(p0.x + step_size*math.cos(angle), p0.y + step_size*math.sin(angle))
            if p1.x > w or p1.x < 0 or p1.y < 0 or p1.y > h:
                break;
            vsk.line(p0.x, p0.y,p1.x,p1.y)
            step_size += self.step_increment
            angle += angle_delta
            p0 = p1


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    TrianglesSketch.display()
