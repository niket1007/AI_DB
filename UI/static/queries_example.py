QUERIES_EXAMPLE = """
---
### 1. SELECT
SELECT DISTINCT column1, column2, ... FROM table_name JOIN another_table ON condition WHERE condition GROUP BY column_name(s) HAVING group_condition ORDER BY column_name(s) ASC|DESC LIMIT number_of_rows;

---
### 2. INSERT INTO SPECIFIC COLUMNS
INSERT INTO table_name (column1, column2, column3, ...) VALUES (value1, value2, value3, ...);

---
### 3. INSERT DATA INTO ALL COLUMNS
INSERT INTO VALUES (value1, value2, value3, ...);

---
### 4. INSERT INTO MULTIPLE ROWS
INSERT INTO table_name (column1, column2) VALUES (valueA1, valueA2),(valueB1, valueB2),(valueC1, valueC2);

---
### 5. INSERT DATA FROM ANOTHER TABLE
INSERT INTO table_name1 (columnA1, columnA2) SELECT .... ;

---
### 6. UPDATE
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition
"""