INSERT INTO regions (id, name, code) VALUES
    ('a1000000-0000-0000-0000-000000000001', 'DKI Jakarta', 'JKT'),
    ('a1000000-0000-0000-0000-000000000002', 'Jawa Barat', 'JBR'),
    ('a1000000-0000-0000-0000-000000000003', 'Jawa Timur', 'JTM'),
    ('a1000000-0000-0000-0000-000000000004', 'Jawa Tengah', 'JTG'),
    ('a1000000-0000-0000-0000-000000000005', 'Banten', 'BTN');

INSERT INTO products (id, name, category, price, sku) VALUES
    ('b1000000-0000-0000-0000-000000000001', 'Laptop ASUS ROG', 'Electronics', 15000000, 'ELC-001'),
    ('b1000000-0000-0000-0000-000000000002', 'iPhone 15 Pro', 'Electronics', 22000000, 'ELC-002'),
    ('b1000000-0000-0000-0000-000000000003', 'Samsung Galaxy S24', 'Electronics', 18000000, 'ELC-003'),
    ('b1000000-0000-0000-0000-000000000004', 'Nike Air Max', 'Fashion', 2500000, 'FAS-001'),
    ('b1000000-0000-0000-0000-000000000005', 'Levis 501 Jeans', 'Fashion', 1200000, 'FAS-002'),
    ('b1000000-0000-0000-0000-000000000006', 'Office Chair', 'Furniture', 3500000, 'FUR-001'),
    ('b1000000-0000-0000-0000-000000000007', 'Standing Desk', 'Furniture', 4200000, 'FUR-002'),
    ('b1000000-0000-0000-0000-000000000008', 'Mech Keyboard', 'Electronics', 1800000, 'ELC-004'),
    ('b1000000-0000-0000-0000-000000000009', 'Wireless Mouse', 'Electronics', 500000, 'ELC-005'),
    ('b1000000-0000-0000-0000-000000000010', 'Monitor 27 inch', 'Electronics', 4500000, 'ELC-006');

INSERT INTO customers (id, name, email, phone, segment) VALUES
    ('c1000000-0000-0000-0000-000000000001', 'PT Maju Bersama', 'info@majubersama.co.id', '021-5551234', 'enterprise'),
    ('c1000000-0000-0000-0000-000000000002', 'PT Sejahtera Abadi', 'contact@sejahtera.co.id', '021-5555678', 'enterprise'),
    ('c1000000-0000-0000-0000-000000000003', 'Toko Berkah', 'berkah@gmail.com', '0812-3456-7890', 'standard'),
    ('c1000000-0000-0000-0000-000000000004', 'Warung Makmur', 'makmur@yahoo.com', '0856-1234-5678', 'standard'),
    ('c1000000-0000-0000-0000-000000000005', 'UD Sentosa', 'sentosa@outlook.com', '0878-9012-3456', 'smb');

INSERT INTO orders (id, customer_id, region_id, order_date, status, total_amount) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'c1000000-0000-0000-0000-000000000001', 'a1000000-0000-0000-0000-000000000001', '2026-07-15', 'completed', 37000000),
    ('d1000000-0000-0000-0000-000000000002', 'c1000000-0000-0000-0000-000000000002', 'a1000000-0000-0000-0000-000000000002', '2026-07-20', 'completed', 22500000),
    ('d1000000-0000-0000-0000-000000000003', 'c1000000-0000-0000-0000-000000000003', 'a1000000-0000-0000-0000-000000000003', '2026-07-25', 'completed', 5000000),
    ('d1000000-0000-0000-0000-000000000004', 'c1000000-0000-0000-0000-000000000004', 'a1000000-0000-0000-0000-000000000004', '2026-08-01', 'completed', 1500000),
    ('d1000000-0000-0000-0000-000000000005', 'c1000000-0000-0000-0000-000000000005', 'a1000000-0000-0000-0000-000000000005', '2026-08-05', 'pending', 18500000);

INSERT INTO payments (order_id, method, amount, status, paid_at) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'bank_transfer', 37000000, 'paid', '2026-07-15'),
    ('d1000000-0000-0000-0000-000000000002', 'credit_card', 22500000, 'paid', '2026-07-20'),
    ('d1000000-0000-0000-0000-000000000003', 'e_wallet', 5000000, 'paid', '2026-07-25'),
    ('d1000000-0000-0000-0000-000000000004', 'bank_transfer', 1500000, 'paid', '2026-08-01'),
    ('d1000000-0000-0000-0000-000000000005', 'credit_card', 18500000, 'pending', NULL);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000001', 1, 15000000),
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000008', 1, 1800000),
    ('d1000000-0000-0000-0000-000000000001', 'b1000000-0000-0000-0000-000000000009', 2, 500000),
    ('d1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000002', 1, 22000000),
    ('d1000000-0000-0000-0000-000000000002', 'b1000000-0000-0000-0000-000000000004', 1, 2500000),
    ('d1000000-0000-0000-0000-000000000003', 'b1000000-0000-0000-0000-000000000005', 2, 1200000),
    ('d1000000-0000-0000-0000-000000000004', 'b1000000-0000-0000-0000-000000000009', 3, 500000),
    ('d1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000003', 1, 18000000),
    ('d1000000-0000-0000-0000-000000000005', 'b1000000-0000-0000-0000-000000000006', 1, 3500000);

