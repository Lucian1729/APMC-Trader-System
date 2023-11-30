-- Create Tables
CREATE TABLE Trader (
    Trader_ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    current_holdings_amount DECIMAL(10, 2),
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Supplier (
    Supplier_ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    balance_amount DECIMAL(10, 2),
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Buyer (
    Buyer_ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(20),
    balance_amount DECIMAL(10, 2),
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Employee (
    Employee_ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    salary DECIMAL(10, 2),
    role VARCHAR(50),
    Trader_ID INT,
    FOREIGN KEY (Trader_ID) REFERENCES Trader(Trader_ID)
);

CREATE TABLE Transaction_Status (
    Transaction_Status_ID INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(50) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE Item (
    Item_ID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    grade VARCHAR(50),
    price_per_unit DECIMAL(10, 2),
    current_stock INT
);

CREATE TABLE Transaction (
    Transaction_ID INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50) NOT NULL,
    date DATE,
    quantity INT,
    total_amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    Trader_ID INT,
    Transaction_Status_ID INT,
    Item_ID INT,
    FOREIGN KEY (Trader_ID) REFERENCES Trader(Trader_ID),
    FOREIGN KEY (Transaction_Status_ID) REFERENCES Transaction_Status(Transaction_Status_ID),
    FOREIGN KEY (Item_ID) REFERENCES Item(Item_ID)
);

CREATE TABLE Seller_Transaction (
    Transaction_ID INT,
    Seller_ID INT,
    PRIMARY KEY (Transaction_ID, Seller_ID),
    FOREIGN KEY (Transaction_ID) REFERENCES Transaction(Transaction_ID),
    FOREIGN KEY (Seller_ID) REFERENCES Supplier(Supplier_ID)
);

CREATE TABLE Buyer_Transaction (
    Transaction_ID INT,
    Buyer_ID INT,
    PRIMARY KEY (Transaction_ID, Buyer_ID),
    FOREIGN KEY (Transaction_ID) REFERENCES Transaction(Transaction_ID),
    FOREIGN KEY (Buyer_ID) REFERENCES Buyer(Buyer_ID)
);

-- Procedures
DELIMITER //

CREATE PROCEDURE get_employee_payment(trader_id INT)
BEGIN
    SELECT SUM(salary) AS total_payment
    FROM Employee
    WHERE Trader_ID = trader_id;
END;
//

DELIMITER ;

--Triggers
CREATE TRIGGER trg_transaction_fulfilled
AFTER UPDATE ON Transaction
FOR EACH ROW
BEGIN
    IF NEW.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'fulfilled') AND
       OLD.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'initialised') THEN

        IF NEW.type = 'With Supplier' THEN
            UPDATE Item
            SET current_stock = current_stock + NEW.quantity
            WHERE Item_ID = NEW.Item_ID;

            UPDATE Supplier
            SET balance_amount = balance_amount + NEW.total_amount
            WHERE Supplier_ID = (SELECT Seller_ID FROM Seller_Transaction WHERE Transaction_ID = NEW.Transaction_ID);
        ELSE
            UPDATE Item
            SET current_stock = current_stock - NEW.quantity
            WHERE Item_ID = NEW.Item_ID;

            UPDATE Buyer
            SET balance_amount = balance_amount + NEW.total_amount
            WHERE Buyer_ID = (SELECT Buyer_ID FROM Buyer_Transaction WHERE Transaction_ID = NEW.Transaction_ID);
        END IF;
    END IF;
END;

CREATE TRIGGER trg_transaction_completed
AFTER UPDATE ON Transaction
FOR EACH ROW
BEGIN
    IF NEW.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'completed') AND
       OLD.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'initialised') THEN

        IF NEW.type = 'With Supplier' THEN
            UPDATE Item
            SET current_stock = current_stock + NEW.quantity
            WHERE Item_ID = NEW.Item_ID;

            UPDATE Trader
            SET current_holdings_amount = current_holdings_amount - NEW.total_amount
            WHERE Trader_ID = NEW.Trader_ID;
        ELSE
            UPDATE Item
            SET current_stock = current_stock - NEW.quantity
            WHERE Item_ID = NEW.Item_ID;

            UPDATE Trader
            SET current_holdings_amount = current_holdings_amount + NEW.total_amount
            WHERE Trader_ID = NEW.Trader_ID;
        END IF;
    END IF;
