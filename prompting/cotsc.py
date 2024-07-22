import random

from utils.utils import *

def cotsc_prompting(client, model, temperature, problem, examples):

  system_prompt = "You are an operations research expert. Write python code to solve the given problem. Assign the final output to a variable 'solution'. Only assign one number."
  problem_description = f"Consider the following problem: {problem['description']}"

  response = client.chat.completions.create(
    model=model,
    messages=[
      {"role": "user", "content": problem_description},
      {"role": "assistant", "content": system_prompt},
      {"role": "user", "content": examples if examples is not None else "Let's think step by step."},
    ],
    temperature=temperature,
    n=5
  )

  sol_ls = []
  res_ls = [choice.message.content for choice in response.choices]
  code_ls = []
  for sample in res_ls:
    generated_code = strip_code(sample)
    code_ls.append(generated_code)
    import_error = check_imports(generated_code)
    if import_error is not None:
      continue
    tmp = run_code(generated_code)
    if isinstance(tmp, (int, float)):
      sol_ls.append(tmp)

  if len(sol_ls) == 0:
    sol = Result.COMPILE_ERROR
  else:
    value_counts = {value: sol_ls.count(value) for value in set(sol_ls)}
    max_count = max(value_counts.values())
    max_value_candidates = [value for value, count in value_counts.items() if count == max_count]
    sol = random.choice(max_value_candidates) # Randomly choose if tie in majority

  logs = {
    "system prompt": system_prompt,
    "problem_description": problem_description,
    "examples": examples,
    "output": res_ls,
    "code": code_ls,
    "solutions": sol_ls,
    "result": sol if isinstance(sol, (int, float)) else sol.name,
  }

  return sol, logs