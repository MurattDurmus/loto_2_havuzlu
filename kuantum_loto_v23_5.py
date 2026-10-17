# =========================================================================
# QUANT LOTO V23.5 (V25 TAM KOZMİK FRAKTAL MİMARİSİ) — OPTİMİZE SÜRÜM
# 3 KATMANLI KOZMİK TARAMA: 40'LIK HAVUZ + TOHUM + 10'LU KOLON MATRİS TESTİ
# =========================================================================
import streamlit as st
import random
import time
import json
import pandas as pd
import numpy as np
import os
import re
from collections import Counter
import datetime
from scipy.spatial.distance import euclidean
import networkx as nx
from itertools import combinations
import matplotlib.pyplot as plt

st.set_page_config(page_title="Quant Loto V23.5 — 3 Katmanlı Kozmik Motor", page_icon="🎯", layout="wide")

st.markdown('''
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 1.05rem; font-weight: bold;}
    .evren-baslik {
        background: linear-gradient(90deg, #0d1b2a 0%, #1b263b 50%, #0d1b2a 100%);
        padding: 12px 18px; border-radius: 10px; border: 1px solid #415a77; margin-bottom: 12px;
    }
    .bant-kart {padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 6px solid; font-weight: bold;}
    .bant-ust {background-color: #2b1114; border-color: #FF1744; color: #FF8A80;}
    .bant-orta {background-color: #122919; border-color: #00E676; color: #B9F6CA;}
    .bant-alt {background-color: #111d2b; border-color: #00B0FF; color: #80D8FF;}
    .gianella-kutu {
        background: linear-gradient(135deg, #111927 0%, #1a2333 100%);
        border: 1px solid #2e3c56; border-left: 6px solid #FFD600;
        padding: 14px 18px; border-radius: 10px; margin-bottom: 14px;
    }
    .tohum-kutu {background-color: #161b22; border: 1px solid #30363d; border-left: 6px solid #00E5FF; padding: 12px 18px; border-radius: 8px; margin-bottom: 14px;}
    .uyari-kutu {background-color: #3e2723; border-left: 6px solid #FF9100; padding: 12px 16px; border-radius: 8px; margin-bottom: 12px;}
    .kolon-satir {
        display: flex; align-items: center; background-color: #181c24; 
        padding: 8px 15px; border-radius: 8px; margin-bottom: 6px; border: 1px solid #2b3548;
        flex-wrap: wrap;
    }
    .kolon-baslik {width: 340px; font-weight: bold; color: #cbd5e1; font-size: 13px;}
    .top-standart {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #FFA000; color: white; 
        text-align: center; font-weight: bold; font-size: 15px; margin-right: 6px;
    }
    .top-karanlik {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #FF1744; color: white; 
        text-align: center; font-weight: bold; font-size: 15px; margin-right: 6px;
        box-shadow: 0 0 8px #FF1744;
    }
    .top-banko {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #9C27B0; color: white; 
        text-align: center; font-weight: bold; font-size: 15px; margin-right: 6px;
        box-shadow: 0 0 12px #9C27B0; border: 2px solid #E1BEE7;
    }
    .top-gold {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #FFD600; color: black; 
        text-align: center; font-weight: bold; font-size: 15px; margin-right: 6px;
        box-shadow: 0 0 12px #FFD600; border: 1px solid #FFF59D;
    }
    .top-joker {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #E65100; color: white; 
        text-align: center; font-weight: bold; font-size: 15px; margin-left: 14px; margin-right: 6px;
        box-shadow: 0 0 10px #E65100; border: 2px dashed #FFB74D;
    }
    .top-super {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #00B0FF; color: white; 
        text-align: center; font-weight: bold; font-size: 15px; margin-left: 8px; margin-right: 6px;
        box-shadow: 0 0 10px #00B0FF; border: 2px solid #80D8FF;
    }
    .top-arti {
        display: inline-block; width: 34px; height: 34px; line-height: 34px; 
        border-radius: 50%; background-color: #00E676; color: black; 
        text-align: center; font-weight: 900; font-size: 13px; margin-left: 14px; margin-right: 6px;
        box-shadow: 0 0 12px #00E676; border: 2px solid #B9F6CA;
    }
    </style>
''', unsafe_allow_html=True)

ASAL_TUM = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89}
FAVORI_KASA_JSON = "favori_kuponlar_kasasi.json"
FAVORI_KASA_TXT = "favori_kuponlar_kasasi.txt"


def onluk_grup_bul(n): return (n - 1) // 10


def dijital_kok(n): return 1 + (n - 1) % 9 if n > 0 else 0


OYUN_EVRENLERI = {
    "🎯 On Numara": {
        "kod": "onnumara", "max_sayi": 80, "kolon_boyutu": 10, "arsiv_top_sayisi": 22,
        "banko_adedi": 2, "hedge_havuz_boyutu": 8,
        "dosyalar": ["OnNumara.csv", "OnNumara_Temiz.csv"],
        "cekilis_gunleri": [0, 4], "grid_w": 10,
        "bant_alt": 850, "bant_ust": 930,
        "kolon_bant_alt": (300, 380), "kolon_bant_orta": (381, 430), "kolon_bant_ust": (431, 510),
        "altin_kesi": (320, 490),
        "alt_yari_sart": {"Orta": [3, 4, 5, 6, 7], "Alt": [5, 6, 7, 8], "Ust": [2, 3, 4, 5]},
        "tek_aralik": [3, 4, 5, 6, 7], "asal_aralik": [1, 2, 3, 4], "dekad_aralik": [5, 6, 7, 8],
        "mod10_max": 3, "ardisik_max": 2, "yayilim_aralik": (50, 76), "std_aralik": (17.0, 27.5),
        "max_bosluk": 25,
        "sinirlar": {
            "mod5": {"h2_oran": (0.60, 0.85), "fraktal": (1.35, 5.20), "sapma": 42,
                     "mat1": (1.20, 3.40), "mat2": (1.80, 36.00), "spin": [-6, -4, -2, 0, 2, 4, 6],
                     "flux": [2, 3, 4, 5, 6, 7, 8], "walk": (18.0, 56.0), "tort": (2.00, 7.20),
                     "cle": (1.0, 27.0), "dens": (0.110, 0.250), "lqg": (6.00, 17.50),
                     "eig": (78.00, 110.00), "gap": (18.00, 36.00), "lambda_u": (0.92, 1.25), "sk": (-2.40, 2.80)}
        }
    },
    "🎱 Şans Topu": {
        "kod": "sanstopu", "max_sayi": 34, "kolon_boyutu": 5, "arsiv_top_sayisi": 5,
        "banko_adedi": 1, "hedge_havuz_boyutu": 5,
        "dosyalar": ["Sans_topu_sonuclar.csv", "Sans_Topu_Temiz.csv"],
        "cekilis_gunleri": [2, 6], "grid_w": 7,
        "bant_alt": 78, "bant_ust": 96,
        "kolon_bant_alt": (40, 78), "kolon_bant_orta": (79, 95), "kolon_bant_ust": (96, 135),
        "altin_kesi": (62, 113),
        "alt_yari_sart": {"Orta": [1, 2, 3, 4], "Alt": [3, 4, 5], "Ust": [0, 1, 2]},
        "tek_aralik": [1, 2, 3, 4], "asal_aralik": [1, 2, 3], "dekad_aralik": [3, 4],
        "mod10_max": 2, "ardisik_max": 1, "yayilim_aralik": (14, 32), "std_aralik": (5.2, 11.8),
        "max_bosluk": 18,
        "sinirlar": {
            "mod5": {"h2_oran": (0.42, 0.78), "fraktal": (1.10, 9.00), "sapma": 22,
                     "mat1": (1.15, 6.20), "mat2": (1.30, 14.00), "spin": [-5, -3, -1, 1, 3, 5],
                     "flux": [1, 2, 3, 4], "walk": (4.5, 19.0), "tort": (1.10, 5.80),
                     "cle": (0.2, 11.0), "dens": (0.100, 0.600), "lqg": (3.20, 8.80),
                     "eig": (20.00, 42.00), "gap": (5.00, 21.00), "lambda_u": (0.82, 1.20), "sk": (-1.80, 2.00)}
        }
    },
    "🌌 Çılgın Sayısal Loto": {
        "kod": "sayisal", "max_sayi": 90, "kolon_boyutu": 6, "arsiv_top_sayisi": 6,
        "banko_adedi": 1, "hedge_havuz_boyutu": 7,
        "dosyalar": ["Cilgin_Sayisal.csv", "Cilgin_Sayisal_Temiz.csv"],
        "cekilis_gunleri": [0, 2, 5], "grid_w": 10,
        "bant_alt": 246, "bant_ust": 300,
        "kolon_bant_alt": (130, 246), "kolon_bant_orta": (247, 299), "kolon_bant_ust": (300, 410),
        "altin_kesi": (212, 338),
        "alt_yari_sart": {"Orta": [2, 3, 4], "Alt": [3, 4, 5, 6], "Ust": [0, 1, 2, 3]},
        "tek_aralik": [2, 3, 4], "asal_aralik": [1, 2, 3], "dekad_aralik": [4, 5, 6],
        "mod10_max": 2, "ardisik_max": 1, "yayilim_aralik": (45, 85), "std_aralik": (15.5, 30.5),
        "max_bosluk": 40,
        "sinirlar": {
            "mod5": {"h2_oran": (0.58, 0.86), "fraktal": (1.1, 5.0), "sapma": 45,
                     "mat1": (1.10, 4.00), "mat2": (1.25, 24.00), "spin": [-4, -2, 0, 2, 4],
                     "flux": [1, 2, 3, 4, 5], "walk": (11.0, 42.0), "tort": (1.30, 6.20),
                     "cle": (1.0, 29.0), "dens": (0.050, 0.240), "lqg": (4.00, 10.00),
                     "eig": (65.00, 110.00), "gap": (8.00, 40.00), "lambda_u": (0.82, 1.20), "sk": (-2.00, 2.50)}
        }
    },
    "🔥 Süper Loto": {
        "kod": "super", "max_sayi": 60, "kolon_boyutu": 6, "arsiv_top_sayisi": 6,
        "banko_adedi": 1, "hedge_havuz_boyutu": 7,
        "dosyalar": ["Super_Loto_2020.csv", "Super_Loto_Temiz.csv"],
        "cekilis_gunleri": [1, 3, 6], "grid_w": 10,
        "bant_alt": 166, "bant_ust": 201,
        "kolon_bant_alt": (106, 166), "kolon_bant_orta": (167, 200), "kolon_bant_ust": (201, 260),
        "altin_kesi": (145, 221),
        "alt_yari_sart": {"Orta": [2, 3, 4], "Alt": [3, 4, 5, 6], "Ust": [0, 1, 2, 3]},
        "tek_aralik": [2, 3, 4], "asal_aralik": [1, 2, 3], "dekad_aralik": [3, 4, 5, 6],
        "mod10_max": 2, "ardisik_max": 1, "yayilim_aralik": (32, 56), "std_aralik": (10.5, 20.5),
        "max_bosluk": 24,
        "sinirlar": {
            "mod5": {"h2_oran": (0.58, 0.86), "fraktal": (1.35, 5.05), "sapma": 26,
                     "mat1": (1.10, 3.80), "mat2": (1.25, 21.00), "spin": [-4, -2, 0, 2, 4],
                     "flux": [1, 2, 3, 4, 5], "walk": (10.0, 28.0), "tort": (1.20, 6.00),
                     "cle": (0.5, 20.0), "dens": (0.080, 0.320), "lqg": (4.00, 8.50),
                     "eig": (45.00, 74.00), "gap": (8.00, 27.00), "lambda_u": (0.82, 1.20), "sk": (-1.60, 2.00)}
        }
    }
}

