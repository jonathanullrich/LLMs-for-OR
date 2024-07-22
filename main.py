import argparse
from experiment import run_test

def main(args):
    run_test(args.method, args.key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the experiment")
    parser.add_argument("--method", choices=["standard", "fewshotcot", "zeroshotcot", "cotsc", "tot"], help="Choose a prompting method: standard, fewshotcot, zeroshotcot, cotsc, tot")
    parser.add_argument("--key", help="OpenAI api key")

    args = parser.parse_args()
    main(args)