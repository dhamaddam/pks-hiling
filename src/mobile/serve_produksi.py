import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.helper.Logfile import LogFile

produksi_module = Blueprint('produksi_module', __name__)

class serveProduksi:
    def __init__(self):
        self.logging = LogFile("daemon")
        self.logging.write("info", "serveProduksi initialized")

        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # ==========================
    # MAPPING KE TABEL MYSQL
    # ==========================
    def get_produksi_mapping(self):
        return {
            "expt_num": "expt_num",
            "palm_id": "palm_id",
            "female": "female",
            "male": "male",
            "tahun": "tahun",
            "bulan": "bulan",
            "tahun_bulan": "tahun_bulan",
            "no_percobaan": "no_percobaan",
            "cr_plan": "cr_plan",
            "crossing": "crossing",
            "baris": "baris",
            "pohon": "pohon",

            # PRODUKSI DATA
            "bn1": "bn1",
            "ffb1": "ffb1",
            "bn2": "bn2",
            "ffb2": "ffb2",
            "bn3": "bn3",
            "ffb3": "ffb3",
            "bn4": "bn4",
            "ffb4": "ffb4",
            "bn5": "bn5",
            "ffb5": "ffb5",
            "bn6": "bn6",
            "ffb6": "ffb6",

            "tot_bn": "tot_bn",
            "tot_ffb": "tot_ffb",
            "abw": "abw",
        }

    # ==========================
    # JSON → DB
    # ==========================
    def map_to_db(self, payload):
        mapping = self.get_produksi_mapping()
        result = {}

        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val

        return result

    # ==========================
    # INSERT
    # ==========================
    def insert_produksi(self, payload):
        self.logging.write("info", f"insert_produksi: {payload}")

        data = self.map_to_db(payload)
        if "expt_num" not in data:
            return {"status": "error", "message": "expt_num is required"}

        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = tuple(data.values())

        query = f"INSERT INTO produksi ({cols}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()

            return {"status": "success", "message": "Produksi inserted successfully"}

        except Exception as e:
            self.logging.write("error", f"Insert error: {str(e)}")
            return {"status": "error", "message": str(e)}


produksi_service = serveProduksi()

@produksi_module.route('/api/insert', methods=['POST'])
def api_produksi_insert():
    payload = request.get_json()
    return jsonify(produksi_service.insert_produksi(payload))
