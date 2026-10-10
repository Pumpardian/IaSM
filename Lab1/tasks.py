import random

def task_1(event_probability: int) -> list[bool]:
    chance = event_probability / 100
    return random.choices([True, False], (chance, 1 - chance), k=1000000)


def task_2(event_probabilities: list[float]) -> list[list[bool]]:
    results = []
    for event_probability in event_probabilities:
        results.append(random.choices([True, False], (event_probability, 1 - event_probability), k=1000000))
    results = list(zip(results[0], results[1], results[2]))
    return results


def task_3(main_event_probability: int, dep_event_probability: int) -> list[int]:
    main_chance = main_event_probability / 100
    dep_chance = dep_event_probability / 100
    chances = [main_chance * dep_chance, main_chance * (1 - dep_chance),
                (1 - main_chance) * dep_chance, (1 - main_chance) * (1 - dep_chance)]
    return random.choices(range(4), chances, k = 1000000)


def task_4(event_probabilities: list[float], k=1000000) -> list[int]:
    return random.choices(range(len(event_probabilities)), event_probabilities, k=k)