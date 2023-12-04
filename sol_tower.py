import numpy as np
from z3 import *

def solve_tower_problem(dimensions, configuration):
    rows, cols = dimensions
    s = Solver()

    # Criação de variáveis proposicionais
    towers_left = [[Bool(f't{i}_{j}_e') for j in range(cols)] for i in range(rows)]
    towers_down = [[Bool(f't{i}_{j}_b') for j in range(cols)] for i in range(rows)]
    towers_right = [[Bool(f't{i}_{j}_d') for j in range(cols)] for i in range(rows)]
    towers_up = [[Bool(f't{i}_{j}_c') for j in range(cols)] for i in range(rows)]

    # Restrições para garantir que cada torre atire em apenas duas direção
    for i in range(rows):
        for j in range(cols):
          if configuration[i][j] == 'T':
            s.add(Xor(towers_left[i][j], towers_down[i][j]))
            s.add(Xor(towers_down[i][j], towers_right[i][j]))
            s.add(Xor(towers_right[i][j], towers_up[i][j]))
            s.add(Xor(towers_up[i][j], towers_left[i][j]))

    # Restrições
    for i in range(rows):
      for j in range(cols):
          if configuration[i][j] == 'T':
              # Cada configuração de tiro deve eliminar pelo menos um atacante
              attackers_in_row = Or([towers_left[k][j] for k in range(rows) if k != i] + [towers_right[k][j] for k in range(rows) if k != i])
              attackers_in_col = Or([towers_up[i][k] for k in range(cols) if k != j] + [towers_down[i][k] for k in range(cols) if k != j])

              s.add(And(Not(configuration[i][j] == 'n'), Or(attackers_in_row, attackers_in_col)));

              # Restrições para evitar que as torres se destruam mutuamente
              neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
              for ni, nj in neighbors:
                  if 0 <= ni < rows and 0 <= nj < cols and configuration[ni][nj] == 'T':
                      s.add(Implies(And(towers_left[i][j], towers_down[i][j]), Not(And(towers_right[ni][nj], towers_down[ni][nj])))) #towers_left[i][j], towers_right[ni][nj]
                      s.add(Implies(And(towers_down[i][j], towers_right[i][j]), Not(And(towers_up[ni][nj], towers_left[ni][nj])))) #towers_down[i][j], towers_up[ni][nj]
                      s.add(Implies(And(towers_right[i][j], towers_up[i][j]), Not(And(towers_left[ni][nj], towers_down[ni][nj])))) #towers_right[i][j], towers_left[ni][nj]
                      s.add(Implies(And(towers_up[i][j], towers_left[i][j]), Not(And(towers_down[ni][nj], towers_right[ni][nj])))) #towers_up[i][j], towers_down[ni][nj]

    check_result = s.check()

    if check_result == sat:
        model = s.model()
        solution = np.full((rows, cols), '.', dtype=str)
       
        for i in range(rows):
            for j in range(cols):
                if configuration[i][j] == 'T':
                    if ((is_true(model.eval(towers_down[i][j])) and (not is_true(model.eval(towers_left[i][j])))) and
                        ((not is_true(model.eval(towers_down[i][j]))) and is_true(model.eval(towers_left[i][j])))):
                        solution[i][j] = '1'

                    elif ((is_true(model.eval(towers_right[i][j])) and (not is_true(model.eval(towers_down[i][j])))) and 
                          ((not is_true(model.eval(towers_right[i][j]))) and is_true(model.eval(towers_down[i][j])))):
                        solution[i][j] = '2'

                    elif ((is_true(model.eval(towers_up[i][j])) and (not is_true(model.eval(towers_right[i][j])))) or
                          ((not is_true(model.eval(towers_up[i][j]))) and is_true(model.eval(towers_right[i][j])))):
                        solution[i][j] = '3'

                    else: solution[i][j] = '4'
                        
                elif configuration[i][j] == '#':
                    solution[i][j] = '#'
                elif configuration[i][j] == 'n':
                    solution[i][j] = 'n'
        return solution
    else:
        print(f"Não foi possível satisfazer as restrições. Resultado do check: {check_result}")
        return None


dimensions = (5, 9)
configuration = [
    ['.', 'n', '.', '.', 'T', '.', '.', 'n', '.'],
    ['.', 'T', '.', '.', 'n', '.', '.', '.', '.'],
    ['.', 'n', '.', '.', '#', '.', '.', 'n', '.'],
    ['.', '.', '.', '.', 'n', '.', '.', 'T', '.'],
    ['.', 'n', '.', '.', 'T', '.', '.', 'n', '.']
]

result = solve_tower_problem(dimensions, configuration)
if result is not None:
    for row in result:
        print(' '.join(row))
else:
    print("Não é possível atender a todas as restrições.")
