from logging import raiseExceptions
import search
import numpy as np
import pandas as pd


class FleetSearch(search.Problem):
    """_summary_

    Args:
        search (_type_): _description_
    """
    
    def __init__(self):
        self.P = []
        self.no_of_points = 0
        
        self.R = {}
        self.no_of_requests = 0
        
        self.V = []
        self.no_of_vehicles = 0
    
    
    def __str__(self):
        return f"""
    
=================================================
Number of Points: {self.no_of_points}.
P matrix: 
{self.P}

Number of Requests: {self.no_of_requests}.
Request Data: {self.R}

Number of Vehicles: {self.no_of_vehicles}.
Max passenger capacity: {self.V}
=================================================

"""
    
    
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
    
    
    def load_new(self, fh):
        
        line_read_state = None 
        for line in fh:
            
            # Checking for commented lines
            if line.startswith("#"):
                continue
            
            # Checking for lines with data indications
            elif line.startswith( ("P", "R", "V") ) and line_read_state is None:
                line_values = line.strip().split(" ") # Getting the content of the line
                
                # Assertation to check for error
                assert len(line_values) == 2, "Length of line values for number of points is not equal to 2"
                
                line_read_state = line_values[0]
                
                if line_read_state == "P":
                    self.no_of_points = int(line_values[1]) # Obtaining the number of points in the line data.
                    self.P = np.zeros([self.no_of_points, self.no_of_points]) # Creating the P matrix
                    max_iteration = self.no_of_points - 1
                    
                elif line_read_state == "R":
                    self.no_of_requests = int(line_values[1]) # Obtaining the number of requests in the line data.
                    max_iteration = self.no_of_requests
                    
                elif line_read_state == "V":
                    self.no_of_vehicles = int(line_values[1]) # Obtaining the number of vehicle in the line data.
                    max_iteration = self.no_of_vehicles
                    
                else:
                    raise Exception(f"Unknown input for line value: {line_read_state}. Expected: P, R or V.")
                
                line_iter_count = 0
                continue
            
            # Reading of data and storing
            elif line_read_state in ["P", "R", "V"]:
                
                line_values = line.strip().split(" ") # Getting the content of the line
                if len(line_values) == 0: continue # Edge case consideration for empty line before next data
                
                if line_read_state == "P":
                    # Assertation to check for error
                    assert len(line_values) == self.no_of_points - line_iter_count - 1, f"Expected {self.no_of_points - line_iter_count - 1} data value for row {line_iter_count + 1} of P but obtained {len(line_values)} data value"
                    
                    # Storing data in the P matrix in a symmetric manner.
                    for i, val in enumerate(line_values): 
                        self.P[line_iter_count, line_iter_count+i+1] = int(val)
                        self.P[line_iter_count+i+1, line_iter_count] = int(val)
                
                elif line_read_state == "R":
                    # Assertation to check for error
                    assert len(line_values) == 4, f"Expected {4} data value for row {line_iter_count + 1} of R but obtained {len(line_values)} data value"
                    
                    # Storing data in the R dictionary
                    request_data = []
                    for i, val in enumerate(line_values): 
                        if i == 0: val = float(val) # Saving the time data as a float
                        else: val = int(val) # Saving indexes and passenger amount as integers
                        request_data.append(val)
                        
                    self.R[line_iter_count] = request_data
                    
                elif line_read_state == "V":
                    # Assertation to check for error
                    assert len(line_values) == 1, f"Expected {1} data value for row {self.v_iter_count + 1} of R but obtained {len(line_values)} data value"
                    
                    # Storing data in the V list
                    self.V.append(int(line_values[0]))
                    
                else:
                    raise Exception("Report error in programming. This point should never be reached.")
                
                
                line_iter_count += 1
                print(line_iter_count, max_iteration)
                
                # Ending the data input into the P matrix
                if line_iter_count == max_iteration:
                    line_read_state = None
                    line_iter_count = None
                    max_iteration = None
                    
            else:
                continue
    
    
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

