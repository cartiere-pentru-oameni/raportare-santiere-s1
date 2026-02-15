import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from psycopg.types.json import Jsonb
from app.config import Config
from contextlib import contextmanager
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

# PostgreSQL connection pool
_connection_pool = None


def get_connection_pool():
    """Get or create the connection pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            Config.DATABASE_URL,
            min_size=1,
            max_size=20
        )
    return _connection_pool


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    pool = get_connection_pool()
    with pool.connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def convert_pg_types(row):
    """Convert PostgreSQL types to JSON-serializable types"""
    if row is None:
        return None

    converted = {}
    for key, value in row.items():
        if isinstance(value, UUID):
            converted[key] = str(value)
        elif isinstance(value, (datetime, date)):
            converted[key] = value.isoformat()
        elif isinstance(value, Decimal):
            converted[key] = float(value)
        else:
            converted[key] = value
    return converted


def prepare_value_for_insert(value):
    """Prepare a value for PostgreSQL insertion, handling JSONB columns"""
    if isinstance(value, dict):
        return Jsonb(value)
    elif isinstance(value, list) and value and isinstance(value[0], dict):
        # Handle list of dicts (JSONB arrays)
        return Jsonb(value)
    return value


class QueryBuilder:
    """Query builder to mimic Supabase API"""

    def __init__(self, table_name):
        self.table_name = table_name
        self._select_cols = '*'
        self._where_clauses = []
        self._where_params = []
        self._order_by = None
        self._limit_val = None
        self._offset_val = None
        self._operation = 'select'  # 'select', 'insert', 'update', 'delete'
        self._insert_data = None
        self._update_data = None

    def select(self, columns='*'):
        """Select columns"""
        self._select_cols = columns
        self._operation = 'select'
        return self

    def eq(self, column, value):
        """Add WHERE column = value"""
        self._where_clauses.append(f"{column} = %s")
        self._where_params.append(value)
        return self

    def neq(self, column, value):
        """Add WHERE column != value"""
        self._where_clauses.append(f"{column} != %s")
        self._where_params.append(value)
        return self

    def like(self, column, pattern):
        """Add WHERE column LIKE pattern"""
        self._where_clauses.append(f"{column} LIKE %s")
        self._where_params.append(pattern)
        return self

    def ilike(self, column, pattern):
        """Add WHERE column ILIKE pattern (case-insensitive)"""
        self._where_clauses.append(f"{column} ILIKE %s")
        self._where_params.append(pattern)
        return self

    def in_(self, column, values):
        """Add WHERE column IN (values)"""
        placeholders = ','.join(['%s'] * len(values))
        self._where_clauses.append(f"{column} IN ({placeholders})")
        self._where_params.extend(values)
        return self

    def order(self, column, desc=False):
        """Order by column"""
        direction = 'DESC' if desc else 'ASC'
        self._order_by = f"{column} {direction}"
        return self

    def limit(self, count):
        """Limit results"""
        self._limit_val = count
        return self

    def offset(self, count):
        """Offset results"""
        self._offset_val = count
        return self

    def insert(self, data):
        """Prepare insert operation"""
        self._operation = 'insert'
        self._insert_data = data
        return self

    def update(self, data):
        """Prepare update operation"""
        self._operation = 'update'
        self._update_data = data
        return self

    def delete(self):
        """Prepare delete operation"""
        self._operation = 'delete'
        return self

    def execute(self):
        """Execute the query based on operation type"""
        if self._operation == 'select':
            return self._execute_select()
        elif self._operation == 'insert':
            return self._execute_insert()
        elif self._operation == 'update':
            return self._execute_update()
        elif self._operation == 'delete':
            return self._execute_delete()

    def _execute_select(self):
        """Execute SELECT query"""
        query = f"SELECT {self._select_cols} FROM {self.table_name}"

        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)

        if self._order_by:
            query += f" ORDER BY {self._order_by}"

        if self._limit_val:
            query += f" LIMIT {self._limit_val}"

        if self._offset_val:
            query += f" OFFSET {self._offset_val}"

        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, self._where_params)
                data = [convert_pg_types(row) for row in cur.fetchall()]

        return type('Response', (), {'data': data})()

    def _execute_insert(self):
        """Execute INSERT query"""
        data = self._insert_data

        if isinstance(data, list):
            # Bulk insert
            if not data:
                return type('Response', (), {'data': []})()

            columns = list(data[0].keys())
            placeholders = ','.join(['%s'] * len(columns))
            query = f"INSERT INTO {self.table_name} ({','.join(columns)}) VALUES ({placeholders}) RETURNING *"

            with get_db_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    results = []
                    for row in data:
                        values = [prepare_value_for_insert(row[col]) for col in columns]
                        cur.execute(query, values)
                        results.append(convert_pg_types(cur.fetchone()))

            return type('Response', (), {'data': results})()
        else:
            # Single insert
            columns = list(data.keys())
            values = [prepare_value_for_insert(v) for v in data.values()]
            placeholders = ','.join(['%s'] * len(columns))
            query = f"INSERT INTO {self.table_name} ({','.join(columns)}) VALUES ({placeholders}) RETURNING *"

            with get_db_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute(query, values)
                    result = convert_pg_types(cur.fetchone())

            return type('Response', (), {'data': [result]})()

    def _execute_update(self):
        """Execute UPDATE query"""
        if not self._where_clauses:
            raise ValueError("UPDATE requires at least one WHERE clause")

        data = self._update_data
        set_clauses = [f"{col} = %s" for col in data.keys()]
        set_params = [prepare_value_for_insert(v) for v in data.values()]

        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)}"
        query += " WHERE " + " AND ".join(self._where_clauses)
        query += " RETURNING *"

        params = set_params + self._where_params

        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, params)
                results = [convert_pg_types(row) for row in cur.fetchall()]

        return type('Response', (), {'data': results})()

    def _execute_delete(self):
        """Execute DELETE query"""
        if not self._where_clauses:
            raise ValueError("DELETE requires at least one WHERE clause")

        query = f"DELETE FROM {self.table_name}"
        query += " WHERE " + " AND ".join(self._where_clauses)
        query += " RETURNING *"

        with get_db_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, self._where_params)
                results = [convert_pg_types(row) for row in cur.fetchall()]

        return type('Response', (), {'data': results})()


class DatabaseClient:
    """Database client to mimic Supabase client interface"""

    def table(self, table_name):
        """Get a query builder for a table"""
        return QueryBuilder(table_name)


# Create database client instances
db = DatabaseClient()
db_admin = DatabaseClient()  # Same as db since we removed RLS

# Legacy aliases for backwards compatibility
supabase = db
supabase_admin = db_admin
