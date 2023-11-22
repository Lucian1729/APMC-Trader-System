DELIMITER //

CREATE PROCEDURE get_employee_payment(trader_id INT)
BEGIN
    SELECT SUM(salary) AS total_payment
    FROM Employee
    WHERE Trader_ID = trader_id;
END;
//

DELIMITER ;