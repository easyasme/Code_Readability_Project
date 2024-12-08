#! /usr/bin/env python3
"""Population utilities."""

import numpy as np

from utils.casting import bin_array_to_int


def evaluate_binary_aptitude(individue: np.ndarray, domain: tuple, aptitude_function: callable):
    bits = individue.shape[0]
    min = 0
    max = 2**bits - 1
    decoded_individue = bin_array_to_int(individue)
    decoded_individue = (decoded_individue - min) / (max - min)
    decoded_individue = (domain[1] - domain[0]) * decoded_individue + domain[0]
    aptitude = aptitude_function(decoded_individue)
    
    return aptitude


def evaluate_population(population: np.ndarray, domain: tuple, aptitude_function: callable, desc: bool = True):
    aptitudes = np.vstack([evaluate_binary_aptitude(individue, domain, aptitude_function) for individue in population])

    direction = -1 if desc else 1
    sorted_indexes = aptitudes[:, -1].argsort()[::direction]
    sorted_population = population[sorted_indexes]
    sorted_aptitudes = aptitudes[sorted_indexes]
    avg_aptitude = np.mean(sorted_aptitudes)
    max_aptitude = np.max(sorted_aptitudes)

    return sorted_population, sorted_aptitudes, avg_aptitude, max_aptitude


def evaluate_tsp_individue(individue: np.ndarray, distances, cities_mapper: dict):
    aptitude = 0
    genes_ = len(individue)
    for idx in range(genes_):
        city_start = individue[idx]
        city_end = individue[idx+1] if idx < genes_-1 else individue[0]
        aptitude += distances.get_distance(cities_mapper[city_start], cities_mapper[city_end])

    return aptitude


def evaluate_tsp_population(population:np.ndarray, distances, cities_mapper: dict, desc: bool = False):
    aptitudes = np.vstack([evaluate_tsp_individue(individue, distances,cities_mapper) for individue in population])

    direction = -1 if desc else 1
    sorted_indexes = aptitudes[:, -1].argsort()[::direction]
    sorted_population = population[sorted_indexes]
    sorted_aptitudes = aptitudes[sorted_indexes]
    avg_aptitude = np.mean(sorted_aptitudes)
    min_aptitude = np.min(sorted_aptitudes)

    return sorted_population, sorted_aptitudes, avg_aptitude, min_aptitude
