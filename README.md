# 'Prompting Large Language Models to Solve Operations Research Problems'

This repository contains the benchmark and code for my master thesis on 'Prompting Large Language Models to Solve Operations Research Problems'.

## Usage

```
python main.py -method METHOD --key OPEN_AI_KEY
```

METHOD = standard/ fewshotcot/ zeroshotcot/ cotsc/ tot

## Contents

- BisorBench problem set (/dataset): contains 15 operations research problems from four text books (/dataset/bisor_bench) and three hand-crafted in-context examples for solving operations research problems (/dataset/examples)
- Logs of the conducted experiment (/logs): contains the models outputs and plots for different evaluations
- The implementation of the prompting methods used in the paper (/prompting)
- Functionality to run generated code dynamically and create plots (/utils)