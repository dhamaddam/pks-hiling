"""
Improvements:
- Remove common academic/professional titles (prefix & suffix)
- Tokenize / normalize names, build token frequency to find candidate marga
- Use blocking by domisili and candidate-marga to reduce comparisons
- Infer relations with safer rules, produce network (GEXF) + CSV
"""

import re
from collections import Counter, defaultdict
import pandas as pd
import networkx as nx
from Levenshtein import ratio  # pip install python-Levenshtein

# ========== CONFIG ==========
file_path = "data_karyawan.xlsx"   # <-- ganti sesuai file
output_gexf = "network_karyawan_improved.gexf"
pairs_csv = "pairs_deteksi_keluarga_improved.csv"
token_freq_csv = "token_frequency.csv"

# threshold: minimal frekuensi token untuk dianggap kandidat marga
MIN_TOKEN_FREQ = 3   # ubah ke 2 jika dataset kecil

# daftar gelar / titel umum (prefix & suffix) - tambahkan sesuai kebutuhan
TITLES = {
    # prefixes
    "dr", "drs", "drg", "drh", "prof", "ir", "h", "hj", "mr", "mrs", "ms", "ny", "ir.", "prof.",
    # suffixes (akademik)
    "s", "s.t", "st", "s.t.", "s.pd", "spd", "s.pd.", "s.si", "ssi", "s.kom", "skom",
    "m.sc", "msc", "m.si", "msi", "phd", "ph.d", "m.keu", "m", "mh", "mpd", "amd"
}
# normalisasi: hilangkan titik dan lower
TITLES = set(t.replace(".", "").lower() for t in TITLES)

# stopwords yang sering muncul tapi bukan marga
STOPWORDS = {"bin", "binti", "putra", "putri", "putro", "putri", "ibn", "bte", "al"}  # dll.

# ============================

def normalize_text(s):
    if pd.isna(s):
        return ""
    s = str(s)
    # buang kurung & isinya
    s = re.sub(r'\(.*?\)', ' ', s)
    # ganti tanda baca jadi spasi
    s = re.sub(r'[^\w\s]', ' ', s, flags=re.UNICODE)
    s = s.lower()
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def tokenize_and_strip_titles(name):
    """Return list of cleaned tokens (lowercased, punctuation removed), with titles removed."""
    norm = normalize_text(name)
    if not norm:
        return []
    toks = norm.split()
    cleaned = []
    for t in toks:
        t_clean = t.replace('.', '').replace(',', '')
        if t_clean in TITLES:
            continue
        cleaned.append(t_clean)
    return cleaned

# ====== read file and basic checks ======
df = pd.read_excel(file_path)
df = df.reset_index(drop=True)

required = ["Nama", "Domisili", "Tanggal Lahir"]
for c in required:
    if c not in df.columns:
        raise ValueError(f"Kolom '{c}' tidak ditemukan. Periksa nama kolom di file Excel.")

# hitung usia (fallback None bila date invalid)
def calc_age(d):
    try:
        return pd.Timestamp.now().year - pd.to_datetime(d).year
    except:
        return None

df["Usia"] = df["Tanggal Lahir"].apply(calc_age)

# tokenize names
df["name_tokens"] = df["Nama"].apply(tokenize_and_strip_titles)

# build token frequency (exclude stopwords & short tokens)
all_tokens = []
for toks in df["name_tokens"]:
    for t in toks:
        if t in STOPWORDS:
            continue
        if len(t) < 3:      # abaikan token sangat pendek
            continue
        all_tokens.append(t)

token_freq = Counter(all_tokens)
# simpan token frequency agar HR bisa review
pd.DataFrame(token_freq.most_common(), columns=["token", "freq"]).to_csv(token_freq_csv, index=False)

# candidate tokens for "marga" = tokens with freq >= MIN_TOKEN_FREQ
candidate_tokens = set(t for t, f in token_freq.items() if f >= MIN_TOKEN_FREQ)

# heuristic: choose family token for each record
def choose_family_token(tokens):
    if not tokens:
        return None
    # jika ada 'bin'/'binti' ambil token setelahnya
    for i, t in enumerate(tokens):
        if t in ("bin", "binti", "ibn", "bte"):
            if i + 1 < len(tokens):
                return tokens[i+1]
    # prefer last token if it's in candidate_tokens
    if tokens[-1] in candidate_tokens and tokens[-1] not in STOPWORDS:
        return tokens[-1]
    # else take any token that is candidate and longest (prefer longer tokens)
    candidates = [t for t in tokens if t in candidate_tokens]
    if candidates:
        # pick most frequent among candidates
        candidates.sort(key=lambda x: token_freq[x], reverse=True)
        return candidates[0]
    # fallback: last token if reasonable
    if len(tokens[-1]) >= 3 and tokens[-1] not in STOPWORDS:
        return tokens[-1]
    # else first useful token
    for t in tokens:
        if len(t) >= 3 and t not in STOPWORDS:
            return t
    return None

df["family_token"] = df["name_tokens"].apply(choose_family_token)
df["dom_norm"] = df["Domisili"].apply(lambda x: normalize_text(x) or "unknown")

