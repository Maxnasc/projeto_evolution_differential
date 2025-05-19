import random
import math

def get_opposite(base, top, xi):
    return (top + base) - xi

def initialize(m, data_config, opposition):
    x1_base, x1_top = data_config["range"]["x1"]["base"], data_config["range"]["x1"]["top"]
    x2_base, x2_top = data_config["range"]["x2"]["base"], data_config["range"]["x2"]["top"]

    if opposition:
        x = []
        for _ in range(m // 2):
            xa1 = random.uniform(x1_base, x1_top)
            xa2 = random.uniform(x2_base, x2_top)
            xb1 = get_opposite(x1_base, x1_top, xa1)
            xb2 = get_opposite(x2_base, x2_top, xa2)
            x.extend([[xa1, xa2], [xb1, xb2]])
        return x
    else:
        return [[random.uniform(x1_base, x1_top), random.uniform(x2_base, x2_top)] for _ in range(m)]

def shubert(x1, x2):
    sum1 = sum(i * math.cos((i + 1) * x1 + i) for i in range(1, 6))
    sum2 = sum(i * math.cos((i + 1) * x2 + i) for i in range(1, 6))
    return sum1 * sum2

def camel(x1, x2):
    term1 = (4 - 2.1 * x1**2 + x1**4 / 3) * x1**2
    term2 = x1 * x2
    term3 = (-4 + 4 * x2**2) * x2**2
    return term1 + term2 + term3

def run_function(data_config, variables):
    problem = data_config["problem"]
    if problem == "shubert":
        return [(1 / (shubert(x[0], x[1]) + 200)) for x in variables]
    else:
        return [(1 / (camel(x[0], x[1]) + 200)) for x in variables]

def rank_population(population, scores):
    indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return [population[i] for i in indices], [scores[i] for i in indices]

def mutate(cl, gamma_seed, data_config, fit):
    x1_base, x1_top = data_config['range']['x1']['base'], data_config['range']['x1']['top']
    x2_base, x2_top = data_config['range']['x2']['base'], data_config['range']['x2']['top']
    range_x1 = x1_top - x1_base
    range_x2 = x2_top - x2_base

    gamma_x1 = gamma_seed * range_x1
    gamma_x2 = gamma_seed * range_x2
    alfa_x1 = gamma_x1 * math.exp(-fit)
    alfa_x2 = gamma_x2 * math.exp(-fit)

    new_x1 = min(x1_top, max(x1_base, cl[0] + random.uniform(-alfa_x1, alfa_x1)))
    new_x2 = min(x2_top, max(x2_base, cl[1] + random.uniform(-alfa_x2, alfa_x2)))
    return [new_x1, new_x2]

def run_clonal_g(generations, P, SR, CR, gama_seed, data_config, opposition):
    x = initialize(P, data_config, opposition)
    scores = run_function(data_config, x)
    x, scores = rank_population(x, scores)

    best_subjects = []

    for _ in range(generations):
        best_subjects.append((1 / max(scores)) - 200)

        for i in range(round(SR * P)):
            score_i = scores[i]
            nc = round((CR * P) / score_i)
            fit = 1 - ((score_i - 1) / (P - 1))

            mutated_clones = [mutate(x[i], gama_seed, data_config, fit) for _ in range(nc)]
            clone_scores = run_function(data_config, mutated_clones)

            best_idx = max(range(len(clone_scores)), key=lambda j: clone_scores[j])
            if clone_scores[best_idx] > score_i:
                x[i] = mutated_clones[best_idx]
                scores[i] = clone_scores[best_idx]

        num_second_pop = P - round(SR * P)
        second_population = initialize(num_second_pop, data_config, opposition)
        second_scores = run_function(data_config, second_population)

        for i in range(num_second_pop):
            x[round(SR * P) + i] = second_population[i]
            scores[round(SR * P) + i] = second_scores[i]

        x, scores = rank_population(x, scores)

    return min(best_subjects), best_subjects

if __name__ == "__main__":
    data_config = {
        "problem": "shubert",
        "range": {
            "x1": {"base": -10, "top": 10},
            "x2": {"base": -10, "top": 10},
        },
    }
    score, bests = run_clonal_g(generations=30, P=100, SR=0.8, CR=0.8, gama_seed=0.8, data_config=data_config, opposition=False)
    print(score)