EVREN_ADIMLARI = {
    "1_Kronolojik": list(range(1, 15)),
    "2_Fibonacci": [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233],
    "3_Kadim_19": [19 * i for i in range(1, 13)],
    "4_Asal_Indis": [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43],
    "5_Lucas_Dizisi": [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199],
    "6_Ucgensel": [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91],
    "7_Phi_Harmonik": [1, 2, 4, 6, 10, 16, 26, 42, 68, 110, 178],
    "8_Karekok_TamKare": [1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144],
    "9_Pell_Dizisi": [1, 2, 5, 12, 29, 70, 169, 408],
    "10_Padovan_Spiral": [1, 2, 3, 4, 5, 7, 9, 12, 16, 21, 28, 37, 49, 65],
    "11_Perrin_Dongu": [2, 3, 5, 7, 10, 12, 17, 22, 29, 39, 51, 68, 90],
    "12_Yildiz_Poligon": [1, 13, 37, 73, 121, 181, 253, 337]
}

rng_master = np.random.default_rng(42)
MASTER_CHATTERJEE_J = rng_master.normal(loc=0, scale=1.0, size=(90, 90))
MASTER_CHATTERJEE_J = (MASTER_CHATTERJEE_J + MASTER_CHATTERJEE_J.T) / 2
np.fill_diagonal(MASTER_CHATTERJEE_J, 0)


# -------------------------------------------------------------------------
# SENTETİK VERİ ÜRETİCİ (CSV DOSYASI YOKSA DEVREYE GİRER)
# -------------------------------------------------------------------------
def sentetik_arsiv_olustur(oyun_adi, cekilis_sayisi=250):
    cfg = OYUN_EVRENLERI[oyun_adi]
    kod = cfg["kod"]
    max_n = cfg["max_sayi"]
    k_arsiv = cfg["arsiv_top_sayisi"]
    dosya = cfg["dosyalar"][0]
    t_cols = [f"T{i}" for i in range(1, k_arsiv + 1)]
    bugun = datetime.date.today()
    rng = np.random.default_rng(int(time.time()))

    rows = []
    for i in range(cekilis_sayisi):
        trh = (bugun - datetime.timedelta(days=(cekilis_sayisi - i) * 3)).strftime("%d.%m.%Y")
        hft = (i % 52) + 1
        toplar = sorted(rng.choice(range(1, max_n + 1), size=k_arsiv, replace=False).tolist())
        if kod == "sayisal":
            kalan = [x for x in range(1, 91) if x not in toplar]
            joker = int(rng.choice(kalan))
            super_top = int(rng.integers(1, 91))
            rows.append([trh, hft] + toplar + [joker, super_top])
        elif kod == "sanstopu":
            arti = int(rng.integers(1, 15))
            rows.append([trh, hft] + toplar + [arti])
        elif kod == "onnumara":
            rows.append([bugun.year, hft] + toplar)
        else:
            rows.append([trh, hft] + toplar)

    if kod == "sayisal":
        cols = ['Tarih', 'Hft'] + t_cols + ['Joker', 'Super']
    elif kod == "sanstopu":
        cols = ['Tarih', 'Hft'] + t_cols + ['Arti']
    elif kod == "onnumara":
        cols = ['Yil', 'Hft'] + t_cols
    else:
        cols = ['Tarih', 'Hft'] + t_cols

    df_syn = pd.DataFrame(rows, columns=cols)
    df_syn.to_csv(dosya, index=False)
    st.cache_data.clear()


# -------------------------------------------------------------------------
# KATMAN 3: KOLONLAR İÇİN 12 EVREN KOZMİK MATRİS TESTİ
# -------------------------------------------------------------------------
def kolonlari_12_evrende_kozmik_puanla(aday_listesi, aktif_cfg, aktif_paket):
    if not aday_listesi:
        return aday_listesi

    draws = aktif_paket["draws"]
    max_n = aktif_cfg["max_sayi"]
    k_boyut = aktif_cfg["kolon_boyutu"]
    k_arsiv = aktif_cfg["arsiv_top_sayisi"]
    toplam_cekilis = len(draws)
    max_idx = toplam_cekilis - 1

    n_aday = len(aday_listesi)
    cols_mat = np.zeros((n_aday, max_n + 1), dtype=np.float32)
    for i, item in enumerate(aday_listesi):
        cols_mat[i, item["kolon"]] = 1.0

    draw_matrix = np.zeros((toplam_cekilis, max_n + 1), dtype=np.float32)
    for idx, d in enumerate(draws):
        for num in d:
            if 1 <= num <= max_n:
                draw_matrix[idx, num] = 1.0

    beklenen_isabet = k_boyut * (k_arsiv / max_n)
    std_isabet = np.sqrt(k_boyut * (k_arsiv / max_n) * (1.0 - (k_arsiv / max_n)))
    tukenmislik_esigi = 6 if k_boyut == 10 else 4

    kozmik_kolon_skoru = np.zeros(n_aday, dtype=np.float32)

    for adimlar in EVREN_ADIMLARI.values():
        g_idx = [max_idx - l for l in adimlar if max_idx - l >= 0]
        if g_idx:
            ev_hits = cols_mat @ draw_matrix[g_idx].T
            beklenen_ev = len(g_idx) * beklenen_isabet
            z_acik = (beklenen_ev - ev_hits.sum(axis=1)) / max(0.5, np.sqrt(len(g_idx)) * std_isabet)
            tukenmislik_cezasi = (ev_hits >= tukenmislik_esigi).sum(axis=1) * 3.0
            kozmik_kolon_skoru += (z_acik * 1.35) - tukenmislik_cezasi

    son_25_idx = list(range(max(0, toplam_cekilis - 25), toplam_cekilis))
    if son_25_idx:
        son_25_hits = cols_mat @ draw_matrix[son_25_idx].T
        yakin_tukenmislik = (son_25_hits >= tukenmislik_esigi).sum(axis=1) * 15.0
        kozmik_kolon_skoru -= yakin_tukenmislik

    min_s, max_s = kozmik_kolon_skoru.min(), kozmik_kolon_skoru.max()
    aralik = max(1.0, max_s - min_s)

    for i, item in enumerate(aday_listesi):
        norm_c_skor = ((kozmik_kolon_skoru[i] - min_s) / aralik) * 100.0
        item["kozmik_kolon_puan"] = round(float(norm_c_skor), 1)
        item["q_puan"] = round(item.get("q_puan", 50.0) * 0.55 + norm_c_skor * 0.45, 1)

    return aday_listesi


def optimal_dagilim_sec(aday_havuzu, hedef_sayi, onceden_secilenler=None):
    if len(aday_havuzu) <= hedef_sayi:
        return aday_havuzu
    havuz_kopya = sorted(list(aday_havuzu), key=lambda x: x.get("q_puan", 50.0), reverse=True)
    secilenler = []
    referans_havuz = list(onceden_secilenler) if onceden_secilenler else []
    sayi_ullanim_sayaci = Counter()

    for r in referans_havuz:
        sayi_ullanim_sayaci.update(r["kolon"])

    if not referans_havuz:
        elit_dilim = min(15, len(havuz_kopya))
        ilk = havuz_kopya.pop(random.randint(0, elit_dilim - 1))
        secilenler.append(ilk)
        referans_havuz.append(ilk)
        sayi_ullanim_sayaci.update(ilk["kolon"])

    while len(secilenler) < hedef_sayi and havuz_kopya:
        en_iyi_aday, en_dusuk_maliyet = None, 999999.0
        taranacak = havuz_kopya if len(havuz_kopya) <= 600 else (
                    havuz_kopya[:250] + random.sample(havuz_kopya[250:], 350))
        for aday in taranacak:
            k_set = set(aday["kolon"])
            max_ortak = max(len(k_set & set(sec["kolon"])) for sec in referans_havuz)
            ort_ortak = sum(len(k_set & set(sec["kolon"])) for sec in referans_havuz) / len(referans_havuz)
            frekans_yuku = sum(sayi_ullanim_sayaci[n] for n in aday["kolon"]) / len(aday["kolon"])
            altin_bonus = -0.45 if aday.get("is_gold") else 0.0
            kalite_bonusu = (aday.get("q_puan", 50.0) / 100.0) * 4.5

            maliyet = (max_ortak * 10.0) + (ort_ortak * 3.5) + (frekans_yuku * 1.8) + altin_bonus - kalite_bonusu
            if maliyet < en_dusuk_maliyet:
                en_dusuk_maliyet, en_iyi_aday = maliyet, aday

        secilenler.append(en_iyi_aday)
        referans_havuz.append(en_iyi_aday)
        sayi_ullanim_sayaci.update(en_iyi_aday["kolon"])
        havuz_kopya.remove(en_iyi_aday)

    return secilenler


