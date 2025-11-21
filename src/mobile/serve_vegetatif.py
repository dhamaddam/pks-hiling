import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.helper.Logfile import LogFile

# 🔹 Blueprint
vegetatif_module = Blueprint('vegetatif_module', __name__)

class serveVegetatif:
    def __init__(self):
        self.logging = LogFile("daemon")
        self.logging.write("info", "serveVegetatif initialized")

        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Database config
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # FIELD MAPPING
    # =====================
    def get_vegetatif_mapping(self):
        self.logging.write("info", "get_vegetatif_mapping called")
        return {
            "id": "id",
            "expt_num": "expt_num",
            "crossing": "crossing",
            "female": "female",
            "male": "male",
            "baris": "baris",
            "pohon": "pohon",
            "tinggi_tanaman": "tinggi_tanaman",
            "lb": "lb",
            "jlh_daun_frond": "jlh_daun_frond",
            "panjang_rachis": "panjang_rachis",
            "petiola_l": "petiola_l",
            "petiola_t": "petiola_t",
            "n": "n",
            "p1": "p1",
            "l1": "l1",
            "p2": "p2",
            "l2": "l2",
            "p3": "p3",
            "l3": "l3",
            "p4": "p4",
            "l4": "l4",
            "p5": "p5",
            "l5": "l5",
            "p6": "p6",
            "l6": "l6",
            "hi": "hi",
            "avg_p": "avg_p",
            "avg_l": "avg_l",
            "la": "la",
            "tot_la": "tot_la",
            "lai": "lai",
            "pcs": "pcs",
            "palm_id": "palm_id",
            "tahun": "tahun",
            "bulan": "bulan",
            "pelaksana_pengamatan" : "pelaksana_pengamatan",
            "usia_tanam": "usia_tanam",
            "tanggal_pengamatan" : "tanggal_pengamatan",
            "created_at": "created_at"
        }

    # =====================
    # JSON → DB
    # =====================
    def map_to_db(self, payload):
        self.logging.write("info", f"map_to_db called with payload: {payload}")

        mapping = self.get_vegetatif_mapping()
        result = {}

        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val

        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.logging.write("info", f"map_to_db result: {result}")
        return result

    # =====================
    # DB → JSON
    # =====================
    def map_to_mobile(self, db_row):
        self.logging.write("info", f"map_to_mobile called with row: {db_row}")

        mapping = self.get_vegetatif_mapping()
        reverse_map = {v: k for k, v in mapping.items()}

        result = {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

        self.logging.write("info", f"map_to_mobile result: {result}")
        return result

    # =====================
    # INSERT
    # =====================
    def insert_vegetatif(self, payload):
        self.logging.write("info", f"insert_vegetatif called with: {payload}")

        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO vegetatif ({columns}) VALUES ({placeholders})"

        self.logging.write("info", f"Executing SQL: {query}")
        self.logging.write("info", f"Values: {values}")

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()

            self.logging.write("info", "Insert vegetatif success")
            return {"status": "success", "message": "Vegetatif data inserted successfully"}

        except Exception as e:
            self.logging.write("error", f"Insert error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =====================
    # GET
    # =====================
    def get_vegetatif(self, id=None):
        self.logging.write("info", f"get_vegetatif called, id={id}")

        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            if id:
                query = "SELECT * FROM vegetatif WHERE id=%s"
                self.logging.write("info", f"Executing SQL: {query} | id={id}")
                cursor.execute(query, (id,))
            else:
                query = "SELECT * FROM vegetatif"
                self.logging.write("info", f"Executing SQL: {query}")
                cursor.execute(query)

            result = cursor.fetchall()
            conn.close()

            mapped = [self.map_to_mobile(row) for row in result]
            self.logging.write("info", f"get_vegetatif result count: {len(mapped)}")

            return mapped

        except Exception as e:
            self.logging.write("error", f"Get error: {str(e)}")
            return {"status": "error", "message": str(e)}


# ==========================================================
# ROUTES
# ==========================================================

vegetatif_service = serveVegetatif()

@vegetatif_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_vegetatif():
    try:
        vegetatif_service.logging.write("info", "api_insert_vegetatif hit")

        if request.method == 'POST':
            if not request.is_json:
                vegetatif_service.logging.write("error", "Invalid Content-Type")
                return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

            payload = request.get_json()
            vegetatif_service.logging.write("info", f"POST payload: {payload}")

            result = vegetatif_service.insert_vegetatif(payload)
            return jsonify(result)

        elif request.method == 'GET':
            id = request.args.get('id')
            vegetatif_service.logging.write("info", f"GET id={id}")

            data = vegetatif_service.get_vegetatif(id)
            return jsonify(data)

    except Exception as e:
        vegetatif_service.logging.write("error", f"Route error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
