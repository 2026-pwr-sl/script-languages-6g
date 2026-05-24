import argparse
import sys
from pathlib import Path

def build_parser():
    parser = argparse.ArgumentParser(
        description="Analyze a CSV dataset."
    )
    
    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the dataset file."
    )
    
    return parser

def validate_dataset_argument(dataset_arg):
    dataset_path = Path(dataset_arg)
    
    if dataset_path.suffix.lower() != ".csv":
        print(f"Error: The file '{dataset_arg}' has an invalid extension. Please provide a .csv file.")
        sys.exit(1)
        
    if not dataset_path.is_file():
        print(f"Error: The file '{dataset_arg}' could not be found.")
        sys.exit(1)
        
    return dataset_path

def main():
    parser = build_parser()
    
    args = parser.parse_args()
    
    dataset_path = validate_dataset_argument(args.dataset)

if __name__ == "__main__":
    main()