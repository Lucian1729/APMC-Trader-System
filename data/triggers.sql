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
