CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

INSERT INTO categories (name) VALUES ('Процесори'), ('Відеокарти'), ('SSD');

INSERT INTO components (name, price, category_id) VALUES 
('AMD Ryzen 5 3600', 2800, 1),
('AMD Ryzen 5 5500', 3400, 1),
('Nvidia RTX 2060 Super', 6500, 2),
('Nvidia RTX 3060 12GB', 9000, 2),
('Kingston NV2 1TB', 2200, 3);

SELECT 
    components.name AS "Деталь", 
    components.price AS "Ціна (грн)", 
    categories.name AS "Категорія"
FROM components
JOIN categories ON components.category_id = categories.id;
