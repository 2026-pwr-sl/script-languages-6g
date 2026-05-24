import argparse
import csv
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape


class SalesData:
    def __init__(
            self,
            transaction_id,
            customer_id,
            age_group,
            gender,
            city,
            customer_segment,
            product_id,
            product_category,
            original_price,
            discount_pct,
            final_price,
            quantity,
            purchase_amount,
            payment_method,
            purchase_date,
            purchase_hour,
            is_weekend,
            is_black_friday,
    ):
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
        return (
            f"SalesData(id='{self.transaction_id}', "
            f"category='{self.product_category}', "
            f"amount=${self.purchase_amount:.2f})"
        )


def load_csv_dataset(file_path):
    data = []

    try:
        with open(
                file_path,
                mode="r",
                encoding="utf-8",
                errors="ignore",
                newline="",
        ) as file:
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
                        is_black_friday=row["is_black_friday"],
                    )
                    data.append(record)
                except (ValueError, KeyError):
                    continue

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' could not be found.")
        sys.exit(1)

    return data


def summarize_sales(data):
    """Return an overall sales summary for the dataset."""
    total_purchase_amount = 0.0
    total_quantity = 0

    for record in data:
        total_purchase_amount += record.purchase_amount
        total_quantity += record.quantity

    return {
        "total_records": len(data),
        "total_quantity": total_quantity,
        "total_purchase_amount": total_purchase_amount,
    }


def aggregate_purchase_amount_by_category(data):
    """Group purchase amount totals by product category."""
    category_totals = {}

    for record in data:
        current_total = category_totals.get(record.product_category, 0.0)
        category_totals[record.product_category] = (
            current_total + record.purchase_amount
        )

    return category_totals


def calculate_average_purchase_amount(data):
    """Calculate average transaction purchase amount."""
    if not data:
        return 0.0

    total_purchase_amount = 0.0

    for record in data:
        total_purchase_amount += record.purchase_amount

    return total_purchase_amount / len(data)


def calculate_sales_statistics(data):
    """Return statistical calculations for the sales dataset."""
    return {
        "average_purchase_amount": calculate_average_purchase_amount(data),
    }


def format_summary(summary):
    return (
        "Summary result\n"
        f"Total records: {summary['total_records']}\n"
        f"Total quantity sold: {summary['total_quantity']}\n"
        "Total purchase amount: "
        f"${summary['total_purchase_amount']:.2f}"
    )


def _column_name(column_number):
    name = ""

    while column_number > 0:
        column_number, remainder = divmod(column_number - 1, 26)
        name = chr(65 + remainder) + name

    return name


def _cell_xml(row_number, column_number, value, style_id=0):
    reference = f"{_column_name(column_number)}{row_number}"
    style_attribute = f' s="{style_id}"' if style_id else ""

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float):
            value = f"{value:.2f}"

        return f'<c r="{reference}"{style_attribute}><v>{value}</v></c>'

    return (
        f'<c r="{reference}" t="inlineStr"{style_attribute}>'
        f"<is><t>{escape(str(value))}</t></is></c>"
    )


def _sheet_xml(rows, currency_columns=None):
    currency_columns = currency_columns or set()
    row_xml = []

    for row_number, row in enumerate(rows, start=1):
        cells = []

        for column_number, value in enumerate(row, start=1):
            style_id = 0

            if row_number == 1:
                style_id = 1
            elif column_number in currency_columns:
                style_id = 2

            cells.append(
                _cell_xml(row_number, column_number, value, style_id)
            )

        row_xml.append(f'<row r="{row_number}">{"".join(cells)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
        '<cols><col min="1" max="1" width="28" customWidth="1"/>'
        '<col min="2" max="2" width="18" customWidth="1"/></cols>'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        '</worksheet>'
    )


def _workbook_xml(sheet_names):
    sheets = []

    for index, name in enumerate(sheet_names, start=1):
        escaped_name = escape(name, {'"': "&quot;"})
        sheets.append(
            f'<sheet name="{escaped_name}" sheetId="{index}" '
            f'r:id="rId{index}"/>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/'
        'officeDocument/2006/relationships">'
        f'<sheets>{"".join(sheets)}</sheets>'
        '</workbook>'
    )


