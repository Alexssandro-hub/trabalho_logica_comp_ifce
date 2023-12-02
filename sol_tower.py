import numpy as np
from z3 import *
from pysat.solvers import Glucose3

def create_tower_formula(dimensions, configuration):
    rows, cols = dimensions
    clauses = []

    for i in range(rows):
        for j in range(cols):
            if configuration[i][j] == 'T':
                index = f'tower_{i}_{j}'

                # Cada torre tem exatamente quatro canhões (cima, baixo, direita, esquerda)
                clauses.append([f'{index}_c', f'{index}_b', f'{index}_d', f'{index}_e'])

                # Cada configuração de tiro deve eliminar pelo menos um atacante
                clauses.append([f'{index}_c', f'{index}_d', f'n_{i}_{j}'])
                clauses.append([f'{index}_d', f'{index}_e', f'n_{i}_{j}'])
                clauses.append([f'{index}_e', f'{index}_c', f'n_{i}_{j}'])
                clauses.append([f'{index}_b', f'{index}_c', f'n_{i}_{j}'])

                # Restrições para evitar que as torres se destruam mutuamente
                neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                for ni, nj in neighbors:
                    if 0 <= ni < rows and 0 <= nj < cols and configuration[ni][nj] == 'T':
                        neighbor_index = f'tower_{ni}_{nj}'
                        clauses.append([f'{index}_c', f'{neighbor_index}_c'])
                        clauses.append([f'{index}_b', f'{neighbor_index}_b'])
                        clauses.append([f'{index}_d', f'{neighbor_index}_d'])
                        clauses.append([f'{index}_e', f'{neighbor_index}_e'])

    return clauses

def solve_with_pysat(dimensions, configuration):
    # Criação da fórmula
    formula = create_tower_formula(dimensions, configuration)

    print(formula)
    # Utilização do Glucose3 como solver
    with Glucose3() as solver:
        for clause in formula:
            solver.add_clause(clause)

        # Verifica a satisfatibilidade
        if solver.solve():
            model = solver.get_model()
            return model
        else:
            return None

# Exemplo de uso
dimensions = (3, 3)
configuration = [
    ['.', 'n', '.'],
    ['T', '.', 'T'],
    ['.', 'n', '.']
]

result = solve_with_pysat(dimensions, configuration)
if result is not None:
    print("Solução encontrada:")
    for item in result:
        print(item)
else:
    print("Não é possível atender a todas as restrições.")