END;

CREATE TRIGGER trg_transaction_fulfilled_completed
AFTER UPDATE ON Transaction
FOR EACH ROW
BEGIN
    IF NEW.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'completed') AND
       OLD.Transaction_Status_ID = (SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = 'fulfilled') THEN

        IF NEW.type = 'With Supplier' THEN
            UPDATE Supplier
            SET balance_amount = balance_amount - NEW.total_amount
            WHERE Supplier_ID = (SELECT Seller_ID FROM Seller_Transaction WHERE Transaction_ID = NEW.Transaction_ID);

            UPDATE Trader
            SET current_holdings_amount = current_holdings_amount - NEW.total_amount
            WHERE Trader_ID = NEW.Trader_ID;
        ELSE
            UPDATE Buyer
            SET balance_amount = balance_amount - NEW.total_amount
            WHERE Buyer_ID = (SELECT Buyer_ID FROM Buyer_Transaction WHERE Transaction_ID = NEW.Transaction_ID);

            UPDATE Trader
            SET current_holdings_amount = current_holdings_amount + NEW.total_amount
            WHERE Trader_ID = NEW.Trader_ID;
        END IF;
    END IF;
END;

--Other Queries

UPDATE Trader
SET name = '{new_name}', 
    address = '{new_address}', 
    phone = '{new_phone}', 
    password = '{new_password}'
WHERE Trader_ID = {trader_id};

SELECT Supplier_ID, name FROM Supplier;

SELECT Buyer_ID, name FROM Buyer;

SELECT t.Transaction_ID, t.type, t.date, t.quantity, t.total_amount, t.payment_method,
    ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Seller_Transaction WHERE Seller_ID = {entity_id}
);

SELECT t.Transaction_ID, t.type, t.date, t.quantity, t.total_amount, t.payment_method,
    ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Buyer_Transaction WHERE Buyer_ID = {entity_id}
);

SELECT t.*, ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Seller_Transaction WHERE Seller_ID = {entity_id}
);

SELECT t.*, ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Buyer_Transaction WHERE Buyer_ID = {entity_id}
);

SELECT Transaction_Status_ID FROM Transaction_Status WHERE status = '{status}';

SELECT LAST_INSERT_ID();

SELECT * FROM Trader WHERE Trader_ID = {trader_id};

UPDATE Item SET price_per_unit = {new_price} WHERE Item_ID = {item_id};

DELETE FROM Supplier WHERE Supplier_ID = {supplier_id_to_delete};

DELETE FROM Buyer WHERE Buyer_ID = {buyer_id_to_delete};

INSERT INTO Transaction (type, date, quantity, total_amount, payment_method, Trader_ID, Transaction_Status_ID, Item_ID)
VALUES ('{transaction_type}', '{transaction_date}', {transaction_quantity}, {transaction_total_amount}, 
        '{transaction_payment_method}', {user["Trader_ID"]}, {fetch_transaction_status_id(initial_status)}, {item_id});

UPDATE Transaction
SET Transaction_Status_ID = {fetch_transaction_status_id(new_status)}
WHERE Transaction_ID = {selected_transaction_id};

INSERT INTO Item (name, type, grade, price_per_unit, current_stock)
VALUES ('{new_item_name}', '{new_item_type}', '{new_item_grade}', {new_item_price}, 0);

UPDATE Item SET price_per_unit = {updated_item_price} WHERE Item_ID = {item_id_to_update};

SELECT t.*, ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Seller_Transaction WHERE Seller_ID = {entity_id}
);

SELECT t.*, ts.status AS transaction_status, i.name AS item_name
FROM Transaction t
JOIN Transaction_Status ts ON t.Transaction_Status_ID = ts.Transaction_Status_ID
JOIN Item i ON t.Item_ID = i.Item_ID
WHERE t.Transaction_ID IN (
    SELECT Transaction_ID FROM Buyer_Transaction WHERE Buyer_ID = {entity_id}
);

SELECT balance_amount FROM {entity_type.capitalize()} WHERE {entity_type.capitalize()}_ID = {entity_id};
