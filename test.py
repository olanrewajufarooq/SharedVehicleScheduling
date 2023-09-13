import solution

autoScheduler = solution.FleetSearch()

f = open("input.txt", 'r')
autoScheduler.load(f)
f.close()

sol = []
cost = autoScheduler.cost(sol)
print(f"The cost = {cost}")