INSERT INTO business_rules (term, definition, example_sql) VALUES
    ('Revenue', 'Total amount of orders with status = completed and payment status = paid', 'SELECT SUM(o.total_amount) FROM orders o JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'''),
    ('Active User', 'A customer who has placed at least one order in the last 30 days', 'SELECT DISTINCT customer_id FROM orders WHERE order_date >= CURRENT_DATE - INTERVAL ''30 days'''),
    ('Monthly Revenue', 'Revenue aggregated by month based on order_date', 'SELECT DATE_TRUNC(''month'', order_date), SUM(total_amount) FROM orders WHERE status = ''completed'' GROUP BY 1'),
    ('Enterprise Customer', 'A customer with segment = enterprise', 'SELECT * FROM customers WHERE segment = ''enterprise'''),
    ('Gross Profit', 'Total revenue minus cost of goods sold', 'SELECT SUM(total_amount) - SUM(cost) FROM orders WHERE status = ''completed'''),
    ('Net Profit', 'Gross profit minus operating expenses', 'SELECT SUM(total_amount) - SUM(cost) - SUM(operating_expense) FROM orders WHERE status = ''completed'''),
    ('Customer Lifetime Value', 'Total revenue from a customer over their entire relationship', 'SELECT c.name, SUM(o.total_amount) AS clv FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = ''completed'' GROUP BY c.id, c.name'),
    ('Churn Rate', 'Percentage of customers who have not placed an order in the last 90 days', 'SELECT COUNT(CASE WHEN last_order < CURRENT_DATE - INTERVAL ''90 days'' THEN 1 END)::FLOAT / COUNT(*) AS churn_rate FROM customers'),
    ('Average Order Value', 'Total revenue divided by number of completed orders', 'SELECT SUM(total_amount) / COUNT(*) AS aov FROM orders WHERE status = ''completed'''),
    ('Customer Segmentation', 'Grouping customers by purchase behavior: enterprise (segment=enterprise), smb (segment=smb), standard (segment=standard)', 'SELECT segment, COUNT(*), SUM(total_amount) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY segment');

INSERT INTO sql_examples (question, sql, description, difficulty) VALUES
    ('Berapa total revenue bulan lalu?', 'SELECT SUM(o.total_amount) AS total_revenue FROM orders o JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'' AND o.order_date >= DATE_TRUNC(''month'', CURRENT_DATE - INTERVAL ''1 month'') AND o.order_date < DATE_TRUNC(''month'', CURRENT_DATE)', 'Calculate total revenue for last month', 'easy'),
    ('10 customer dengan revenue terbesar', 'SELECT c.name, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.status = ''completed'' GROUP BY c.id, c.name ORDER BY total_spent DESC LIMIT 10', 'Top 10 customers by revenue', 'medium'),
    ('Revenue per region bulan lalu', 'SELECT r.name AS region, SUM(o.total_amount) AS revenue FROM orders o JOIN regions r ON o.region_id = r.id JOIN payments p ON o.id = p.order_id WHERE o.status = ''completed'' AND p.status = ''paid'' AND o.order_date >= DATE_TRUNC(''month'', CURRENT_DATE - INTERVAL ''1 month'') GROUP BY r.id, r.name ORDER BY revenue DESC', 'Revenue breakdown by region', 'medium'),
    ('Berapa jumlah produk per kategori?', 'SELECT category, COUNT(*) AS product_count FROM products GROUP BY category ORDER BY product_count DESC', 'Count products per category', 'easy'),
    ('Siapa saja customer enterprise?', 'SELECT name, email, phone FROM customers WHERE segment = ''enterprise''', 'List enterprise customers', 'easy'),
    ('Order pending saat ini?', 'SELECT o.id, c.name, o.total_amount, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.status = ''pending'' ORDER BY o.order_date DESC', 'List pending orders', 'easy'),
    ('Total pembayaran per metode?', 'SELECT method, COUNT(*) AS transaction_count, SUM(amount) AS total_amount FROM payments WHERE status = ''paid'' GROUP BY method ORDER BY total_amount DESC', 'Payment summary by method', 'medium'),
    ('Produk termahal di kategori Electronics?', 'SELECT name, price, sku FROM products WHERE category = ''Electronics'' ORDER BY price DESC LIMIT 5', 'Top 5 most expensive electronics', 'easy'),
    ('Customer dengan order terbanyak?', 'SELECT c.name, COUNT(o.id) AS order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name ORDER BY order_count DESC LIMIT 10', 'Customers with most orders', 'medium'),
    ('Revenue bulanan tahun 2026?', 'SELECT DATE_TRUNC(''month'', order_date) AS month, SUM(total_amount) AS revenue FROM orders WHERE status = ''completed'' AND order_date >= ''2026-01-01'' AND order_date < ''2027-01-01'' GROUP BY 1 ORDER BY 1', 'Monthly revenue for 2026', 'medium'),
    ('Order items terbanyak?', 'SELECT p.name, SUM(oi.quantity) AS total_quantity FROM order_items oi JOIN products p ON oi.product_id = p.id GROUP BY p.id, p.name ORDER BY total_quantity DESC LIMIT 10', 'Most ordered products', 'medium'),
    ('Customer yang belum bayar?', 'SELECT DISTINCT c.name, c.email FROM customers c JOIN orders o ON c.id = o.customer_id JOIN payments p ON o.id = p.order_id WHERE p.status = ''pending''', 'Customers with pending payments', 'medium');
