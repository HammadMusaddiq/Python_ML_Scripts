#!/usr/bin/python

import psycopg2

ignore_table = ["auth_user_groups", "auth_group", "django_content_type", "auth_group_permissions", "auth_permission",
 "auth_user_user_permissions", "authtoken_token", "auth_user", "django_session", "django_migrations", "OCS_caches",
 "account_management_useractivity", "account_management_userprofile"]

def delete_part():
    
    conn = None
    rows_deleted = 0
    try:
        
        conn = psycopg2.connect(
        database="new_stagging", user='osint_db', password='1234', host='10.100.104.111', port= '5432'
        )
        print(conn)
        
        cur = conn.cursor()

        cur.execute("""SELECT relname FROM pg_class WHERE relkind='r'
                  AND relname !~ '^(pg_|sql_)';""") # "rel" is short for relation.

        tables = [i[0] for i in cur.fetchall()] # A list() of tables.
        for each_table in tables:
            
            if each_table not in ignore_table:
                cur.execute(f"DELETE FROM {each_table};")
                rows_deleted = cur.rowcount
                print(f"{rows_deleted} rows deleted from {each_table} ")
            else:
                pass
        
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return rows_deleted

delete_part()