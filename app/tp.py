from ortools.sat.python import cp_model

class Problem:
    def __init__(self,id,starts,ends) -> None:
        self.id=id;
        self.starts=starts;
        self.ends=ends;

def solveConstraintProblem():
    # Problem data
    orders = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    pj = [140, 80, 160, 120, 160, 120, 130, 100, 40, 140, 160, 60]
    rj = [20, 30, 40, 50, 100, 10, 20, 40, 100, 10, 50, 20]
    lj = [120 ,150 ,170 ,100 ,140 ,100 ,150 ,230 ,100 ,90 ,180 ,280]
    w1j = [100 ,80 ,120 ,100 ,80 ,120 ,120 ,90 ,100 ,80 ,150 ,130]
    w2j = [30 ,20 ,40 ,20 ,10 ,30 ,40 ,10 ,40 ,20 ,30 ,50]

    num_employees = 3
    working_hours = 650

    # Create the model.
    model = cp_model.CpModel()

    # Variables
    start_vars = []
    end_vars = []
    intervals = []

    for i in range(len(orders)):
        start_vars.append(model.NewIntVar(0, working_hours - lj[i], 'start_%i' % i))
        end_vars.append(model.NewIntVar(0, working_hours - lj[i], 'end_%i' % i))
    #intervals.append(model.NewIntervalVar(start_vars[i], pj[i], end_vars[i], 'interval_%i' % i))
    # Additional variables for postponing and speeding up
    postpone_vars = []
    speedup_vars = []
    for i in range(len(orders)):
        postpone_vars.append(model.NewBoolVar('postpone_%i' % i))
        speedup_vars.append(model.NewBoolVar('speedup_%i' % i))

    for i in range(len(orders)):
        intervals.append(model.NewIntervalVar(start_vars[i], pj[i], end_vars[i], 'interval_%i' % i))
    # Constraints
    model.AddCumulative(intervals,[1]*len(orders),num_employees)
    # Postponing tasks
    for i in range(len(orders)):
        model.Add(start_vars[i] >= working_hours).OnlyEnforceIf(postpone_vars[i])
    # Speed
    penalties = []
    for i in range(len(orders)):
        late_delivery = model.NewBoolVar('late_delivery_%i' % i)
        model.Add(end_vars[i] > working_hours).OnlyEnforceIf(late_delivery)
        model.Add(end_vars[i] <= working_hours).OnlyEnforceIf(late_delivery.Not())

        early_delivery = model.NewBoolVar('early_delivery_%i' % i)
        model.Add(end_vars[i] < working_hours).OnlyEnforceIf(early_delivery)
        model.Add(end_vars[i] >= working_hours).OnlyEnforceIf(early_delivery.Not())

        penalties.append(w1j[i]*late_delivery + w2j[i]*early_delivery)


    obj_var = model.NewIntVar(0, working_hours, 'obj_var')
    model.AddMaxEquality(obj_var, end_vars)

    range_penalty = model.NewIntVar(0, 1000, 'range_penalty')
    model.Add(range_penalty == sum(penalties))


    model.Minimize(range_penalty)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    final_result = [];

    if status == cp_model.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.ObjectiveValue())
        for i in range(len(orders)):
            final_result.append(Problem(i,solver.Value(start_vars[i]),solver.Value(end_vars[i])))
            print('Order %i starts at minute %i and ends at minute %i.' % (i,solver.Value(start_vars[i]),solver.Value(end_vars[i])))
    else:
        print('The problem does not have an optimal solution.')

    return sorted(final_result,key=lambda x: x.starts);