def _workbook_relationships_xml(sheet_count):
    relationships = []

    for index in range(1, sheet_count + 1):
        relationships.append(
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )

    relationships.append(
        f'<Relationship Id="rId{sheet_count + 1}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/'
        '2006/relationships/styles" Target="styles.xml"/>'
    )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        f'{"".join(relationships)}'
        '</Relationships>'
    )


def _content_types_xml(sheet_count):
    worksheets = []

    for index in range(1, sheet_count + 1):
        worksheets.append(
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        )

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
        'content-types">'
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        f'{"".join(worksheets)}'
        '</Types>'
    )


def _styles_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
        '<numFmts count="1"><numFmt numFmtId="164" '
        'formatCode="$#,##0.00"/></numFmts>'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/>'
        '</font><font><b/><sz val="11"/><color rgb="FFFFFFFF"/>'
        '<name val="Calibri"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/>'
        '<bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/>'
        '<diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" '
        'borderId="0" xfId="0" applyFont="1" applyFill="1"/>'
        '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" '
        'xfId="0" applyNumberFormat="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles><dxfs count="0"/>'
        '<tableStyles count="0" defaultTableStyle="TableStyleMedium2" '
        'defaultPivotStyle="PivotStyleLight16"/></styleSheet>'
    )


def write_excel_report(summary, category_totals, statistics, output_path):
    summary_rows = [
        ["Metric", "Value"],
        ["Total records", summary["total_records"]],
        ["Total quantity sold", summary["total_quantity"]],
        [
            "Total purchase amount",
            f"${summary['total_purchase_amount']:.2f}",
        ],
    ]
    category_rows = [["Product category", "Purchase amount"]]

    for category, total in sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True,
    ):
        category_rows.append([category, total])

    statistics_rows = [
        ["Statistic", "Value"],
        [
            "Average purchase amount",
            statistics["average_purchase_amount"],
        ],
    ]
    sheet_names = ["Summary", "Category totals", "Statistics"]
    sheet_contents = [
        _sheet_xml(summary_rows),
        _sheet_xml(category_rows, currency_columns={2}),
        _sheet_xml(statistics_rows, currency_columns={2}),
    ]

    with ZipFile(output_path, "w", ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", _content_types_xml(3))
        workbook.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships"><Relationship Id="rId1" '
            'Type="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>',
        )
        workbook.writestr("xl/workbook.xml", _workbook_xml(sheet_names))
        workbook.writestr(
            "xl/_rels/workbook.xml.rels",
            _workbook_relationships_xml(len(sheet_names)),
        )
        workbook.writestr("xl/styles.xml", _styles_xml())

        for index, contents in enumerate(sheet_contents, start=1):
            workbook.writestr(f"xl/worksheets/sheet{index}.xml", contents)


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Analyze Black Friday sales data from a CSV file. "
            "Without -o, only the summary result is printed."
        )
    )

    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the CSV dataset file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Optional path to the generated Excel .xlsx report.",
    )

    return parser


def validate_dataset_argument(dataset_arg):
    dataset_path = Path(dataset_arg)

    if dataset_path.suffix.lower() != ".csv":
        print(
            f"Error: The file '{dataset_arg}' has an invalid extension. "
            "Please provide a .csv file."
        )
        sys.exit(1)

    if not dataset_path.is_file():
        print(f"Error: The file '{dataset_arg}' could not be found.")
        sys.exit(1)

    return dataset_path


def validate_output_argument(output_arg):
    if output_arg is None:
        return None

    output_path = Path(output_arg)

    if output_path.suffix.lower() != ".xlsx":
        print(
            f"Error: The output file '{output_arg}' has an invalid "
            "extension. Please provide a .xlsx file."
        )
        sys.exit(1)

    if output_path.parent != Path(".") and not output_path.parent.exists():
        print(
            f"Error: The output directory '{output_path.parent}' "
            "could not be found."
        )
        sys.exit(1)

    return output_path


def main():
    parser = build_parser()
    args = parser.parse_args()

    dataset_path = validate_dataset_argument(args.dataset)
    output_path = validate_output_argument(args.output)
    data = load_csv_dataset(dataset_path)

    summary = summarize_sales(data)
    category_totals = aggregate_purchase_amount_by_category(data)
    statistics = calculate_sales_statistics(data)

    if output_path is None:
        print(format_summary(summary))
        return

    write_excel_report(summary, category_totals, statistics, output_path)
    print(f"Excel report saved to {output_path}")


if __name__ == "__main__":
    main()
