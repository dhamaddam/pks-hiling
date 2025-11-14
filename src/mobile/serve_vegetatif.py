import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint name and URL prefix
vegetatif_module = Blueprint('vegetatif_module', __name__)

class serveVegetatif:
    def __init__(self):
        # Optional upload folder (if needed later)
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
    def get_vegetatif_mapping(self):
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
            "usia_tanam": "usia_tanam",
            "created_at": "created_at"
        }

    # 🔁 Convert JSON → DB format
    def map_to_db(self, payload):
        mapping = self.get_vegetatif_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        # Auto timestamp
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 Convert DB → JSON for mobile
    def map_to_mobile(self, db_row):
        mapping = self.get_vegetatif_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_vegetatif(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())

        query = f"INSERT INTO vegetatif ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Vegetatif data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_vegetatif(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM vegetatif WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM vegetatif")
            
            result = cursor.fetchall()
            conn.close()

            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 API ROUTES
# ==========================================================

vegetatif_service = serveVegetatif()

# POST: Insert | GET: Retrieve
@vegetatif_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_vegetatif():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

        payload = request.get_json()
        result = vegetatif_service.insert_vegetatif(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = vegetatif_service.get_vegetatif(id)
        return jsonify(data)
