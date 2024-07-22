import os
import json
from collections import Counter

from openai import OpenAI

from utils.utils import *
from prompting import standard, cot, cotsc, tot

def run_test(prompting_method, api_key):
    
    client = OpenAI(
        api_key=api_key,
    )

    # read problem set and in-context examples
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_folder = os.path.join(current_dir, "dataset", "bisor_bench")
    filepath = os.path.join(dataset_folder, "problems.json")
    with open(filepath, "r") as file:
        problem_set = json.load(file)
    dataset_folder = os.path.join(current_dir, "dataset", "examples")
    filepath = os.path.join(dataset_folder, "examples.json")
    with open(filepath, "r") as file:
        example_set = json.load(file)
    
    # run test
    if prompting_method == "standard":
        prompt_and_log(client, "gpt-4", 0.7, problem_set, "standard")
    elif prompting_method == "fewshotcot":
        examples = "Here are a few examples how to solve operations research problems:\n" + '\n---\n'.join(['\n'.join(["Problem: " + example["description"], example["steps"]]) for example in example_set]) + "\nLet's think step by step." # concatenates examples in single string
        prompt_and_log(client, "gpt-4", 0.7, problem_set, "few-shot cot", examples)
    elif prompting_method == "zeroshotcot":
        prompt_and_log(client, "gpt-4", 0.7, problem_set, "zero-shot cot")
    elif prompting_method == "cotsc":
        prompt_and_log(client, "gpt-4", 0.7, problem_set, "cotsc")
    elif prompting_method == "tot":
        prompt_and_log(client, "gpt-4", 0.7, problem_set, "tot")


def prompt_and_log(client, model, temperature, problem_set, prompting_method, examples=None):

    if prompting_method == "standard":
        prompting_func = standard.standard_prompting
    elif prompting_method == "zero-shot cot" or prompting_method == "few-shot cot":
        prompting_func = cot.cot_prompting
    elif prompting_method == "cotsc":
        prompting_func = cotsc.cotsc_prompting
    elif prompting_method == "tot":
        prompting_func = tot.tot_prompting

    res_arr = []
    accept_arr = []
    wrong_arr = []
    runtime_arr = []
    compile_arr = []
    lp_arr = []
    nlp_arr = []
    dynamic_arr = []
    progress_counter = 0
    for problem in problem_set:
        res, log = prompting_func(client, model, temperature, problem, examples)
        log_output("logs", f'{model}-{problem["name"]}-{prompting_method}', log)
        if not isinstance(res, Result):
            res = check_solution(res, problem['solution'])
        res_arr.append(res)

        if res == Result.ACCEPT:
            accept_arr.append(problem["name"])
        if res == Result.WRONG_ANSWER:
            wrong_arr.append(problem["name"])
        if res == Result.RUNTIME_ERROR:
            runtime_arr.append(problem["name"])
        if res == Result.COMPILE_ERROR:
            compile_arr.append(problem["name"])

        if problem["class"] == "linear":
            lp_arr.append(res)
        elif problem["class"] == "nonlinear":
            nlp_arr.append(res)
        elif problem["class"] == "dynamic":
            dynamic_arr.append(res)
        progress_counter += 1
        print(progress_counter, "/ 15")
        print("Problem:", problem['name'], "Result: ", res)

    # write results of each category to text file
    log_results("logs", f'{prompting_method}-accept', accept_arr)
    log_results("logs", f'{prompting_method}-wrong', wrong_arr)
    log_results("logs", f'{prompting_method}-runtime', runtime_arr)
    log_results("logs", f'{prompting_method}-compile', compile_arr)

    # create plots for each category
    res_cnt = Counter(res_arr)
    create_plot(res_cnt, f'{prompting_method}-total', "logs")
    lp_cnt = Counter(lp_arr)
    create_plot(lp_cnt, f'{prompting_method}-linear', "logs")
    nlp_cnt = Counter(nlp_arr)
    create_plot(nlp_cnt, f'{prompting_method}-nonlinear', "logs")
    dynamic_cnt = Counter(dynamic_arr)
    create_plot(dynamic_cnt, f'{prompting_method}-dynamic', "logs")