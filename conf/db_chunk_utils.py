import psycopg2
from psycopg2.extras import execute_values


def execute_query_in_chunks(cursor, query, data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        try:
            execute_values(cursor, query, chunk)
        except psycopg2.DatabaseError as e:
            print(f"Database error occurred: {e}")
