from utils.utils import *

def tot_prompting(client, model, temperature, problem, examples):

  system_prompt = "You are an operations research expert. Keep your answers concise."
  problem_description = f"Consider the following problem: {problem['description']}"

  cot_prompt_plan = "Determine the best approach to solve the problem. Do not write code yet."
  cot_prompt_init = "Write python code to model the problem. Do not solve the problem yet, only make sure to model the problem correctly. Use libraries, if needed."
  cot_prompt_solve = "Consider the python code to model the problem. Extend the code to solve the problem. Assign the final output to a variable 'solution'. Only assign one number."

  tot_breadth = 3
  cot_prompts = [cot_prompt_plan, cot_prompt_init, cot_prompt_solve] # tot depth = 3

  sequential_logs = []
  previous_layer_output = "" # succesively build context based on previous layers' output

  for layer_prompt in cot_prompts:

    # generate thought by sampling from a CoT prompt
    response = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "user", "content": problem_description},
        {"role": "assistant", "content": system_prompt},
        {"role": "user", "content": examples if examples is not None else "Let's think step by step."},
        {"role": "assistant", "content": previous_layer_output},
        {"role": "user", "content": layer_prompt},
      ],
      temperature=temperature,
      n=tot_breadth
    )

    layer_samples = [f'Choice {i}: ' + choice.message.content for i, choice in enumerate(response.choices)]
    sequential_logs.append("\n".join(layer_samples)) # log samples

    # evaluate thought by voting
    vote_prompt = "You are given the following choices for the current step. Decide which choice is most promising. Analyze each choice in detail, then conclude in the last line 'The best choice is {i}', where i the integer id of the choice."

    selection = client.chat.completions.create(
      model=model,
      messages=[
        {"role": "user", "content": problem_description},
        {"role": "assistant", "content": system_prompt},
        {"role": "user", "content": vote_prompt},
        {"role": "assistant", "content": previous_layer_output},
        {"role": "user", "content": "\n".join(layer_samples)},
      ],
      temperature=0
    )

    sequential_logs.append(selection.choices[0].message.content) # log selection

    pattern = r'The best choice is (\d+)'
    match = re.search(pattern, selection.choices[0].message.content)
    if match:
        number_str = match.group(1)
        try:
          choice = int(number_str)
          previous_layer_output += layer_samples[choice] # might not have 3 previous output here then
          sequential_logs.append("Choice: " + str(choice)) # log choice
        except ValueError as e:
          continue


  generated_code = strip_code(previous_layer_output)
  import_error = check_imports(generated_code)
  if import_error is not None:
    res = import_error
  else:
    res = run_code(generated_code)

  logs = {
    "system_prompt": system_prompt,
    "problem_description": problem_description,
    "output": sequential_logs,
    "code": generated_code,
    "solution": res if isinstance(res, (int, float)) else res.name,
  }

  return res, logs