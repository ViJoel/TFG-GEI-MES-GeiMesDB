create table if not exists connections (
    id text primary key,
    name text not null,
    driver text not null,
    host text,
    port integer,
    database text,
    username text,
    password text,
    path text
);

insert into connections (
    id,
    name,
    driver,
    host,
    port,
    database,
    username,
    password,
    path
) values
(
    '1',
    'Producción PostgreSQL',
    'postgresql',
    '192.168.1.10',
    5432,
    'erp_prod',
    'admin',
    'secret123',
    null
),
(
    '2',
    'Desarrollo PostgreSQL',
    'postgresql',
    'localhost',
    5432,
    'erp_dev',
    'dev_user',
    'devpass',
    null
),
(
    '3',
    'MySQL Docker',
    'mysql',
    '172.17.0.2',
    3306,
    'shop_db',
    'root',
    'root',
    null
),
(
    '4',
    'Oracle Empresa',
    'oracle',
    '10.0.0.50',
    1521,
    'ORCLCDB',
    'system',
    'oracle',
    null
),
(
    '5',
    'SQLite Local',
    'sqlite',
    null,
    null,
    null,
    null,
    null,
    '/home/usuario/databases/local.db'
),
(
    '6',
    'SQLite Testing',
    'sqlite',
    null,
    null,
    null,
    null,
    null,
    '/tmp/testing.db'
),
(
    '7',
    'Servidor QA',
    'mysql',
    'qa.internal.local',
    3306,
    'qa_system',
    'qa_user',
    'qa_pass',
    null
),
(
    '8',
    'Analytics DB',
    'postgresql',
    'analytics.company.local',
    5432,
    'analytics',
    'bi_user',
    'analytics123',
    null
),
(
    '9',
    'Backup Oracle',
    'oracle',
    '192.168.100.20',
    1521,
    'BACKUPDB',
    'backup',
    'backup123',
    null
),
(
    '10',
    'Local MySQL',
    'mysql',
    '127.0.0.1',
    3306,
    'test_db',
    'tester',
    '1234',
    null
);