# ====== Build inverted indices for blocking ======
token_index = defaultdict(list)   # family_token -> list of indices
dom_index = defaultdict(list)     # dom_norm -> list of indices

for idx, row in df.iterrows():
    if pd.notna(row["family_token"]):
        token_index[row["family_token"]].append(idx)
    dom_index[row["dom_norm"]].append(idx)

# For safety: also build index by any name token to catch cases where family_token None
name_token_index = defaultdict(list)
for idx, toks in enumerate(df["name_tokens"]):
    for t in toks:
        name_token_index[t].append(idx)

# ====== Generate candidate pairs using blocking (avoid full O(n^2)) ======
candidate_pairs = set()
n = len(df)

for i in range(n):
    neighbors = set()
    ft = df.loc[i, "family_token"]
    if ft:
        neighbors.update(token_index.get(ft, []))
    # domain (domisili) neighbors
    dom = df.loc[i, "dom_norm"]
    neighbors.update(dom_index.get(dom, []))
    # also neighbors by any shared token
    for t in df.loc[i, "name_tokens"]:
        neighbors.update(name_token_index.get(t, []))

    # remove self
    neighbors.discard(i)
    for j in neighbors:
        a, b = min(i, j), max(i, j)
        candidate_pairs.add((a, b))

print(f"Total candidate pairs after blocking: {len(candidate_pairs)} (vs full {(n*(n-1))//2})")

# ====== Infer relation for candidate pairs ======
pairs = []
for i, j in candidate_pairs:
    r1 = df.loc[i]
    r2 = df.loc[j]

    # quick heuristics:
    dom_same = r1["dom_norm"] == r2["dom_norm"]
    ft_same = (pd.notna(r1["family_token"]) and pd.notna(r2["family_token"]) and r1["family_token"] == r2["family_token"])
    usia1, usia2 = r1["Usia"], r2["Usia"]
    usia_diff = None
    if usia1 is not None and usia2 is not None:
        usia_diff = abs(usia1 - usia2)

    name_sim = ratio(str(r1["Nama"]).lower(), str(r2["Nama"]).lower())

    # scoring / rules
    relation = None
    score = 0.0
    reasons = []

    if ft_same:
        score += 0.6
        reasons.append("family_token sama")
    if dom_same:
        score += 0.25
        reasons.append("domisili sama")
    if name_sim > 0.75:
        score += 0.15
        reasons.append(f"nama mirip ({name_sim:.2f})")

    # age-based inference
    if usia_diff is not None:
        if usia_diff <= 6 and ft_same:
            relation = "Saudara Kandung"
            score += 0.3
        elif 18 <= usia_diff <= 45 and ft_same:
            # tentukan arah: orang tua adalah yang lebih tua
            if r1["Usia"] > r2["Usia"]:
                relation = "Orang Tua -> Anak"
            else:
                relation = "Orang Tua <- Anak"
            score += 0.4
        elif usia_diff < 10 and dom_same and name_sim < 0.9:
            # bisa pasangan / suami-istri atau saudara dekat; butuh gender
            # jika ada kolom 'Gender' gunakan itu (opsional)
            if "Gender" in df.columns:
                g1 = str(r1["Gender"]).strip().lower()
                g2 = str(r2["Gender"]).strip().lower()
                if g1 and g2 and g1 != g2:
                    relation = "Suami/Istri (kemungkinan)"
                    score += 0.35
            else:
                relation = "Kemungkinan Suami/Istri atau Saudara Dekat"
                score += 0.15

    # fallback: jika score besar dan no age-based label, give generic label
    if relation is None:
        if score >= 0.7:
            relation = "Kemungkinan Keluarga (kuat)"
        elif score >= 0.45:
            relation = "Kemungkinan Keluarga (sedang)"
        elif score >= 0.25:
            relation = "Kemungkinan Keluarga (lemah)"
        else:
            relation = None

    if relation:
        pairs.append({
            "idx1": i,
            "Nama 1": r1["Nama"],
            "idx2": j,
            "Nama 2": r2["Nama"],
            "family_token_1": r1["family_token"],
            "family_token_2": r2["family_token"],
            "dom_same": dom_same,
            "usia_diff": usia_diff,
            "name_sim": round(name_sim, 3),
            "score": round(score, 3),
            "relation": relation,
            "reasons": "; ".join(reasons)
        })

# simpan hasil pairs ke CSV
pd.DataFrame(pairs).sort_values(by="score", ascending=False).to_csv(pairs_csv, index=False)
print(f"✅ Pair results saved to {pairs_csv} (total {len(pairs)} pasangan terdeteksi)")

# ====== Create graph and export to GEXF for Gephi ======
G = nx.Graph()
for idx, row in df.iterrows():
    G.add_node(idx,
               label=row["Nama"],
               domisili=row["Domisili"],
               usia=row["Usia"],
               family_token=row["family_token"])

for p in pairs:
    G.add_edge(p["idx1"], p["idx2"],
               relation=p["relation"],
               score=p["score"],
               reasons=p["reasons"])

nx.write_gexf(G, output_gexf)
print(f"✅ GEXF file ready: {output_gexf}")
print("Buka di Gephi: File -> Open -> pilih file GEXF. Kamu bisa pakai 'relation' atau 'score' sebagai edge attribute untuk style/filter.")
