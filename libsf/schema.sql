CREATE TABLE orders (
    id INTEGER AUTO_INCREMENT,
    ok BOOLEAN,
    stock TEXT,
    venue TEXT,
		direction INTEGER,
		originalQty INTEGER,
		qty INTEGER,
		price FLOAT,
		orderType INTEGER,
		account TEXT,
    ts DATETIME,
		totalFilled INTEGER,
		open BOOLEAN,
    primary key (id)
);


CREATE TABLE fills (
    id INTEGER AUTO_INCREMENT,
    price INTEGER,
    qty INTEGER,
		ts DATETIME,
    order_id INTEGER,
    primary key (id)
);
