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
    working_hours = 570

    # Create the model.
    model = cp_model.CpModel()

    # Variables
    start_vars = []
    end_vars = []
    intervals = []


    #Se inician los dominios
    ###Nota 1: Se define en primera instancia los inicios y fin como el límiite de tiempo general menos el tiempo de delivery de cada tarea.
    for i in range(len(orders)):
        start_vars.append(model.NewIntVar(0, working_hours, 'start_%i' % i))

        end_vars.append(model.NewIntVar(0, working_hours, 'end_%i' % i))
        intervals.append(model.NewIntervalVar(start_vars[i], pj[i], end_vars[i], 'interval_%i' % i))
    

    #Iniciamos las restricciones
    ###Nota 2:Se definen las restricciones, debido a que una entrega se puede definir como que se puede hacer siempre y cuando el tiempo de delivery y el tiempo de ejecución se pueda hacer antes del tiempo definido, entonces se define dos variables que cuando el tiempo de delivery es tarde significa que ya no se puede entregar el trabajo y se pospone. Esto nos sirve para añadir al cumulado de la penalización de costo por posponer.
    model.AddCumulative(intervals,[1]*len(orders),num_employees)
    penalties = []
    list_l = []

    for i in range(len(orders)):
        late_delivery = model.NewBoolVar('late_delivery_%i' % i)
        early_delivery = model.NewBoolVar('early_delivery_%i' % i)

        model.Add(start_vars[i]+pj[i] > working_hours-lj[i]).OnlyEnforceIf(late_delivery)
        model.Add(start_vars[i]+pj[i] <= working_hours-lj[i]).OnlyEnforceIf(late_delivery.Not())
        model.Add(end_vars[i]==start_vars[i]).OnlyEnforceIf(late_delivery)
        model.Add(end_vars[i]==start_vars[i]+pj[i]).OnlyEnforceIf(late_delivery.Not())

        model.Add(start_vars[i]+int(0.8*pj[i]) <= working_hours-lj[i]).OnlyEnforceIf(early_delivery)
        model.Add(start_vars[i]+int(0.8*pj[i]) > working_hours-lj[i]).OnlyEnforceIf(early_delivery.Not())
        model.Add(end_vars[i]>=start_vars[i]+int(0.8*pj[i])).OnlyEnforceIf(early_delivery)
        model.Add((end_vars[i])==(start_vars[i])).OnlyEnforceIf(early_delivery.Not())

        list_l.append(late_delivery)
        list_l.append(early_delivery)
        penalties.append(w1j[i]*late_delivery + w2j[i]*early_delivery.Not())

    #Se define el objetivo del modelo
    ##Debido a que el objetivo del modelo es minimizar los costos, se coloca a minimizar la sumatoria total de costos que permitió pasar las restricciones
    ### Nota 3: Luego se usa un pequeño artifico de "range_penalty" con la intención de permitir al objetivo que pueda tomar valores entre 0 a 1000, con la finalidad que se pueda ejecutar el problema con 480 minutos y que el límite de la sumatoria sea alto.
    obj_var = model.NewIntVar(0, working_hours, 'obj_var')

    model.AddMaxEquality(obj_var, end_vars)
    model.Minimize(sum(penalties))

    
    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    final_result = [];

    if status == cp_model.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.ObjectiveValue())
        for i in range(len(orders)):
            print('Val %i, %i, %i' % (i,solver.Value(list_l[i*2]),solver.Value(list_l[i*2+1])))

        for i in range(len(orders)):
            print('Order %i starts at minute %i and ends at minute %i.' % (i,solver.Value(start_vars[i]),solver.Value(end_vars[i])))
            final_result.append(Problem(i,solver.Value(start_vars[i]),solver.Value(end_vars[i])))

    else:
        print('The problem does not have an optimal solution.')

    return sorted(final_result,key=lambda x: x.starts);

#Conclusiones
###Nota 1: Las rangos funcionan, pero se tiene que tomar en consideración la posibilidad de ser 0 del pj, esto con la finalidad del que el Accumulate pueda "actualizar" este valor en caso no se pueda ejecutar.
###Nota 2: Lógica errada, en un principio parecía estar bien, pero en la ejecución, nos damos cuenta que considera a todos como 1 y suma los w2j.
###Nota 3: El límite range_penalty no funciona. No lee el registro ya que solo suma w2j para todo momento.