-- Bulk seed for load testing (~2.5M rows total).
-- Appends to existing seed.sql data. NOT idempotent: for a fresh run use
--   make infra-fresh && make migrate && make seed && make seed-bulk
-- Volumes: 100k customers, 10k products, 500k orders, 1.5M order items, ~460k payments.

INSERT INTO regions (id, name, code)
VALUES
    ('a1000000-0000-0000-0000-000000000006', 'Sumatera Utara', 'SMU'),
    ('a1000000-0000-0000-0000-000000000007', 'Riau', 'RIA'),
    ('a1000000-0000-0000-0000-000000000008', 'Kalimantan Timur', 'KTM'),
    ('a1000000-0000-0000-0000-000000000009', 'Sulawesi Selatan', 'SLS'),
    ('a1000000-0000-0000-0000-000000000010', 'Bali', 'BAL')
ON CONFLICT (code) DO NOTHING;

INSERT INTO customers (id, name, email, phone, segment)
SELECT
    ('c1000000-0000-0000-0000-000000' || lpad(i::text, 6, '0'))::uuid,
    'Customer ' || i,
    'customer' || i || '@example.com',
    '08' || lpad(i::text, 10, '0'),
    (ARRAY['standard', 'standard', 'standard', 'standard', 'smb', 'smb', 'enterprise'])[1 + trunc(random() * 7)::int]
FROM generate_series(6, 100005) AS i;

INSERT INTO products (id, name, category, price, sku)
SELECT
    ('b2000000-0000-0000-0000-000000' || lpad(i::text, 6, '0'))::uuid,
    'Produk ' || i,
    (ARRAY['Electronics', 'Fashion', 'Furniture', 'Groceries'])[1 + (i % 4)],
    50000 + trunc(random() * 29950000),
    'SKU-' || i
FROM generate_series(1, 10000) AS i;

INSERT INTO orders (id, customer_id, region_id, order_date, status, total_amount)
SELECT
    ('d2000000-0000-0000-0000-000000' || lpad(i::text, 6, '0'))::uuid,
    ('c1000000-0000-0000-0000-000000' || lpad((1 + trunc(random() * 100005)::int)::text, 6, '0'))::uuid,
    ('a1000000-0000-0000-0000-0000000000' || lpad((1 + trunc(random() * 10)::int)::text, 2, '0'))::uuid,
    now() - (trunc(random() * 540)::int || ' days')::interval - (trunc(random() * 86400)::int || ' seconds')::interval,
    (ARRAY['completed', 'completed', 'completed', 'completed', 'completed', 'completed', 'pending', 'pending', 'cancelled', 'cancelled'])[1 + trunc(random() * 10)::int],
    0
FROM generate_series(1, 500000) AS i;

-- 1.5M items in two batches. All picks derive from g.seq so the planner must
-- evaluate them per row (a constant from random() got reused for the whole batch).
INSERT INTO order_items (id, order_id, product_id, quantity, unit_price)
SELECT
    ('e1000000-0000-0000-0000-000000' || lpad(g.seq::text, 6, '0'))::uuid,
    ('d2000000-0000-0000-0000-000000' || lpad((((g.seq - 1) % 500000) + 1)::text, 6, '0'))::uuid,
    p.id,
    ((g.seq + 3) % 5) + 1,
    p.price
FROM generate_series(1, 999999) AS g(seq)
JOIN products p
  ON p.id = ('b2000000-0000-0000-0000-000000' || lpad(((((g.seq * 2654435761) % 10000) + 10000) % 10000 + 1)::text, 6, '0'))::uuid;

INSERT INTO order_items (id, order_id, product_id, quantity, unit_price)
SELECT
    ('e2000000-0000-0000-0000-000000' || lpad(g.seq::text, 6, '0'))::uuid,
    ('d2000000-0000-0000-0000-000000' || lpad((((g.seq - 1) % 500000) + 1)::text, 6, '0'))::uuid,
    p.id,
    ((g.seq + 8) % 5) + 1,
    p.price
FROM generate_series(1, 500001) AS g(seq)
JOIN products p
  ON p.id = ('b2000000-0000-0000-0000-000000' || lpad(((((g.seq * 2654435761) % 10000) + 10000) % 10000 + 1)::text, 6, '0'))::uuid;

UPDATE orders o
SET total_amount = s.tot
FROM (
    SELECT order_id, SUM(quantity::numeric * unit_price) AS tot
    FROM order_items
    GROUP BY order_id
) s
WHERE s.order_id = o.id;

INSERT INTO payments (order_id, method, amount, status, paid_at)
SELECT
    id,
    (ARRAY['bank_transfer', 'credit_card', 'e_wallet', 'gopay', 'bca_va'])[1 + trunc(random() * 5)::int],
    total_amount,
    'paid',
    order_date + (trunc(random() * 72)::int || ' hours')::interval
FROM orders
WHERE status = 'completed'
  AND random() < 0.97;