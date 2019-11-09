CREATE TABLE public.chat_ids (
	chat_id int4 NULL,
	"name" varchar NULL
);


/* name of the table - can be different and you need to specify it in Config Vars as CHANNEL_NAME */
CREATE TABLE public.<your_table_name>(
	subscribers int4 NULL,
	"views" int4 NULL,
	datetime timestamp NULL
);

commit