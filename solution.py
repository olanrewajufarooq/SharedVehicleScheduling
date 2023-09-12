import search
import numpy as np
class FleetSearch(search.Problem):
    def __init__(self,fh):
        self.data = self.load(fh)

    def load(self, fh):
        with open(fh,'r') as fh:
            for line in fh:
                if line.startswith('#'):
                    continue
                elif line.startswith('P'):
                    p = line.split(' ')
                    p = np.zeros((int(p[1]),int(p[1])))
                    print(p)

    def cost(self, sol):
        pass


obj = FleetSearch('input.txt')

