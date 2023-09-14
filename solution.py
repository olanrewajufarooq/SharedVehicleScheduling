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
                p = line.strip().split(' ')
                number_of_geopoints = int(p[1])
                p = np.zeros((int(p[1]),int(p[1])))
                up_t = []
                for i,l in enumerate(fh):
                    # print(l)
                    if i<number_of_geopoints - 1:
                        up_t.append(l.strip().split(" "))
                    else:
                        rest_of_the_file = [l] + list(fh)
                        break
                up_t = [[int(j) for j in i] for i in up_t]
                max_l = number_of_geopoints
                for sublist in up_t:
                    while len(sublist) < max_l:
                        sublist.insert(0,0)   
                up_t = np.triu(up_t)
                row_of_zeros = np.zeros((1, up_t.shape[1]))
                up_t = np.vstack((up_t,row_of_zeros))
                low_t = np.tril(up_t.T)
                p = up_t + low_t
                print(p)

        for lines in rest_of_the_file:
            if lines.startswith('R'):
                r = lines.strip().split(' ')
                number_of_requests = int(r[1])
                # print(number_of_requests)
                requests = []
                # print(number_of_requests)
                for i,l in enumerate(rest_of_the_file,start=0):
                    # print(l)
                    if i<=number_of_requests:
                        # print(l)
                        requests.append(l.strip().split("\n"))
                    else:
                        rest_of_the_file.pop(0)
                        rest_of_the_file2 = [l] + list(rest_of_the_file)
                        # print(rest_of_the_file2)
                        break

                requests.pop(0)
                # print(requests)
                requests = [[int(num) for num in sublist[0].split()] for sublist in requests]
                final_requests = {}
                for k,subl in enumerate(requests):
                    final_requests[k] = subl
                print(final_requests)

        for lines in rest_of_the_file2:
            # print(lines)
            if lines.startswith('V'):
                v = lines.strip().split(' ')
                number_of_vehicles = int(int(v[1]))
                # print(number_of_vehicles)
        capacity = rest_of_the_file2[-number_of_vehicles:]
        capacity = [int(item.strip()) for item in capacity]
        print(capacity)
                

            


            
            

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

