import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Choose between 'relative' and 'absolute', each taking one or two integers.")

    # Positional argument: filename (string)
    parser.add_argument("filename", type=str, help="Input filename.")

    # Create mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)

    # "relative" option: takes 1 or 2 int numbers
    group.add_argument("-r", "--relative", nargs="+", type=int, help="Relative mode: provide 1 or 2 integers.")

    # "absolute" option: takes 1 or 2 int numbers
    group.add_argument("-a", "--absolute", nargs="+", type=int, help="Absolute mode: provide 1 or 2 integers.")

    args = parser.parse_args()

    # Validate the number of arguments (only 1 or 2 numbers allowed)
    for key in ["relative", "absolute"]:
        values = getattr(args, key)
        if values is not None and not (1 <= len(values) <= 2):
            parser.error(f"--{key} must take 1 or 2 numbers, but got {len(values)}.")

    return args

if __name__ == "__main__":
    args = parse_args()
    print(args)