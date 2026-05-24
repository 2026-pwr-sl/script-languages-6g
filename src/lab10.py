import argparse
import sys
import csv
import sys
from pathlib import Path


class SalesData:
    def __init__(self, transaction_id, customer_id, age_group, gender, city, 
                 customer_segment, product_id, product_category, original_price, 
                 discount_pct, final_price, quantity, purchase_amount, payment_method, 
                 purchase_date, purchase_hour, is_weekend, is_black_friday):
        self.transaction_id = transaction_id
        self.customer_id = customer_id
        self.age_group = age_group
        self.gender = gender
        self.city = city
        self.customer_segment = customer_segment
        self.product_id = product_id
        self.product_category = product_category
        self.original_price = float(original_price)
        self.discount_pct = int(discount_pct)
        self.final_price = float(final_price)
        self.quantity = int(quantity)
        self.purchase_amount = float(purchase_amount)
        self.payment_method = payment_method
        self.purchase_date = purchase_date
        self.purchase_hour = int(purchase_hour)
        self.is_weekend = bool(int(is_weekend))
        self.is_black_friday = bool(int(is_black_friday))

    def __repr__(self):
        return f"SalesData(id='{self.transaction_id}', category='{self.product_category}', amount=${self.purchase_amount:.2f})"


def load_csv_dataset(file_path):
    data = []
    
    try:
        with open(file_path, mode="r", encoding="utf-8", errors="ignore") as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                try:
                    record = SalesData(
                        transaction_id=row["transaction_id"],
                        customer_id=row["customer_id"],
                        age_group=row["age_group"],
                        gender=row["gender"],
                        city=row["city"],
                        customer_segment=row["customer_segment"],
                        product_id=row["product_id"],
                        product_category=row["product_category"],
                        original_price=row["original_price"],
                        discount_pct=row["discount_pct"],
                        final_price=row["final_price"],
                        quantity=row["quantity"],
                        purchase_amount=row["purchase_amount"],
                        payment_method=row["payment_method"],
                        purchase_date=row["purchase_date"],
                        purchase_hour=row["purchase_hour"],
                        is_weekend=row["is_weekend"],
                        is_black_friday=row["is_black_friday"]
                    )
                    data.append(record)
                except (ValueError, KeyError):
                    continue
                    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' could not be found.")
        sys.exit(1)
        
    return data


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
    
    data = load_csv_dataset(dataset_path)
    

if __name__ == "__main__":
    main()