from ovito.data import DataCollection
from ovito.io import FileReaderInterface
from typing import Any
from traits.api import Union, Float


def strToInt(inp: str):
    return int(float(inp))


class ChargemolBondsReader(FileReaderInterface):
    lowerCutoff = Union(None, Float, label="Lower cutoff")
    upperCutoff = Union(None, Float, label="Upper cutoff")

    @staticmethod
    def detect(filename: str):
        try:
            with open(filename, "r") as f:
                for _, line in enumerate(f):
                    if "Chargemol" in line:
                        return True
        except Exception:
            return False
        return False

    def parse(self, data: DataCollection, filename: str, *args: Any, **kwargs: Any):
        bondsSection = False
        topology = []
        pbcFlag = []
        bondOrder = []

        with open(filename, "r") as f:
            for line in f:
                if line == " The final bond pair matrix is\n":
                    bondsSection = True
                    continue
                elif line == " The legend for the bond pair matrix follows:\n":
                    bondsSection = False
                    break
                if not bondsSection:
                    continue

                tokens = line.strip().split()
                currBondOrder = float(tokens[19])
                if self.lowerCutoff and currBondOrder < self.lowerCutoff:
                    continue
                if self.upperCutoff and currBondOrder > self.upperCutoff:
                    continue

                topology.append((float(tokens[0]) - 1, float(tokens[1]) - 1))
                pbcFlag.append(tuple(map(strToInt, tokens[2:5])))
                bondOrder.append(currBondOrder)

        particles = data.create_particles(count=0)
        bonds = data.particles_.create_bonds(count=len(topology))
        if topology:
            bonds.create_property("Topology", data=topology)
            bonds.create_property("Periodic Image", data=pbcFlag)
            bonds.create_property("Bond Order", data=bondOrder)
