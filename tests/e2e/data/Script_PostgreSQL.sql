DROP TABLE IF EXISTS table_e2e_refresh;

DROP TABLE IF EXISTS table_complex;
DROP TABLE IF EXISTS table_supported;
DROP TABLE IF EXISTS table_simple;

CREATE TABLE table_simple (
    id INTEGER PRIMARY KEY,
    text_value TEXT NOT NULL
);

INSERT INTO table_simple (id, text_value)
VALUES
    (1, 'First row'),
    (2, 'Second row'),
    (3, 'Third row');

CREATE TABLE table_supported (
    id INTEGER PRIMARY KEY,
    boolean_value BOOLEAN NOT NULL,
    date_value DATE NOT NULL,
    datetime_value TIMESTAMP NOT NULL,
    float_value DOUBLE PRECISION NOT NULL,
    integer_value INTEGER NOT NULL,
    numeric_value NUMERIC(10, 2) NOT NULL,
    string_value VARCHAR(100) NOT NULL,
    time_value TIME NOT NULL,
    uuid_value UUID NOT NULL
);

INSERT INTO table_supported (
    id,
    boolean_value,
    date_value,
    datetime_value,
    float_value,
    integer_value,
    numeric_value,
    string_value,
    time_value,
    uuid_value
)
VALUES
    (
        1,
        TRUE,
        '2026-01-01',
        '2026-01-01 10:30:00',
        10.5,
        100,
        123.45,
        'First row',
        '10:30:00',
        '11111111-1111-1111-1111-111111111111'
    ),
    (
        2,
        FALSE,
        '2026-06-15',
        '2026-06-15 15:45:30',
        20.75,
        200,
        678.90,
        'Second row',
        '15:45:30',
        '22222222-2222-2222-2222-222222222222'
    ),
    (
        3,
        TRUE,
        '2026-12-31',
        '2026-12-31 23:59:59',
        30.25,
        300,
        999.99,
        'Third row',
        '23:59:59',
        '33333333-3333-3333-3333-333333333333'
    );

CREATE TABLE table_complex (
    id INTEGER PRIMARY KEY,
    json_value JSONB NOT NULL,
    array_value INTEGER[] NOT NULL,
    binary_value BYTEA NOT NULL
);

INSERT INTO table_complex (
    id,
    json_value,
    array_value,
    binary_value
)
VALUES
    (
        1,
        '{"name": "Alice", "active": true}',
        ARRAY[1, 2, 3],
        decode('48656C6C6F', 'hex')
    ),
    (
        2,
        '{"name": "Bob", "active": false}',
        ARRAY[4, 5, 6],
        decode('576F726C64', 'hex')
    ),
    (
        3,
        '{"name": "Charlie", "active": true}',
        ARRAY[7, 8, 9],
        decode('54657374', 'hex')
    );

-- ============================================================================
-- TABLES FOR CONSTRAINT TESTS
-- ============================================================================

DROP TABLE IF EXISTS table_constraints_child;
DROP TABLE IF EXISTS table_constraints_parent;

-- ============================================================================
-- PARENT TABLE
-- ============================================================================

CREATE TABLE table_constraints_parent (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE
);

-- ============================================================================
-- CHILD TABLE
-- ============================================================================

CREATE TABLE table_constraints_child (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    value INTEGER CHECK (value >= 0),

    CONSTRAINT fk_table_constraints_child_parent
        FOREIGN KEY (parent_id)
        REFERENCES table_constraints_parent(id)
);
