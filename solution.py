import search
import numpy as np
import re


class FleetProblem(search.Problem):
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
        
        self.initial = {}
        # self.goal = {}
    
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
        """Loading of scheduling input data from a file handle

        Args:
            fh (file handle): a text input loaded from a file containing details of scheduling in a specific format. 

        Raises:
            Exception: Error raised when a wrong code is given for the data input
        """
        
        line_read_state = None 
        for line in fh:
            
            # Checking for commented lines
            if line.startswith("#"):
                continue
            
            # Checking for lines with data indications
            elif line.startswith( ("P", "R", "V") ) and line_read_state is None:
                line = re.sub(' +', ' ', line) # Changing multiple whitespaces to one whitespace.
                line_values = line.strip().split(' ') # Getting the content of the line
                
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

                line = re.sub(' +', ' ', line) # Changing multiple whitespaces to one whitespace.
                line_values = line.strip().split(" ") # Getting the content of the line
                if len(line_values) == 0: continue # Edge case consideration for empty line before next data

                if line_read_state == "P":
                    # Assertation to check for error
                    assert len(line_values) == self.no_of_points - line_iter_count - 1, f"Expected {self.no_of_points - line_iter_count - 1} data value for row {line_iter_count + 1} of P but obtained {len(line_values)} data value. \nData: {line_values}"

                    # Storing data in the P matrix in a symmetric manner.
                    for i, val in enumerate(line_values): 
                        self.P[line_iter_count, line_iter_count+i+1] = float(val)
                        self.P[line_iter_count+i+1, line_iter_count] = float(val)

                elif line_read_state == "R":
                    # Assertation to check for error
                    assert len(line_values) == 4, f"Expected {4} data value for row {line_iter_count + 1} of R but obtained {len(line_values)} data value. \nData: {line_values}"

                    # Storing data in the R dictionary
                    request_data = []
                    for i, val in enumerate(line_values):
                        if i == 0: val = float(val) # Saving the time data as a float 
                        else: val = int(val) # Saving indexes and passenger amount as integers
                        request_data.append(val)
                    
                    # Saving request data with a request ID (i.e. line_iter_count) as the index.
                    self.R[line_iter_count] = request_data
                    
                elif line_read_state == "V":
                    # Assertation to check for error
                    assert len(line_values) == 1, f"Expected {1} data value for row {self.v_iter_count + 1} of R but obtained {len(line_values)} data value. \nData: {line_values}"

                    # Storing data in the V list
                    self.V.append( int(line_values[0]) )
                    
                else:
                    raise Exception("Report error in programming. This point should never be reached.")


                line_iter_count += 1

                # Ending the data input into the P matrix
                if line_iter_count == max_iteration:
                    line_read_state = None
                    line_iter_count = None
                    max_iteration = None

            else:
                continue
        
        self.create_initial_goal_states()


    def cost(self, sol):
        """Calculation of the cost of the solution by summing all the delays.

        Args:
            sol (list of tuples): A list of tuples for all the scheduled pickup and dropoff
                                    actions. The tuple contains: 
                                    (action, vehicle id, request id, action time)

        Returns:
            float: the calcuted cost
        """

        # Convert the solution to a dictionary
        sol_data = {}
        for data in sol:
            # Data: (action, veh id, request id, action time).
            sol_data[(data[0], data[2])] = {"action time": data[3], "veh id": data[1]}

        calculated_cost = 0
        for req_id in range(self.no_of_requests):

            dropoff_time = sol_data["Dropoff", req_id]["action time"]

            request_time = self.R[req_id][0] # Getting the request time from the dictionary
            pickup_point = self.R[req_id][1]
            dropoff_point = self.R[req_id][2]
            Tod = self.P[ pickup_point, dropoff_point ]

            delay = dropoff_time - request_time - Tod
            calculated_cost += delay

        return calculated_cost
    
    # ASSIGNMENT 2 ADDITIONS
    def create_initial_goal_states(self):
        """Creating the initial state and the goal state for the given problem"""
        self.initial = {"R": [i for i in self.R.keys()], "V": { id: {"time": 0, "location": 0, "space_left": self.V[id], "passengers": [], "passengers_pick_time": []} for id in range(len(self.V)) }}
        # self.goal = {"R": [], "V": { id: [] for id in self.V.keys() }}
    
    
    def result(self, state, action):
        new_state = state
        if action[0] == 'Pickup':
            new_state["R"].remove([action[2]])
            new_state["V"][action[1]].append(action[2])
        elif action[0] == 'Dropoff':
            new_state["V"][action[1]].remove(action[2])
        
        return new_state
    
    def actions(self, state):
        
        for req_id in state["R"]:
            pick_up_loc = self.R[req_id][1]
            requested_pick_up_time = self.R[req_id][0]
            
            for veh_id in state["V"].keys():
                
                if state["V"][veh_id]["space_left"] >= self.R[req_id][3]: # Pick up if there is space for passengers
                
                    # Current veh time + time to arrive at pick up point
                    arrival_time = state["V"][veh_id]["time"] + self.P[ pick_up_loc, state["V"][veh_id]["location"] ]
                    t = requested_pick_up_time if arrival_time < requested_pick_up_time else arrival_time
                    
                    yield ["Pickup", veh_id, req_id, t ]
        
        for veh_id in state["V"].keys():
            if len(state["V"][veh_id]["passengers"]) != 0: # Checking if the vehicle is carrying any request to drop-off
                for req_id in state["V"][veh_id]["passengers"]:
                    
                    # Current veh time + time to move from current position to dropoff point.
                    drop_off_time = state["V"][veh_id]["time"] + self.P[ self.R[req_id][2], state["V"][veh_id]["location"] ]
                    yield ["Dropoff", veh_id, req_id, drop_off_time]
            
            
    
    
    def goal_test(self, state):
        pass
    
    
    def path_cost(self, c, state1, action, state2):
        pass
    
    
    def solve(self):
        pass
    