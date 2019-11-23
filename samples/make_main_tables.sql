/* name of the table - can be different and you need to specify it in Config Vars as CHANNEL_NAME */

/* postgres */
CREATE TABLE public.chat_ids (
	chat_id int4 NULL,
	"name" varchar NULL
);

CREATE TABLE public.<your_table_name>(
	subscribers int4 NULL,
	"views" int4 NULL,
	datetime timestamp NULL
);

commit

/* oracle */
CREATE TABLE CHAT_IDS (
    CHAT_ID   NUMBER(10) NULL,
    NAME   VARCHAR2(50) NULL
);

CREATE TABLE <your_table_name> (
    SUBSCRIBERS   NUMBER(10) NULL,
    VIEWS       NUMBER(10) NULL,
    DATETIME      TIMESTAMP NULL
);

commit