import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint WITHOUT prefix
sexratio_module = Blueprint('sexratio_module', __name__)

class serveSexRatio:
    def __init__(self):
        # Optional upload directory
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Database configuration
        self.db_config = {
            'host': '43.218.37.170',
            'user': 'iopri',
            'password': '^c56unJ^#X',
            'database': '1011pemulliandb',
            'cursorclass': pymysql.cursors.DictCursor
        }

    # =====================
    # 🔹 FIELD MAPPING
    # =====================
    def get_sexratio_mapping(self):
        return {
            "id": "id",
            "tahun": "tahun",
            "bulan": "bulan",
            "expt_num": "expt_num",
            "crossing": "crossing",
            "female": "female",
            "male": "male",
            "baris": "baris",
            "pohon": "pohon",
            "jantan": "jantan",
            "betina": "betina",
            "banci": "banci",
            "dompet": "dompet",
            "pelepah": "pelepah",
            "sex_ratio": "sex_ratio",
            "palm_id": "palm_id",
            "created_at": "created_at"
        }

    # 🔁 Convert JSON → DB format
    def map_to_db(self, payload):
        mapping = self.get_sexratio_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        # Add timestamp automatically
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 Convert DB → JSON for response
    def map_to_mobile(self, db_row):
        mapping = self.get_sexratio_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_sexratio(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO sex_ratio ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Sex Ratio data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_sexratio(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM sex_ratio WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM sex_ratio ORDER BY created_at DESC")
            result = cursor.fetchall()
            conn.close()
            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 API ROUTES
# ==========================================================

sexratio_service = serveSexRatio()

@sexratio_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_sexratio():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        payload = request.get_json()
        result = sexratio_service.insert_sexratio(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = sexratio_service.get_sexratio(id)
        return jsonify(data)
