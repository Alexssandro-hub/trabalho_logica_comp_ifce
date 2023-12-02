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

    # Adiciona cláusulas para garantir que cada torre atire em apenas uma direção
    for i in range(rows):
        for j in range(cols):
            s.add(Implies(towers_left[i][j] > 0, And(towers_down[i][j] == 0, towers_right[i][j] == 0, towers_up[i][j] == 0)))
            s.add(Implies(towers_down[i][j] > 0, And(towers_left[i][j] == 0, towers_right[i][j] == 0, towers_up[i][j] == 0)))
            s.add(Implies(towers_right[i][j] > 0, And(towers_left[i][j] == 0, towers_down[i][j] == 0, towers_up[i][j] == 0)))
            s.add(Implies(towers_up[i][j] > 0, And(towers_left[i][j] == 0, towers_down[i][j] == 0, towers_right[i][j] == 0)))

    # Restrições
    for i in range(rows):
        for j in range(cols):
            if configuration[i][j] == 'T':
                index = [(i * cols + j) * 4 + k for k in range(4) if (i * cols + j) * 4 + k < len(tower_cannons)]  # Índices para as variáveis do canhão desta torre
                
                # Cada torre tem exatamente quatro canhões (cima, baixo, direita, esquerda)
                for k, dir in enumerate(['c', 'b', 'd', 'e']):
                    if index and index[0] + k < len(tower_cannons):
                        s.add(tower_cannons[index[0] + k][dir] >= 1, tower_cannons[index[0] + k][dir] <= 4)

                # Cada configuração de tiro deve eliminar pelo menos um atacante
                attacker_eliminated = Or(
                    And(configuration[i][j] == 'n', 
                        Or([Or(tower_cannons[index[0] + k][dir] == k + 1, tower_cannons[index[1] + k][dir] == k + 1) for k, dir in enumerate(['c', 'b']) if index and index[0] + k < len(tower_cannons)])),
                    And(configuration[i][j] == 'n', 
                        Or([Or(tower_cannons[index[0] + k][dir] == k + 1, tower_cannons[index[1] + k][dir] == k + 1) for k, dir in enumerate(['d', 'e']) if index and index[0] + k < len(tower_cannons)])),
                )

                s.add(attacker_eliminated)

                # Restrições para evitar que as torres se destruam mutuamente
                neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                for ni, nj in neighbors:
                    if 0 <= ni < rows and 0 <= nj < cols and configuration[ni][nj] == 'T':
                        neighbor_index = [(ni * cols + nj) * 4 + k for k in range(4) if (ni * cols + nj) * 4 + k < len(tower_cannons)]
                        for k, dir in enumerate(['c', 'b', 'd', 'e']):
                            s.add(Or([tower_cannons[index[0] + k][dir] != tower_cannons[n_idx + k][dir] for n_idx in neighbor_index if n_idx + k < len(tower_cannons)]))

    # Verifica se é possível satisfazer as restrições
    check_result = s.check()

    if check_result == sat:
        model = s.model()
        # Gera a saída do jogo
        solution = np.full((rows, cols), '.', dtype=str)
        for i in range(rows):
            for j in range(cols):
                if configuration[i][j] == 'T':
                    index = [(i * cols + j) * 4 + k for k in range(4) if (i * cols + j) * 4 + k < len(tower_cannons)]
                    for k, dir in enumerate(['c', 'b', 'd', 'e']):
                        solution[i][j] = str(model.eval(tower_cannons[index[0] + k][dir]))
        return solution
    else:
        print(f"Não foi possível satisfazer as restrições. Resultado do check: {check_result}")
        return None

# Exemplo de uso
dimensions = (5, 9)
configuration = [
    ['.', 'n', '.', '.', 'T', '.', '.', 'n', '.'],
    ['T', '.', '.', 'n', '.', '.', '.', '.', '.'],
    ['.', 'n', '.', '.', '#', '.', '.', 'n', '.'],
    ['.', '.', '.', 'n', '.', '.', 'T', '.', '.'],
    ['.', 'n', '.', '.', 'T', '.', '.', 'n', '.']
]

result = solve_tower_problem(dimensions, configuration)
if result is not None:
    for row in result:
        print(' '.join(row))
else:
    print("Não é possível atender a todas as restrições.")
