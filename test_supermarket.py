import tempfile
import unittest
from pathlib import Path

from welcome_app import SupermarketDB, parse_money, render_page


class SupermarketDBTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = SupermarketDB(str(Path(self.temp_dir.name) / "test.db"))
        self.db.add_goods("MILK-1", "Milk", "Dairy", parse_money("2.50"))
        self.db.add_supplier("Farm Supply", "Alex", "555-0100")
        self.goods_id = self.db.rows("SELECT id FROM goods WHERE sku = ?", ("MILK-1",))[0]["id"]
        self.supplier_id = self.db.rows(
            "SELECT id FROM supplier WHERE name = ?", ("Farm Supply",)
        )[0]["id"]
        self.db.add_goods("BREAD-1", "Bread", "Bakery", parse_money("1.80"))
        self.bread_id = self.db.rows(
            "SELECT id FROM goods WHERE sku = ?", ("BREAD-1",)
        )[0]["id"]

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_purchase_and_sale_update_inventory_and_log(self) -> None:
        purchase_no = self.db.create_purchase(
            self.supplier_id,
            [
                (self.goods_id, 10, parse_money("1.25")),
                (self.bread_id, 4, parse_money("0.80")),
            ],
        )
        sale_no = self.db.create_sale(
            "Walk-in",
            [
                (self.goods_id, 3, parse_money("2.50")),
                (self.bread_id, 2, parse_money("1.80")),
            ],
        )

        inventory = self.db.rows(
            "SELECT quantity FROM inventory WHERE goods_id = ?", (self.goods_id,)
        )[0]["quantity"]
        bread_inventory = self.db.rows(
            "SELECT quantity FROM inventory WHERE goods_id = ?", (self.bread_id,)
        )[0]["quantity"]
        logs = self.db.rows(
            "SELECT action, change_qty, after_qty, reference_no FROM inventory_log "
            "ORDER BY id"
        )
        purchases = self.db.rows("SELECT total_cents FROM purchase_order")
        purchase_details = self.db.rows(
            "SELECT quantity FROM purchase_detail ORDER BY goods_id"
        )
        sales = self.db.rows("SELECT total_cents FROM sales_order")
        sales_details = self.db.rows("SELECT quantity FROM sales_detail ORDER BY goods_id")

        self.assertEqual(inventory, 7)
        self.assertEqual(bread_inventory, 2)
        self.assertEqual(
            [(row["action"], row["change_qty"]) for row in logs],
            [("PURCHASE", 10), ("PURCHASE", 4), ("SALE", -3), ("SALE", -2)],
        )
        self.assertEqual(
            [row["reference_no"] for row in logs],
            [purchase_no, purchase_no, sale_no, sale_no],
        )
        self.assertEqual(purchases[0]["total_cents"], 1570)
        self.assertEqual([row["quantity"] for row in purchase_details], [10, 4])
        self.assertEqual(sales[0]["total_cents"], 1110)
        self.assertEqual([row["quantity"] for row in sales_details], [3, 2])

    def test_sale_cannot_exceed_available_stock(self) -> None:
        self.db.create_purchase(
            self.supplier_id, [(self.goods_id, 2, parse_money("1.25"))]
        )

        with self.assertRaisesRegex(ValueError, "Insufficient stock"):
            self.db.create_sale("", [(self.goods_id, 3, parse_money("2.50"))])

        self.assertEqual(self.db.count("sales_order"), 0)
        self.assertEqual(
            self.db.rows(
                "SELECT quantity FROM inventory WHERE goods_id = ?", (self.goods_id,)
            )[0]["quantity"],
            2,
        )
        self.assertEqual(
            len(self.db.rows("SELECT id FROM inventory_log WHERE action = 'SALE'")), 0
        )

    def test_duplicate_product_lines_cannot_exceed_stock_in_total(self) -> None:
        self.db.create_purchase(
            self.supplier_id, [(self.goods_id, 4, parse_money("1.25"))]
        )

        with self.assertRaisesRegex(ValueError, "Insufficient stock"):
            self.db.create_sale(
                "",
                [
                    (self.goods_id, 3, parse_money("2.50")),
                    (self.goods_id, 2, parse_money("2.40")),
                ],
            )

        self.assertEqual(self.db.count("sales_order"), 0)
        self.assertEqual(
            self.db.rows(
                "SELECT quantity FROM inventory WHERE goods_id = ?", (self.goods_id,)
            )[0]["quantity"],
            4,
        )

    def test_dashboard_and_errors_are_html_escaped(self) -> None:
        dashboard = render_page(self.db, "dashboard")
        error_page = render_page(self.db, "goods", "<script>alert(1)</script>", error=True)
        purchase_page = render_page(self.db, "purchases")

        self.assertIn("MarketDesk", dashboard)
        self.assertIn('id="add-item"', purchase_page)
        self.assertIn('name="unit_price"', purchase_page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", error_page)
        self.assertNotIn("<script>alert(1)</script>", error_page)


if __name__ == "__main__":
    unittest.main()
