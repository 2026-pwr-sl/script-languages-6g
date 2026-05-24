import os
import sys
from zipfile import ZipFile

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)

from lab10 import (
    SalesData,
    aggregate_purchase_amount_by_category,
    calculate_average_purchase_amount,
    calculate_sales_statistics,
    summarize_sales,
    write_excel_report,
)


def make_sale(category, quantity, amount):
    return SalesData(
        transaction_id="T0001",
        customer_id="C0001",
        age_group="26-35",
        gender="Other",
        city="Wroclaw",
        customer_segment="Loyal",
        product_id="P0001",
        product_category=category,
        original_price="100.00",
        discount_pct="0",
        final_price="100.00",
        quantity=str(quantity),
        purchase_amount=str(amount),
        payment_method="Credit Card",
        purchase_date="2025-11-28",
        purchase_hour="12",
        is_weekend="0",
        is_black_friday="1",
    )


def sample_sales():
    return [
        make_sale("Electronics", 1, 100.00),
        make_sale("Electronics", 2, 250.00),
        make_sale("Beauty", 3, 50.00),
    ]


def test_summarize_sales_returns_overall_dataset_values():
    summary = summarize_sales(sample_sales())

    assert summary["total_records"] == 3
    assert summary["total_quantity"] == 6
    assert summary["total_purchase_amount"] == pytest.approx(400.00)


def test_aggregate_purchase_amount_by_category_groups_sales_manually():
    result = aggregate_purchase_amount_by_category(sample_sales())

    assert result == {
        "Electronics": pytest.approx(350.00),
        "Beauty": pytest.approx(50.00),
    }


def test_calculate_average_purchase_amount_returns_statistic():
    result = calculate_average_purchase_amount(sample_sales())

    assert result == pytest.approx(400.00 / 3)


def test_calculate_sales_statistics_handles_empty_dataset():
    result = calculate_sales_statistics([])

    assert result["average_purchase_amount"] == 0.0


def test_write_excel_report_includes_all_operation_sections(tmp_path):
    data = sample_sales()
    summary = summarize_sales(data)
    category_totals = aggregate_purchase_amount_by_category(data)
    statistics = calculate_sales_statistics(data)
    output_path = tmp_path / "report.xlsx"

    write_excel_report(summary, category_totals, statistics, output_path)

    with ZipFile(output_path) as workbook:
        workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")
        summary_xml = workbook.read("xl/worksheets/sheet1.xml").decode(
            "utf-8"
        )
        category_xml = workbook.read("xl/worksheets/sheet2.xml").decode(
            "utf-8"
        )
        statistics_xml = workbook.read("xl/worksheets/sheet3.xml").decode(
            "utf-8"
        )

    assert "Summary" in workbook_xml
    assert "Category totals" in workbook_xml
    assert "Statistics" in workbook_xml
    assert "Total purchase amount" in summary_xml
    assert "Electronics" in category_xml
    assert "Average purchase amount" in statistics_xml
