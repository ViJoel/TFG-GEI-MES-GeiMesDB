create table if not exists connections (
    id integer primary key autoincrement,
    name text not null,
    driver text not null,
    host text,
    port integer,
    database text,
    username text,
    password text,
    path text
);