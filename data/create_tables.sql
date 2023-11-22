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
