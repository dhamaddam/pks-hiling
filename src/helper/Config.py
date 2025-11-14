import configparser
import os
import mysql.connector
import pandas as pd
from mysql.connector import Error

class Config:
    def __init__(self, config_file='config.ini', config_section='mysql'):
        self.config_file = config_file
        self.config_section = config_section
        self.connection = None
        self.config = self.read_db_config()

    def read_db_config(self):
        parser = configparser.ConfigParser()
        parser.read(self.config_file)

        if not parser.has_section(self.config_section):
            raise Exception(f"Section '{self.config_section}' not found in '{self.config_file}'")

        return {key: value for key, value in parser.items(self.config_section)}

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                port=int(self.config.get('port', 3306)),
                database=self.config.get('database', '')
            )
            if self.connection.is_connected():
                print("Koneksi berhasil!")
            return self.connection
        except Error as e:
            print("Gagal koneksi:", e)
            return None

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Koneksi ditutup.")

    def query(self, sql):
        try:
            conn = self.connect()
            df = pd.read_sql(sql, conn)
            return df
        except Exception as e:
            print("Gagal menjalankan query:", e)
            return None
        finally:
            self.disconnect()
