import search
import numpy as np


class FleetSearch(search.Problem):


    def load(self, fh):
        for line in fh:
            if line.startswith('#'):
                continue
            elif line.startswith('P'):
                p = line.split(' ')
                p = np.zeros((int(p[1]),int(p[1])))
                print(p)


    def cost(self, sol):
        return calculated_cost

