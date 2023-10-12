import search
import numpy as np
import re, copy
import signal


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
        
        self.initial = State()
        self.goal = State()
    
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
        self.initial = State(request= [i for i, _ in self.R.items()], 
                             vehicles=[ [0, 0, [], []] for _ in range(len(self.V)) ], # Time, Location, Passengers, Pickup Time
                             path_cost= 0,
                             problem=self)
        
        # self.goal = State(request=[], 
        #                   vehicles=[ [None, None, [], []] for id in range(len(self.V)) ], # Time, Location, Passengers, Pickup Time
        #                   path_cost= 0,
        #                   problem=self)
        
        # self.initial = {"R": [i for i in self.R.keys()], "V": { id: {"time": 0, "location": 0, "space_left": self.V[id], "passengers": []} for id in range(len(self.V)) }}
        # self.goal = {"R": [], "V": { id: [] for id in self.V.keys() }}
    
    def result(self, state, action):
        # new_state = state.__copy__()
        new_state = copy.deepcopy(state)
        # new_state = state
        
        if action[0] == 'Pickup':
            
            # Request Adjustments
            new_state.request.remove( action[2] ) #Remove request id from state
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[action[1]][0] = action[-1] #Pickup time
            new_state.vehicles[action[1]][1] = self.R[action[2]][1] #Pickup Location 
            
            # Passenger Parameters Adjustments
            new_state.vehicles[action[1]][2].append( action[2] ) #Passengers of this particular request
            new_state.vehicles[action[1]][3].append( action[3] ) #Pickup TIme of this particular request
            
        
        elif action[0] == 'Dropoff':
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[action[1]][0] = action[-1] #Dropoff time
            new_state.vehicles[action[1]][1] = self.R[action[2]][2] #Dropoff Location
            
            # Passenger Parameters Adjustments
            ind = state.vehicles[action[1]][2].index( action[2] )
            new_state.vehicles[action[1]][2].pop( ind ) # remove passengers of this particular request
            new_state.vehicles[action[1]][3].pop( ind ) # remove corresponding pickup time
            
        new_state.compute_path_cost(state, action)
        
        return new_state
    
    def actions(self, state):
        
        for veh_id, veh_values in enumerate(state.vehicles):
            if len(veh_values[2]) != 0: # Checking if the vehicle is carrying any request to drop-off
                for req_id in state.vehicles[veh_id][2]:
                                        
                    # Current veh time + time to move from current position to dropoff point.
                    drop_off_time = veh_values[0] + self.P[ self.R[req_id][2], veh_values[1] ]
                    yield ("Dropoff", veh_id, req_id, drop_off_time)
                    
            for req_id in state.request:
                pick_up_loc = self.R[req_id][1]
                requested_pick_up_time = self.R[req_id][0]
                
                if state.vehicle_space_left(veh_id) >= self.R[req_id][3]: # Pick up if there is space for passengers
                    
                    # Current veh time + time from current veh location to pickup location
                    arrival_time = veh_values[0] + self.P[ veh_values[1], pick_up_loc ]
                    t = requested_pick_up_time if arrival_time < requested_pick_up_time else arrival_time
                    
                    yield ("Pickup", veh_id, req_id, t )
        
        # for req_id in state.request:
        #     pick_up_loc = self.R[req_id][1]
        #     requested_pick_up_time = self.R[req_id][0]
            
        #     for veh_id, _ in enumerate(state.vehicles):
                
        #         if state.vehicle_space_left(veh_id) >= self.R[req_id][3]: # Pick up if there is space for passengers
                
        #             # Current veh time + time to arrive at pick up point
        #             arrival_time = state.vehicles[veh_id][0] + self.P[ state.vehicles[veh_id][1], pick_up_loc ]
        #             t = requested_pick_up_time if arrival_time <= requested_pick_up_time else arrival_time
                    
        #             yield ("Pickup", veh_id, req_id, t )
        
        
    
    def goal_test(self, state):
        # result = False
        # if len(state["R"]) == 0:
        #     for _, veh_value in enumerate(state.vehicles):
        #         if len(veh_value["passengers"]) != 0:
        #             break
        #     else:
        #         result = True
        # return result
        
        expanded_actions = self.actions(state)
        if len( list(expanded_actions) ) == 0:
            return True
        else:
            return False
        
        # if state == self.goal:
        #     return True
        # else:
        #     return False
        
        # For optimal solutions
    
    def path_cost(self, c, state1, action, state2):
        # veh_id = action[1] # Determining vehicle that performed action
        # Path cost of previous state + time to travel from previous state to new state
        # return c + ( state2.vehicles[veh_id][0] - state1.vehicles[veh_id][0] )
        # return state2.vehicles[veh_id][0]
        return state2.path_cost
    
    def solve(self):
            
        # goal_node = search.depth_limited_search(self, limit=self.no_of_requests*2)
        # goal_node = search.iterative_deepening_search(self)
        goal_node = search.uniform_cost_search(self, display=True)
        solution = goal_node.solution()
        
        assert self.validate_solution(solution), f"Invalid Solution: {solution}"
        
        return solution
    
    def validate_solution(self, solution):
        if len(solution) != self.no_of_requests * 2:
            raise Exception( "Solution: {solution}. \nThe length of the solution is more than expected" )
        
        pick_up_times = np.zeros(self.no_of_requests)
        
        # Verification of the Pickups
        for data in solution:
            action, _, req_id, pick_up_time = data
            if action != 'Pickup':
                continue
            
            # Assert that the pickuptime is more than or equal to the request time.
            assert pick_up_time >= self.R[req_id][0], f"Solution: {solution}. \nFor Request {req_id}: Impossible for the Pickup time ({pick_up_time}) to be less than the Request time ({self.R[req_id][0]})"
            pick_up_times[req_id] = pick_up_time
        
        # Verification of the Dropoff Results
        for data in solution:
            action, _, req_id, drop_off_time = data
            if action != 'Dropoff':
                continue
            
            # Check that dropoff is more than or equal to pickup time + direct travel.
            direct_travel = self.R[req_id][0] + self.P[ self.R[req_id][1], self.R[req_id][2] ]
            assert drop_off_time >= direct_travel, f"Solution: {solution}. \nFor Request {req_id}: Impossible for the Dropoff time ({drop_off_time}) to be less than the Direct travel time ({direct_travel}).\nPickup Time = {pick_up_times[req_id]}\nRequests = {self.R}\nP Matrix = {self.P}"
            
        return True