# -------------------------------------------------------------------------
# KASA YÖNETİCİSİ (.JSON & .TXT)
# -------------------------------------------------------------------------
def numpy_json_donusturucu(obj):
    """NumPy veri tiplerini (int64, float32, bool_, ndarray) JSON uyumlu standart Python tiplerine çevirir."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def kasayi_yukle():
    if os.path.exists(FAVORI_KASA_JSON):
        try:
            with open(FAVORI_KASA_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def kasayi_txt_olarak_senkronize_et(kasa_listesi):
    try:
        satirlar = ["====================================================================",
                    "       🎯 QUANT TERMİNALİ V25 - FAVORİ KUPON KASASI               ",
                    "====================================================================\n"]
        for kayit in kasa_listesi:
            satirlar.append(f"📅 Tarih: {kayit['tarih']} | 🎯 Oyun: {kayit['oyun']} | ⚙️ Paket: {kayit['mod']}")
            if kayit.get("banko"):
                satirlar.append(f"🔮 Çekirdek Banko: {kayit['banko']} | Elit Hedge: {kayit.get('hedge', [])}")
            for idx, item in enumerate(kayit["kolonlar"], 1):
                k = item["kolon"]
                eks = item.get("ekstra", {})
                etk = item.get("etiket", f"Kolon {idx:02d}")
                s_str = f"  {etk:28s} (Top:{sum(k):3d}): " + " - ".join(f"{n:02d}" for n in k)
                if "joker" in eks: s_str += f" | Joker: {eks['joker']:02d} | Süper: {eks['super']:02d}"
                if "arti" in eks: s_str += f" | +1 Topu: +{eks['arti']:02d}"
                satirlar.append(s_str)
            satirlar.append("-" * 68 + "\n")
        with open(FAVORI_KASA_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(satirlar))
    except Exception:
        pass

def kasaya_kupon_ekle(oyun_adi, mod_adi, kolon_listesi, banko_list, diger_karanliklar):
    kasa = kasayi_yukle()
    yeni_kayit = {
        "id": int(time.time() * 1000),
        "tarih": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
        "oyun": oyun_adi,
        "mod": mod_adi,
        "banko": [int(x) for x in banko_list],
        "hedge": [int(x) for x in diger_karanliklar],
        "kolonlar": kolon_listesi
    }
    kasa.insert(0, yeni_kayit)
    with open(FAVORI_KASA_JSON, "w", encoding="utf-8") as f:
        json.dump(kasa, f, ensure_ascii=False, indent=2, default=numpy_json_donusturucu)
    kasayi_txt_olarak_senkronize_et(kasa)

def kasadan_sil(kayit_id):
    kasa = [k for k in kasayi_yukle() if k.get("id") != kayit_id]
    with open(FAVORI_KASA_JSON, "w", encoding="utf-8") as f:
        json.dump(kasa, f, ensure_ascii=False, indent=2, default=numpy_json_donusturucu)
    kasayi_txt_olarak_senkronize_et(kasa)


# -------------------------------------------------------------------------
# VERİTABANI OKUYUCU
# -------------------------------------------------------------------------
@st.cache_data(ttl=60)
def evren_verisini_yukle(oyun_adi):
    cfg = OYUN_EVRENLERI[oyun_adi]
    kod = cfg["kod"]
    max_n = cfg["max_sayi"]
    k_arsiv = cfg["arsiv_top_sayisi"]
    dosya = next((f for f in cfg["dosyalar"] if os.path.exists(f)), None)
    if not dosya:
        return None

    try:
        t_cols = [f"T{i}" for i in range(1, k_arsiv + 1)]
        if kod == "sayisal":
            df = pd.read_csv(dosya) if dosya.endswith('.csv') else pd.read_excel(dosya, header=1)
            if 'Tarih' not in df.columns and dosya.endswith('.csv'):
                df = pd.read_csv(dosya, header=1)
            df = df.rename(
                columns={'Tarih': 'Tarih', 'T1': 'T1', 'T2': 'T2', 'T3': 'T3', 'T4': 'T4', 'T5': 'T5', 'T6': 'T6',
                         'Joker': 'Joker', 'Super': 'Super'})
            df = df.dropna(subset=['Tarih'])
            df = df[~df['Tarih'].astype(str).str.contains('Tarih', case=False, na=False)]
            for c in t_cols + ['Joker', 'Super']:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors='coerce')
                else:
                    df[c] = 0
            df = df.dropna(subset=t_cols)
            for c in t_cols + ['Joker', 'Super']:
                df[c] = df[c].fillna(0).astype(int)
            df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y', errors='coerce').fillna(
                pd.to_datetime(df['Tarih'], format='%Y-%m-%d', errors='coerce')
            ).fillna(
                pd.to_datetime(df['Tarih'], format='mixed', errors='coerce')
            )
            df = df.sort_values('Tarih_DT').reset_index(drop=True)

        elif kod == "super":
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                ilk_satir = f.readline()
                sep = '\t' if '\t' in ilk_satir else (';' if ';' in ilk_satir else ',')
            df = pd.read_csv(dosya, delimiter=sep)
            if len(df.columns) <= 1:
                df = pd.read_csv(dosya, delimiter=',')
            for c in t_cols:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=t_cols)
            for c in t_cols:
                df[c] = df[c].astype(int)
            if 'Tarih' in df.columns:
                df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='%d.%m.%Y', errors='coerce').fillna(
                    pd.to_datetime(df['Tarih'], format='%Y-%m-%d', errors='coerce')
                ).fillna(
                    pd.to_datetime(df['Tarih'], format='mixed', errors='coerce')
                )
                df = df.sort_values('Tarih_DT').reset_index(drop=True)
            else:
                df['Tarih_DT'] = pd.NaT
                df = df.iloc[::-1].reset_index(drop=True)

        elif kod == "onnumara":
            rows = []
            aktif_yil = datetime.datetime.now().year
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    sep = '\t' if '\t' in line else (';' if ';' in line else ',')
                    parts = line.strip().split(sep)
                    first_val = parts[0].strip() if parts else ""
                    if first_val.isdigit() and len(first_val) == 4 and (len(parts) == 1 or parts[1] == ''):
                        aktif_yil = int(first_val)
                        continue
                    if len(parts) >= 22:
                        if first_val in ['Hft', 'Yil'] or 'Tarih' in first_val:
                            continue
                        if len(parts) >= 24 and parts[0].isdigit() and len(parts[0]) == 4:
                            rows.append([int(parts[0]), parts[1]] + parts[2:24])
                        elif len(parts) >= 23:
                            rows.append([aktif_yil, parts[0]] + parts[1:23])
                        else:
                            rows.append([aktif_yil, '0'] + parts[:22])
            df = pd.DataFrame(rows, columns=['Yil', 'Hft'] + t_cols)
            df['Hft'] = pd.to_numeric(df['Hft'], errors='coerce').fillna(0).astype(int)
            for c in t_cols:
                df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=t_cols)
            for c in t_cols:
                df[c] = df[c].astype(int)
            df['Tarih_DT'] = pd.NaT
            if len(df) > 1 and df.iloc[0]['Hft'] > df.iloc[-1]['Hft']:
                df = df.iloc[::-1].reset_index(drop=True)

        elif kod == "sanstopu":
            df_raw = pd.read_csv(dosya, sep=None, engine='python', header=None)
            clean_rows = []
            for idx, row in df_raw.iterrows():
                val0 = str(row[0]).strip()
                if val0 in ['Tarih', 'nan', 'None'] or (
                        val0.isdigit() and len(val0) == 4 and (len(row) <= 2 or pd.isna(row[2]))):
                    continue
                if str(row[1]).strip() == 'Hft':
                    continue
                try:
                    nums = [int(float(row[i])) for i in range(2, 8)]
                    t1_5, arti = nums[:5], nums[5]
                    if all(1 <= x <= 34 for x in t1_5) and (1 <= arti <= 14) and len(set(t1_5)) == 5:
                        clean_rows.append(
                            [row[0], int(float(row[1])) if str(row[1]).replace('.0', '').isdigit() else 0] + sorted(
                                t1_5) + [arti])
                except Exception:
                    pass
            df = pd.DataFrame(clean_rows, columns=['Tarih', 'Hft'] + t_cols + ['Arti'])
            df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='mixed', errors='coerce')
            df = df.sort_values('Tarih_DT').reset_index(drop=True)

        if len(df) == 0:
            return None

        df['Toplam'] = df[t_cols].sum(axis=1)
        draws = df[t_cols].values.tolist()
        num_draws = len(draws)
        counts = Counter(num for draw in draws for num in draw if 1 <= num <= max_n)

        median_freq = np.median(list(counts.values())) if counts else 0
        spins = {i: 1 if counts.get(i, 0) > median_freq else -1 for i in range(1, max_n + 1)}
        mean_f = np.mean(list(counts.values())) if counts else 1
        std_f = np.std(list(counts.values())) if (counts and np.std(list(counts.values())) > 0) else 1
        gff_h = {k: (counts.get(k, 0) - mean_f) / std_f for k in range(1, max_n + 1)}

        pair_counts = Counter()
        for draw in draws:
            pair_counts.update(combinations(sorted(draw), 2))
        perc_thresh = int(np.percentile(list(pair_counts.values()), 94)) if pair_counts else 10

        appearances = {i: [] for i in range(1, max_n + 1)}
        for idx, draw in enumerate(draws):
            for num in draw:
                if 1 <= num <= max_n:
                    appearances[num].append(idx)
        all_gaps = [np.diff(app) for app in appearances.values() if len(app) > 1]
        all_gaps = [g for sublist in all_gaps for g in sublist]
        t_c_95 = np.percentile(all_gaps, 95) if all_gaps else 20
        current_sleep = {num: (num_draws - 1) - (app[-1] if app else 0) for num, app in appearances.items()}
        faz_bankolari = [k for k, v in current_sleep.items() if v >= t_c_95]

        h = np.zeros(max_n)
        for draw in draws:
            for num in draw:
                if 1 <= num <= max_n:
                    h[num - 1] += 1
        mean_h, std_h = np.mean(h), np.std(h)
        kpz_zirveler = set(np.where(h > mean_h + std_h)[0] + 1)
        kpz_vadiler = set(np.where(h < mean_h - std_h)[0] + 1)

        frek_serisi = pd.Series(0, index=np.arange(1, max_n + 1)).add(pd.Series(counts), fill_value=0)
        k_top = max(8, int(max_n * 0.22))
        zirveler = set(frek_serisi.nlargest(k_top).index)
        vadiler = set(frek_serisi.nsmallest(k_top).index)

        ekstra = {}
        if kod == "sayisal":
            ekstra["joker_freqs"] = dict(df['Joker'].value_counts())
            ekstra["super_freqs"] = dict(df['Super'].value_counts())
        elif kod == "sanstopu":
            arti_list = df['Arti'].tolist()
            a_last = {i: -1 for i in range(1, 15)}
            for idx, val in enumerate(arti_list):
                if 1 <= val <= 14:
                    a_last[val] = idx
            ekstra["arti_sleep"] = {i: (num_draws - 1 - a_last[i]) for i in range(1, 15)}

        return {
            "df": df, "dosya": dosya, "draws": draws, "counts": counts, "current_sleep": current_sleep,
            "spins": spins, "gff_h": gff_h, "pair_counts": pair_counts, "perc_thresh": perc_thresh,
            "faz_bankolari": faz_bankolari, "kpz_zirveler": kpz_zirveler, "kpz_vadiler": kpz_vadiler,
            "zirveler": zirveler, "vadiler": vadiler, "ekstra": ekstra, "t_c_95": t_c_95
        }
    except Exception as e:
        st.error(f"{oyun_adi} verisi yüklenirken hata: {e}")
        return None


@st.cache_data(ttl=60)
def mutlak_kuantum_alani_hesapla():
    evrensel_basinc = {i: 0.0 for i in range(1, 91)}
    katilim_sayisi = {i: 0 for i in range(1, 91)}
    yuklenen_evrenler = []
    for oyun_adi, cfg in OYUN_EVRENLERI.items():
        paket = evren_verisini_yukle(oyun_adi)
        if paket is not None:
            yuklenen_evrenler.append(oyun_adi)
            max_n, k_arsiv = cfg["max_sayi"], cfg["arsiv_top_sayisi"]
            beklenen_dongu = max_n / k_arsiv
            sleeps, gff = paket["current_sleep"], paket["gff_h"]
            for num in range(1, max_n + 1):
                norm_uyku = sleeps.get(num, 0) / beklenen_dongu
                evrensel_basinc[num] += (norm_uyku * 1.5) - gff.get(num, 0)
                katilim_sayisi[num] += 1
    for num in range(1, 91):
        if katilim_sayisi[num] > 0:
            evrensel_basinc[num] = round(evrensel_basinc[num] / katilim_sayisi[num], 3)
    return evrensel_basinc, yuklenen_evrenler


# -------------------------------------------------------------------------
# KATMAN 1: KOZMİK 40'LIK HAVUZ TARAYICISI (MONTE CARLO 12 EVREN)
# -------------------------------------------------------------------------
@st.cache_data(ttl=60)
def dinamik_gianella_havuz_analizi(oyun_adi, pencere=80, aday_havuz_sayisi=2000):
    paket = evren_verisini_yukle(oyun_adi)
    cfg = OYUN_EVRENLERI[oyun_adi]
    max_n, k_arsiv = cfg["max_sayi"], cfg["arsiv_top_sayisi"]
    yari_boyut = max_n // 2

    if paket is None or len(paket["draws"]) < 20:
        return {"havuz_a": list(range(1, yari_boyut + 1)), "havuz_b": list(range(yari_boyut + 1, max_n + 1)),
                "olasilik_a": 50.0, "olasilik_b": 50.0, "a_top_sayisi": 0, "b_top_sayisi": 0,
                "beklenen_top": 0, "pencere": pencere, "z_skoru": 0.0, "seri_baski": 0}

    draws = paket["draws"]
    toplam_cekilis = len(draws)
    max_idx = toplam_cekilis - 1
    gercek_pencere = min(pencere, toplam_cekilis)
    evrensel_basinc, _ = mutlak_kuantum_alani_hesapla()

    draw_matrix = np.zeros((toplam_cekilis, max_n + 1), dtype=np.float32)
    for idx, d in enumerate(draws):
        for num in d:
            if 1 <= num <= max_n:
                draw_matrix[idx, num] = 1.0

    bireysel_kozmik = np.zeros(max_n + 1, dtype=np.float32)
    for adimlar in EVREN_ADIMLARI.values():
        g_idx = [max_idx - l for l in adimlar if max_idx - l >= 0]
        if g_idx:
            bireysel_kozmik += (len(g_idx) * (k_arsiv / max_n) - draw_matrix[g_idx].sum(axis=0))
    for n in range(1, max_n + 1):
        bireysel_kozmik[n] += evrensel_basinc.get(n, 0) * 0.5

    dekad_sayisi = (max_n - 1) // 10 + 1
    dekad_tek = {d: [n for n in range(d * 10 + 1, min(max_n + 1, (d + 1) * 10 + 1)) if n % 2 != 0] for d in
                 range(dekad_sayisi)}
    dekad_cift = {d: [n for n in range(d * 10 + 1, min(max_n + 1, (d + 1) * 10 + 1)) if n % 2 == 0] for d in
                  range(dekad_sayisi)}

    rng = np.random.default_rng(int(toplam_cekilis * 100 + max_n + gercek_pencere))
    pools_matrix = np.zeros((aday_havuz_sayisi, max_n + 1), dtype=np.float32)

    for i in range(aday_havuz_sayisi):
        secilen_havuz = []
        for d in range(dekad_sayisi):
            t_list, c_list = dekad_tek[d], dekad_cift[d]
            hedef_d = (len(t_list) + len(c_list)) // 2
            if (d + i) % 2 == 0:
                k_t = min(len(t_list), (hedef_d + 1) // 2)
                k_c = min(len(c_list), hedef_d - k_t)
            else:
                k_c = min(len(c_list), (hedef_d + 1) // 2)
                k_t = min(len(t_list), hedef_d - k_c)

            if i < aday_havuz_sayisi // 3:
                sec_t = rng.choice(t_list, size=k_t, replace=False).tolist() if k_t > 0 else []
                sec_c = rng.choice(c_list, size=k_c, replace=False).tolist() if k_c > 0 else []
            else:
                g_std = 2.0 if i < (2 * aday_havuz_sayisi // 3) else 4.0
                sec_t = sorted(t_list, key=lambda x: bireysel_kozmik[x] + rng.normal(0, g_std), reverse=True)[:k_t]
                sec_c = sorted(c_list, key=lambda x: bireysel_kozmik[x] + rng.normal(0, g_std), reverse=True)[:k_c]
            secilen_havuz.extend(sec_t + sec_c)

        if len(secilen_havuz) < yari_boyut:
            kalanlar = list(set(range(1, max_n + 1)) - set(secilen_havuz))
            secilen_havuz.extend(rng.choice(kalanlar, size=yari_boyut - len(secilen_havuz), replace=False).tolist())
        pools_matrix[i, secilen_havuz[:yari_boyut]] = 1.0

    beklenen_cek_basi = k_arsiv * 0.5
    std_cek_basi = np.sqrt(k_arsiv * 0.5 * 0.5)
    patlama_esigi = int(np.ceil(beklenen_cek_basi + std_cek_basi * 0.85))

    kozmik_skor = np.zeros(aday_havuz_sayisi, dtype=np.float32)
    for adimlar in EVREN_ADIMLARI.values():
        g_idx = [max_idx - l for l in adimlar if max_idx - l >= 0]
        if g_idx:
            ev_isabet = pools_matrix @ draw_matrix[g_idx].T
            z_acik_ev = (len(g_idx) * beklenen_cek_basi - ev_isabet.sum(axis=1)) / max(1.0, np.sqrt(
                len(g_idx)) * std_cek_basi)
            patlama_kurakligi = (ev_isabet < patlama_esigi).mean(axis=1)
            kozmik_skor += (z_acik_ev * 1.4) + (patlama_kurakligi * 2.5)

    son_idx = list(range(toplam_cekilis - gercek_pencere, toplam_cekilis))
    pencere_isabet = pools_matrix @ draw_matrix[son_idx].T
    a_top = pencere_isabet.sum(axis=1)
    b_top = (gercek_pencere * k_arsiv) - a_top
    z_pencere = (b_top - a_top) / (2.0 * max(1.0, np.sqrt(gercek_pencere * k_arsiv * 0.25)))
    pencere_kuraklik = (pencere_isabet < patlama_esigi).mean(axis=1) * 10.0

    nihai_skor = (kozmik_skor * 0.60) + ((z_pencere * 4.5 + pencere_kuraklik) * 0.40)
    en_iyi_idx = int(np.argmax(nihai_skor))

    havuz_a = sorted(np.where(pools_matrix[en_iyi_idx] == 1.0)[0].tolist())
    havuz_b = sorted(list(set(range(1, max_n + 1)) - set(havuz_a)))

    a_gercek = a_top[en_iyi_idx]
    b_gercek = b_top[en_iyi_idx]
    z_gercek = z_pencere[en_iyi_idx]

    b_ustun_seri = 0
    for i_c in range(gercek_pencere - 1, -1, -1):
        if (k_arsiv - pencere_isabet[en_iyi_idx, i_c]) >= pencere_isabet[en_iyi_idx, i_c]:
            b_ustun_seri += 1
        else:
            break

    normalize_baski = max(0.0, (z_gercek - 1.5) / 3.8) + (b_ustun_seri / 45.0)
    olasilik_a = 50.0 + (38.0 * np.tanh(normalize_baski))

    return {
        "havuz_a": havuz_a, "havuz_b": havuz_b, "olasilik_a": round(float(olasilik_a), 1),
        "olasilik_b": round(float(100.0 - olasilik_a), 1),
        "a_top_sayisi": int(a_gercek), "b_top_sayisi": int(b_gercek),
        "beklenen_top": int(gercek_pencere * beklenen_cek_basi),
        "pencere": gercek_pencere, "z_skoru": round(float(z_gercek), 2), "seri_baski": b_ustun_seri
    }


def bant_radari_hesapla(df, cfg):
    if df is None or len(df) < 20:
        return "Orta", "Ust", {"Alt": 33.3, "Orta": 33.4, "Ust": 33.3}, {}
    b_alt, b_ust = cfg["bant_alt"], cfg["bant_ust"]
    tum_bantlar = df['Toplam'].apply(lambda t: 'Alt' if t <= b_alt else ('Ust' if t >= b_ust else 'Orta')).tolist()
    bant_isimleri = ['Alt', 'Orta', 'Ust']
    gecis_sayaci = {b1: {b2: 1 for b2 in bant_isimleri} for b1 in bant_isimleri}
    for i in range(len(tum_bantlar) - 1):
        gecis_sayaci[tum_bantlar[i]][tum_bantlar[i + 1]] += 1
    markov_matrisi = {b1: {b2: (gecis_sayaci[b1][b2] / sum(gecis_sayaci[b1].values())) * 100.0 for b2 in bant_isimleri}
                      for b1 in bant_isimleri}

    counts = Counter(tum_bantlar[-20:])
    actual = {'Alt': counts.get('Alt', 0), 'Orta': counts.get('Orta', 0), 'Ust': counts.get('Ust', 0)}
    sarkac_p = {k: max(5.0, 33.33 + (6.66 - actual[k]) * 3.2) for k in actual}

    aktif_seri = tum_bantlar[-1]
    seri_sayisi = 0
    for b in reversed(tum_bantlar):
        if b == aktif_seri:
            seri_sayisi += 1
        else:
            break
    if seri_sayisi >= 3:
        sarkac_p[aktif_seri] = max(5.0, sarkac_p[aktif_seri] - (seri_sayisi * 3.5))

    hibrit_p = {k: (sarkac_p[k] * 0.55) + (markov_matrisi[aktif_seri][k] * 0.45) for k in bant_isimleri}
    final_p = {k: (v / sum(hibrit_p.values())) * 100.0 for k, v in hibrit_p.items()}
    sirali_bantlar = sorted(final_p, key=final_p.get, reverse=True)
    return sirali_bantlar[0], sirali_bantlar[1], final_p, markov_matrisi


def eksik_cekilisleri_kontrol_et(oyun_adi, paket):
    cfg = OYUN_EVRENLERI[oyun_adi]
    df, bugun = paket["df"], datetime.date.today()
    if df['Tarih_DT'].notna().sum() > 0:
        son_tarih = df['Tarih_DT'].max().date()
        eksikler = [(son_tarih + datetime.timedelta(days=d)).strftime("%d.%m.%Y") for d in
                    range(1, max(1, (bugun - son_tarih).days + 1)) if
                    (son_tarih + datetime.timedelta(days=d)).weekday() in cfg["cekilis_gunleri"]]
        return son_tarih.strftime("%d.%m.%Y"), eksikler
    else:
        son_yil, son_hft = int(df.iloc[-1].get('Yil', bugun.year)), int(df.iloc[-1].get('Hft', 0))
        tahmini_hft = int((bugun.timetuple().tm_yday / 7) * len(cfg["cekilis_gunleri"]))
        return f"{son_yil} / {son_hft}. Hafta", [f"{son_yil} - {h}. Hafta" for h in range(son_hft + 1,
                                                                                          tahmini_hft + 1)] if son_yil == bugun.year and tahmini_hft > son_hft else []


def yeni_cekilis_ekle(oyun_adi, paket, tarih_str, hft_no, sayilar_listesi):
    dosya, kod = paket["dosya"], OYUN_EVRENLERI[oyun_adi]["kod"]
    try:
        if kod == "onnumara":
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                icerik = f.readlines()
            sep = '\t' if '\t' in (icerik[1] if len(icerik) > 1 else icerik[0]) else (
                ';' if ';' in (icerik[1] if len(icerik) > 1 else icerik[0]) else ',')
            yeni_satir = f"{datetime.date.today().year}{sep}{hft_no}{sep}" + sep.join(str(x) for x in sorted(sayilar_listesi[:22])) + "\n"
            icerik.append(yeni_satir)
            with open(dosya, 'w', encoding='utf-8') as f:
                f.writelines(icerik)
        else:
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                sep = '\t' if '\t' in f.readline() else (';' if ';' in f.readline() else ',')
            df_m = pd.read_csv(dosya, delimiter=sep)
            sirali = sorted(sayilar_listesi[:5]) + [sayilar_listesi[5]] if kod == "sanstopu" else (
                sorted(sayilar_listesi[:6]) + sayilar_listesi[6:8] if kod == "sayisal" else sorted(sayilar_listesi))
            yeni_veri = [tarih_str, int(hft_no)] + sirali
            if len(yeni_veri) == len(df_m.columns):
                pd.concat([df_m, pd.DataFrame([yeni_veri], columns=df_m.columns)], ignore_index=True).to_csv(dosya, index=False, sep=sep)
            elif len([tarih_str] + sirali) == len(df_m.columns):
                pd.concat([df_m, pd.DataFrame([[tarih_str] + sirali], columns=df_m.columns)], ignore_index=True).to_csv(dosya, index=False, sep=sep)
            else:
                return False, f"⚠️ Sütun uyumsuz! Beklenen {len(df_m.columns)}, Girilen {len(yeni_veri)}."
        st.cache_data.clear()
        return True, "✅ Çekiliş başarıyla veritabanına işlendi!"
    except Exception as e:
        return False, f"Hata: {e}"


def get_coord(num, grid_w): return ((num - 1) % grid_w, (num - 1) // grid_w)


def calc_walk_len(kolon, grid_w): return sum(
    euclidean(get_coord(kolon[i], grid_w), get_coord(kolon[i + 1], grid_w)) for i in range(len(kolon) - 1))


def poly_area(coords):
    x, y = [c[0] for c in coords], [c[1] for c in coords]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def get_cluster_density(kolon, grid_w):
    c = [get_coord(n, grid_w) for n in kolon]
    xs, ys = [x[0] for x in c], [x[1] for x in c]
    alan = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    return len(kolon) / alan if alan > 0 else 0


def get_spin_flux(kolon, spins):
    draw_spins = [spins.get(n, 1) for n in kolon]
    return sum(1 for i in range(len(kolon) - 1) if draw_spins[i] != draw_spins[i + 1])


def calc_matruska(kolon):
    k = len(kolon)
    if k == 6:
        dis, orta, cek = kolon[5] - kolon[0], kolon[4] - kolon[1], kolon[3] - kolon[2]
    elif k == 10:
        dis, orta, cek = kolon[9] - kolon[0], kolon[7] - kolon[2], kolon[5] - kolon[4]
    else:
        dis, orta, cek = kolon[4] - kolon[0], kolon[3] - kolon[1], min(kolon[2] - kolon[1], kolon[3] - kolon[2])
    return (999.0, 999.0) if orta <= 0 or cek <= 0 else (dis / orta, orta / cek)


def get_rmt_stats(kolon):
    k = len(kolon)
    arr = np.array(kolon, dtype=np.float32)
    diff = np.sqrt(np.abs(arr[:, None] - arr[None, :]))
    np.fill_diagonal(diff, arr)
    e = np.linalg.eigvalsh(diff)
    return float(e[-1]), float(e[-1] - e[-2])


def get_chatterjee_energy(kolon):
    idx = np.array(kolon) - 1
    sub = MASTER_CHATTERJEE_J[np.ix_(idx, idx)]
    return float(np.sum(np.triu(sub, k=1)) / np.sqrt(len(kolon)))


def is_percolated(kolon, pair_counts, perc_thresh):
    if not pair_counts:
        return False
    subG = nx.Graph()
    subG.add_nodes_from(kolon)
    subG.add_edges_from([(u, v) for u, v in combinations(kolon, 2) if pair_counts.get((u, v), 0) >= perc_thresh])
    return nx.is_connected(subG)


def calc_antipodal_pairs(kolon, max_n):
    k_set = set(kolon)
    return sum(1 for x in kolon if (max_n + 1 - x) in k_set and x < (max_n + 1 - x))


def calc_holographic_shadow_mean(kolon, max_n):
    return (max_n * (max_n + 1) / 2.0 - sum(kolon)) / (max_n - len(kolon))


def calc_harmonic_grid_resonance(kolon, max_n):
    ideal = max_n / (len(kolon) + 1.0)
    return np.mean([abs((kolon[i + 1] - kolon[i]) - ideal) for i in range(len(kolon) - 1)]) / ideal


def calc_spatial_markov_jump_ok(kolon, max_n):
    sic = [kolon[0]] + [kolon[i + 1] - kolon[i] for i in range(len(kolon) - 1)] + [max_n + 1 - kolon[-1]]
    ideal = max_n / (len(kolon) + 1.0)
    return 0.32 * ideal <= np.std(sic) <= 1.65 * ideal


def calc_mahalanobis_d2_ok(kolon, max_n):
    d2, k = 0.0, len(kolon)
    for idx, val in enumerate(kolon, 1):
        v = (idx * (k - idx + 1.0) * (max_n + 1.0) * (max_n - k)) / (((k + 1.0) ** 2) * (k + 2.0))
        if v > 0:
            d2 += ((val - (idx / (k + 1.0) * (max_n + 1.0))) ** 2) / v
    return 0.15 <= (d2 / k) <= 2.45


# -------------------------------------------------------------------------
# KATMAN 3 ÜRETİMİ: FİZİK/TOPOLOJİ + 12 EVREN KOZMİK PUANLAMA
# -------------------------------------------------------------------------
def hibrit_kalkan_ve_kuantum_puanla(kolon, cfg, paket, mode="mod5", hedefler=None, bant_tipi="Orta",
                                    esnek_tolerans=False, tek_havuz_modu=False):
    k, max_n, top = len(kolon), cfg["max_sayi"], sum(kolon)
    # KeyError: 'mod4' hatasını önleyen güvenli erişim
    s = cfg["sinirlar"].get(mode, cfg["sinirlar"]["mod5"])

    if hedefler and not any(h_min <= top <= h_max for (h_min, h_max) in hedefler):
        return False, 0.0, 0
    elif not hedefler and not (cfg["altin_kesi"][0] <= top <= cfg["altin_kesi"][1]):
        return False, 0.0, 0

    ihlal, iz_ih = 0, (1 if esnek_tolerans else 0)
    if sum(1 for n in kolon if n % 2 != 0) not in cfg["tek_aralik"]:
        ihlal += 1
        if ihlal > iz_ih:
            return False, 0.0, 0
    if sum(1 for n in kolon if n <= max_n // 2) not in cfg["alt_yari_sart"].get(bant_tipi, cfg["alt_yari_sart"]["Orta"]):
        ihlal += 1
        if ihlal > iz_ih:
            return False, 0.0, 0

    bos = [kolon[i + 1] - kolon[i] - 1 for i in range(k - 1)]
    if (max(bos) > cfg["max_bosluk"] or bos.count(0) > cfg.get("ardisik_max", 2) or
            not (cfg["yayilim_aralik"][0] <= kolon[-1] - kolon[0] <= cfg["yayilim_aralik"][1]) or
            not (cfg["std_aralik"][0] <= np.std(kolon) <= cfg["std_aralik"][1])):
        ihlal += 1
        if ihlal > iz_ih:
            return False, 0.0, 0

    d_say = Counter(onluk_grup_bul(n) for n in kolon)
    max_dekad_izni = (4 if tek_havuz_modu else 3) if k == 10 else (3 if tek_havuz_modu else 2)
    if (len(d_say) not in cfg["dekad_aralik"] or max(d_say.values()) > max_dekad_izni or
            max(Counter(n % 10 for n in kolon).values()) > cfg["mod10_max"]):
        ihlal += 1
        if ihlal > iz_ih:
            return False, 0.0, 0

    if sum(1 for n in kolon if n in ASAL_TUM and n <= max_n) not in cfg["asal_aralik"]:
        ihlal += 1
        if ihlal > iz_ih:
            return False, 0.0, 0

    g_f, puan = 9 - ihlal, 35.0 - (ihlal * 5.0)

    if max(Counter(n % 7 for n in kolon).values()) <= (3 if k == 10 else 2) and max(
            Counter(dijital_kok(n) for n in kolon).values()) <= (3 if k == 10 else 2):
        puan += 5.0
        g_f += 1
    if calc_antipodal_pairs(kolon, max_n) <= (2 if k == 10 else 1):
        puan += 4.0
        g_f += 1

    slps = paket["current_sleep"]
    if (sum(1 for n in kolon if slps.get(n, 0) >= paket.get("t_c_95", 20)) <= (3 if k == 10 else 2) and
            sum(1 for n in kolon if n in (paket["zirveler"] | paket["kpz_zirveler"])) <= (4 if k == 10 else 2) and
            sum(1 for n in kolon if n in (paket["vadiler"] | paket["kpz_vadiler"])) >= 1):
        puan += 8.0
        g_f += 1

    if calc_mahalanobis_d2_ok(kolon, max_n):
        puan += 7.0
        g_f += 1

    H1, H2 = (sum(kolon[:k // 2]), sum(kolon[k // 2:])) if k != 5 else (kolon[0] + kolon[1], kolon[3] + kolon[4])
    yor = [kolon[i] + kolon[k - 1 - i] for i in range(k // 2)] if k != 5 else [kolon[0] + kolon[4], kolon[1] + kolon[3], 2 * kolon[2]]
    if H1 > 0 and top > 0:
        if s["h2_oran"][0] <= H2 / top <= s["h2_oran"][1] and s["fraktal"][0] <= H2 / H1 <= s["fraktal"][1]:
            puan += 4.0
            g_f += 1
        m1, m2 = calc_matruska(kolon)
        if (max(yor) - min(yor)) <= s["sapma"] and s["mat1"][0] <= m1 <= s["mat1"][1] and s["mat2"][0] <= m2 <= s["mat2"][1]:
            puan += 4.0
            g_f += 1

    i_o = (max_n + 1.0) / 2.0
    if abs(calc_holographic_shadow_mean(kolon, max_n) - i_o) <= i_o * 0.14:
        puan += 3.0
        g_f += 1
    if 0.20 <= calc_harmonic_grid_resonance(kolon, max_n) <= 0.95:
        puan += 3.0
        g_f += 1
    if calc_spatial_markov_jump_ok(kolon, max_n):
        puan += 3.0
        g_f += 1

    sp = paket["spins"]
    if sum(sp[n] for n in kolon) in s["spin"]:
        puan += 3.0
        g_f += 1
    if get_spin_flux(kolon, sp) in s["flux"]:
        puan += 3.0
        g_f += 1

    gw = cfg["grid_w"]
    wl = calc_walk_len(kolon, gw)
    crds = [get_coord(n, gw) for n in kolon]
    C = euclidean(crds[0], crds[-1])
    if s["walk"][0] <= wl <= s["walk"][1]:
        puan += 2.0
        g_f += 1
    if s["tort"][0] <= (wl / C if C > 0 else 999) <= s["tort"][1]:
        puan += 2.0
        g_f += 1
    if s["cle"][0] <= poly_area(crds) <= s["cle"][1]:
        puan += 2.0
        g_f += 1

    gff = paket["gff_h"]
    if s["dens"][0] <= get_cluster_density(kolon, gw) <= s["dens"][1]:
        puan += 3.0
        g_f += 1
    if s["lqg"][0] <= sum(np.exp(0.5 * gff.get(n, 0)) for n in kolon) <= s["lqg"][1]:
        puan += 3.0
        g_f += 1

    me, rgap = get_rmt_stats(kolon)
    if s["lambda_u"][0] <= me / (kolon[-1] + 0.42 * np.sqrt(k * max_n)) <= s["lambda_u"][1]:
        puan += 2.0
        g_f += 1
    if s["gap"][0] * 0.85 <= rgap <= s["gap"][1] * 1.15:
        puan += 2.0
        g_f += 1
    if s["sk"][0] <= get_chatterjee_energy(kolon) <= s["sk"][1]:
        puan += 2.0
        g_f += 1

    return True, round(puan, 1), g_f


# -------------------------------------------------------------------------
# KATMAN 2: KOZMİK TOHUM SEÇİMİ (BANKO & HEDGE)
# -------------------------------------------------------------------------
def kozmik_tohum_uret(oyun_adi, paket, mutlak_alan_aktif=True, aktif_alt_havuz=None):
    cfg = OYUN_EVRENLERI[oyun_adi]
    max_n, k_arsiv = cfg["max_sayi"], cfg["arsiv_top_sayisi"]
    gecerli = set(aktif_alt_havuz) if aktif_alt_havuz else set(range(1, max_n + 1))

    df = paket["df"]
    slps, f_b, pairs = paket["current_sleep"], set(paket["faz_bankolari"]), paket["pair_counts"]
    t_cols = [f"T{i}" for i in range(1, k_arsiv + 1)]
    m_idx = len(df) - 1

    d_c = {i: 0 for i in range((max_n - 1) // 10 + 1)}
    e_soguk = Counter()
    for adimlar in EVREN_ADIMLARI.values():
        gorulen = set()
        g_ad = sum(1 for l in adimlar if m_idx - l >= 0)
        for l in adimlar:
            if m_idx - l >= 0:
                c_set = set(df.iloc[m_idx - l][t_cols])
                gorulen.update(c_set)
                for n in c_set:
                    if 1 <= n <= max_n:
                        d_c[onluk_grup_bul(n)] += 1
        if g_ad > 0:
            e_soguk.update(gecerli - gorulen)

    e_dek = min(d_c, key=d_c.get)
    ezik_h = set(range(e_dek * 10 + 1, min(max_n + 1, e_dek * 10 + 11)))
    ev_skor, _ = mutlak_kuantum_alani_hesapla()

    ham_s = {}
    for n in gecerli:
        uyk = slps.get(n, 0) / (max_n / k_arsiv)
        ham_s[n] = (e_soguk.get(n, 0) * 1.65) + uyk + (1.6 if n in f_b else 0.0) + (
            1.25 if 0.8 <= uyk <= 1.8 else 0.0) + (0.9 if n in ezik_h else 0.0) + (
                       (ev_skor.get(n, 0) * 1.4) if mutlak_alan_aktif else 0.0)

    s_tum = sorted(ham_s, key=ham_s.get, reverse=True)
    bankolar = sorted(s_tum[:cfg.get("banko_adedi", 1)])

    mp = max(pairs.values()) if pairs else 1
    hdg_s = {n: ham_s[n] + (sum(pairs.get(tuple(sorted((b, n))), 0) for b in bankolar) / max(1, mp) * 3.5) for n in
             s_tum[len(bankolar):len(bankolar) + 18]}
    d_kar = sorted(hdg_s, key=hdg_s.get, reverse=True)[:cfg.get("hedge_havuz_boyutu", 6)]

    ek_t = {"ezik_dekad": f"{e_dek * 10 + 1}-{min(max_n, (e_dek + 1) * 10)}"}
    if cfg["kod"] == "sayisal":
        sf, jf = paket["ekstra"].get("super_freqs", {}), paket["ekstra"].get("joker_freqs", {})
        ek_t["super_havuz"] = sorted(range(1, 91), key=lambda x: (sf.get(x, 0), -ham_s.get(x, 0)))[:5]
        ek_t["joker_havuz"] = sorted([x for x in range(1, 91) if x not in bankolar],
                                     key=lambda x: (jf.get(x, 0), -ham_s.get(x, 0)))[:15]
    elif cfg["kod"] == "sanstopu":
        a_sl = paket["ekstra"].get("arti_sleep", {})
        ek_t["arti_havuz"] = sorted(range(1, 15), key=lambda x: (a_sl.get(x, 0), -ham_s.get(x, 0)), reverse=True)[:5]

    return bankolar, d_kar, ek_t


def gianella_havuzundan_kolon_uret(alt_havuz_sayilari, aranan_adet, secilen_bantlar, aktif_cfg, aktif_paket,
                                   mutlak_alan_aktif, esnek_aktif, havuz_etiketi, onceden_secilen=None):
    if aranan_adet <= 0:
        return [], [], [], {}

    k_boyut = aktif_cfg["kolon_boyutu"]
    oyun_adi = next(k for k, v in OYUN_EVRENLERI.items() if v["kod"] == aktif_cfg["kod"])
    bankolar, diger_karanliklar, ek_tohum = kozmik_tohum_uret(
        oyun_adi, aktif_paket, mutlak_alan_aktif, aktif_alt_havuz=alt_havuz_sayilari)
    kalan_sayilar = list(set(alt_havuz_sayilari) - set(bankolar + diger_karanliklar))

    b_arl = [aktif_cfg[f"kolon_bant_{b.lower()}"] for b in ["Alt", "Orta", "Ust"] if
             b in secilen_bantlar] if secilen_bantlar else None
    ana_bant = secilen_bantlar[0] if len(secilen_bantlar) == 1 else "Orta"

    adaylar, gorulen = [], set(tuple(x["kolon"]) for x in (onceden_secilen or []))
    tek_hvz = len(alt_havuz_sayilari) <= (aktif_cfg["max_sayi"] // 2)

    h_aday = max(aranan_adet * 4, 100)
    max_iter = 35000  # Optimize edilmiş iterasyon sınırı
    for iter_idx in range(max_iter):
        if len(adaylar) >= h_aday:
            break
        b_secim = random.sample(bankolar, min(1, len(bankolar))) if (iter_idx % 2 == 0 and bankolar) else []
        h_secim_sayisi = min(random.choice([1, 2] if k_boyut == 10 else [0, 1]), len(diger_karanliklar))
        cekirdek = b_secim + random.sample(diger_karanliklar, h_secim_sayisi)
        eksik = k_boyut - len(cekirdek)
        if eksik < 0 or len(kalan_sayilar) < eksik:
            continue
        aday = sorted(cekirdek + random.sample(kalan_sayilar, eksik))
        aday_t = tuple(aday)

        if aday_t not in gorulen:
            gecti, qp, gf = hibrit_kalkan_ve_kuantum_puanla(
                aday, aktif_cfg, aktif_paket,
                mode="mod5", hedefler=b_arl,
                bant_tipi=ana_bant, esnek_tolerans=esnek_aktif,
                tek_havuz_modu=tek_hvz
            )
            if gecti:
                gorulen.add(aday_t)
                ig = is_percolated(aday, aktif_paket["pair_counts"], aktif_paket["perc_thresh"])
                if ig:
                    qp = min(100.0, qp + 5.0)
                tp = sum(aday)
                be = "Alt" if tp <= aktif_cfg["kolon_bant_alt"][1] else (
                    "Üst" if tp >= aktif_cfg["kolon_bant_ust"][0] else "Orta")
                adaylar.append({"kolon": aday, "etiket": f"{havuz_etiketi} [{be} | {gf}/28 Q:{int(qp)}]", "is_gold": ig,
                                "q_puan": qp, "gecen_filtre": gf})

    if len(adaylar) < aranan_adet * 2:
        for _ in range(15000):
            if len(adaylar) >= aranan_adet * 2:
                break
            aday = sorted(random.sample(alt_havuz_sayilari, k_boyut))
            aday_t = tuple(aday)
            if aday_t not in gorulen:
                gecti, qp, gf = hibrit_kalkan_ve_kuantum_puanla(
                    aday, aktif_cfg, aktif_paket, mode="mod5",
                    hedefler=b_arl, bant_tipi=ana_bant, esnek_tolerans=True,
                    tek_havuz_modu=True
                )
                if gecti:
                    gorulen.add(aday_t)
                    ig = is_percolated(aday, aktif_paket["pair_counts"], aktif_paket["perc_thresh"])
                    tp = sum(aday)
                    be = "Alt" if tp <= aktif_cfg["kolon_bant_alt"][1] else (
                        "Üst" if tp >= aktif_cfg["kolon_bant_ust"][0] else "Orta")
                    adaylar.append(
                        {"kolon": aday, "etiket": f"{havuz_etiketi}* [{be} | {gf}/28 Q:{int(qp)}]", "is_gold": ig,
                         "q_puan": qp, "gecen_filtre": gf})

    adaylar = kolonlari_12_evrende_kozmik_puanla(adaylar, aktif_cfg, aktif_paket)

    for it in adaylar:
        if "kozmik_kolon_puan" in it:
            it["etiket"] = it["etiket"].replace("]", f" K:{int(it['kozmik_kolon_puan'])}]")

    sec_opt = optimal_dagilim_sec(adaylar, aranan_adet, onceden_secilenler=onceden_secilen)
    return sec_opt, bankolar, diger_karanliklar, ek_tohum


def ekstra_top_hesapla(kolon, cfg, ek_tohum, kolon_idx=0):
    if cfg["kod"] == "sayisal":
        jh = [x for x in ek_tohum.get("joker_havuz", range(1, 91)) if x not in kolon] or [x for x in range(1, 91) if x not in kolon]
        ad_s = sorted(
            [(abs(get_chatterjee_energy(kolon + [ad])) * 2.0 + abs(get_rmt_stats(kolon + [ad])[0] - 86.0) / 15.0, ad)
             for ad in jh[:10]], key=lambda x: x[0])
        sh = ek_tohum.get("super_havuz", [1, 2, 3, 4, 5])
        return {"joker": random.choice([x[1] for x in ad_s[:3]]), "super": sh[kolon_idx % len(sh)]}
    elif cfg["kod"] == "sanstopu":
        ah = ek_tohum.get("arti_havuz", [1, 2, 3, 4, 5])
        return {"arti": ah[kolon_idx % len(ah)]}
    return {}


def kolon_html_olustur(kolon, baslik, bankolar=None, diger_karanliklar=None, ekstra=None, is_gold=False):
    b_s = set(bankolar) if isinstance(bankolar, (list, set, tuple)) else ({bankolar} if bankolar else set())
    d_s = set(diger_karanliklar or [])
    h = "".join(f"<div class='top-banko'>{n:02d}</div>" if n in b_s else (
        f"<div class='top-karanlik'>{n:02d}</div>" if n in d_s else (
            f"<div class='top-gold'>{n:02d}</div>" if is_gold else f"<div class='top-standart'>{n:02d}</div>")) for n in
                kolon)

    if ekstra:
        if "joker" in ekstra:
            h += f"<div class='top-joker'>{ekstra['joker']:02d}</div>"
        if "super" in ekstra:
            h += f"<div class='top-super'>{ekstra['super']:02d}</div>"
        if "arti" in ekstra:
            h += f"<div class='top-arti'>+{ekstra['arti']:02d}</div>"

    rozet = "<span style='color:#FFD600; font-weight:bold; margin-left:auto;'>💎 ALTIN BAĞ</span>" if is_gold else ""
    return f"<div class='kolon-satir'><div class='kolon-baslik'>{baslik}</div><div>{h}</div>{rozet}</div>"


# =========================================================================
# STREAMLIT ARAYÜZ (GLOBAL DÜZEY - GİRİNTİ HATASI DÜZELTİLDİ)
# =========================================================================
st.title("🎯 Quant Loto V23.5 — 3 Katmanlı Kozmik Tarama Motoru")
secilen_oyun = st.radio("🎯 Oynamak İstediğiniz Kuantum Evrenini Seçin:", list(OYUN_EVRENLERI.keys()), horizontal=True)

aktif_cfg = OYUN_EVRENLERI[secilen_oyun]
aktif_paket = evren_verisini_yukle(secilen_oyun)
evrensel_basinc_vektoru, aktif_evrenler_listesi = mutlak_kuantum_alani_hesapla()

st.sidebar.markdown("### ⚛️ Kozmik Kontrol Paneli")
st.sidebar.caption(
    f"Aktif Veritabanları ({len(aktif_evrenler_listesi)}/4): {', '.join([e.split()[1] for e in aktif_evrenler_listesi]) if aktif_evrenler_listesi else 'Yok'}")
pencere_boyutu = st.sidebar.slider("🔎 Gianella Sarkaç Penceresi (Son N Çekiliş):", 40, 150, 80, step=10)
mutlak_alan_aktif = st.sidebar.checkbox("🌌 4 Evren Ortak Dolanıklığı", value=True)
esnek_tolerans_aktif = st.sidebar.checkbox("🔓 Esnek Kalkan Toleransı (5/6 Kalkan)", value=False)

if st.sidebar.button("🔄 Analizleri ve Tohumları Yenile", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# EĞER VERİTABANI YOKSA KULLANICIYA YÜKLEME VEYA SENTETİK OLUŞTURMA SEÇENEĞİ SUN
if aktif_paket is None:
    st.warning(f"⚠️ **{secilen_oyun}** için `{aktif_cfg['dosyalar'][0]}` dosyası çalışma klasöründe bulunamadı!")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("#### 📂 1. Kendi CSV Dosyanızı Yükleyin")
        yuklenen_csv = st.file_uploader(f"{aktif_cfg['dosyalar'][0]} dosyasını seçin:", type=["csv", "txt"])
        if yuklenen_csv is not None:
            with open(aktif_cfg["dosyalar"][0], "wb") as f:
                f.write(yuklenen_csv.getbuffer())
            st.cache_data.clear()
            st.success("✅ Dosya kaydedildi! Yükleniyor...")
            st.rerun()
    with col_v2:
        st.markdown("#### 🧪 2. Sentetik Kuantum Arşivi Oluştur")
        st.caption("Elinde veri dosyası yoksa motoru test etmek için gerçekçi kurallarla 250 çekilişlik arşiv üretir.")
        if st.button("⚡ Tüm Oyunlar İçin Test Veritabanı Oluştur", type="primary"):
            for o_adi in OYUN_EVRENLERI.keys():
                sentetik_arsiv_olustur(o_adi, 250)
            st.success("✅ Tüm oyun evrenleri oluşturuldu!")
            st.rerun()
    st.stop()

son_kayit_bilgisi, eksik_cekilisler = eksik_cekilisleri_kontrol_et(secilen_oyun, aktif_paket)
evren_kilidi_acik = True

if len(eksik_cekilisler) > 0:
    st.markdown(
        f'<div class="uyari-kutu"><b style="color:#FFD600;">⚠️ VERİTABANI UYARISI ({len(eksik_cekilisler)} Eksik):</b> Son Kayıt: <b>{son_kayit_bilgisi}</b> | Eksikler: {", ".join(eksik_cekilisler[:6])}</div>',
        unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.info("💡 Yeni çekilişleri **📊 Yeni Çekiliş Girişi** sekmesinden ekleyebilirsiniz.")
    with c2:
        evren_kilidi_acik = st.checkbox("🔓 Eksikleri Geç ve Evreni Aç", value=True)
else:
    st.caption(
        f"✅ **Veritabanı Güncel!** Son Kayıt: **{son_kayit_bilgisi}** | Toplam Arşiv: **{len(aktif_paket['df']):,} Çekiliş**")

if not evren_kilidi_acik:
    st.stop()

df_global = aktif_paket["df"]
bant_1, bant_2, ihtimaller, markov_matrisi = bant_radari_hesapla(df_global, aktif_cfg)
gianella_rapor = dinamik_gianella_havuz_analizi(secilen_oyun, pencere=pencere_boyutu)

tabs = st.tabs(["🚀 3 Katmanlı Kozmik Üretim", "💾 Kupon Kasası", "🧪 Hızlı Backtest", "📊 Yeni Çekiliş Girişi"])

with tabs[0]:
    h_a, h_b, ol_a, ol_b = gianella_rapor["havuz_a"], gianella_rapor["havuz_b"], gianella_rapor["olasilik_a"], gianella_rapor["olasilik_b"]
    st.markdown(f'''
    <div class="gianella-kutu">
        <div style="color:#FFD600; font-weight:bold; font-size:15.5px; margin-bottom:6px;">
            🧬 KOZMİK HAVUZ TARAMASI (2.000 Aday İçinden En Güçlüsü)
        </div>
        <div style="color:#e2e8f0; font-size:13.5px; line-height:1.5;">
            🔥 <b>Havuz A (12 Evrende En Çok Sıkışan Havuz - Olasılık: %{ol_a}):</b> Z-Skoru: <b>+{gianella_rapor['z_skoru']}σ</b><br>
            ⚖️ <b>Havuz B (Simetrik Karşılık / Doygun Havuz - %{ol_b}):</b> Üst Üste Baskınlık Serisi: <b>{gianella_rapor['seri_baski']} Çekiliş</b>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    b_alt, b_ust = aktif_cfg["bant_alt"], aktif_cfg["bant_ust"]
    cg, co = st.columns([2.3, 1])
    with cg:
        fig, ax = plt.subplots(figsize=(9.5, 2.8))
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#161b22')
        son_25 = df_global.tail(25).copy().reset_index(drop=True)
        y_vals = son_25['Toplam'].values
        y_min, y_max = min(min(y_vals) - 15, int(b_alt * 0.72)), max(max(y_vals) + 20, int(b_ust * 1.22))
        ax.axhspan(0, b_alt, color='#00B0FF', alpha=0.16)
        ax.axhspan(b_alt, b_ust, color='#00E676', alpha=0.16)
        ax.axhspan(b_ust, y_max + 250, color='#FF1744', alpha=0.16)
        x_vals = range(1, len(son_25) + 1)
        ax.plot(x_vals, y_vals, color='#94a3b8', linestyle='--', linewidth=1.4, alpha=0.8)
        ax.scatter(x_vals, y_vals,
                   color=['#00B0FF' if v <= b_alt else ('#00E676' if v < b_ust else '#FF1744') for v in y_vals],
                   s=95, zorder=5, edgecolor='white', linewidth=1.1)
        ax.set_ylim(y_min, y_max)
        ax.set_xlim(0.5, len(son_25) + 0.5)
        ax.set_xticks(x_vals)
        ax.tick_params(colors='white', labelsize=8)
        ax.set_title("Son 25 Çekiliş 3 Bant Seyri", color='#00E5FF', fontsize=10.5, fontweight='bold')
        for sp in ax.spines.values():
            sp.set_color('#30363d')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)  # Bellek sızıntısını önler
    with co:
        st.markdown("##### 📡 3x3 Markov İhtimalleri")
        st.markdown(
            f"<div class='bant-kart bant-ust'>🔴 ÜST ({b_ust}+): %{ihtimaller['Ust']:.1f}</div>"
            f"<div class='bant-kart bant-orta'>🟢 ORTA ({b_alt + 1}-{b_ust - 1}): %{ihtimaller['Orta']:.1f}</div>"
            f"<div class='bant-kart bant-alt'>🔵 ALT (<={b_alt}): %{ihtimaller['Alt']:.1f}</div>",
            unsafe_allow_html=True)

    c_u1, c_u2, c_u3 = st.columns([1.6, 1.4, 1])
    with c_u1:
        havuz_tercihi = st.selectbox("🧬 1. Gianella Havuzu:",
                                     [f"🎯 Akıllı Oto-Dağılım (%{ol_a} A / %{ol_b} B)", "🔥 Sadece Havuz A",
                                      "⚖️ Eşit Dağılımlı", "🪐 Sadece Havuz B"])
    with c_u2:
        bmap = {"🔵 Alt": "Alt", "🟢 Orta": "Orta", "🔴 Üst": "Ust"}
        secilen_bant_etiketleri = st.multiselect("📡 2. Bantlar:", list(bmap.keys()),
                                                 default=[k for k, v in bmap.items() if v in [bant_1, bant_2]])
    with c_u3:
        kolon_adedi = int(st.number_input("🔢 3. Kolon Sayısı:", 1, 200, 20, 1))

    if st.button("🚀 3 KATMANLI KOZMİK MOTOR İLE ÜRET", type="primary", use_container_width=True):
        start_t = time.time()
        with st.spinner("Havuzlar, Mezo Tohumlar ve Kolonlar 12 evrende taranarak kupon örülüyor..."):
            b_kodlari = [bmap[e] for e in secilen_bant_etiketleri] if secilen_bant_etiketleri else ["Alt", "Orta", "Ust"]
            if "Akıllı Oto" in havuz_tercihi:
                adet_a = max(1, int(round(kolon_adedi * (ol_a / 100.0))))
                kol_a, b_a, hdg_a, e_t = gianella_havuzundan_kolon_uret(h_a, adet_a, b_kodlari, aktif_cfg,
                                                                        aktif_paket, mutlak_alan_aktif,
                                                                        esnek_tolerans_aktif, "🎯 Havuz-A (Oto)")
                kalan_adet = kolon_adedi - adet_a
                kol_b, b_b, hdg_b, _ = gianella_havuzundan_kolon_uret(h_b, kalan_adet, b_kodlari,
                                                                      aktif_cfg, aktif_paket, mutlak_alan_aktif,
                                                                      esnek_tolerans_aktif, "🪐 Havuz-B (Oto)") if kalan_adet > 0 else ([], [], [], {})
                n_h = kol_a + kol_b
                bnks = sorted(list(set(b_a + b_b)))
                dkr = sorted(list(set(hdg_a + hdg_b)))
            elif "Sadece Havuz A" in havuz_tercihi:
                n_h, bnks, dkr, e_t = gianella_havuzundan_kolon_uret(h_a, kolon_adedi, b_kodlari, aktif_cfg,
                                                                     aktif_paket, mutlak_alan_aktif,
                                                                     esnek_tolerans_aktif, "🎯 Havuz-A")
            elif "Sadece Havuz B" in havuz_tercihi:
                n_h, bnks, dkr, e_t = gianella_havuzundan_kolon_uret(h_b, kolon_adedi, b_kodlari, aktif_cfg,
                                                                     aktif_paket, mutlak_alan_aktif,
                                                                     esnek_tolerans_aktif, "🪐 Havuz-B")
            else:
                kol_a, b_a, hdg_a, e_t = gianella_havuzundan_kolon_uret(h_a, kolon_adedi - (kolon_adedi // 2),
                                                                        b_kodlari, aktif_cfg, aktif_paket,
                                                                        mutlak_alan_aktif, esnek_tolerans_aktif,
                                                                        "🎯 Havuz-A")
                kol_b, b_b, hdg_b, _ = gianella_havuzundan_kolon_uret(h_b, kolon_adedi // 2, b_kodlari, aktif_cfg,
                                                                      aktif_paket, mutlak_alan_aktif,
                                                                      esnek_tolerans_aktif, "🪐 Havuz-B")
                n_h = kol_a + kol_b
                bnks = sorted(list(set(b_a + b_b)))
                dkr = sorted(list(set(hdg_a + hdg_b)))

            for i, it in enumerate(n_h):
                it["ekstra"] = ekstra_top_hesapla(it["kolon"], aktif_cfg, e_t, i)
        if n_h:
            st.session_state[f"v_uret_{aktif_cfg['kod']}"] = (n_h, bnks, dkr, e_t, time.time() - start_t)

    if f"v_uret_{aktif_cfg['kod']}" in st.session_state:
        hvz, bk, dk, et, sure = st.session_state[f"v_uret_{aktif_cfg['kod']}"]
        ort_q = np.mean([i.get("q_puan", 75) for i in hvz])
        ort_k = np.mean([i.get("kozmik_kolon_puan", 75) for i in hvz])
        st.markdown(f'''
        <div class="tohum-kutu"><div style="color:#00E5FF; font-weight:bold; font-size:14px; margin-bottom:6px;">
        🌌 3 KATMANLI KOZMİK AĞ ({len(hvz)} Kolon — {sure:.2f} sn)</div>
        <div style="color:white; font-size:13.5px;"><b style="color:#E1BEE7;">Bankolar:</b> {" ".join([f"<span class='top-banko'>{b:02d}</span>" for b in bk])} | <b style="color:#FF8A80;">Hedge:</b> {dk[:8]} | <b>Ort. Puanlar:</b> Q:{ort_q:.1f} / K:{ort_k:.1f}</div></div>
        ''', unsafe_allow_html=True)
        for i, it in enumerate(hvz, 1):
            st.markdown(
                kolon_html_olustur(it["kolon"], f"{i:02d}. {it['etiket']} (Top:{sum(it['kolon'])})", bk, dk,
                                   it["ekstra"], it["is_gold"]), unsafe_allow_html=True)
        ca, cb = st.columns([1, 2])
        with ca:
            if st.button("💾 Kasaya Kaydet"):
                kasaya_kupon_ekle(secilen_oyun, havuz_tercihi.split('(')[0], hvz, bk, dk)
                st.success("✅ Kupon Kasaya Kaydedildi!")
        with cb:
            with st.expander("📋 Kopyalanabilir Metin"):
                st.code("\n".join(
                    f"{it.get('etiket', '')} (Top:{sum(it['kolon'])}): " + " - ".join(f"{n:02d}" for n in it["kolon"])
                    for it in hvz))

with tabs[1]:
    kasa = kasayi_yukle()
    if not kasa:
        st.info("Kayıtlı kupon yok.")
    else:
        kst_input = st.text_input("🎯 Çıkan Sonucu Gir (Sayıları boşlukla ayırın):")
        kst = set(int(s) for s in re.findall(r'\d+', kst_input))
        for kayit in kasa:
            with st.expander(f"📁 [{kayit['tarih']}] {kayit['oyun']} — {len(kayit['kolonlar'])} Kolon"):
                if kst:
                    say = Counter(len(set(it["kolon"]) & kst) for it in kayit["kolonlar"])
                    st.success("🏆 " + " | ".join(
                        f"{k} Bilen: {v} Adet" for k, v in sorted(say.items(), reverse=True) if k >= 3 or k == 0))
                for i, it in enumerate(kayit["kolonlar"], 1):
                    k = it["kolon"]
                    st.markdown(kolon_html_olustur(k, f"Kolon {i:02d} ({sum(k)})" + (
                        f" 🎯[{len(set(k) & kst)}]" if kst else ""), kayit.get("banko"), kayit.get("hedge"),
                                                   it.get("ekstra", {})), unsafe_allow_html=True)
                if st.button("🗑️ Sil", key=f"d_{kayit['id']}"):
                    kasadan_sil(kayit["id"])
                    st.rerun()

with tabs[2]:
    st.markdown("### 🧪 Hızlı Backtest (Geçmiş Çekiliş Simülasyonu)")
    if f"v_uret_{aktif_cfg['kod']}" not in st.session_state:
        st.info("Backtest yapmak için önce 1. Sekmeden kupon üretin.")
    else:
        hvz_bt, _, _, _, _ = st.session_state[f"v_uret_{aktif_cfg['kod']}"]
        test_sayisi = st.slider("Son Kaç Çekilişte Test Edilsin?", 5, min(100, len(aktif_paket["draws"])), 20)
        son_cekilisler = aktif_paket["draws"][-test_sayisi:]
        genel_isabet = Counter()
        for cek in son_cekilisler:
            c_set = set(cek)
            en_iyi_isabet = max(len(set(it["kolon"]) & c_set) for it in hvz_bt)
            genel_isabet[en_iyi_isabet] += 1

        st.markdown(f"**Son {test_sayisi} Çekilişte Kuponun En Yüksek İsabet Dağılımı:**")
        bt_cols = st.columns(len(genel_isabet) if genel_isabet else 1)
        for idx, (isabet, adet) in enumerate(sorted(genel_isabet.items(), reverse=True)):
            bt_cols[idx].metric(label=f"🎯 {isabet} İsabet", value=f"{adet} Çekiliş")

with tabs[3]:
    st.markdown("### 📊 Yeni Çekiliş Ekle & Analiz Et")
    cg1, cg2 = st.columns([2, 1])
    with cg1:
        ba = 8 if aktif_cfg["kod"] == "sayisal" else (6 if aktif_cfg["kod"] in ["super", "sanstopu"] else 22)
        c_trh = st.text_input("📅 Çekiliş Tarihi:", datetime.date.today().strftime("%d.%m.%Y"))
        c_hft = st.number_input("📌 Hafta No:", 1, 500, 84)
        c_syl = st.text_input(f"🎱 Çıkan Sayılar ({ba} adet):")
        if st.button("💾 Kaydet"):
            syl = [int(s) for s in re.findall(r'\d+', c_syl)]
            if len(syl) != ba:
                st.error(f"Lütfen {ba} adet sayı girin! (Şu an {len(syl)} adet girdiniz)")
            else:
                bas, mes = yeni_cekilis_ekle(secilen_oyun, aktif_paket, c_trh, c_hft, syl)
                if bas:
                    st.success(mes)
                else:
                    st.error(mes)