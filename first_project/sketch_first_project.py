import vsketch
from shapely.geometry import Point


class FirstProjectSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(10.0)
    num_shapes = vsketch.Param(5, step=1)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=True)
        vsk.scale("cm")

        # document = vsk.document
        # help(document)

        # bounds = vsk.document.bounds()
        # help(bounds)
        # (xmin, xmax, ymin, ymax)  = bounds
        # implement your sketch here
        shapes = []
        # points = [Point(vsk.random(xmin,xmax), vsk.random(ymin,ymax)) for i in range(self.num_shapes)]
        points = [Point(0,0) for i in range(self.num_shapes)]
        for p in points:
            radius = vsk.random(self.min_radius, self.max_radius)
            #circle = p.buffer(radius)
            #vsk.geometry(circle)

            vsk.circle(p.x,p.y,radius, mode="radius")

            # vsk.circle(0, 0, vsk.random(self.min_radius,self.max_radius), mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FirstProjectSketch.display()