class State:
    
    def __init__(self, request = None, vehicles = None, path_cost = None, problem = None ):
        self.request = request
        self.vehicles = vehicles
        self.path_cost = path_cost
        self.problem = problem
        
    def vehicle_space_left(self, veh_id):
        avilable_space = self.problem.V[veh_id]
        
        for req_id in self.vehicles[veh_id][2]:
            avilable_space -= self.problem.R[req_id][-1]
        
        return avilable_space
    
    def __eq__(self, state):
        # all_vehicle_states_equal = False
        
        # for vehicle, vehicle_values in enumerate(self.vehicles):
        #     if set(vehicle_values["passengers"]) != set(state.vehicles[vehicle]["passengers"]):
        #         break
        # else:
        #     all_vehicle_states_equal = True
        
        # return isinstance(state, State) and ( set(self.request) == set(state.request) ) and all_vehicle_states_equal and (self.path_cost == state.path_cost)
        # return True if (self.path_cost == state.path_cost) else False
        equal = False
        
        if set(self.request) == set(state.request):
            for veh, veh_values in enumerate(self.vehicles):
                if ( set(veh_values[2]) != set(state.vehicles[veh][2]) ) or ( veh_values[0] != state.vehicles[veh][0] ) or ( veh_values[1] != state.vehicles[veh][1] ):
                    break
            else:
                if self.path_cost == state.path_cost:
                    equal = True
                
        
        return equal
    
    def __lt__(self, state):
        # less_than = False
        
        # if len(self.request) < len(state.request):
        #     less_than = True
        # else:
        #     for veh, veh_values in enumerate(self.vehicles):
        #         if len(veh_values["passengers"]) < len(state.vehicles[veh]["passengers"]):
        #             less_than = True
        #             break
        
        # if (self == state) and (self.path_cost < state.path_cost):
        #     less_than = True
        
        # return less_than
        return True if (self.path_cost < state.path_cost) else False
    
    def compute_path_cost(self, previous_state, action):
        _, veh_id, req_id, action_time = action
        
        if action[0] == 'Pickup':
            # Step cost = Pickup Time - Expected PickUp Time
            step_cost = action_time - self.problem.R[req_id][0]
            # step_cost = action_time
            # step_cost = 0
        
        elif action[0] == 'Dropoff':
            pick_up_time_id = previous_state.vehicles[veh_id][2].index(req_id)
            pick_up_time = previous_state.vehicles[veh_id][3][pick_up_time_id]
            
            # Step cost = Dropoff Time - (Pickup Time + Time of Direct Travel)
            step_cost = action_time - ( pick_up_time + self.problem.P[ self.problem.R[req_id][2], self.problem.R[req_id][1] ] )
            # step_cost = action_time - ( self.problem.R[req_id][0] + self.problem.P[ self.problem.R[req_id][2], self.problem.R[req_id][1] ] )
            # step_cost = 0
        
        # Path cost of previous state + time to travel from previous state to new state
        # self.path_cost = previous_state.path_cost + ( self.vehicles[veh_id][0] - previous_state.vehicles[veh_id][0] )
        self.path_cost = previous_state.path_cost + step_cost
    
    
    def __hash__(self):
        return hash(self.id)
    
    def __deepcopy__(self, memo):
        new_inst = type(self).__new__(self.__class__)  # skips calling __init__
        new_inst.problem = self.problem  # just assign

        # rinse and repeat this for other attrs that need to be deepcopied:
        new_inst.request = copy.deepcopy(self.request, memo)
        new_inst.vehicles = copy.deepcopy(self.vehicles, memo)
        new_inst.path_cost = copy.deepcopy(self.path_cost, memo)
        return new_inst
    
    @property
    def id(self):
        
        id_value = [tuple(set(self.request))]
        for _, vehicle_values in enumerate(self.vehicles):
            id_value.append( tuple( [ vehicle_values[0], vehicle_values[1], tuple(set(vehicle_values[2])) ] ) )
            
        return tuple(id_value)
    
    def __str__(self) -> str:
        return f"""
=================================================
Requests: {self.request}.
Vehicles: 
{self.vehicles}
=================================================
"""

    