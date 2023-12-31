import solution

autoScheduler = solution.FleetProblem()

f = open("input.txt", 'r')
autoScheduler.load(f)
f.close()

print(autoScheduler)

sol = [("Pickup", 0, 3, 30.0), ("Pickup", 1, 4, 25.0), ("Pickup", 1, 0, 25.0),
       ("Dropoff", 1, 4, 75.0), ("Dropoff", 1, 0, 75.0), ("Pickup", 0, 2, 30.0),
       ("Dropoff", 0, 3, 80.0), ("Pickup", 0, 1, 80.0), ("Dropoff", 0, 1, 140.0),
       ("Dropoff", 0, 2, 140.0)]

cost = autoScheduler.cost(sol)
print(f"The cost = {cost}")
