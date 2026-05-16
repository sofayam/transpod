# find the missing summary files and print out the corresponding transcript files that need to be reprocessed

import argparse
import glob
import re

def main():
    parser = argparse.ArgumentParser(description="Find the missing summary files.")
    parser.add_argument("dir", help="Path to the directory containing transcript files")
    parser.add_argument("startidx", type=int, default=1, help="Starting index of the transcript files to check")
    parser.add_argument("endidx", type=int, default=999999, help="Ending index of the transcript files to check")
    args = parser.parse_args()

    for i in range(args.startidx, args.endidx + 1):
        for section in ["simple", "japanese", "english", "vocabulary", "idioms", "culture"]:
            pattern = f"{args.dir}/#{i}*.summary.{section}"
            regex = re.compile(rf"#({i})[^\d].*\.{section}$")

            results = [f for f in glob.glob(pattern) if regex.search(f)]
            
            if len(results) == 0:
                print(f"Missing summary file for transcript {i} section {section}")


if __name__ == "__main__":
    main()
