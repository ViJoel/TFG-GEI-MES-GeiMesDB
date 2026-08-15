create table if not exists connections (
    id text primary key,
    name text not null,
    driver text not null,
    host text,
    port text,
    database text,
    username text,
    password text,
    path text
);

create table if not exists queries_history (
    connection_id text not null,
    query text not null,
    executed_at timestamp default current_timestamp,

    foreign key (connection_id)
        references connections(id)
        on delete cascade
);

CREATE TABLE if not exists settings (
    key text primary key,
    value text not null
);
