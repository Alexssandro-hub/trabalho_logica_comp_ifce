import numpy as np
from z3 import *

def solve_tower_problem(dimensions, configuration):
    rows, cols = dimensions
    s = Solver()

    # Criação de variáveis proposicionais
    towers_left = [[Int(f't{i}_{j}_e') for j in range(cols)] for i in range(rows)]
    towers_down = [[Int(f't{i}_{j}_b') for j in range(cols)] for i in range(rows)]
    towers_right = [[Int(f't{i}_{j}_d') for j in range(cols)] for i in range(rows)]
    towers_up = [[Int(f't{i}_{j}_c') for j in range(cols)] for i in range(rows)]

    # Restrições para garantir que cada torre atire em apenas uma direção
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
                # Cada torre atira em pelo menos uma direção
                s.add(Or(towers_left[i][j] > 0, towers_down[i][j] > 0, towers_right[i][j] > 0, towers_up[i][j] > 0))

                # Cada configuração de tiro deve eliminar pelo menos um atacante
                attackers_in_row = Or([towers_left[k][j] > 0 for k in range(rows)] + [towers_up[i][k] > 0 for k in range(cols)])
                attackers_in_col = Or([towers_left[k][j] > 0 for k in range(rows)] + [towers_up[i][k] > 0 for k in range(cols)])

                s.add(Implies(configuration[i][j] == 'n', Or(attackers_in_row, attackers_in_col)))

                # Restrições para evitar que as torres se destruam mutuamente
                neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                for ni, nj in neighbors:
                    if 0 <= ni < rows and 0 <= nj < cols and configuration[ni][nj] == 'T':
                        for k in range(rows):
                            s.add(Implies(towers_left[i][j] > 0, towers_left[k][nj] == 0))
                            s.add(Implies(towers_down[i][j] > 0, towers_down[k][nj] == 0))
                            s.add(Implies(towers_right[i][j] > 0, towers_right[k][nj] == 0))
                            s.add(Implies(towers_up[i][j] > 0, towers_up[k][nj] == 0))

    # Verifica se é possível satisfazer as restrições
    check_result = s.check()

    if check_result == sat:
        model = s.model()
        # Gera a saída do jogo
        solution = np.full((rows, cols), '.', dtype=str)
        for i in range(rows):
            for j in range(cols):
                if configuration[i][j] == 'T':
                    if is_true(model.eval(towers_left[i][j] > 0)):
                        solution[i][j] = '1'
                    elif is_true(model.eval(towers_down[i][j] > 0)):
                        solution[i][j] = '2'
                    elif is_true(model.eval(towers_right[i][j] > 0)):
                        solution[i][j] = '3'
                    elif is_true(model.eval(towers_up[i][j] > 0)):
                        solution[i][j] = '4'
                elif configuration[i][j] == '#':
                    solution[i][j] = '#'
                elif configuration[i][j] == 'n':
                    solution[i][j] = 'n'
        return solution
    else:
        print(f"Não foi possível satisfazer as restrições. Resultado do check: {check_result}")
        return None

# Exemplo de uso
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
