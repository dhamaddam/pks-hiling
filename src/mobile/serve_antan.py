import os
import pymysql
from datetime import datetime
from flask import Blueprint, request, jsonify

# 🔹 Blueprint (no prefix, clean routes)
analisa_tandan_module = Blueprint('analisa_tandan_module', __name__)

class serveAnalisaTandan:
    def __init__(self):
        self.UPLOAD_FOLDER = 'uploads'
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # ✅ Database connection configuration
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
    def get_analisa_mapping(self):
        return {
            "id": "id",
            "tanggal_panen": "tanggal_panen",
            "no_percobaan": "no_percobaan",
            "no_kartu": "no_kartu",
            "no_analisa": "no_analisa",
            "no_baris": "no_baris",
            "no_pokok": "no_pokok",
            "no_sampel": "no_sampel",
            "no_persilangan": "no_persilangan",
            "berat_tandan": "berat_tandan",
            "stalk": "stalk",
            "tipe_buah": "tipe_buah",
            "spikelet": "spikelet",
            "berat_contoh_buah": "berat_contoh_buah",
            "jumlah_buah": "jumlah_buah",
            "berat_buah_a": "berat_buah_a",
            "berat_buah_b": "berat_buah_b",
            "berat_mes_a": "berat_mes_a",
            "berat_mes_b": "berat_mes_b",
            "berat_biji": "berat_biji",
            "berat_inti": "berat_inti",
            "berat_cangkang": "berat_cangkang",
            "mesokarp": "mesokarp",
            "berat_mesokarp_segar": "berat_mesokarp_segar",
            "berat_mesokarp_kering": "berat_mesokarp_kering",
            "berat_mangkok": "berat_mangkok",
            "mangkok_mesocarp": "mangkok_mesocarp",
            "mangkok_mesocarp_kering": "mangkok_mesocarp_kering",
            "berat_kantong_kosong_a": "berat_kantong_kosong_a",
            "berat_kantong_kosong_b": "berat_kantong_kosong_b",
            "berat_kantong_mes_a": "berat_kantong_mes_a",
            "berat_kantong_mes_b": "berat_kantong_mes_b",
            "berat_kantong_meso_sox_a": "berat_kantong_meso_sox_a",
            "berat_kantong_meso_sox_b": "berat_kantong_meso_sox_b",
            "contoh_a": "contoh_a",
            "contoh_b": "contoh_b",
            "berat_serat_a": "berat_serat_a",
            "berat_serat_b": "berat_serat_b",
            "berat_minyak_a": "berat_minyak_a",
            "berat_minyak_b": "berat_minyak_b",
            "persen_serat_meso_a": "persen_serat_meso_a",
            "persen_serat_meso_b": "persen_serat_meso_b",
            "persen_minyak_mes_kering_a": "persen_minyak_mes_kering_a",
            "persen_minyak_mes_kering_b": "persen_minyak_mes_kering_b",
            "persen_minyak_mes_segar_a": "persen_minyak_mes_segar_a",
            "persen_minyak_mes_segar_b": "persen_minyak_mes_segar_b",
            "kadar_air": "kadar_air",
            "persen_tandan": "persen_tandan",
            "persen_mesocarp": "persen_mesocarp",
            "persen_cangkang": "persen_cangkang",
            "persen_inti_buah": "persen_inti_buah",
            "persen_minyak_mes_kering": "persen_minyak_mes_kering",
            "persen_minyak_mes_segar": "persen_minyak_mes_segar",
            "persen_minyak_tandan": "persen_minyak_tandan",
            "persen_rendemen": "persen_rendemen",
            "persen_inti_tandan": "persen_inti_tandan",
            "selisih": "selisih",
            "palm_id": "palm_id",
            "created_at": "created_at"
        }

    # 🔁 JSON → DB
    def map_to_db(self, payload):
        mapping = self.get_analisa_mapping()
        result = {}
        for key, val in payload.items():
            if key in mapping:
                result[mapping[key]] = val
        if 'created_at' not in result:
            result['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return result

    # 🔁 DB → JSON
    def map_to_mobile(self, db_row):
        mapping = self.get_analisa_mapping()
        reverse_map = {v: k for k, v in mapping.items()}
        return {reverse_map[k]: v for k, v in db_row.items() if k in reverse_map}

    # =====================
    # 💾 INSERT DATA
    # =====================
    def insert_analisa_tandan(self, payload):
        data = self.map_to_db(payload)
        placeholders = ", ".join(["%s"] * len(data))
        columns = ", ".join(data.keys())
        values = tuple(data.values())
        query = f"INSERT INTO analisa_tandan ({columns}) VALUES ({placeholders})"

        try:
            conn = pymysql.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                conn.commit()
            conn.close()
            return {"status": "success", "message": "Analisa Tandan data inserted successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # =====================
    # 📥 GET DATA
    # =====================
    def get_analisa_tandan(self, id=None):
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        try:
            if id:
                cursor.execute("SELECT * FROM analisa_tandan WHERE id=%s", (id,))
            else:
                cursor.execute("SELECT * FROM analisa_tandan ORDER BY created_at DESC")
            result = cursor.fetchall()
            conn.close()
            return [self.map_to_mobile(row) for row in result]
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ==========================================================
# 🔹 ROUTES
# ==========================================================

analisa_service = serveAnalisaTandan()

@analisa_tandan_module.route('/api/insert', methods=['POST', 'GET'])
def api_insert_analisa_tandan():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Content-Type must be application/json"
            }), 415

        payload = request.get_json()
        result = analisa_service.insert_analisa_tandan(payload)
        return jsonify(result)

    elif request.method == 'GET':
        id = request.args.get('id')
        data = analisa_service.get_analisa_tandan(id)
        return jsonify(data)
