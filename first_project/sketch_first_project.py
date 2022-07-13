import vsketch


class FirstProjectSketch(vsketch.SketchClass):
    # Sketch parameters:
    min_radius = vsketch.Param(2.0)
    max_radius = vsketch.Param(10.0)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("a4", landscape=True)
        vsk.scale("cm")

        # implement your sketch here

        vsk.circle(0, 0, vsk.random(self.min_radius,self.max_radius), mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    FirstProjectSketch.display()
