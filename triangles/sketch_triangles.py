import vsketch
from shapely.geometry import Point
import math
 
class TrianglesSketch(vsketch.SketchClass):
    # Sketch parameters:
    step_increment = vsketch.Param(5.0)
    angle_ish_N = vsketch.Param(1)
    angle_ish_D = vsketch.Param(3)
    steps = vsketch.Param(50)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a6", landscape=True)
        vsk.scale("cm")

        # implement your sketch here
        xmin = 0
        xmax = vsk.width
        ymin = 0
        ymax = vsk.height
        p0 = Point(vsk.random(xmin,xmax), vsk.random(ymin,ymax))
        angle_delta = math.pi * (1.0 - self.angle_ish_N/self.angle_ish_D )
        angle = vsk.random(0, 2 * math.pi)
        step_size = self.step_increment
        for i in range(self.steps):
            p1 = Point(p0.x + step_size*math.cos(angle), p0.y + step_size*math.sin(angle))
            vsk.line(p0.x, p0.y,p1.x,p1.y)
            step_size += self.step_increment
            angle += angle_delta
            p0 = p1


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    TrianglesSketch.display()
