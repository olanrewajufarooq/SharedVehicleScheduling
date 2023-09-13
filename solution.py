import search
import numpy as np
import pandas as pd

class FleetSearch(search.Problem):
    def __init__(self):
        pass
    
    def load(self, fh):
        for line in fh:
            if line.startswith('#'):
                continue
            elif line.startswith('P'):
                p = line.split(' ')
                p = np.zeros((int(p[1]),int(p[1])))
                print(p)

    def cost(self, sol):
        """Calculation of the cost of the solution by summing all the delays.

        Args:
            sol (list of tuples): A list of tuples for all the scheduled pickup and dropoff
                                    actions. The tuple contains: 
                                    (action, vehicle id, request id, action time)

        Returns:
            float: the calcuted cost
        """
        
        # Convert the solution to a DataFrame
        sol_df = pd.DataFrame(sol, columns=["action", "veh id", "req id", "action time"])
        sol_df.set_index(["action", "req id"], inplace=True)
                
        calculated_cost = 0
        # for req_id in range(self.no_of_req):
        for req_id in range(5):
            
            dropoff_time = sol_df["action time"]["Dropoff", req_id]
            pickup_time = sol_df["action time"]["Pickup", req_id]
            request_time = 0
            Tod = dropoff_time - pickup_time
            
            delay = dropoff_time - request_time - Tod            
            calculated_cost += delay
        
        return calculated_cost

