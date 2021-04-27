/*
	#
	# Bases de Dados 2020/2021
	# Trabalho Prático
	#
*/

/* Create users' table */
CREATE TABLE auction_user (
	username varchar(512) UNIQUE NOT NULL,
	password varchar(512) NOT NULL,
	PRIMARY KEY(username)
);


/* Create auction table */
CREATE TABLE auction (
	title		 varchar(512) NOT NULL,
	description		 varchar(512) NOT NULL,
	id			 varchar(512) UNIQUE NOT NULL,
	finish_date		 DATE,
	biddding		 FLOAT(8) NOT NULL,
	auction_user_username varchar(512) NOT NULL,
	PRIMARY KEY(id)
);

/* Create bidding table */
CREATE TABLE bidding (
	price		 FLOAT(8) NOT NULL,
	bid_date		 DATE,
	auction_id		 varchar(512),
	auction_user_username varchar(512),
	PRIMARY KEY(bid_date,auction_id,auction_user_username)
);

/* Create bidding message table */
CREATE TABLE bidding_msg (
	id_			 varchar(512),
	content		 varchar(512),
	auction_user_username varchar(512) NOT NULL,
	auction_id		 varchar(512) NOT NULL,
	PRIMARY KEY(id_)
);

/* Create mural message table */
CREATE TABLE mural_msg (
	id			 varchar(512),
	content		 varchar(512),
	sent_date		 DATE,
	auction_id		 varchar(512) NOT NULL,
	auction_user_username varchar(512) NOT NULL,
	PRIMARY KEY(id)
);

/* Create auction history table */
CREATE TABLE history (
	change_date	 DATE NOT NULL,
	old_title	 varchar(512),
	old_description varchar(512),
	auction_id	 varchar(512),
	PRIMARY KEY(auction_id)
);

ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk2 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding_msg ADD CONSTRAINT bidding_msg_fk1 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding_msg ADD CONSTRAINT bidding_msg_fk2 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_msg ADD CONSTRAINT mural_msg_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_msg ADD CONSTRAINT mural_msg_fk2 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE history ADD CONSTRAINT history_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);

INSERT INTO auction_user VALUES ('debug', 'pass');
INSERT INTO auction_user VALUES ('Alberto', 't9FrBVvgy');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Bonita cama de madeira', 'Cama feita em madeira bem conservada de 2010', 'cama', 100, '2021-04-27T00:00:00'::timestamp, 'debug');


/* Insere os departamentos

INSERT INTO dep VALUES (10, 'Contabilidade', 'Condeixa');
INSERT INTO dep VALUES (20, 'Investigacao',  'Mealhada');
INSERT INTO dep VALUES (30, 'Vendas',        'Coimbra');
INSERT INTO dep VALUES (40, 'Planeamento',   'Montemor');
*/


/* Insere os empregrados
 * Note-se  que  como  existe a  restricao  de  o  numero
 * do encarregado ser uma chave estrangeira (que por acaso
 * aponta  para a  chave primaria  da  mesma  tabela)  os
 * empregados  teem  que  ser  inseridos na  ordem certa.
 * Primeiro o presidente (que nao tem superiores)  depois
 * os empregados cujo encarregado e' o presidente e assim
 * sucessivamente.
 *

INSERT INTO emp VALUES(1839, 'Jorge Sampaio',  'Presidente'  ,NULL, '1984-02-11', 890000,  NULL, 10);

INSERT INTO emp VALUES(1566, 'Augusto Reis',   'Encarregado' ,1839, '1985-02-13', 450975,  NULL, 20);
INSERT INTO emp VALUES(1698, 'Duarte Guedes',  'Encarregado' ,1839, '1991-11-25', 380850,  NULL, 30);
INSERT INTO emp VALUES(1782, 'Silvia Teles',   'Encarregado' ,1839, '1986-11-03',  279450,  NULL, 10);

INSERT INTO emp VALUES(1788, 'Maria Dias',     'Analista'    ,1566, '1982-11-07',  565000,  NULL, 20);
INSERT INTO emp VALUES(1902, 'Catarina Silva', 'Analista'    ,1566, '1993-04-13',  435000,  NULL, 20);

INSERT INTO emp VALUES(1499, 'Joana Mendes',   'Vendedor'    ,1698, '1984-10-04',  145600, 56300, 30);
INSERT INTO emp VALUES(1521, 'Nelson Neves',   'Vendedor'    ,1698, '1983-02-27',  212250, 98500, 30);
INSERT INTO emp VALUES(1654, 'Ana Rodrigues',  'Vendedor'    ,1698, '1990-12-17',  221250, 81400, 30);
INSERT INTO emp VALUES(1844, 'Manuel Madeira', 'Vendedor'    ,1698, '1985-04-21',  157800,     0, 30);
INSERT INTO emp VALUES(1900, 'Tome Ribeiro',   'Continuo'    ,1698, '1994-03-05',   56950,  NULL, 30);

INSERT INTO emp VALUES(1876, 'Rita Pereira',   'Continuo'    ,1788, '1996-02-07',   65100,  NULL, 20);
INSERT INTO emp VALUES(1934, 'Olga Costa',     'Continuo'    ,1782, '1986-06-22',   68300,  NULL, 10);

INSERT INTO emp VALUES(1369, 'Antonio Silva',  'Continuo'    ,1902, '1996-12-22',  70800,  NULL, 20);




INSERT INTO descontos VALUES (1, 55000, 99999);
INSERT INTO descontos VALUES (2, 100000, 210000);
INSERT INTO descontos VALUES (3, 210001, 350000);
INSERT INTO descontos VALUES (4, 350001, 550000);
INSERT INTO descontos VALUES (5, 550001, 9999999);
*/

