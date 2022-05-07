ALTER TABLE builds
RENAME COLUMN group_item TO group_name;

ALTER TABLE units
RENAME COLUMN group_item TO group_name;

DROP FUNCTION get_needed_count_build;
DROP FUNCTION get_needed_count_unit;
DROP FUNCTION get_builds_shop;
DROP FUNCTION get_units_shop;
DROP FUNCTION get_builds_inventory;
DROP FUNCTION get_units_inventory;

CREATE OR REPLACE FUNCTION get_country_build_count(getting_country_id int, getting_build_id int) RETURNS int AS $$
    WITH inventory AS (
        SELECT country_id, count
        FROM builds_inventory
        WHERE country_id = getting_country_id AND build_id = getting_build_id
    )
    SELECT COALESCE(count, 0)
    FROM countries
    LEFT JOIN inventory USING(country_id)
    WHERE country_id = getting_country_id
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_country_unit_count(getting_country_id int, getting_unit_id int) RETURNS int AS $$
    WITH inventory AS (
        SELECT country_id, count
        FROM units_inventory
        WHERE country_id = getting_country_id AND unit_id = getting_unit_id
    )
    SELECT COALESCE(count, 0)
    FROM countries
    LEFT JOIN inventory USING(country_id)
    WHERE country_id = getting_country_id
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_builds_shop() RETURNS TABLE(name varchar, group_name varchar, price item_price, description text, income real, buyability boolean, saleability boolean, needed_for_purchase varchar) AS $$
    WITH default_buyability AS (
        SELECT column_default::boolean
        FROM information_schema.columns
        WHERE (table_schema, table_name, column_name) = ('public', 'builds', 'buyability')
    ),
    default_saleability AS (
        SELECT column_default::boolean
        FROM information_schema.columns
        WHERE (table_schema, table_name, column_name) = ('public', 'builds', 'saleability')
    ),
    needed_for_purchase AS (
        SELECT DISTINCT(build_id), build_group_id
        FROM builds_groups_needed_for_purchase
    )
    SELECT b.name AS build_name, b.group_name, b.price, b.description, b.income, 
           CASE
               WHEN b.buyability = (SELECT * FROM default_buyability) THEN NULL
               ELSE b.buyability
           END AS buyability,
           CASE
               WHEN b.saleability = (SELECT * FROM default_saleability) THEN NULL
               ELSE b.saleability
           END AS saleability,
           get_build_needed_for_purchase(b.build_id) AS needed_for_purchase
    FROM builds b
    ORDER BY group_name NULLS FIRST;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_units_shop() RETURNS TABLE(name varchar, group_name varchar, price item_price, description text, features text, buyability boolean, saleability boolean, needed_for_purchase varchar) AS $$
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
    SELECT u.name AS unit_name, u.group_name, u.price, u.description, u.features, 
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

CREATE OR REPLACE FUNCTION get_builds_inventory(getting_country_id int) RETURNS TABLE(name varchar, group_name varchar, count int, description text, income real) AS $$
    SELECT name, group_name, count, description, income*count AS income
    FROM builds
    JOIN builds_inventory USING(build_id)
    WHERE country_id = getting_country_id
    ORDER BY group_name NULLS FIRST
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_units_inventory(getting_country_id int) RETURNS TABLE(name varchar, group_name varchar, count int, description text, features text) AS $$
    SELECT name, group_name, count, description, features
    FROM units
    JOIN units_inventory USING(unit_id)
    WHERE country_id = getting_country_id
    ORDER BY group_name NULLS FIRST
$$ LANGUAGE SQL;
