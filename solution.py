import re, math
import numpy as np
import search


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
Number of Requests: {self.no_of_requests}.
Number of Vehicles: {self.no_of_vehicles}.
=================================================
"""
    
    # ASSIGNMENT 2 ADDITIONS
    def create_initial_goal_states(self):
        """Creating the initial state and the goal state for the given problem"""
        self.initial = State(request= [i for i, _ in self.R.items()],
                             vehicles=[ Vehicle(time=0,
                                                loc=0,
                                                space_left=veh_capacity, # Initial space is the vehicle capacity.
                                                capacity=veh_capacity, # Vehicle capacity.
                                                passengers=[], # The passengers onboard the vehicle (defined in terms of request IDs)
                                                pickup_times=[], # The time at which the passengers are taken onboard the vehicle
                                                ) for veh_capacity in self.V ], # Creating Vehicle object for each vehicle
                             path_cost= 0,
                             problem=self)
        
        self.initial.compute_hash() # Computing the hash of the initial state
        # self.initial.compute_heuristic()
        
        self.goal = State(request= [],
                          vehicles= [ Vehicle() for _ in self.V ], # Creating vehicle objects with empty passengers.
                          path_cost= None,
                          problem= self) # Not used for the current problem.
    
    def result(self, state, action):
        """A function to obtain the result of an action on a state.

        Args:
            state (State): previous state of the world
            action (list(tuples)): action taken by the agent

        Returns:
            state (State): new state of the world due to the agent action on the previous state
        """
        
        action_, veh_id, req_id, action_time = action
        
        # new_state = copy.deepcopy(state) # Making deep copy of the previous state to avoid referencing same objects
        new_state = State(request=state.request[:],
                          vehicles=[ Vehicle(
                              time=state.vehicles[veh_id].time,
                              loc=state.vehicles[veh_id].loc,
                              space_left = state.vehicles[veh_id].space_left,
                              capacity = state.vehicles[veh_id].capacity,
                              passengers=state.vehicles[veh_id].passengers[:],
                              pickup_times=state.vehicles[veh_id].pickup_times[:]
                              ) for veh_id, _ in enumerate(self.V) ],
                          problem=self)
        
        if action_ == 'Pickup':
            
            # Request Adjustments
            new_state.request.remove( req_id ) # Remove the picked-up request id from the child state
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[veh_id].time = action_time # Pickup time
            new_state.vehicles[veh_id].loc = self.R[req_id][1] # Pickup Location
            new_state.vehicles[veh_id].space_left = state.vehicles[veh_id].space_left - self.R[req_id][3]
            
            # Passenger Parameters Adjustments
            new_state.vehicles[veh_id].passengers.append( req_id ) # Adding the new passengers to the vehicle
            new_state.vehicles[veh_id].pickup_times.append( action_time ) # Adding the pickup time of the new passengers
            
        elif action_ == 'Dropoff':
            
            # Vehicle Parameters Adjustments
            new_state.vehicles[veh_id].time = action_time #Dropoff time
            new_state.vehicles[veh_id].loc = self.R[req_id][2] #Dropoff Location
            new_state.vehicles[veh_id].space_left = state.vehicles[veh_id].space_left + self.R[req_id][3]
            
            # Passenger Parameters Adjustments
            ind = state.vehicles[veh_id].passengers.index( req_id ) # Getting the index of the passenger
            new_state.vehicles[veh_id].passengers.pop( ind ) # Removing the passengers from the vehicle
            new_state.vehicles[veh_id].pickup_times.pop( ind ) # Removing the corresponding pickup time
        
        new_state.compute_path_cost(state, action)
        new_state.compute_hash()
        # new_state.compute_heuristic()
        
        return new_state
    
    def actions(self, state):
        """A function to get all actions possible in a given state

        Args:
            state (State): current state of the environment

        Yields:
            tuple: possible actions by the agent. 
                        A tuple of ("Pickup/Dropoff", Vehicle ID, Request ID, Action Completion Time)
        """
        
        for veh_id, veh_values in sorted(enumerate(state.vehicles), key=lambda val: val[1].capacity, reverse=False): # Getting possible actions for each vehicle
            
            if len(veh_values.passengers) != 0: # Checking if the vehicle is carrying any passenger
                
                for req_id in veh_values.passengers:
                    
                    # Current veh time + time to move from current position to dropoff point.
                    drop_off_time = veh_values.time + self.P[ self.R[req_id][2], veh_values.loc ]
                    yield ("Dropoff", int(veh_id), int(req_id), float(drop_off_time) ) # Dropping off passengers onboard.
                    
            for req_id in state.request: # Checking for available requests
                
                if state.vehicles[veh_id].space_left >= self.R[req_id][3]: # Checking if there is space for the passengers in the vehicle
                    
                    pick_up_loc = self.R[req_id][1] # Pickup Location of Request
                    requested_pick_up_time = self.R[req_id][0] # Pickup Time of Request
                    
                    # Current veh time + time from current veh location to pickup location
                    arrival_time = veh_values.time + self.P[ veh_values.loc, pick_up_loc ]
                    t = requested_pick_up_time if arrival_time < requested_pick_up_time else arrival_time

                    yield ("Pickup", veh_id, req_id, t)  # Picking up the passengers







    def goal_test(self, state):
        """A function to check for a goal state in the environment

        Args:
            state (State): current state of the environment

        Returns:
            bool: True if the state is a goal state else False.
        """
        
        # Checking if the current state could have any further actions.
        # At goal: all requests have been picked up and no passenger is onboard any vehicle. Hence, no possible action.
        return True if len( list(self.actions(state)) ) == 0 else False
    
    def path_cost(self, c, state1, action, state2):
        """A function to obtain the path cost of a state

        Args:
            c (float): path cost of previous state
            state1 (State): previous state of the environment
            action (tuple): action taken to reach the current state
            state2 (State): current state of the environment

        Returns:
            float: path cost to reach the current state
        """
        return state2.path_cost

    def solve(self, display_solutions = False):
        """A function to call a solver for the search problem

        Returns:
            list: a list of all actions taken to reach the goal
        """

        
        
        if display_solutions:
            goal_node = search.astar_search(self, display=True)
            print(f"Cost: {self.cost(goal_node.solution())}")
            print(f"Goal Estimates: {[node.f for node in goal_node.path()[1:]]}")
            print(f"Solution: {goal_node.solution()}")
        else:
            goal_node = search.astar_search(self, display=False)
        
        return goal_node.solution()
    
    #ASSIGNMENT 3
    def h(self, node):

        #the request fulfillment times for all requests
        request_fulfillment_times = np.empty(len(node.state.request))
        
        for i, req_id in enumerate(node.state.request):
            pickup_loc = self.R[req_id][1] # pickup location
            dropoff_loc = self.R[req_id][2] # dropoff location
            fullfilment_times = []
            if self.no_of_vehicles >=5:
                for veh_id in range(self.no_of_vehicles):
                    # request_fulfillment_time = node.state.vehicles[veh_id].time + self.P[node.state.vehicles[veh_id].loc, pickup_loc] + self.P[node.state.vehicles[veh_id].loc, dropoff_loc]
                    request_fulfillment_time = node.state.vehicles[veh_id].time + self.P[node.state.vehicles[veh_id].loc, pickup_loc] + self.P[pickup_loc, dropoff_loc]
                    fullfilment_times.append(request_fulfillment_time)    
                    # request_fulfillment_times[i] = request_fulfillment_time
                request_fulfillment_times[i] = min(fullfilment_times)
            else:
                min_fullfilment_time = float('inf')
                for veh_id in range(self.no_of_vehicles):
                    request_fulfillment_time = node.state.vehicles[veh_id].time + self.P[node.state.vehicles[veh_id].loc, pickup_loc] 
                    min_fulfillment_time = min(min_fullfilment_time, request_fulfillment_time)
                request_fulfillment_times[i] = min_fulfillment_time

        #difference between request times and request fulfillment times
        request_times = np.array([self.R[req_id][0] for req_id in node.state.request])
        if self.no_of_vehicles>=5:
            delay = abs(request_fulfillment_times - request_times)
        else:
            delay = request_fulfillment_times - request_times
        delays = np.maximum(delay,0)

        # Sum up the delays for all requests
        return np.sum(delays)

    # END ASSIGNMENT 3


class State:
    """A class for the states of the environment
    """
    
    def __init__(self, request = None, vehicles = None, path_cost = None, problem = None ):
        """_summary_

        Args:
            request (list, optional): unfulfilled requests in the environment. Defaults to None.
            vehicles (list, optional): a list of Vehicle objects. Defaults to None.
            path_cost (float, optional): the total cost to reach the current state. Defaults to None.
            problem (FleetProblem, optional): the fleet problem to be solved. Defaults to None.
        """
        self.request = request
        self.vehicles = vehicles
        self.path_cost = path_cost
        self.problem = problem  

    def __eq__(self, state):
        return True if self.hash == state.hash else False
    
    def __lt__(self, state):
        return True if (self.path_cost < state.path_cost) else False
    
    def compute_path_cost(self, previous_state, action):
        """A function to compute the path cost to reach the current state

        Args:
            previous_state (State): previous state of the environment
            action (tuple): a tuple of action taken to reach the current state from previous state.
        """
        
        # The action variable contains: (Pickup/Dropoff, Vehicle ID, Request ID, Action Completion Time)
        _, veh_id, req_id, action_time = action
        
        if action[0] == 'Pickup':
            # Step cost = Pickup Time - Expected PickUp Time (i.e. step_cost is the pickup delay)
            step_cost = action_time - self.problem.R[req_id][0]
        
        elif action[0] == 'Dropoff':
            pick_up_time_id = previous_state.vehicles[veh_id].passengers.index(req_id)
            pick_up_time = previous_state.vehicles[veh_id].pickup_times[pick_up_time_id]
            
            # Step cost = Dropoff Time - (Pickup Time + Time of Direct Travel) => step_cost is delay in expected arrival time from pickup
            step_cost = action_time - ( pick_up_time + self.problem.P[ self.problem.R[req_id][2], self.problem.R[req_id][1] ] )
        
        # Path cost of previous state + step_cost to travel from previous state to new state
        self.path_cost = previous_state.path_cost + step_cost
    
    
    def __hash__(self):
        return self.hash
    
    def compute_hash(self):
        """Computing a identifier for the state.
            States that are exactly the same will give same output.
        """
        
        id_value = [tuple(set(self.request))] # Creating a list of [Unfilfilled Requests]
        
        for _, vehicle_values in enumerate(self.vehicles):
            # Appending the Requests onboard each vehicle to the list.
            id_value.append( tuple( [ vehicle_values.time, vehicle_values.loc, tuple(set(vehicle_values.passengers)) ] ) ) 
            
        self.hash = hash( tuple(id_value) ) # Converting to a hash.
    
    def __str__(self) -> str:
        return f"""
=================================================
Requests: {self.request}.
Vehicles: 
{[veh.__str__() for veh in self.vehicles]}
=================================================
"""


class Vehicle:
    """A class for vehicle information
    """
    
    def __init__(self, time = 0, loc = 0, space_left = 0, capacity = 0, passengers = None, pickup_times = None):
        """Initializing the parameters for the vehicle

        Args:
            time (int, optional): the current time elapsed by the vehicle. Defaults to 0.
            loc (int, optional): the current location of the vehicle in the environment. Defaults to 0.
            space_left (int, optional): amount of space left for passengers in the vehicle. Defaults to 0.
            passengers (list, optional): request IDs onboard the vehicle. Defaults to None.
            pickup_times (list, optional): the pickup time for the request IDs. Defaults to None.
        """
        self.time = time
        self.loc = loc
        self.space_left = space_left
        self.capacity = capacity
        self.passengers = passengers
        self.pickup_times = pickup_times
    
    def __str__(self):
        return f"Time: {self.time}, Location: {self.loc}, SpaceLeft: {self.space_left}, Passengers: {self.passengers}"
    
    def __lt__(self, vehicle):
        return True if self.time < vehicle.time else False
    
    def __eq__(self, vehicle):
        return True if self.time == vehicle.time else False
        

