BEGIN;
alter TABLE "webconsole_trade" add "h1" varchar(200) NULL;
alter TABLE "webconsole_trade" add "m10" varchar(200) NULL;
alter TABLE "webconsole_trade" add "h3" varchar(200) NULL;
alter TABLE "webconsole_trade" add "d" varchar(200) NULL;
COMMIT;
