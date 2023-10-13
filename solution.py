import search
import numpy as np
import re, copy


class FleetProblem(search.Problem):
    """The class that defines the problem of an autonomous fleet scheduling.
    """
    
    def __init__(self):
        """The function that defines the initial state of the problem
        """
        
        self.P = []
        self.no_of_points = 0
        
        self.R = {}
        self.no_of_requests = 0
        
        self.V = []
        self.no_of_vehicles = 0
        
        self.initial = State()
        self.goal = State()

    def load(self, fh):
        """Loading of scheduling input data from a file handle.

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
    
    def __str__(self):
        """The function that defines the output when the class is to be printed
        """
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
    
    # ASSIGNMENT 2 ADDITIONS
    def create_initial_goal_states(self):
        """Creating the initial state and the goal state for the given problem"""
        self.initial = State(request= [i for i, _ in self.R.items()], 
                             vehicles=[ [0, 0, [], []] for _ in range(len(self.V)) ], # Time, Location, Passengers in Vehicle, Pickup Time of Passengers
                             path_cost= 0,
                             problem=self)
        
        self.goal = State(request=[], 
                          vehicles=[ [None, None, [], []] for id in range(len(self.V)) ], # Time, Location, Passengers, Pickup Time
                          path_cost= 0,
                          problem=self) # Not used for the current problem.
    
    def result(self, state, action):
        """A function to obtain the result of an action on a state.

        Args:
            state (State): previous state of the world
            action (list(tuples)): action taken by the agent

        Returns:
            state (State): new state of the world due to the agent action on the previous state
        """
        
        action_, veh_id, req_id, action_time = action
        
        new_state = copy.deepcopy(state) # Making deep copy of the previous state to avoid referencing same objects
        
        if action_ == 'Pickup':
            
            # Request Adjustments
            new_state.request.remove( req_id ) # Remove the picked-up request id from the child state
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[veh_id][0] = action_time # Pickup time
            new_state.vehicles[veh_id][1] = self.R[req_id][1] # Pickup Location
            
            # Passenger Parameters Adjustments
            new_state.vehicles[veh_id][2].append( req_id ) # Adding the new passengers to the vehicle
            new_state.vehicles[veh_id][3].append( action_time ) # Adding the pickup time of the new passengers
            
        elif action_ == 'Dropoff':
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[veh_id][0] = action_time #Dropoff time
            new_state.vehicles[veh_id][1] = self.R[req_id][2] #Dropoff Location
            
            # Passenger Parameters Adjustments
            ind = state.vehicles[veh_id][2].index( req_id ) # Getting the index of the passenger
            new_state.vehicles[veh_id][2].pop( ind ) # Removing the passengers from the vehicle
            new_state.vehicles[veh_id][3].pop( ind ) # Removing the corresponding pickup time
        
        new_state.compute_path_cost(state, action)
        
        return new_state
    
    def actions(self, state):
        """A function to get all actions possible in a given state

        Args:
            state (State): current state of the environment

        Yields:
            tuple: possible actions by the agent. 
                        A tuple of ("Pickup/Dropoff", Vehicle ID, Request ID, Action Completion Time)
        """
        
        for veh_id, veh_values in enumerate(state.vehicles): # Getting possible actions for each vehicle
            
            if len(veh_values[2]) != 0: # Checking if the vehicle is carrying any passenger
                
                for req_id in state.vehicles[veh_id][2]: 
                    
                    # Current veh time + time to move from current position to dropoff point.
                    drop_off_time = veh_values[0] + self.P[ self.R[req_id][2], veh_values[1] ]
                    yield ("Dropoff", veh_id, req_id, drop_off_time) # Dropping off passengers onboard.
                    
            for req_id in state.request: # Checking for available requests
                
                if state.vehicle_space_left(veh_id) >= self.R[req_id][3]: # Checking if there is space for the passengers in the vehicle
                    
                    pick_up_loc = self.R[req_id][1] # Pickup Location of Request
                    requested_pick_up_time = self.R[req_id][0] # Pickup Time of Request
                    
                    # Current veh time + time from current veh location to pickup location
                    arrival_time = veh_values[0] + self.P[ veh_values[1], pick_up_loc ]
                    t = requested_pick_up_time if arrival_time < requested_pick_up_time else arrival_time
                    
                    yield ("Pickup", veh_id, req_id, t )  # Picking up the passengers
    
    def goal_test(self, state):
        """_summary_

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        
        expanded_actions = self.actions(state)
        if len( list(expanded_actions) ) == 0:
            return True
        else:
            return False
    
    def path_cost(self, c, state1, action, state2):
        """_summary_

        Args:
            c (float): _description_
            state1 (State): _description_
            action (tuple): _description_
            state2 (State): _description_

        Returns:
            float: _description_
        """
        return state2.path_cost
    
    def solve(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        
        goal_node = search.uniform_cost_search(self, display=True)
        
        return goal_node.solution()


class State:
    """_summary_
    """
    
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
        """_summary_

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        
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
        """_summary_

        Args:
            state (_type_): _description_

        Returns:
            _type_: _description_
        """
        return True if (self.path_cost < state.path_cost) else False
    
    def compute_path_cost(self, previous_state, action):
        """_summary_

        Args:
            previous_state (_type_): _description_
            action (_type_): _description_
        """
        
        _, veh_id, req_id, action_time = action
        
        if action[0] == 'Pickup':
            # Step cost = Pickup Time - Expected PickUp Time
            step_cost = action_time - self.problem.R[req_id][0]
        
        elif action[0] == 'Dropoff':
            pick_up_time_id = previous_state.vehicles[veh_id][2].index(req_id)
            pick_up_time = previous_state.vehicles[veh_id][3][pick_up_time_id]
            
            # Step cost = Dropoff Time - (Pickup Time + Time of Direct Travel)
            step_cost = action_time - ( pick_up_time + self.problem.P[ self.problem.R[req_id][2], self.problem.R[req_id][1] ] )
        
        # Path cost of previous state + step_cost to travel from previous state to new state
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
        """_summary_

        Returns:
            _type_: _description_
        """
        
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


class Vehicle:
    
    def __init__(self, time = 0, loc = 0, capacity = 0, passengers = [], pickup_times = []):
        self.time = time
        self.loc = loc
        self.capacity = capacity
        self.space_left = capacity
        self.passengers = passengers
        self.pickup_times = pickup_times
        
    def pickup_passengers(self, passenger_amount):
        pass
    
    def drop_off_passengers(self, passenger_amount):
        pass

