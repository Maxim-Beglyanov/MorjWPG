CREATE TABLE items(
    name varchar(128) NOT NULL,
    group_name varchar(128),
    price item_price,
    description text DEFAULT '',
    buyability boolean DEFAULT True,
    saleability boolean
);

ALTER TABLE builds
INHERIT items;

ALTER TABLE units
INHERIT items;
ALTER TABLE units
ADD COLUMN expenses real DEFAULT 0.0;

ALTER TABLE countries
ADD COLUMN alliance varchar(128);

DROP FUNCTION get_units_shop;
CREATE OR REPLACE FUNCTION get_units_shop() RETURNS TABLE(name varchar, group_name varchar, price item_price, description text, features text, expenses real, buyability boolean, saleability boolean, needed_for_purchase varchar) AS $$
    WITH default_buyability AS (
        SELECT column_default::boolean
        FROM information_schema.columns
        WHERE (table_schema, table_name, column_name) = ('public', 'units', 'buyability')
    ),
    default_saleability AS (
        SELECT column_default::boolean
        FROM information_schema.columns
        WHERE (table_schema, table_name, column_name) = ('public', 'units', 'saleability')
    )
    SELECT u.name AS unit_name, u.group_name, u.price, u.description, u.features, u.expenses,
           CASE
               WHEN u.buyability = (SELECT * FROM default_buyability) THEN NULL
               ELSE u.buyability
           END AS buyability,
           CASE
               WHEN u.saleability = (SELECT * FROM default_saleability) THEN NULL
               ELSE u.saleability
           END AS saleability,
           get_unit_needed_for_purchase(u.unit_id) AS needed_for_purchase
        FROM units u
    LEFT JOIN units_needed_for_purchase USING(unit_id)
    ORDER BY group_name NULLS FIRST;
$$ LANGUAGE SQL;

DROP FUNCTION get_units_inventory;
CREATE OR REPLACE FUNCTION get_units_inventory(getting_country_id int) RETURNS TABLE(name varchar, group_name varchar, count int, description text, features text, expenses real) AS $$
    SELECT name, group_name, count, description, features, expenses*count as expenses
    FROM units
    JOIN units_inventory USING(unit_id)
    WHERE country_id = getting_country_id
    ORDER BY group_name NULLS FIRST
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_income_country(getting_country_id int) RETURNS real AS $$
    SELECT COALESCE(
        (
            SELECT SUM(income*count) AS income
            FROM builds
            JOIN builds_inventory USING(build_id)
            WHERE country_id = getting_country_id
            GROUP BY country_id
        ), 0)-COALESCE(
        (
            SELECT SUM(expenses*count) AS expenses
            FROM units
            JOIN units_inventory USING(unit_id)
            WHERE country_id = getting_country_id
            GROUP BY country_id
        ), 0) AS income
$$ LANGUAGE SQL;
