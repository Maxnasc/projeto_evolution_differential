import random
import math
import statistics


def get_opposite(base, top, xi):
    return (top + base) - xi


def initialize(m, data_config, opposition):
    if opposition:
        x = []
        for i in range(int(m / 2)):
            xa = [
                random.uniform(
                    data_config.get("range").get("x1").get("base"),
                    data_config.get("range").get("x1").get("top"),
                ),
                random.uniform(
                    data_config.get("range").get("x2").get("base"),
                    data_config.get("range").get("x2").get("top"),
                ),
            ]
            xb = [
                get_opposite(
                    data_config.get("range").get("x1").get("base"),
                    data_config.get("range").get("x1").get("top"),
                    xa[0],
                ),
                get_opposite(
                    data_config.get("range").get("x2").get("base"),
                    data_config.get("range").get("x2").get("top"),
                    xa[1],
                ),
            ]
            x.extend([xa, xb])
    else:
        x = [
            [
                random.uniform(
                    data_config.get("range").get("x1").get("base"),
                    data_config.get("range").get("x1").get("top"),
                ),
                random.uniform(
                    data_config.get("range").get("x2").get("base"),
                    data_config.get("range").get("x2").get("top"),
                ),
            ]
            for i in range(m)
        ]

    return x


def shubert(x1, x2):
    sum1 = sum(i * math.cos((i + 1) * x1 + i) for i in range(1, 6))
    sum2 = sum(i * math.cos((i + 1) * x2 + i) for i in range(1, 6))
    return sum1 * sum2


def camel(x1, x2):
    term1 = (4 - 2.1 * x1**2 + x1**4 / 3) * x1**2
    term2 = x1 * x2
    term3 = (-4 + 4 * x2**2) * x2**2
    return term1 + term2 + term3


def get_r():
    return random.random()


def run_function(data_config, variables):
    if data_config.get("problem") == "shubert":
        return [1 / (shubert(x[0], x[1]) + 200) for x in variables]
    else:
        return [1 / (camel(x[0], x[1]) + 200) for x in variables]


def select_fathers(X):
    return random.sample(X, 3)


def get_best_result(scores):
    best_idx = max(scores.items(), key=lambda item: item[1])[0]
    best_value = (1 / scores[best_idx]) - 200  # Corrigir a volta da translação
    return best_value


def get_mean_fitness(scores):
    mean_fitness = statistics.mean(scores.values())
    mean_fitness_tranformed = (1 / mean_fitness) - 200  # Corrigir a volta da translação
    return mean_fitness_tranformed


def get_metrics(best_results):
    return {
        "mean": statistics.mean(best_results),
        "median": statistics.median(best_results),
        "max": max(best_results),
        "min": min(best_results),
    }


def run_differential_evolution(generations, m, data_config, F, CR, opposition):
    x = initialize(m, data_config, opposition)
    scores = run_function(data_config, x)
    best_subects = []

    for gen in range(generations):
        best_subects.append((1 / max(scores)) - 200) 

        if opposition:
            for i in range(int(len(x) / 2)):
                r1, r2, r3 = select_fathers(x)
                var_selected = random.choice([0, 1])
                trial = []
                for j, xij in enumerate(x[i]):
                    if random.random() < CR or j == var_selected:
                        trial.append(r1[j] + F * (r3[j] - r2[j]))
                        trial[j] = max(min(trial[j],
                                           data_config["range"][f"x{j+1}"]["top"]),
                                       data_config["range"][f"x{j+1}"]["base"])
                    else:
                        trial.append(xij)
                score_trial = run_function(data_config, [trial])[0]
                if score_trial > scores[i]: # (busca pelo maior score transformado)
                    x[i] = trial
                    scores[i] = score_trial 

            for i in range(int(len(x) / 2) + 1, len(x)):
                trial = [
                    get_opposite(data_config["range"]["x1"]["base"],
                                 data_config["range"]["x1"]["top"], x[i][0]),
                    get_opposite(data_config["range"]["x2"]["base"],
                                 data_config["range"]["x2"]["top"], x[i][1])
                ]
                score_trial = run_function(data_config, [trial])[0]
                if score_trial > scores[i]: 
                    x[i] = trial
                    scores[i] = score_trial 
        else:
            for i in range(len(x)):
                r1, r2, r3 = select_fathers(x)
                var_selected = random.choice([0, 1])
                trial = []
                for j, xij in enumerate(x[i]):
                    if random.random() < CR or j == var_selected:
                        trial.append(r1[j] + F * (r3[j] - r2[j]))
                        trial[j] = max(min(trial[j],
                                           data_config["range"][f"x{j+1}"]["top"]),
                                       data_config["range"][f"x{j+1}"]["base"])
                    else:
                        trial.append(xij)
                score_trial = run_function(data_config, [trial])[0]
                if score_trial > scores[i]: 
                    x[i] = trial
                    scores[i] = score_trial 

    return min(best_subects), best_subects


if __name__ == "__main__":
    g = 100
    m = 100
    data_config = {
        "problem": "shubert",
        "range": {
            "x1": {"base": -10, "top": 10},
            "x2": {"base": -10, "top": 10},
        },
    }
    F = 2
    CR = 0.8
    opposition = False
    score = run_differential_evolution(g, m, data_config, F, CR, opposition)
    print(score)
