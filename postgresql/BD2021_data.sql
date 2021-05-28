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
	finish_date		 timestamp,
	bidding		 FLOAT(8) NOT NULL,
	final_user_username varchar(512),
	auction_user_username varchar(512) NOT NULL,
	PRIMARY KEY(id)
);
/* Create bidding table */
CREATE TABLE bidding (
	price		 FLOAT(8) NOT NULL,
	bid_date		 timestamp,
	auction_id		 varchar(512),
	auction_user_username varchar(512),
	PRIMARY KEY(bid_date,auction_id,auction_user_username)
);

CREATE TABLE bidding_msg (
	id_			 varchar(512),
	content		 varchar(512),
	auction_user_username varchar(512) NOT NULL,
	auction_id		 varchar(512) NOT NULL,
	PRIMARY KEY(id_)
);

CREATE TABLE mural_msg (
	id			 varchar(512),
	content		 varchar(512),
	sent_date		 timestamp,
	auction_id		 varchar(512) NOT NULL,
	auction_user_username varchar(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE history (
	change_date	 timestamp NOT NULL,
	old_title	 varchar(512),
	old_description varchar(512),
	auction_id	 varchar(512),
	PRIMARY KEY(change_date,auction_id)
);

ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk2 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding_msg ADD CONSTRAINT bidding_msg_fk1 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE bidding_msg ADD CONSTRAINT bidding_msg_fk2 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_msg ADD CONSTRAINT mural_msg_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_msg ADD CONSTRAINT mural_msg_fk2 FOREIGN KEY (auction_user_username) REFERENCES auction_user(username);
ALTER TABLE history ADD CONSTRAINT history_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);

/*INDICES*/
create index bidding_value on auction (bidding);
create index auction_aux on auction (id);
create index user_aux on auction_user (username);
create index bidding_aux on bidding (auction_id, auction_user_username);
create index message_aux on mural_msg (auction_id, auction_user_username);


/*TRIGGERS*/
create or replace function notif_bid() returns trigger
	language plpgsql
	as $$
	declare
		c1 cursor for
		SELECT auction_user_username 
		from auction where id=old.id
		UNION select auction_user_username 
		from bidding where auction_id=old.id;

		id varchar(512);
		message_content varchar(512);
	begin

		for r in c1
		loop
			if (r.auction_user_username!=old.auction_user_username) then
			SELECT CONCAT(r.auction_user_username, now(), old.id) into id;
			SELECT CONCAT('Bid has increased in auction ', old.id) into message_content;
			INSERT INTO mural_msg VALUES(id, message_content , now(), old.id, r.auction_user_username);
			end if;
		end loop;
	return new;
	end;
	$$;

create trigger notif_bid_trig
after UPDATE of bidding on auction
for each row
execute procedure notif_bid();


create or replace function history_auction() returns trigger
	language plpgsql
	as $$
	declare
		id varchar(512);
		message_content varchar(512);
	begin
		INSERT INTO history VALUES (now(), old.title, old.description, old.id);
		return new;
	end;
	$$;

create trigger history_auction_trig
after UPDATE of title on auction
for each row
execute procedure history_auction();


/*{ "username": "debug", "password": "pass" }*/
INSERT INTO auction_user VALUES ('debug', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MTk1NTY1NDQsInN1YiI6InBhc3MifQ.rBxKYTw2UPxXjnF4ODsxntTFOisWiHvvZPcwHz-URMs');
INSERT INTO auction_user VALUES ('marianaLanca', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MTk1NTY1NDQsInN1YiI6InBhc3MifQ.rBxKYTw2UPxXjnF4ODsxntTFOisWiHvvZPcwHz-URMs');
INSERT INTO auction_user VALUES ('marianaLoreto', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MTk1NTY1NDQsInN1YiI6InBhc3MifQ.rBxKYTw2UPxXjnF4ODsxntTFOisWiHvvZPcwHz-URMs');
INSERT INTO auction_user VALUES ('debug1', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3MDYsInN1YiI6InBhc3MifQ.h6Pmj-2ao7MNKTKesYANFVJtkVYoiF2SzIegYSYF1MY');
INSERT INTO auction_user VALUES ('debug2', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3MTAsInN1YiI6InBhc3MifQ.NYY5sRbHisPE-aswDKldCWq1N5fby_6AyUJ0Ko_5jPQ');
INSERT INTO auction_user VALUES ('debug3', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3MTQsInN1YiI6InBhc3MifQ.9S-c-F0yd6ZGr8MDftLfYS78x1VNBQXQU9RlvwxuS0U');
INSERT INTO auction_user VALUES ('debug4', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3MTcsInN1YiI6InBhc3MifQ.sTKp3Ne0hevGkn6Ui8u7LN_49d5z-uGKgfOi2fCUfCY');
INSERT INTO auction_user VALUES ('debug5', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3MjEsInN1YiI6InBhc3MifQ.iDPc0XP0e7hJVhrEYaYqJFdvIHKnbJDI1a3UumJH8U0');
INSERT INTO auction_user VALUES ('debug6', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3NTUsInN1YiI6InBhc3MifQ.KISRAB7IgA8mg8snzxGAEzE0VMctFUXKSEHRJX8iNKE');
INSERT INTO auction_user VALUES ('debug7', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3NjAsInN1YiI6InBhc3MifQ.sdMNcd6G5BeHq6Ym5XZvZ6YMHoVOFt23lEiBGbiMW4c');
INSERT INTO auction_user VALUES ('debug8', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3NjIsInN1YiI6InBhc3MifQ.sq9ycK4oA48e-74NUoI9HwrGrwbW0FyjhsTrj_W7jbk');
INSERT INTO auction_user VALUES ('debug9', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3NjQsInN1YiI6InBhc3MifQ.MpTpFcODvutO3WwQrYjrMpGO12trwh8Jcs-4Ym5e_8s');
INSERT INTO auction_user VALUES ('debug10', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MjE5NTA3NjYsInN1YiI6InBhc3MifQ.X9yOc-ZLeitOdMqzzNZRN9WQAFybp3GYf2aWMSpp6pc');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Bonita cama de madeira', 'Cama feita em madeira bem conservada de 2010', 'cama 1.0', 100, '2022-04-28T20:00:00'::timestamp, 'debug');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Bonita cama de madeira de carvalho', 'Cama feita em madeira bem conservada de 2011', 'cama 2.0', 150, '2022-04-27T19:10:00'::timestamp, 'debug');

INSERT INTO auction (title, description, id, bidding, finish_date, final_user_username, auction_user_username)
                VALUES ('Cana de pesca antiga', 'Cana hiper mega antiga', 'cana 1.0', 150, '2021-06-27T19:10:00'::timestamp, null, 'marianaLoreto');

INSERT INTO auction (title, description, id, bidding, finish_date, final_user_username, auction_user_username)
                VALUES ('Cana de pesca antiga de madeira', 'Cana hiper mega antiga de madeira', 'cana 2.0', 150, '2021-05-31T19:10:00'::timestamp, null, 'marianaLoreto');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Dente de Trex', 'Dente de Trex super fixe! mais velho do que todos nós', 'dente dinossauro', 1000, '2021-05-28T19:10:00'::timestamp, 'debug3');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Escova de dentes da Britney Espargos', 'Escova de dentes usada pela própria e única BRITNEY ESPARGOS', 'escova dentes', 5000, '2021-06-03T19:00:00'::timestamp, 'marianaLoreto');

INSERT INTO auction (title, description, id, bidding, finish_date, auction_user_username)
                VALUES ('Cabelo do Vinho Diesel', 'Último cabelo da cabeça do Vinho Diesel <3', 'cabelo', 3000, '2021-08-30T19:01:00'::timestamp, 'marianaLanca');


INSERT INTO bidding VALUES (150, '2021-05-24T11:13:16'::timestamp, 'cama 1.0', 'debug');
INSERT INTO bidding VALUES (160, '2021-05-25T13:56:32'::timestamp, 'cama 1.0', 'debug1');

UPDATE auction SET bidding=160 WHERE id='cama 1.0';

INSERT INTO bidding VALUES (180, '2021-05-15T10:15:00'::timestamp, 'cama 2.0', 'debug5');

UPDATE auction SET bidding=180 WHERE id='cama 2.0';

INSERT INTO bidding VALUES (160, '2021-05-02T12:00:16'::timestamp, 'cana 2.0', 'debug8');
INSERT INTO bidding VALUES (200, '2021-05-08T13:20:50'::timestamp, 'cana 2.0', 'debug1');
INSERT INTO bidding VALUES (251, '2021-05-20T16:20:59'::timestamp, 'cana 2.0', 'debug5');

UPDATE auction SET bidding=251 WHERE id='cana 2.0';

INSERT INTO bidding VALUES (1900, '2021-05-21T11:15:36'::timestamp, 'dente dinossauro', 'debug');
INSERT INTO bidding VALUES (1901, '2021-05-21T11:16:02'::timestamp, 'dente dinossauro', 'debug1');

UPDATE auction SET bidding=1901 WHERE id='dente dinossauro';

INSERT INTO bidding VALUES (150, '2021-05-28T00:00:03'::timestamp, 'escova dentes', 'debug10');
INSERT INTO bidding VALUES (160, '2021-05-28T01:25:12'::timestamp, 'escova dentes', 'debug8');
INSERT INTO bidding VALUES (180, '2021-05-28T00:25:25'::timestamp, 'escova dentes', 'debug2');
INSERT INTO bidding VALUES (200, '2021-05-28T13:10:49'::timestamp, 'escova dentes', 'debug9');

UPDATE auction SET bidding=200 WHERE id='escova dentes';

INSERT INTO mural_msg VALUES('debug1_escova dentes_2021-05-28T00:00:03', 'Is this toothbrush authentic?', '2021-05-28T00:00:03', 'escova dentes', 'debug1'); 
