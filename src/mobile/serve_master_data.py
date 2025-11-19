import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify
from src.helper.Logfile import LogFile

# 🔹 Blueprint without prefix
master_data_module = Blueprint('master_data_module', __name__)

class serveMasterData:
    def __init__(self):
        self.logging = LogFile("daemon")
        self.logging.write("info", "serveMasterData initialized")

        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # Database configuration
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
    def get_master_mapping(self):
        self.logging.write("info", "get_master_mapping called")
        return {
            "id": "id",
            "expt_num": "expt_num",
            "cr_plan": "cr_plan",
            "crossing": "crossing",
            "female": "female",
            "male": "male",
            "female_gp_f": "female_gp_f",
            "female_gp_m": "female_gp_m",
            "male_gp_f": "male_gp_f",
            "male_gp_m": "male_gp_m",
            "rep": "rep",
            "block": "block",
            "plot": "plot",
            "baris": "baris",
            "pohon": "pohon",
            "design": "design",
            "sph": "sph",
            "field": "field",
            "planting_year": "planting_year",
            "estate": "estate",
            "population": "population",
            "pos": "pos",
            "clone": "clone",
            "ortet": "ortet",
            "ha": "ha",
            "palm_id": "palm_id",
            "created_at": "created_at"
        }

    # =====================
    # JSON → DB
    # =====================
    def map_to_db(self, payload):
        self.logging.write("info", f"map_to_db called with payload: {payload}")

        mapping = self.get_master_mapping()
        result = {}

        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val

        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.logging.write("info", f"map_to_db result: {result}")
        return result

    # =====================
    # DB → MOBILE
    # =====================
    def map_to_mobile(self, db_row):
        self.logging.write("info", f"map_to_mobile called with row: {db_row}")

        mapping = self.get_master_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        result = {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

        self.logging.write("info", f"map_to_mobile result: {result}")
        return result

    # =====================
    # INSERT
    # =====================
    def insert_master_data(self, payload):
        self.logging.write("info", f"insert_master_data called with: {payload}")

        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO master_data ({columns}) VALUES ({placeholders})"

        self.logging.write("info", f"Executing SQL: {query}")
        self.logging.write("info", f"Values: {values}")

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()

            self.logging.write("info", "Insert master_data success")
            return {"status": "success", "message": "Master Data inserted successfully"}

        except Exception as e:
            self.logging.write("error", f"Insert error: {str(e)}")
            return {"status": "error", "message": str(e)}

    # =====================
    # GET
    # =====================
    def get_master_data(self, id=None):
        self.logging.write("info", f"get_master_data called, id={id}")

        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            if id:
                query = "SELECT * FROM master_data WHERE id=%s"
                self.logging.write("info", f"Executing SQL: {query} | id={id}")
                cursor.execute(query, (id,))
            else:
                query = "SELECT * FROM master_data ORDER BY created_at DESC"
                self.logging.write("info", f"Executing SQL: {query}")
                cursor.execute(query)

            result = cursor.fetchall()
            conn.close()

            mapped = [self.map_to_mobile(row) for row in result]
            self.logging.write("info", f"get_master_data result count: {len(mapped)}")

            return mapped

        except Exception as e:
            self.logging.write("error", f"Get error: {str(e)}")
            return {"status": "error", "message": str(e)}


# ==========================================================
# ROUTES
# ==========================================================

master_service = serveMasterData()

@master_data_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_master_data():
    try:
        master_service.logging.write("info", "api_insert_master_data hit")

        if request.method == 'POST':
            if not request.is_json:
                master_service.logging.write("error", "Invalid Content-Type")
                return jsonify({
                    "status": "error",
                    "message": "Content-Type must be application/json"
                }), 415

            payload = request.get_json()
            master_service.logging.write("info", f"POST payload: {payload}")

            result = master_service.insert_master_data(payload)
            return jsonify(result)

        elif request.method == 'GET':
            id = request.args.get('id')
            master_service.logging.write("info", f"GET id={id}")

            data = master_service.get_master_data(id)
            return jsonify(data)

    except Exception as e:
        master_service.logging.write("error", f"Route error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
