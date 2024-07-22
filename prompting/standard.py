from utils.utils import *

def standard_prompting(client, model, temperature, problem, examples):

    system_prompt = "You are an operations research expert. Write python code to solve the given problem. Assign the final output to a variable 'solution'. Only assign one number."
    problem_description = f"Consider the following problem: {problem['description']}"

    response = client.chat.completions.create(
        model=model,
        messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": problem_description},
        ],
        temperature=temperature
    )

    generated_code = strip_code(response.choices[0].message.content)
    import_error = check_imports(generated_code)
    if import_error is not None:
        res = import_error
    else:
        res = run_code(generated_code)

    log = {
        "system_prompt": system_prompt,
        "problem_description": problem_description,
        "output": response.choices[0].message.content,
        "code": generated_code,
        "solution": res if isinstance(res, (int, float)) else res.name,
    }
    return res, log