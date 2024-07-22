import warnings
import subprocess
import re
import ast
import uuid
import json
import os
import signal
from enum import Enum
import importlib.util

import matplotlib.pyplot as plt

class Result(Enum):
    ACCEPT = 0
    WRONG_ANSWER = 1
    RUNTIME_ERROR = 2
    COMPILE_ERROR = 3

def strip_code(text):
  """Removes non-code blocks from generated text and concatenates it"""
  pattern = r'```python\s*([\s\S]*?)\s*```'
  matches = re.findall(pattern, text)
  concatenated_code = '\n'.join(matches)
  return concatenated_code

def check_imports(code):
    """Checks imports in generated code and installs them, if necessary"""
    try:
      tree = ast.parse(code)
    except Exception as e:
      return Result.COMPILE_ERROR
    imps = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imps.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            for alias in node.names:
                imps.add(f"{module_name}.{alias.name}")
    for imp in imps:
        imp = imp.split(".")[0]
        try:
            importlib.import_module(imp)
        except ImportError:
            #print(f"{imp} cannot be imported - attempting to install with pip.")
            try:
                subprocess.check_call(['pip', 'install', imp])
            except Exception as e:
                return Result.COMPILE_ERROR
            
class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

def run_code(generated_code, timeout=10):
    """Compiles and executes generated code with a timeout. Returns either solution number or <Result>"""
    vars = {"solution": None}
    if generated_code == "":
        return Result.COMPILE_ERROR
    try:
        warnings.filterwarnings("ignore")
        signal.signal(signal.SIGALRM, timeout_handler)
        compiled_code = compile(generated_code, '<string>', 'exec')
        signal.alarm(timeout)  # set timeout
        exec(compiled_code, vars)
        signal.alarm(0)  # reset timeout
        warnings.filterwarnings("default")
    except TimeoutError:
        print("Execution timed out")
        return Result.RUNTIME_ERROR
    except (SyntaxError, IndentationError, NameError, TypeError, ValueError) as e:
        print(f"Compile error: {e}")
        return Result.COMPILE_ERROR
    except Exception as e:
        print(f"Runtime error: {e}")
        return Result.RUNTIME_ERROR
    return vars["solution"] if isinstance(vars["solution"], (int, float)) else Result.RUNTIME_ERROR

def check_solution(pred_sol, ground_truth):
  # pred_sol = round(pred_sol, 3)
  return Result.ACCEPT if pred_sol == ground_truth else Result.WRONG_ANSWER

def log_output(path, prefix, dict):
    uid = uuid.uuid4()
    uid_str = str(uid)
    log_file_path = os.path.join(path, f"{prefix}-{uid_str}.json")
    with open(log_file_path, "w") as file:
        json.dump(dict, file)

def log_results(path, prefix, arr):
    uid = uuid.uuid4()
    uid_str = str(uid)
    log_file_path = os.path.join(path, f"{prefix}-{uid_str}.txt")
    with open(log_file_path, "w") as file:
        for item in arr:
            file.write("%s\n" % item)

def create_plot(data, title, path):
    result_labels = ["Correct", "Wrong", "Runtime", "Compile"]
    result_values = [data[result] for result in Result]

    plt.bar(result_labels, result_values, color=['green', 'blue', 'orange', 'red']) # chart
    plt.xlabel('Result')
    plt.ylabel('Count')
    plt.title(title)

    uid = uuid.uuid4()
    uid_str = str(uid)
    plt.savefig(f'{path}/{title}-result-distribution-{uid_str}.png')
    plt.close()