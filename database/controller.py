#!/usr/bin/python
import mysql.connector as mariadb

mariadb_connection = mariadb.connect(user='ioto', password='tumadre', database='USERS')
cursor = mariadb_connection.cursor()
cursor.execute("SELECT * FROM users")

for row in cursor.fetchall():
    print row[1]

mariadb_connection.close()
