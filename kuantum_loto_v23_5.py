# =========================================================================
# QUANT LOTO V23.5 — PARÇA 1 / 3
# KÜTÜPHANELER, 4 EVREN KONFİGÜRASYONU, KASA, VERİTABANI OKUYUCU,
# DİNAMİK GIANELLA SARKAÇ MOTORU (SON 80 ÇEKİLİŞ) & 3x3 MARKOV MATRİSİ
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

st.set_page_config(page_title="Quant Loto V23.5 — Dinamik Gianella & 28 Filtre", page_icon="🎯", layout="wide")

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
    }
    .kolon-baslik {width: 245px; font-weight: bold; color: #cbd5e1; font-size: 13px;}
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


def onluk_grup_bul(n):
    return (n - 1) // 10


def dijital_kok(n):
    return 1 + (n - 1) % 9 if n > 0 else 0


OYUN_EVRENLERI = {
    "🎯 On Numara": {
        "kod": "onnumara",
        "max_sayi": 80,
        "kolon_boyutu": 10,
        "arsiv_top_sayisi": 22,
        "banko_adedi": 2,
        "hedge_havuz_boyutu": 8,
        "dosyalar": ["OnNumara.csv", "On_Numara_Kusursuz.csv", "OnNumara_3.csv"],
        "cekilis_gunleri": [0, 4],
        "gun_isimleri": "Pazartesi, Cuma",
        "grid_w": 10,
        "bant_alt": 850, "bant_ust": 930,
        "kolon_bant_alt": (300, 380), "kolon_bant_orta": (381, 430), "kolon_bant_ust": (431, 510),
        "altin_kesi": (320, 490),
        "alt_yari_sart": {"Orta": [3, 4, 5, 6, 7], "Alt": [5, 6, 7, 8], "Ust": [2, 3, 4, 5]},
        "tek_aralik": [3, 4, 5, 6, 7],
        "asal_aralik": [1, 2, 3, 4],
        "dekad_aralik": [5, 6, 7, 8],
        "mod10_max": 3,
        "ardisik_max": 2,
        "yayilim_aralik": (50, 76),
        "std_aralik": (17.0, 27.5),
        "t1_max": 18, "tson_min": 62,
        "max_bosluk": 25,
        "sinirlar": {
            "mod4": {"H1": (70, 155), "H2": (245, 340), "h2_oran": (0.65, 0.80), "fraktal": (1.75, 4.20), "sapma": 28,
                     "mat1": (1.35, 2.60), "mat2": (2.50, 20.00), "spin": [-4, -2, 0, 2, 4], "flux": [3, 4, 5, 6, 7],
                     "walk": (22.0, 46.0), "tort": (2.60, 5.55), "cle": (2.0, 22.0), "dens": (0.125, 0.195),
                     "lqg": (8.00, 14.50),
                     "eig": (86.00, 102.00), "gap": (22.00, 31.00), "lambda_u": (0.98, 1.18), "sk": (-1.50, 2.00)},
            "mod5": {"H1": (55, 180), "H2": (215, 365), "h2_oran": (0.60, 0.85), "fraktal": (1.35, 5.20), "sapma": 42,
                     "mat1": (1.20, 3.40), "mat2": (1.80, 36.00), "spin": [-6, -4, -2, 0, 2, 4, 6],
                     "flux": [2, 3, 4, 5, 6, 7, 8],
                     "walk": (18.0, 56.0), "tort": (2.00, 7.20), "cle": (1.0, 27.0), "dens": (0.110, 0.250),
                     "lqg": (6.00, 17.50),
                     "eig": (78.00, 110.00), "gap": (18.00, 36.00), "lambda_u": (0.92, 1.25), "sk": (-2.40, 2.80)}
        }
    },
    "🎱 Şans Topu": {
        "kod": "sanstopu",
        "max_sayi": 34,
        "kolon_boyutu": 5,
        "arsiv_top_sayisi": 5,
        "banko_adedi": 1,
        "hedge_havuz_boyutu": 5,
        "dosyalar": ["Sans_topu_sonuclar.xlsx", "Sans_Topu.xlsx", "Sans_topu_sonuclar.csv"],
        "cekilis_gunleri": [2, 6],
        "gun_isimleri": "Çarşamba, Pazar",
        "grid_w": 7,
        "bant_alt": 78, "bant_ust": 96,
        "kolon_bant_alt": (40, 78), "kolon_bant_orta": (79, 95), "kolon_bant_ust": (96, 135),
        "altin_kesi": (62, 113),
        "alt_yari_sart": {"Orta": [1, 2, 3, 4], "Alt": [3, 4, 5], "Ust": [0, 1, 2]},
        "tek_aralik": [1, 2, 3, 4],
        "asal_aralik": [1, 2, 3],
        "dekad_aralik": [3, 4],
        "mod10_max": 2,
        "ardisik_max": 1,
        "yayilim_aralik": (14, 32),
        "std_aralik": (5.2, 11.8),
        "t1_max": 15, "tson_min": 20,
        "max_bosluk": 18,
        "sinirlar": {
            "mod4": {"H1": (8, 28), "H2": (40, 63), "h2_oran": (0.48, 0.72), "fraktal": (1.60, 6.00), "sapma": 15,
                     "mat1": (1.30, 3.85), "mat2": (1.80, 9.00), "spin": [-3, -1, 1, 3], "flux": [1, 2, 3],
                     "walk": (6.5, 15.5), "tort": (1.40, 4.20), "cle": (0.5, 8.5), "dens": (0.140, 0.420),
                     "lqg": (4.00, 7.50),
                     "eig": (26.00, 39.50), "gap": (7.50, 16.50), "lambda_u": (0.88, 1.12), "sk": (-1.10, 1.35)},
            "mod5": {"H1": (4, 36), "H2": (32, 67), "h2_oran": (0.42, 0.78), "fraktal": (1.10, 9.00), "sapma": 22,
                     "mat1": (1.15, 6.20), "mat2": (1.30, 14.00), "spin": [-5, -3, -1, 1, 3, 5], "flux": [1, 2, 3, 4],
                     "walk": (4.5, 19.0), "tort": (1.10, 5.80), "cle": (0.2, 11.0), "dens": (0.100, 0.600),
                     "lqg": (3.20, 8.80),
                     "eig": (20.00, 42.00), "gap": (5.00, 21.00), "lambda_u": (0.82, 1.20), "sk": (-1.80, 2.00)}
        }
    },
    "🌌 Çılgın Sayısal Loto": {
        "kod": "sayisal",
        "max_sayi": 90,
        "kolon_boyutu": 6,
        "arsiv_top_sayisi": 6,
        "banko_adedi": 1,
        "hedge_havuz_boyutu": 7,
        "dosyalar": ["Cilgin_Sayisal_sonuclari.xlsx", "Cilgin_Sayisal_sonuclari_2.xlsx", "Cilgin_Sayisal.csv"],
        "cekilis_gunleri": [0, 2, 5],
        "gun_isimleri": "Pazartesi, Çarşamba, Cumartesi",
        "grid_w": 10,
        "bant_alt": 246, "bant_ust": 300,
        "kolon_bant_alt": (130, 246), "kolon_bant_orta": (247, 299), "kolon_bant_ust": (300, 410),
        "altin_kesi": (212, 338),
        "alt_yari_sart": {"Orta": [2, 3, 4], "Alt": [3, 4, 5, 6], "Ust": [0, 1, 2, 3]},
        "tek_aralik": [2, 3, 4],
        "asal_aralik": [1, 2, 3],
        "dekad_aralik": [4, 5, 6],
        "mod10_max": 2,
        "ardisik_max": 1,
        "yayilim_aralik": (45, 85),
        "std_aralik": (15.5, 30.5),
        "t1_max": 32, "tson_min": 58,
        "max_bosluk": 40,
        "sinirlar": {
            "mod4": {"H1": (40, 120), "H2": (160, 240), "h2_oran": (0.64, 0.81), "fraktal": (1.5, 4.0), "sapma": 30,
                     "mat1": (1.20, 2.75), "mat2": (1.60, 12.00), "spin": [-2, 0, 2], "flux": [1, 2, 3, 4],
                     "walk": (15.0, 35.0), "tort": (1.65, 4.88), "cle": (1.5, 23.0), "dens": (0.073, 0.165),
                     "lqg": (5.50, 8.50),
                     "eig": (75.17, 96.95), "gap": (11.07, 30.17), "lambda_u": (0.88, 1.12), "sk": (-1.20, 1.50)},
            "mod5": {"H1": (30, 150), "H2": (130, 270), "h2_oran": (0.58, 0.86), "fraktal": (1.1, 5.0), "sapma": 45,
                     "mat1": (1.10, 4.00), "mat2": (1.25, 24.00), "spin": [-4, -2, 0, 2, 4], "flux": [1, 2, 3, 4, 5],
                     "walk": (11.0, 42.0), "tort": (1.30, 6.20), "cle": (1.0, 29.0), "dens": (0.050, 0.240),
                     "lqg": (4.00, 10.00),
                     "eig": (65.00, 110.00), "gap": (8.00, 40.00), "lambda_u": (0.82, 1.20), "sk": (-2.00, 2.50)}
        }
    },
    "🔥 Süper Loto": {
        "kod": "super",
        "max_sayi": 60,
        "kolon_boyutu": 6,
        "arsiv_top_sayisi": 6,
        "banko_adedi": 1,
        "hedge_havuz_boyutu": 7,
        "dosyalar": ["Super_Loto_2020.csv", "Super_Loto.xlsx", "Super_Loto_sonuclar.xlsx"],
        "cekilis_gunleri": [1, 3, 6],
        "gun_isimleri": "Salı, Perşembe, Pazar",
        "grid_w": 10,
        "bant_alt": 166, "bant_ust": 201,
        "kolon_bant_alt": (106, 166), "kolon_bant_orta": (167, 200), "kolon_bant_ust": (201, 260),
        "altin_kesi": (145, 221),
        "alt_yari_sart": {"Orta": [2, 3, 4], "Alt": [3, 4, 5, 6], "Ust": [0, 1, 2, 3]},
        "tek_aralik": [2, 3, 4],
        "asal_aralik": [1, 2, 3],
        "dekad_aralik": [3, 4, 5, 6],
        "mod10_max": 2,
        "ardisik_max": 1,
        "yayilim_aralik": (32, 56),
        "std_aralik": (10.5, 20.5),
        "t1_max": 22, "tson_min": 39,
        "max_bosluk": 24,
        "sinirlar": {
            "mod4": {"H1": (30, 72), "H2": (108, 154), "h2_oran": (0.64, 0.81), "fraktal": (1.70, 3.90), "sapma": 21,
                     "mat1": (1.18, 2.75), "mat2": (1.50, 12.00), "spin": [-2, 0, 2], "flux": [1, 2, 3, 4],
                     "walk": (12.0, 24.5), "tort": (1.55, 4.95), "cle": (1.0, 17.5), "dens": (0.095, 0.230),
                     "lqg": (4.70, 7.60),
                     "eig": (50.50, 69.00), "gap": (9.80, 23.50), "lambda_u": (0.87, 1.13), "sk": (-1.15, 1.45)},
            "mod5": {"H1": (20, 88), "H2": (90, 168), "h2_oran": (0.58, 0.86), "fraktal": (1.35, 5.05), "sapma": 26,
                     "mat1": (1.10, 3.80), "mat2": (1.25, 21.00), "spin": [-4, -2, 0, 2, 4], "flux": [1, 2, 3, 4, 5],
                     "walk": (10.0, 28.0), "tort": (1.20, 6.00), "cle": (0.5, 20.0), "dens": (0.080, 0.320),
                     "lqg": (4.00, 8.50),
                     "eig": (45.00, 74.00), "gap": (8.00, 27.00), "lambda_u": (0.82, 1.20), "sk": (-1.60, 2.00)}
        }
    }
}

np.random.seed(42)
MASTER_CHATTERJEE_J = np.random.normal(loc=0, scale=1.0, size=(90, 90))
MASTER_CHATTERJEE_J = (MASTER_CHATTERJEE_J + MASTER_CHATTERJEE_J.T) / 2
np.fill_diagonal(MASTER_CHATTERJEE_J, 0)


# -------------------------------------------------------------------------
# MAX-DISPERSION & FERMAT COVERING (BALANCED WHEEL OPTİMİZASYONU)
# -------------------------------------------------------------------------
def optimal_dagilim_sec(aday_havuzu, hedef_sayi, onceden_secilenler=None):
    """
    Aday havuzu içinden hem satırlar arası kesişimi minimize eden (Max-Dispersion)
    hem de havuzdaki tüm sayıları eşit frekansta tarayan (Fermat Covering / Balanced Wheel)
    optimal kolon setini seçer.
    """
    if len(aday_havuzu) <= hedef_sayi:
        return aday_havuzu
    havuz_kopya = list(aday_havuzu)
    secilenler = []
    referans_havuz = list(onceden_secilenler) if onceden_secilenler else []
    sayi_ullanim_sayaci = Counter()

    for r in referans_havuz:
        sayi_ullanim_sayaci.update(r["kolon"])

    if not referans_havuz:
        ilk = havuz_kopya.pop(random.randint(0, len(havuz_kopya) - 1))
        secilenler.append(ilk)
        referans_havuz.append(ilk)
        sayi_ullanim_sayaci.update(ilk["kolon"])

    while len(secilenler) < hedef_sayi and havuz_kopya:
        en_iyi_aday, en_dusuk_maliyet = None, 999999.0
        # Performans için havuz çok büyükse örnekleme yap
        taranacak = havuz_kopya if len(havuz_kopya) <= 450 else random.sample(havuz_kopya, 450)
        for aday in taranacak:
            k_set = set(aday["kolon"])
            max_ortak = max(len(k_set & set(sec["kolon"])) for sec in referans_havuz)
            ort_ortak = sum(len(k_set & set(sec["kolon"])) for sec in referans_havuz) / len(referans_havuz)
            frekans_yuku = sum(sayi_ullanim_sayaci[n] for n in aday["kolon"]) / len(aday["kolon"])
            altin_bonus = -0.35 if aday.get("is_gold") else 0.0

            maliyet = (max_ortak * 10.0) + (ort_ortak * 3.5) + (frekans_yuku * 1.8) + altin_bonus
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
                    "       🎯 QUANT TERMİNALİ V23.5 - FAVORİ KUPON KASASI               ",
                    "====================================================================\n"]
        for kayit in kasa_listesi:
            satirlar.append(f"📅 Tarih: {kayit['tarih']} | 🎯 Oyun: {kayit['oyun']} | ⚙️ Paket: {kayit['mod']}")
            if kayit.get("banko"):
                satirlar.append(f"🔮 Çekirdek Banko: {kayit['banko']} | Elit Hedge: {kayit.get('hedge', [])}")
            for idx, item in enumerate(kayit["kolonlar"], 1):
                k = item["kolon"]
                eks = item.get("ekstra", {})
                etk = item.get("etiket", f"Kolon {idx:02d}")
                s_str = f"  {etk:22s} (Top:{sum(k):3d}): " + " - ".join(f"{n:02d}" for n in k)
                if "joker" in eks: s_str += f" | Joker: {eks['joker']:02d} | Süper: {eks['super']:02d}"
                if "arti" in eks: s_str += f" | +1 Topu: +{eks['arti']:02d}"
                if item.get("is_gold"): s_str += " [💎 ALTIN BAĞ]"
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
        "banko": banko_list,
        "hedge": diger_karanliklar,
        "kolonlar": kolon_listesi
    }
    kasa.insert(0, yeni_kayit)
    with open(FAVORI_KASA_JSON, "w", encoding="utf-8") as f:
        json.dump(kasa, f, ensure_ascii=False, indent=2)
    kasayi_txt_olarak_senkronize_et(kasa)


def kasadan_sil(kayit_id):
    kasa = [k for k in kasayi_yukle() if k.get("id") != kayit_id]
    with open(FAVORI_KASA_JSON, "w", encoding="utf-8") as f:
        json.dump(kasa, f, ensure_ascii=False, indent=2)
    kasayi_txt_olarak_senkronize_et(kasa)


# -------------------------------------------------------------------------
# VERİTABANI OKUYUCU & ARŞİV İSTATİSTİK MOTORU
# -------------------------------------------------------------------------
def dosya_bul(aday_listesi):
    return next((f for f in aday_listesi if os.path.exists(f)), None)


@st.cache_data(ttl=60)
def evren_verisini_yukle(oyun_adi):
    cfg = OYUN_EVRENLERI[oyun_adi]
    kod = cfg["kod"]
    max_n = cfg["max_sayi"]
    k_arsiv = cfg["arsiv_top_sayisi"]
    dosya = dosya_bul(cfg["dosyalar"])

    if not dosya:
        return None

    try:
        t_cols = [f"T{i}" for i in range(1, k_arsiv + 1)]

        if kod == "sayisal":
            df = pd.read_excel(dosya, header=1)
            df = df.rename(
                columns={'Tarih': 'Tarih', 'T1': 'T1', 'T2': 'T2', 'T3': 'T3', 'T4': 'T4', 'T5': 'T5', 'T6': 'T6',
                         'Joker': 'Joker', 'Super': 'Super'})
            df = df.dropna(subset=['Tarih'])
            df = df[~df['Tarih'].astype(str).str.contains('Tarih', case=False, na=False)]
            num_cols = t_cols + ['Joker', 'Super']
            for c in num_cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=num_cols)
            for c in num_cols: df[c] = df[c].astype(int)
            df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='mixed', dayfirst=True, errors='coerce')
            df = df.sort_values('Tarih_DT').reset_index(drop=True)

        elif kod == "super":
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                sep = '\t' if '\t' in f.readline() else ';'
            df = pd.read_csv(dosya, delimiter=sep)
            if len(df.columns) <= 1: df = pd.read_csv(dosya, delimiter=',')
            for c in t_cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=t_cols)
            for c in t_cols: df[c] = df[c].astype(int)
            if 'Tarih' in df.columns:
                df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='mixed', dayfirst=True, errors='coerce')
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
                        if first_val == 'Hft' or 'Tarih' in first_val: continue
                        if len(parts) >= 23:
                            rows.append([aktif_yil, parts[0]] + parts[1:23])
                        else:
                            rows.append([aktif_yil, '0'] + parts[:22])
            df = pd.DataFrame(rows, columns=['Yil', 'Hft'] + t_cols)
            df['Hft'] = pd.to_numeric(df['Hft'], errors='coerce').fillna(0).astype(int)
            for c in t_cols: df[c] = pd.to_numeric(df[c], errors='coerce')
            df = df.dropna(subset=t_cols)
            for c in t_cols: df[c] = df[c].astype(int)
            df['Tarih_DT'] = pd.NaT
            df = df.iloc[::-1].reset_index(drop=True)

        elif kod == "sanstopu":
            df_raw = pd.read_excel(dosya, header=None) if dosya.endswith('.xlsx') else pd.read_csv(dosya, sep=None,
                                                                                                   engine='python',
                                                                                                   header=None)
            clean_rows = []
            for idx, row in df_raw.iterrows():
                val0, val1 = str(row[0]).strip(), str(row[1]).strip() if len(row) > 1 else ""
                if val0 in ['Tarih', 'nan', 'None'] or (
                        val0.isdigit() and len(val0) == 4 and (len(row) <= 2 or pd.isna(row[2]))):
                    continue
                if val1 == 'Hft': continue
                try:
                    nums = [int(float(row[i])) for i in range(2, 8)]
                    t1_5, arti = nums[:5], nums[5]
                    if all(1 <= x <= 34 for x in t1_5) and (1 <= arti <= 14) and len(set(t1_5)) == 5:
                        clean_rows.append(
                            [row[0], int(float(row[1])) if str(row[1]).replace('.0', '').isdigit() else 0] + sorted(
                                t1_5) + [arti])
                except:
                    pass
            df = pd.DataFrame(clean_rows, columns=['Tarih', 'Hft'] + t_cols + ['Arti'])
            df['Tarih_DT'] = pd.to_datetime(df['Tarih'], format='mixed', dayfirst=True, errors='coerce')
            df = df.sort_values('Tarih_DT').reset_index(drop=True)

        df['Toplam'] = df[t_cols].sum(axis=1)
        draws = df[t_cols].values.tolist()
        num_draws = len(draws)
        all_numbers = [num for draw in draws for num in draw if 1 <= num <= max_n]
        counts = Counter(all_numbers)

        median_freq = np.median(list(counts.values())) if counts else 0
        spins = {i: 1 if counts.get(i, 0) > median_freq else -1 for i in range(1, max_n + 1)}

        mean_f = np.mean(list(counts.values())) if counts else 1
        std_f = np.std(list(counts.values())) if (counts and np.std(list(counts.values())) > 0) else 1
        gff_h = {k: (counts.get(k, 0) - mean_f) / std_f for k in range(1, max_n + 1)}

        pair_counts = Counter()
        for draw in draws: pair_counts.update(combinations(sorted(draw), 2))
        perc_thresh = int(np.percentile(list(pair_counts.values()), 94)) if pair_counts else 10

        appearances = {i: [] for i in range(1, max_n + 1)}
        for idx, draw in enumerate(draws):
            for num in draw:
                if 1 <= num <= max_n: appearances[num].append(idx)
        all_gaps = []
        for num, app in appearances.items():
            if len(app) > 1: all_gaps.extend(np.diff(app))
        t_c_95 = np.percentile(all_gaps, 95) if all_gaps else 20
        current_sleep = {num: (num_draws - 1) - (app[-1] if len(app) > 0 else 0) for num, app in appearances.items()}
        faz_bankolari = [k for k, v in current_sleep.items() if v >= t_c_95]

        h = np.zeros(max_n)
        for draw in draws:
            for num in draw:
                if 1 <= num <= max_n: h[num - 1] += 1
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
                if 1 <= val <= 14: a_last[val] = idx
            ekstra["arti_sleep"] = {i: (num_draws - 1 - a_last[i]) for i in range(1, 15)}
            ekstra["arti_counts"] = dict(Counter(arti_list))

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
            max_n = cfg["max_sayi"]
            k_arsiv = cfg["arsiv_top_sayisi"]
            beklenen_dongu = max_n / k_arsiv

            sleeps = paket["current_sleep"]
            gff = paket["gff_h"]
            for num in range(1, max_n + 1):
                norm_uyku = sleeps.get(num, 0) / beklenen_dongu
                sogukluk = -gff.get(num, 0)
                evrensel_basinc[num] += (norm_uyku * 1.5) + sogukluk
                katilim_sayisi[num] += 1

    for num in range(1, 91):
        if katilim_sayisi[num] > 0:
            evrensel_basinc[num] = round(evrensel_basinc[num] / katilim_sayisi[num], 3)

    return evrensel_basinc, yuklenen_evrenler


# -------------------------------------------------------------------------
# DİNAMİK GIANELLA SARKAÇ MOTORU (SON 80 ÇEKİLİŞ ANALİZİ - TÜM OYUNLAR)
# -------------------------------------------------------------------------
@st.cache_data(ttl=60)
def dinamik_gianella_havuz_analizi(oyun_adi, pencere=80):
    """
    Son 80 çekilişi analiz eder. Her oyunun kendi dekad/grup yapısına ve tek/çift
    simetrisine tam uyumlu (Gianella Dengeli) kombinasyon uzayını tarayarak;
    son 80 çekilişte en çok 'baskı biriktirmiş' (sarkaç potansiyeli en yüksek)
    Havuz A'yı (max_sayi // 2) ve onun simetrik karşılığı Havuz B'yi tespit eder.
    """
    paket = evren_verisini_yukle(oyun_adi)
    cfg = OYUN_EVRENLERI[oyun_adi]
    max_n = cfg["max_sayi"]
    k_arsiv = cfg["arsiv_top_sayisi"]
    yari_boyut = max_n // 2

    if paket is None or len(paket["draws"]) == 0:
        orta = max_n // 2
        return {
            "havuz_a": list(range(1, orta + 1)),
            "havuz_b": list(range(orta + 1, max_n + 1)),
            "olasilik_a": 50.0, "olasilik_b": 50.0,
            "a_top_sayisi": 0, "b_top_sayisi": 0, "beklenen_top": 0,
            "pencere": pencere, "z_skoru": 0.0, "seri_baski": 0
        }

    draws = paket["draws"]
    son_cekilisler = draws[-min(pencere, len(draws)):]
    gercek_pencere = len(son_cekilisler)
    current_sleep = paket["current_sleep"]
    evrensel_basinc, _ = mutlak_kuantum_alani_hesapla()

    # 1. Son 80 çekilişte her sayının frekansını ve beklenen ortalamadan sapmasını hesapla
    pencere_sayaci = Counter(num for d in son_cekilisler for num in d if 1 <= num <= max_n)
    beklenen_bireysel = (gercek_pencere * k_arsiv) / max_n
    std_bireysel = np.sqrt(gercek_pencere * (k_arsiv / max_n) * (1.0 - (k_arsiv / max_n)))
    if std_bireysel <= 0:
        std_bireysel = 1.0

    # Bireysel Sarkaç Baskı Skoru (Az çıkan + uzun süredir uyuyan + evrensel basıncı yüksek olan)
    baski_skoru = {}
    for n in range(1, max_n + 1):
        acik = beklenen_bireysel - pencere_sayaci.get(n, 0)
        z_acik = acik / std_bireysel
        uyku_norm = current_sleep.get(n, 0) / (max_n / k_arsiv)
        evr_katki = evrensel_basinc.get(n, 0) * 0.35
        baski_skoru[n] = (z_acik * 2.2) + (uyku_norm * 1.15) + evr_katki

    # 2. Dekad (Onluk Grup) bazında Gianella Dengeli Havuz A İnşası
    # Her dekaddan tam yarısı kadar sayı seçilir ve toplam Tek/Çift eşitliği korunur.
    dekad_gruplari = {}
    for n in range(1, max_n + 1):
        d = onluk_grup_bul(n)
        dekad_gruplari.setdefault(d, []).append(n)

    havuz_a = []
    artik_havuz = []

    for d, sayilar in sorted(dekad_gruplari.items()):
        sirali_d = sorted(sayilar, key=lambda x: baski_skoru[x], reverse=True)
        grup_uzunluk = len(sayilar)

        if grup_uzunluk % 2 == 0:
            hedef_k = grup_uzunluk // 2
            tekler = [x for x in sirali_d if x % 2 != 0]
            ciftler = [x for x in sirali_d if x % 2 == 0]
            # Gianella Tek/Çift simetrisi için her 10'luktan 2-3 tek ve 2-3 çift al
            t_al = hedef_k // 2
            c_al = hedef_k // 2
            secilen_d = tekler[:t_al] + ciftler[:c_al]
            kalan_d = [x for x in sirali_d if x not in secilen_d]
            while len(secilen_d) < hedef_k and kalan_d:
                secilen_d.append(kalan_d.pop(0))
            havuz_a.extend(secilen_d)
        else:
            # Şans Topu (31-34 arası 4 sayı çift, ama olası tek sayıda grup kalırsa)
            artik_havuz.extend(sirali_d)

    if len(havuz_a) < yari_boyut and artik_havuz:
        eksik = yari_boyut - len(havuz_a)
        havuz_a.extend(sorted(artik_havuz, key=lambda x: baski_skoru[x], reverse=True)[:eksik])

    # Genel Tek / Çift Simetri Düzeltmesi (Tam %50 Tek - %50 Çift Gianella Kuralı)
    havuz_a = sorted(havuz_a[:yari_boyut])
    havuz_b = sorted(list(set(range(1, max_n + 1)) - set(havuz_a)))

    hedef_tek = yari_boyut // 2
    mevcut_tek = sum(1 for x in havuz_a if x % 2 != 0)

    while mevcut_tek > hedef_tek:
        # Havuz A'daki en düşük baskılı Tek sayıyı, Havuz B'deki en yüksek baskılı Çift sayıyla aynı dekadda takas et
        a_tekler = sorted([x for x in havuz_a if x % 2 != 0], key=lambda x: baski_skoru[x])
        b_ciftler = sorted([x for x in havuz_b if x % 2 == 0], key=lambda x: baski_skoru[x], reverse=True)
        if not a_tekler or not b_ciftler:
            break
        cikar = a_tekler[0]
        ekle = next((y for y in b_ciftler if onluk_grup_bul(y) == onluk_grup_bul(cikar)), b_ciftler[0])
        havuz_a.remove(cikar); havuz_b.append(cikar)
        havuz_b.remove(ekle); havuz_a.append(ekle)
        mevcut_tek -= 1

    while mevcut_tek < hedef_tek:
        a_ciftler = sorted([x for x in havuz_a if x % 2 == 0], key=lambda x: baski_skoru[x])
        b_tekler = sorted([x for x in havuz_b if x % 2 != 0], key=lambda x: baski_skoru[x], reverse=True)
        if not a_ciftler or not b_tekler:
            break
        cikar = a_ciftler[0]
        ekle = next((y for y in b_tekler if onluk_grup_bul(y) == onluk_grup_bul(cikar)), b_tekler[0])
        havuz_a.remove(cikar); havuz_b.append(cikar)
        havuz_b.remove(ekle); havuz_a.append(ekle)
        mevcut_tek += 1

    havuz_a = sorted(havuz_a)
    havuz_b = sorted(havuz_b)
    set_a = set(havuz_a)

    # 3. Son 80 Çekiliş Üzerinde Havuz A ve Havuz B Performans & Seri Testi
    a_top_toplam = 0
    b_top_toplam = 0
    b_ustun_seri = 0

    for d in son_cekilisler:
        a_bu_cekilis = sum(1 for num in d if num in set_a)
        b_bu_cekilis = len(d) - a_bu_cekilis
        a_top_toplam += a_bu_cekilis
        b_top_toplam += b_bu_cekilis

    # Son çekilişlerde Havuz B'nin üst üste baskın gelme serisi (Yazı-Tura serisi)
    for d in reversed(son_cekilisler):
        a_c = sum(1 for num in d if num in set_a)
        if (len(d) - a_c) >= a_c:
            b_ustun_seri += 1
        else:
            break

    toplam_top = a_top_toplam + b_top_toplam
    beklenen_yarim = toplam_top / 2.0
    std_toplam = np.sqrt(toplam_top * 0.5 * 0.5) if toplam_top > 0 else 1.0
    z_fark = (b_top_toplam - a_top_toplam) / (2.0 * std_toplam)

    # Sarkaç Olasılık Hesabı (Açık farkı + Seri bonusu -> Sigmoid projeksiyonu)
    seri_etkisi = min(12.0, b_ustun_seri * 1.8)
    olasilik_a = 50.0 + min(34.0, max(4.0, z_fark * 6.8 + seri_etkisi))
    olasilik_b = 100.0 - olasilik_a

    return {
        "havuz_a": havuz_a,
        "havuz_b": havuz_b,
        "olasilik_a": round(olasilik_a, 1),
        "olasilik_b": round(olasilik_b, 1),
        "a_top_sayisi": a_top_toplam,
        "b_top_sayisi": b_top_toplam,
        "beklenen_top": int(beklenen_yarim),
        "pencere": gercek_pencere,
        "z_skoru": round(z_fark, 2),
        "seri_baski": b_ustun_seri,
        "baski_skoru": baski_skoru
    }


# -------------------------------------------------------------------------
# 3x3 MARKOV BANT GEÇİŞ MATRİSİ & SARKAÇ RADARI
# -------------------------------------------------------------------------
def bant_radari_hesapla(df, cfg):
    """
    Arşivdeki tüm çekilişlerden 3x3 Markov Bant Geçiş Matrisini (Alt -> Orta -> Üst)
    ve son 25 çekilişin sarkaç momentumunu birleştirerek bant olasılıklarını hesaplar.
    """
    if df is None or len(df) < 20:
        return "Orta", "Ust", {"Alt": 33.3, "Orta": 33.4, "Ust": 33.3}, {}
    b_alt, b_ust = cfg["bant_alt"], cfg["bant_ust"]

    def get_bant(t):
        return 'Alt' if t <= b_alt else ('Ust' if t >= b_ust else 'Orta')

    tum_bantlar = df['Toplam'].apply(get_bant).tolist()
    bant_isimleri = ['Alt', 'Orta', 'Ust']

    # 1. 3x3 Markov Geçiş Matrisi Hesabı
    gecis_sayaci = {b1: {b2: 1 for b2 in bant_isimleri} for b1 in bant_isimleri}  # Laplace smoothing
    for i in range(len(tum_bantlar) - 1):
        onceki, sonraki = tum_bantlar[i], tum_bantlar[i + 1]
        gecis_sayaci[onceki][sonraki] += 1

    markov_matrisi = {}
    for b1 in bant_isimleri:
        satir_top = sum(gecis_sayaci[b1].values())
        markov_matrisi[b1] = {b2: (gecis_sayaci[b1][b2] / satir_top) * 100.0 for b2 in bant_isimleri}

    son_durum = tum_bantlar[-1]
    markov_beklentisi = markov_matrisi[son_durum]

    # 2. Son 20 Çekiliş Sarkaç Dengesi
    son_20 = tum_bantlar[-20:]
    counts = Counter(son_20)
    actual = {'Alt': counts.get('Alt', 0), 'Orta': counts.get('Orta', 0), 'Ust': counts.get('Ust', 0)}
    diff = {k: 6.66 - actual[k] for k in actual}

    son_bantlar_ters = son_20[::-1]
    aktif_seri = son_bantlar_ters[0]
    seri_sayisi = 0
    for b in son_bantlar_ters:
        if b == aktif_seri:
            seri_sayisi += 1
        else:
            break

    sarkac_p = {k: max(5.0, 33.33 + diff[k] * 3.2) for k in actual}
    if seri_sayisi >= 3:
        sarkac_p[aktif_seri] = max(5.0, sarkac_p[aktif_seri] - (seri_sayisi * 3.5))

    # %55 Sarkaç + %45 Markov Geçiş Olasılığı Hibrit Füzyonu
    hibrit_p = {k: (sarkac_p[k] * 0.55) + (markov_beklentisi[k] * 0.45) for k in bant_isimleri}
    t_raw = sum(hibrit_p.values())
    final_p = {k: (v / t_raw) * 100.0 for k, v in hibrit_p.items()}
    sirali_bantlar = sorted(final_p, key=final_p.get, reverse=True)

    return sirali_bantlar[0], sirali_bantlar[1], final_p, markov_matrisi

# =========================================================================
# QUANT LOTO V23.5 — PARÇA 2 / 3
# EKSİK ÇEKİLİŞ KAPISI, FİZİK & TOPOLOJİ MOTORU, 28 FİLTRELİ ÇİFT KADEMELİ
# HUNİ (DOUBLE-GATE PIPELINE), 3 SÜPER HAVUZ & GIANELLA ÜRETİM MOTORU
# =========================================================================

def eksik_cekilisleri_kontrol_et(oyun_adi, paket):
    cfg = OYUN_EVRENLERI[oyun_adi]
    df = paket["df"]
    bugun = datetime.date.today()

    if df['Tarih_DT'].notna().sum() > 0:
        son_tarih = df['Tarih_DT'].max().date()
        eksik_tarihler = []
        gun_farki = (bugun - son_tarih).days
        if gun_farki > 0:
            for d in range(1, gun_farki + 1):
                kontrol_gunu = son_tarih + datetime.timedelta(days=d)
                if kontrol_gunu.weekday() in cfg["cekilis_gunleri"]:
                    eksik_tarihler.append(kontrol_gunu.strftime("%d.%m.%Y"))
        return son_tarih.strftime("%d.%m.%Y"), eksik_tarihler
    else:
        son_yil = int(df.iloc[-1].get('Yil', bugun.year))
        son_hft = int(df.iloc[-1].get('Hft', 0))
        yilin_gunu = bugun.timetuple().tm_yday
        tahmini_aktif_hft = int((yilin_gunu / 7) * len(cfg["cekilis_gunleri"]))
        eksik_haftalar = []
        if son_yil == bugun.year and tahmini_aktif_hft > son_hft:
            eksik_haftalar = [f"{son_yil} - {h}. Hafta" for h in range(son_hft + 1, tahmini_aktif_hft + 1)]
        return f"{son_yil} / {son_hft}. Hafta", eksik_haftalar


def yeni_cekilis_ekle(oyun_adi, paket, tarih_str, hft_no, sayilar_listesi):
    dosya = paket["dosya"]
    kod = OYUN_EVRENLERI[oyun_adi]["kod"]
    try:
        if dosya.endswith('.csv'):
            with open(dosya, 'r', encoding='utf-8', errors='ignore') as f:
                icerik = f.readlines()
            sep = ';' if ';' in icerik[1] else ','
            if kod == "onnumara":
                yeni_satir = f"{hft_no}" + sep + sep.join(str(x) for x in sorted(sayilar_listesi)) + "\n"
                for i, l in enumerate(icerik):
                    if l.startswith('Hft'):
                        icerik.insert(i + 1, yeni_satir)
                        break
                with open(dosya, 'w', encoding='utf-8') as f:
                    f.writelines(icerik)
            else:
                yeni_satir = f"\n{tarih_str}{sep}" + sep.join(str(x) for x in sayilar_listesi)
                with open(dosya, 'a', encoding='utf-8') as f:
                    f.write(yeni_satir)
        else:
            df_mevcut = pd.read_excel(dosya)
            yeni_veri = [tarih_str] + sayilar_listesi
            if len(df_mevcut.columns) == len(yeni_veri) + 1:
                yeni_veri = [tarih_str, hft_no] + sayilar_listesi
            yeni_df = pd.DataFrame([yeni_veri[:len(df_mevcut.columns)]], columns=df_mevcut.columns)
            df_guncel = pd.concat([df_mevcut.iloc[:1], yeni_df, df_mevcut.iloc[1:]], ignore_index=True)
            df_guncel.to_excel(dosya, index=False)

        # Yeni veri girildiğinde tüm önbelleği ve sarkaç analizlerini sıfırla (Madde 5)
        st.cache_data.clear()
        for k in list(st.session_state.keys()):
            if k.startswith("tohum_") or k.startswith("v23_uretim_"):
                del st.session_state[k]
        return True, "✅ Çekiliş başarıyla veritabanına işlendi ve tüm Gianella/Markov hesaplamaları güncellendi!"
    except PermissionError:
        return False, f"⚠️ '{dosya}' şu anda Excel'de açık! Lütfen Excel programını kapatıp tekrar 'Kaydet' butonuna basın."
    except Exception as e:
        return False, f"Kayıt sırasında hata: {e}"


# -------------------------------------------------------------------------
# FİZİK, TOPOLOJİ, MAHALANOBİS, HOLOGRAFİK GÖLGE & MARKOV YARDIMCILARI
# -------------------------------------------------------------------------
def get_coord(num, grid_w):
    return ((num - 1) % grid_w, (num - 1) // grid_w)


def calc_walk_len(kolon, grid_w):
    return sum(euclidean(get_coord(kolon[i], grid_w), get_coord(kolon[i + 1], grid_w)) for i in range(len(kolon) - 1))


def poly_area(coords):
    x, y = [c[0] for c in coords], [c[1] for c in coords]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def get_cluster_density(kolon, grid_w):
    coords = [get_coord(n, grid_w) for n in kolon]
    xs, ys = [c[0] for c in coords], [c[1] for c in coords]
    area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
    return len(kolon) / area if area > 0 else 0


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
        dis, orta = kolon[4] - kolon[0], kolon[3] - kolon[1]
        cek = min(kolon[2] - kolon[1], kolon[3] - kolon[2])
    if orta <= 0 or cek <= 0:
        return 999.0, 999.0
    return dis / orta, orta / cek


def get_rmt_stats(kolon):
    k_len = len(kolon)
    M = np.zeros((k_len, k_len))
    for i in range(k_len):
        for j in range(k_len):
            M[i, j] = kolon[i] if i == j else np.sqrt(abs(kolon[i] - kolon[j]))
    eigs = np.linalg.eigvalsh(M)
    return eigs[-1], (eigs[-1] - eigs[-2])


def get_chatterjee_energy(kolon):
    k_len = len(kolon)
    energy = sum(MASTER_CHATTERJEE_J[kolon[i] - 1, kolon[j] - 1] for i in range(k_len) for j in range(i + 1, k_len))
    return energy / np.sqrt(k_len)


def is_percolated(kolon, pair_counts, perc_thresh):
    if not pair_counts:
        return False
    subG = nx.Graph()
    subG.add_nodes_from(kolon)
    valid_edges = [(u, v) for u, v in combinations(kolon, 2) if pair_counts.get((u, v), 0) >= perc_thresh]
    subG.add_edges_from(valid_edges)
    return nx.is_connected(subG)


def calc_antipodal_pairs(kolon, max_n):
    """3D Küre Antipodal Ayna Çifti sayısı (x + y == max_n + 1)"""
    k_set = set(kolon)
    return sum(1 for x in kolon if (max_n + 1 - x) in k_set and x < (max_n + 1 - x))


def calc_holographic_shadow_mean(kolon, max_n):
    """10/22 Holografik Gölge Kalkanı: Kupon dışındaki gölge sayıların ortalaması"""
    toplam_evren = max_n * (max_n + 1) / 2.0
    golge_toplam = toplam_evren - sum(kolon)
    return golge_toplam / (max_n - len(kolon))


def calc_harmonic_grid_resonance(kolon, max_n):
    """Harmonik Izgara Rezonansı (Delta): Küresel uzay adımlarıyla uyum"""
    k_len = len(kolon)
    ideal_adim = max_n / (k_len + 1.0)
    adimlar = [kolon[i + 1] - kolon[i] for i in range(k_len - 1)]
    return np.mean([abs(a - ideal_adim) for a in adimlar]) / ideal_adim


def calc_spatial_markov_jump_ok(kolon, max_n):
    """Uzaysal Markov Sıra-İstatistiği Geçişi: Chebyshev sıçrama varyansı denetimi"""
    k_len = len(kolon)
    beklenen_sicrama = max_n / (k_len + 1.0)
    sicramalar = [kolon[0]] + [kolon[i + 1] - kolon[i] for i in range(k_len - 1)] + [max_n + 1 - kolon[-1]]
    std_sicrama = np.std(sicramalar)
    return 0.32 * beklenen_sicrama <= std_sicrama <= 1.65 * beklenen_sicrama


def calc_mahalanobis_d2_ok(kolon, max_n):
    """Mahalanobis Kovaryans Matrisi (D^2): Sıra istatistiklerinin teorik pozisyonel sapması"""
    k_len = len(kolon)
    d2_top = 0.0
    for idx, val in enumerate(kolon, 1):
        p = idx / (k_len + 1.0)
        mu_i = p * (max_n + 1.0)
        var_i = (idx * (k_len - idx + 1.0) * (max_n + 1.0) * (max_n - k_len)) / (((k_len + 1.0) ** 2) * (k_len + 2.0))
        if var_i > 0:
            d2_top += ((val - mu_i) ** 2) / var_i
    d2_norm = d2_top / k_len
    return 0.15 <= d2_norm <= 2.45


# -------------------------------------------------------------------------
# 28 FİLTRELİ ÇİFT KADEMELİ HUNİ (DOUBLE-GATE PIPELINE - V23.5)
# -------------------------------------------------------------------------
def cift_kademeli_28_filtre_denetimi(kolon, cfg, paket, mode="mod4", hedefler=None, bant_tipi="Orta",
                                     altin_kesi_aktif=True, esnek_tolerans=False, tek_havuz_modu=False):
    """
    A. Temel İstatistiksel ve Fiziksel Süzgeçler (1-8)
    B. Modüler, Simetri ve Gecikme Süzgeçleri (9-12)
    C. Holografik, Kuantum Alan ve Markov Süzgeçleri (13-28)
    olmak üzere 28 kuralı denetler.
    """
    k_len = len(kolon)
    max_n = cfg["max_sayi"]
    toplam = sum(kolon)
    sinir_tipi = "mod4" if mode == "makro" else ("mod5" if mode == "mod3" else mode)
    s = cfg["sinirlar"][sinir_tipi]
    bant_aktif_mi = hedefler is not None
    ihlal_sayisi = 0
    izinli_ihlal = (2 if tek_havuz_modu else 1) if esnek_tolerans else (1 if tek_havuz_modu else 0)

    # --- A. TEMEL İSTATİSTİKSEL VE FİZİKSEL SÜZGEÇLER ---
    # 1 & 2. CLT Gauss Toplam Bandı & Renkli 3 Bant Kısıtı (P33 / P66)
    if hedefler:
        gec_bant = any(h_min <= toplam <= h_max for (h_min, h_max) in hedefler)
    elif altin_kesi_aktif:
        ak_min, ak_max = cfg["altin_kesi"]
        gec_bant = (ak_min <= toplam <= ak_max)
    else:
        gec_bant = True
    if not gec_bant:
        return False  # Seçilen hedef bant kilitlidir, esnetilmez

    # 3. İsing Tek/Çift Dengesi
    if sum(1 for n in kolon if n % 2 != 0) not in cfg["tek_aralik"]:
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 4. İsing Alt/Üst Yarı Dengesi
    dusuk_sayisi = sum(1 for n in kolon if n <= max_n // 2)
    izinli_yari = cfg["alt_yari_sart"].get(bant_tipi, cfg["alt_yari_sart"]["Orta"])
    if dusuk_sayisi not in izinli_yari:
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 5, 6, 7. Paul Lévy Maksimum Boşluk, Yayılım, Standart Sapma & RMT Ardışık Çift Sınırı
    bosluklar = [kolon[i + 1] - kolon[i] - 1 for i in range(k_len - 1)]
    ardisik_cift = bosluklar.count(0)
    yay_min, yay_max = cfg["yayilim_aralik"]
    std_min, std_max = cfg["std_aralik"]
    if (max(bosluklar) > cfg["max_bosluk"] or
            ardisik_cift > cfg.get("ardisik_max", 2) or
            not (yay_min <= kolon[-1] - kolon[0] <= yay_max) or
            not (std_min <= np.std(kolon) <= std_max)):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 8. Poisson Onluk Blok Sınırları ve Yayılımı + Mod-10 Sınırı
    dekad_sayaci = Counter(onluk_grup_bul(n) for n in kolon)
    max_dekad_ici = 3 if k_len == 10 else 2
    if (len(dekad_sayaci) not in cfg["dekad_aralik"] or
            max(dekad_sayaci.values()) > max_dekad_ici or
            max(Counter(n % 10 for n in kolon).values()) > cfg["mod10_max"]):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # --- B. MODÜLER, SİMETRİ VE GECİKME SÜZGEÇLERİ ---
    # 9. Asal Sayı Rezonansı
    asallar = {p for p in ASAL_TUM if p <= max_n}
    if sum(1 for n in kolon if n in asallar) not in cfg["asal_aralik"]:
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 10. Fermat Mod-7 ve Mod-9 (Dijital Kök) Homojenliği
    mod7_max = 3 if k_len == 10 else 2
    mod9_max = 3 if k_len == 10 else 2
    if (max(Counter(n % 7 for n in kolon).values()) > mod7_max or
            max(Counter(dijital_kok(n) for n in kolon).values()) > mod9_max):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 11. 3D Küre Antipodal Ayna Çifti Sınırı
    max_ayna = 2 if k_len == 10 else 1
    if calc_antipodal_pairs(kolon, max_n) > max_ayna:
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 12. Poisson Gecikme (Lag) & Soğuk Sayı Tavanı + Çift Katmanlı KPZ Yüzeyi
    t_c_95 = paket.get("t_c_95", 20)
    sleeps = paket["current_sleep"]
    asiri_soguk_adedi = sum(1 for n in kolon if sleeps.get(n, 0) >= t_c_95)
    max_soguk_tavan = 3 if k_len == 10 else 2
    zirveler = paket["zirveler"] | paket["kpz_zirveler"]
    vadiler = paket["vadiler"] | paket["kpz_vadiler"]
    max_zirve = 4 if k_len == 10 else 2
    if (asiri_soguk_adedi > max_soguk_tavan or
            (zirveler and sum(1 for n in kolon if n in zirveler) > max_zirve) or
            (vadiler and sum(1 for n in kolon if n in vadiler) < 1)):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 13. Mahalanobis Kovaryans Matrisi (D^2)
    if not calc_mahalanobis_d2_ok(kolon, max_n):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    if mode == "makro":
        return True

    # --- C. HOLOGRAFİK, KUANTUM FİZİK VE MARKOV SÜZGEÇLERİ ---
    # 14 & 15. Evrensel Phi-Kütle Oranı, Fraktal Denge & Matruşka Kabuk Dengesi (Q1-Q3)
    if k_len == 5:
        H1, H2 = kolon[0] + kolon[1], kolon[3] + kolon[4]
        yorungeler = [kolon[0] + kolon[4], kolon[1] + kolon[3], 2 * kolon[2]]
    else:
        yari = k_len // 2
        H1, H2 = sum(kolon[:yari]), sum(kolon[yari:])
        yorungeler = [kolon[i] + kolon[k_len - 1 - i] for i in range(yari)]

    if H1 == 0 or toplam == 0:
        return False
    h2_oran = H2 / toplam
    fraktal = H2 / H1
    gec_7 = (s["h2_oran"][0] <= h2_oran <= s["h2_oran"][1]) and (s["fraktal"][0] <= fraktal <= s["fraktal"][1])
    mat1, mat2 = calc_matruska(kolon)
    gec_8 = (max(yorungeler) - min(yorungeler)) <= s["sapma"] and (s["mat1"][0] <= mat1 <= s["mat1"][1]) and (
                s["mat2"][0] <= mat2 <= s["mat2"][1])
    if not (gec_7 and gec_8):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 16, 17, 18. Holografik Gölge Kalkanı, Harmonik Izgara Rezonansı & Uzaysal Markov Sıra-İstatistiği
    golge_ort = calc_holographic_shadow_mean(kolon, max_n)
    ideal_ort = (max_n + 1.0) / 2.0
    harmonik_delta = calc_harmonic_grid_resonance(kolon, max_n)
    if (abs(golge_ort - ideal_ort) > ideal_ort * 0.14 or
            not (0.20 <= harmonik_delta <= 0.95) or
            not calc_spatial_markov_jump_ok(kolon, max_n)):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 19 & 20. İsing Manyetik Spin Dengesi & Smirnov Spin Akısı (Domain Wall)
    spins = paket["spins"]
    manyetik = sum(spins[n] for n in kolon)
    flux = get_spin_flux(kolon, spins)
    if (manyetik not in s["spin"]) or (flux not in s["flux"]):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 21, 22, 23. SAW Yürüyüş, Werner SLE Kıvrımlılık & Werner CLE Döngü Alanı
    grid_w = cfg["grid_w"]
    walk_len = calc_walk_len(kolon, grid_w)
    coords = [get_coord(n, grid_w) for n in kolon]
    C = euclidean(coords[0], coords[-1])
    tort = walk_len / C if C > 0 else 999
    cle_area = poly_area(coords)
    if not (s["walk"][0] <= walk_len <= s["walk"][1]) or not (s["tort"][0] <= tort <= s["tort"][1]) or not (
            s["cle"][0] <= cle_area <= s["cle"][1]):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 24 & 25. Smirnov Küme Yoğunluğu & Sheffield LQG Kütlesi
    dens = get_cluster_density(kolon, grid_w)
    gff_h = paket["gff_h"]
    lqg_mass = sum(np.exp(0.5 * gff_h.get(n, 0)) for n in kolon)
    if not (s["dens"][0] <= dens <= s["dens"][1]) or not (s["lqg"][0] <= lqg_mass <= s["lqg"][1]):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    # 26, 27, 28. Guionnet RMT, Evrensel Lambda_U Birlik Sabiti & Chatterjee Spin Camı Enerjisi
    max_eig, rmt_gap = get_rmt_stats(kolon)
    lambda_u = max_eig / (kolon[-1] + 0.42 * np.sqrt(k_len * max_n))
    sk_energy = get_chatterjee_energy(kolon)
    gec_rmt = (s["lambda_u"][0] <= lambda_u <= s["lambda_u"][1]) and (
                s["gap"][0] * 0.85 <= rmt_gap <= s["gap"][1] * 1.15)
    gec_sk = (s["sk"][0] <= sk_energy <= s["sk"][1])
    if not (gec_rmt and gec_sk):
        ihlal_sayisi += 1
        if ihlal_sayisi > izinli_ihlal: return False

    return True


# -------------------------------------------------------------------------
# 3 BAĞIMSIZ SÜPER HAVUZ & 12 ZAMAN ÇİZGİSİ TOHUM MOTORU
# -------------------------------------------------------------------------
def kozmik_tohum_uret(oyun_adi, paket, mutlak_alan_aktif=True, zorla_yenile=False, aktif_alt_havuz=None):
    """
    Seçilen Gianella havuzu (veya tam evren) içinde:
    1. Havuz (Kinetik Momentum & Trend)
    2. Havuz (Topolojik & Küresel Simetri)
    3. Havuz (Ergodik Sıçrama & Kaos / 12 Paralel Evren)
    olmak üzere 3 Süper Havuzun kesişiminden çekirdek Banko ve Mıknatıslı Hedge toplarını üretir.
    """
    cfg = OYUN_EVRENLERI[oyun_adi]
    max_n = cfg["max_sayi"]
    k_arsiv = cfg["arsiv_top_sayisi"]
    banko_adedi = cfg.get("banko_adedi", 1)
    hedge_boyutu = cfg.get("hedge_havuz_boyutu", 6)

    gecerli_sayilar = set(aktif_alt_havuz) if aktif_alt_havuz else set(range(1, max_n + 1))

    df = paket["df"]
    current_sleep = paket["current_sleep"]
    faz_bankolari = set(paket["faz_bankolari"])
    pair_counts = paket["pair_counts"]
    counts = paket["counts"]

    t_cols = [f"T{i}" for i in range(1, k_arsiv + 1)]
    max_idx = len(df) - 1

    evren_adimlari = {
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

    decade_counts = {i: 0 for i in range((max_n - 1) // 10 + 1)}
    evren_sogukluk_sayaci = Counter()

    for evren_adi, adimlar in evren_adimlari.items():
        gorulenler = set()
        gecerli_adim = 0
        for l in adimlar:
            if max_idx - l >= 0:
                gecerli_adim += 1
                cekilis_seti = set(df.iloc[max_idx - l][t_cols])
                gorulenler.update(cekilis_seti)
                for num in cekilis_seti:
                    if 1 <= num <= max_n:
                        decade_counts[onluk_grup_bul(num)] += 1
        if gecerli_adim > 0:
            bu_evrende_cikmayanlar = gecerli_sayilar - gorulenler
            for n in bu_evrende_cikmayanlar:
                evren_sogukluk_sayaci[n] += 1

    en_ezik_dekad = min(decade_counts, key=decade_counts.get)
    ezik_havuz = set(range(en_ezik_dekad * 10 + 1, min(max_n + 1, en_ezik_dekad * 10 + 11)))
    evrensel_skor, _ = mutlak_kuantum_alani_hesapla()

    # 3 Süper Havuzun Birleşik Skorlaması
    ham_skor = {}
    beklenen_periyot = max_n / k_arsiv
    for n in gecerli_sayilar:
        # Süper Havuz 3: Ergodik Sıçrama & 12 Paralel Evren Soğukluğu
        evren_puani = evren_sogukluk_sayaci.get(n, 0) * 1.65
        uyku_puani = current_sleep.get(n, 0) / beklenen_periyot
        faz_bonus = 1.6 if n in faz_bankolari else 0.0
        # Süper Havuz 1: Kinetik Momentum & Poisson Rezonansı
        poisson_rezonans = 1.25 if 0.8 <= uyku_puani <= 1.8 else 0.0
        # Süper Havuz 2: Topolojik & Dekad Simetrisi
        ezik_bonus = 0.9 if n in ezik_havuz else 0.0
        alan_bonus = (evrensel_skor.get(n, 0) * 1.4) if mutlak_alan_aktif else 0.0
        ham_skor[n] = evren_puani + uyku_puani + faz_bonus + poisson_rezonans + ezik_bonus + alan_bonus

    sirali_tum = sorted(ham_skor, key=ham_skor.get, reverse=True)
    bankolar = sorted(sirali_tum[:banko_adedi])

    # İkili Perkolasyon Çapası (Seçilen Gianella havuzu içindeki en güçlü bağlar)
    max_pair_val = max(pair_counts.values()) if pair_counts else 1
    hedge_skor = {}
    aday_pencere = sirali_tum[banko_adedi:banko_adedi + min(18, len(sirali_tum) - banko_adedi)]
    for n in aday_pencere:
        bag_puani = sum(pair_counts.get(tuple(sorted((b, n))), 0) for b in bankolar) / max(1, max_pair_val)
        hedge_skor[n] = ham_skor[n] + (bag_puani * 3.5)

    diger_karanliklar = sorted(hedge_skor, key=hedge_skor.get, reverse=True)[:hedge_boyutu]

    ek_tohum = {
        "ezik_dekad": f"{en_ezik_dekad * 10 + 1}-{min(max_n, (en_ezik_dekad + 1) * 10)}",
        "aktif_evren_sayisi": 12
    }
    if cfg["kod"] == "sayisal":
        s_freqs = paket["ekstra"].get("super_freqs", {})
        j_freqs = paket["ekstra"].get("joker_freqs", {})
        sirali_super = sorted(range(1, 91), key=lambda x: (s_freqs.get(x, 0), -ham_skor.get(x, 0)))
        ek_tohum["super_havuz"] = sirali_super[:5]
        sirali_joker = sorted([x for x in range(1, 91) if x not in bankolar],
                              key=lambda x: (j_freqs.get(x, 0), -ham_skor.get(x, 0)))
        ek_tohum["joker_havuz"] = sirali_joker[:15]
    elif cfg["kod"] == "sanstopu":
        a_sleep = paket["ekstra"].get("arti_sleep", {})
        sirali_arti = sorted(range(1, 15), key=lambda x: (a_sleep.get(x, 0), -ham_skor.get(x, 0)), reverse=True)
        ek_tohum["arti_havuz"] = sirali_arti[:5]

    return bankolar, diger_karanliklar, ek_tohum


# -------------------------------------------------------------------------
# GIANELLA HAVUZUNDAN OPTİMAL KOLON ÜRETİM MOTORU (ÇİFT KADEMELİ HUNİ)
# -------------------------------------------------------------------------
def gianella_havuzundan_kolon_uret(alt_havuz_sayilari, aranan_adet, secilen_bantlar, aktif_cfg, aktif_paket,
                                   mutlak_alan_aktif, esnek_aktif, havuz_etiketi, onceden_secilen=None):
    """
    Seçilen Gianella havuzunu (Örn: 40 sayı) alır, kendi içinde 3 Süper Havuz tohumlarını
    çıkarır ve 28 Filtreli Çift Kademeli Huniden geçirerek istenen kolon sayısı kadar
    optimal dağılmış (Balanced Wheel) kupon üretir.
    """
    if aranan_adet <= 0:
        return [], [], [], {}

    k_boyut = aktif_cfg["kolon_boyutu"]
    bankolar, diger_karanliklar, ek_tohum = kozmik_tohum_uret(
         next(k for k, v in OYUN_EVRENLERI.items() if v["kod"] == aktif_cfg["kod"]),
        aktif_paket, mutlak_alan_aktif, zorla_yenile=True, aktif_alt_havuz=alt_havuz_sayilari
    )
    kalan_sayilar = list(set(alt_havuz_sayilari) - set(bankolar + diger_karanliklar))

    # Seçilen bantların toplam aralıklarını birleştir
    bant_araliklari = []
    if "Alt" in secilen_bantlar: bant_araliklari.append(aktif_cfg["kolon_bant_alt"])
    if "Orta" in secilen_bantlar: bant_araliklari.append(aktif_cfg["kolon_bant_orta"])
    if "Ust" in secilen_bantlar: bant_araliklari.append(aktif_cfg["kolon_bant_ust"])
    if not bant_araliklari:
        bant_araliklari = None
    ana_bant_tipi = secilen_bantlar[0] if len(secilen_bantlar) == 1 else "Orta"

    adaylar = []
    mevcut_kolonlar = [x["kolon"] for x in (onceden_secilen or [])]
    hedge_secim_adedi = [1, 2] if k_boyut == 10 else [0, 1]
    tek_havuz_mu = len(alt_havuz_sayilari) <= (aktif_cfg["max_sayi"] // 2)

    # AŞAMA 1: Katı 28 Filtre (Mod 4 & Mod 5 Hibrit Tarama)
    hedef_aday_havuzu = max(aranan_adet * 4, 80)
    for iter_idx in range(450000):
        if len(adaylar) >= hedef_aday_havuzu:
            break
        # Havuzun tamamının taranabilmesi için kolonların yarısında banko zorunlu, yarısında serbest çekirdek
        if iter_idx % 2 == 0 and len(bankolar) > 0:
            aktif_b = random.sample(bankolar, min(1, len(bankolar)))
        else:
            aktif_b = []
        kac_h = random.choice(hedge_secim_adedi)
        secilen_h = random.sample(diger_karanliklar, min(kac_h, len(diger_karanliklar)))
        cekirdek = aktif_b + secilen_h
        eksik = k_boyut - len(cekirdek)
        if eksik < 0 or len(kalan_sayilar) < eksik:
            continue
        aday = sorted(cekirdek + random.sample(kalan_sayilar, eksik))

        if aday not in mevcut_kolonlar and aday not in [x["kolon"] for x in adaylar]:
            aktif_mod = "mod4" if len(adaylar) < (hedef_aday_havuzu // 2) else "mod5"
            if cift_kademeli_28_filtre_denetimi(aday, aktif_cfg, aktif_paket, mode=aktif_mod,
                                                hedefler=bant_araliklari, bant_tipi=ana_bant_tipi,
                                                esnek_tolerans=esnek_aktif, tek_havuz_modu=tek_havuz_mu):
                is_gold = is_percolated(aday, aktif_paket["pair_counts"], aktif_paket["perc_thresh"])
                toplam_puan = sum(aday)
                b_etk = "Alt" if toplam_puan <= aktif_cfg["kolon_bant_alt"][1] else (
                    "Üst" if toplam_puan >= aktif_cfg["kolon_bant_ust"][0] else "Orta")
                adaylar.append({
                    "kolon": aday,
                    "etiket": f"{havuz_etiketi} [{b_etk}]",
                    "is_gold": is_gold
                })

    # AŞAMA 2: Çok dar bant veya yüksek kolon sayısında aday yetmezse esnek 27/28 toleransla tamamla
    if len(adaylar) < aranan_adet * 2:
        for _ in range(250000):
            if len(adaylar) >= aranan_adet * 2:
                break
            aday = sorted(random.sample(alt_havuz_sayilari, k_boyut))
            if aday not in mevcut_kolonlar and aday not in [x["kolon"] for x in adaylar]:
                if cift_kademeli_28_filtre_denetimi(aday, aktif_cfg, aktif_paket, mode="mod5",
                                                    hedefler=bant_araliklari, bant_tipi=ana_bant_tipi,
                                                    esnek_tolerans=True, tek_havuz_modu=True):
                    is_gold = is_percolated(aday, aktif_paket["pair_counts"], aktif_paket["perc_thresh"])
                    toplam_puan = sum(aday)
                    b_etk = "Alt" if toplam_puan <= aktif_cfg["kolon_bant_alt"][1] else (
                        "Üst" if toplam_puan >= aktif_cfg["kolon_bant_ust"][0] else "Orta")
                    adaylar.append({
                        "kolon": aday,
                        "etiket": f"{havuz_etiketi}* [{b_etk}]",
                        "is_gold": is_gold
                    })

    secilen_optimal = optimal_dagilim_sec(adaylar, aranan_adet, onceden_secilenler=onceden_secilen)
    return secilen_optimal, bankolar, diger_karanliklar, ek_tohum


def ekstra_top_hesapla(kolon, cfg, ek_tohum, kolon_idx=0):
    kod = cfg["kod"]
    if kod == "sayisal":
        j_havuz = [x for x in ek_tohum.get("joker_havuz", range(1, 91)) if x not in kolon]
        if not j_havuz: j_havuz = [x for x in range(1, 91) if x not in kolon]
        aday_skorlari = []
        for ad in j_havuz:
            test_7li = kolon + [ad]
            me, _ = get_rmt_stats(test_7li)
            sk = get_chatterjee_energy(test_7li)
            aday_skorlari.append((abs(sk) * 2.0 + abs(me - 86.0) / 15.0, ad))
        aday_skorlari.sort(key=lambda x: x[0])
        secilen_joker = random.choice([x[1] for x in aday_skorlari[:3]])
        s_havuz = ek_tohum.get("super_havuz", [1, 2, 3, 4, 5])
        secilen_super = s_havuz[kolon_idx % len(s_havuz)]
        return {"joker": secilen_joker, "super": secilen_super}
    elif kod == "sanstopu":
        a_havuz = ek_tohum.get("arti_havuz", [1, 2, 3, 4, 5])
        secilen_arti = a_havuz[kolon_idx % len(a_havuz)]
        return {"arti": secilen_arti}
    return {}


def kolon_html_olustur(kolon, baslik, bankolar=None, diger_karanliklar=None, ekstra=None, is_gold=False):
    banko_set = set(bankolar) if isinstance(bankolar, (list, set, tuple)) else ({bankolar} if bankolar else set())
    diger_set = set(diger_karanliklar) if diger_karanliklar else set()
    h = ""
    for n in kolon:
        if n in banko_set:
            h += f"<div class='top-banko' title='Çekirdek Banko'>{n:02d}</div>"
        elif n in diger_set:
            h += f"<div class='top-karanlik' title='Perkolasyon Mıknatıslı Hedge'>{n:02d}</div>"
        elif is_gold:
            h += f"<div class='top-gold' title='Perkolasyon Altın Bağ'>{n:02d}</div>"
        else:
            h += f"<div class='top-standart'>{n:02d}</div>"

    if ekstra:
        if "joker" in ekstra: h += f"<div class='top-joker' title='Dinamik Joker'>{ekstra['joker']:02d}</div>"
        if "super" in ekstra: h += f"<div class='top-super' title='Süper Star'>{ekstra['super']:02d}</div>"
        if "arti" in ekstra: h += f"<div class='top-arti' title='+1 Şans Topu'>+{ekstra['arti']:02d}</div>"

    rozet = "<span style='color:#FFD600; font-weight:bold; margin-left:auto;'>💎 ALTIN BAĞ</span>" if is_gold else ""
    return f"<div class='kolon-satir'><div class='kolon-baslik'>{baslik}</div><div>{h}</div>{rozet}</div>"


def kupon_alt_aksiyon_paneli(kolon_listesi, oyun_adi, mod_adi, bankolar=None, diger_karanliklar=None, key_prefix="k"):
    col_a, col_b = st.columns([1, 2])
    with col_a:
        if st.button("💾 Bu Kuponları Kasaya Kaydet (.json & .txt)", type="secondary", use_container_width=True,
                     key=f"save_{key_prefix}"):
            kasaya_kupon_ekle(oyun_adi, mod_adi, kolon_listesi, bankolar, diger_karanliklar)
            st.success(f"✅ Kuponlar '💾 Kupon Kasası' sekmesine kaydedildi!")
    with col_b:
        with st.expander("📋 Üretilen Kuponları Kopyalanabilir Metin Olarak Gör (Bayi / Mobil İçin)"):
            metin_satirlari = [f"=== {oyun_adi.upper()} ({mod_adi}) KUANTUM V23.5 KUPONU ==="]
            for idx, item in enumerate(kolon_listesi, 1):
                k = item["kolon"]
                eks = item.get("ekstra", {})
                etk = item.get("etiket", f"Kolon {idx:02d}")
                satir = f"{etk:22s} (Top:{sum(k):3d}): " + " - ".join(f"{n:02d}" for n in k)
                if "joker" in eks: satir += f" | Joker: {eks['joker']:02d} | Süper: {eks['super']:02d}"
                if "arti" in eks: satir += f" | +1 Topu: +{eks['arti']:02d}"
                metin_satirlari.append(satir)
            st.code("\n".join(metin_satirlari), language="text")

# =========================================================================
# QUANT LOTO V23.5 — PARÇA 3 / 3
# STREAMLIT KOMUTA MERKEZİ, SON 80 ÇEKİLİŞ GIANELLA SARKAÇ PANOSU,
# ESNEK HAVUZ/BANT/KOLON SEÇİMİ, KASA KONTROLÜ & GIANELLA BACKTEST MOTORU
# =========================================================================
st.title("🎯 Quant Loto V23.5 — Dinamik Gianella Sarkaç & 28 Filtreli Çift Kademeli Huni")

secilen_oyun = st.radio(
    "🎯 Oynamak İstediğiniz Kuantum Evrenini Seçin (Tüm Oyunlarda Dinamik Gianella Aktif):",
    list(OYUN_EVRENLERI.keys()),
    horizontal=True
)

aktif_cfg = OYUN_EVRENLERI[secilen_oyun]
aktif_paket = evren_verisini_yukle(secilen_oyun)
evrensel_basinc_vektoru, aktif_evrenler_listesi = mutlak_kuantum_alani_hesapla()

# Sol Çekmece (Sidebar) - Kontrol Paneli
st.sidebar.markdown("### ⚛️ V23.5 Kuantum Kontrol Paneli")
st.sidebar.caption(
    f"Aktif Veritabanları ({len(aktif_evrenler_listesi)}/4): {', '.join([e.split()[1] for e in aktif_evrenler_listesi])}")
pencere_boyutu = st.sidebar.slider("🔎 Gianella Analiz Penceresi (Son N Çekiliş):", 40, 150, 80, step=10,
                                   help="Varsayılan olarak son 80 çekilişi analiz ederek en yüksek sarkaç baskısına sahip Gianella havuzunu tespit eder.")
mutlak_alan_aktif = st.sidebar.checkbox("🌌 4 Evren Ortak Dolanıklığı", value=True,
                                        help="4 oyunun birleşik kuantum alanından soğukluk sinyali alır.")
esnek_tolerans_aktif = st.sidebar.checkbox("🔓 Esnek Huni Toleransı (27/28 Kural)", value=False,
                                           help="Açık olduğunda 28 filtreden 1-2 esnek hata payına izin vererek dar bantlarda üretimi hızlandırır.")

if st.sidebar.button("🔄 Analizleri ve Tohumları Yenile", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.sidebar.success("Son 80 Çekiliş Gianella Sarkaç Analizi ve Tohumlar Yenilendi!")
    st.rerun()

if aktif_paket is None:
    st.error(
        f"⚠️ **{secilen_oyun}** için veritabanı dosyası (`{aktif_cfg['dosyalar'][0]}`) çalışma klasöründe bulunamadı!")
    st.stop()

# -------------------------------------------------------------------------
# VERİTABANI EKSİK ÇEKİLİŞ KAPISI (GATEKEEPER - OTOMATİK YENİDEN HESAPLAMA)
# -------------------------------------------------------------------------
son_kayit_bilgisi, eksik_cekilisler = eksik_cekilisleri_kontrol_et(secilen_oyun, aktif_paket)
evren_kilidi_acik = True

if len(eksik_cekilisler) > 0:
    st.markdown(f'''
    <div class="uyari-kutu">
        <b style="color:#FFD600;">⚠️ VERİTABANI UYARISI ({len(eksik_cekilisler)} Eksik Çekiliş):</b> 
        Son Kayıt: <b>{son_kayit_bilgisi}</b> | Eksikler: {', '.join(eksik_cekilisler[:6])}
    </div>
    ''', unsafe_allow_html=True)
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        with st.expander("➕ Eksik Çekilişi Şimdi Veritabanına Ekle (Tüm Hesaplamalar Otomatik Güncellenir)", expanded=False):
            beklenen_sayi_adedi = 8 if aktif_cfg["kod"] == "sayisal" else (
                6 if aktif_cfg["kod"] in ["super", "sanstopu"] else 22)
            ornek_metin = "3, 14, 25, 41, 62, 78, 12, 44" if aktif_cfg["kod"] == "sayisal" else (
                "4, 12, 19, 24, 31, 8" if aktif_cfg["kod"] == "sanstopu" else f"{beklenen_sayi_adedi} adet sayı")
            c_tarih = st.text_input("Çekiliş Tarihi (GG.AA.YYYY):",
                                    value=eksik_cekilisler[0] if '.' in eksik_cekilisler[
                                        0] else datetime.date.today().strftime("%d.%m.%Y"))
            c_hft = st.number_input("Hafta No:", min_value=1, max_value=200, value=82)
            c_sayilar = st.text_input(f"Çıkan Sayılar ({ornek_metin}):")
            if st.button("💾 Kaydet ve Tüm Sarkaçları Güncelle", type="primary"):
                girilen_sayilar = [int(s) for s in re.findall(r'\d+', c_sayilar)]
                if len(girilen_sayilar) != beklenen_sayi_adedi:
                    st.error(f"Lütfen tam {beklenen_sayi_adedi} adet sayı girin! (Girilen: {len(girilen_sayilar)})")
                else:
                    basari, mesaj = yeni_cekilis_ekle(secilen_oyun, aktif_paket, c_tarih, c_hft, girilen_sayilar)
                    if basari:
                        st.success(mesaj)
                        st.rerun()
                    else:
                        st.error(mesaj)
    with col_g2:
        bypass_onay = st.checkbox("🔓 Eksikleri Geç ve Evreni Aç", value=True, key=f"bypass_{aktif_cfg['kod']}")
        if not bypass_onay:
            evren_kilidi_acik = False
            st.info("👆 Sekmeleri açmak için çekiliş girin veya kutucuğu işaretleyin.")
else:
    st.caption(
        f"✅ **Veritabanı Güncel!** Son Kayıt: **{son_kayit_bilgisi}** | Toplam Arşiv: **{len(aktif_paket['df']):,} Çekiliş** | 🧬 **28 Filtreli Çift Kademeli Huni & Markov Aktif**")

if not evren_kilidi_acik:
    st.stop()

# -------------------------------------------------------------------------
# SON 80 ÇEKİLİŞ GIANELLA ANALİZİ & 3x3 MARKOV BANT HESAPLAMASI
# -------------------------------------------------------------------------
df_global = aktif_paket["df"]
bant_1, bant_2, ihtimaller, markov_matrisi = bant_radari_hesapla(df_global, aktif_cfg)
gianella_rapor = dinamik_gianella_havuz_analizi(secilen_oyun, pencere=pencere_boyutu)

k_boyut = aktif_cfg["kolon_boyutu"]
max_sayi = aktif_cfg["max_sayi"]
yari_havuz_boyutu = max_sayi // 2

tabs = st.tabs([
    "🚀 Dinamik Gianella Havuzları, Bant Seçimi & Kuantum Üretim",
    "💾 Kupon Kasası & İkramiye Kontrolü",
    "🧪 Hızlı Backtest (Gianella & 28 Filtre vs Rastgele)"
])

# =========================================================================
# SEKME 1: GIANELLA SARKAÇ PANOSU + 3 BANT GRAFİĞİ + DİNAMİK ÜRETİM MERKEZİ
# =========================================================================
with tabs[0]:
    # 1. BÖLÜM: SON 80 ÇEKİLİŞ DİNAMİK GIANELLA HAVUZ RAPORU (MADDE 1)
    h_a = gianella_rapor["havuz_a"]
    h_b = gianella_rapor["havuz_b"]
    ol_a = gianella_rapor["olasilik_a"]
    ol_b = gianella_rapor["olasilik_b"]

    st.markdown(f'''
    <div class="gianella-kutu">
        <div style="color:#FFD600; font-weight:bold; font-size:15.5px; margin-bottom:6px;">
            🧬 SON {gianella_rapor['pencere']} ÇEKİLİŞ DİNAMİK GIANELLA SARKAÇ ANALİZİ ({yari_havuz_boyutu} + {yari_havuz_boyutu} = {max_sayi} Sayı)
        </div>
        <div style="color:#e2e8f0; font-size:13.5px; line-height:1.5;">
            🔥 <b>Havuz A (En Yüksek Gelme Olasılıklı Gianella Havuzu - %{ol_a}):</b> Son {gianella_rapor['pencere']} çekilişte <b>{gianella_rapor['a_top_sayisi']}</b> top üretti (Beklenen: {gianella_rapor['beklenen_top']}) | Sarkaç Z-Skoru: <b>+{gianella_rapor['z_skoru']}σ</b><br>
            ⚖️ <b>Havuz B (Simetrik Karşılık / Doygun Havuz - %{ol_b}):</b> Son {gianella_rapor['pencere']} çekilişte <b>{gianella_rapor['b_top_sayisi']}</b> top üretti | Üst Üste Baskınlık Serisi: <b>{gianella_rapor['seri_baski']} Çekiliş</b>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    with st.expander(f"🔍 Tespit Edilen Dinamik Gianella Havuzlarını Gör (Havuz A: {len(h_a)} Sayı | Havuz B: {len(h_b)} Sayı - %100 Tek/Çift ve Dekad Dengeli)", expanded=False):
        c_ha, c_hb = st.columns(2)
        with c_ha:
            st.markdown(f"**🎯 Havuz A (Sarkaç Baskısı En Yüksek {len(h_a)} Sayı — Olasılık: %{ol_a}):**")
            st.code(", ".join(f"{n:02d}" for n in h_a), language="text")
        with c_hb:
            st.markdown(f"**🪐 Havuz B (Simetrik Karşılık {len(h_b)} Sayı — Olasılık: %{ol_b}):**")
            st.code(", ".join(f"{n:02d}" for n in h_b), language="text")

    # 2. BÖLÜM: CANLI 3 BANT GRAFİĞİ VE 3x3 MARKOV OLASILIK KARTLARI
    b_alt, b_ust = aktif_cfg["bant_alt"], aktif_cfg["bant_ust"]
    col_grafik, col_oranlar = st.columns([2.3, 1])

    with col_grafik:
        son_25 = df_global.tail(25).copy().reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(9.5, 2.8))
        fig.patch.set_facecolor('#0d1117')
        ax.set_facecolor('#161b22')

        y_vals = son_25['Toplam'].values
        y_min = min(min(y_vals) - 15, int(b_alt * 0.72))
        y_max = max(max(y_vals) + 20, int(b_ust * 1.22))

        ax.axhspan(0, b_alt, color='#00B0FF', alpha=0.16, label=f'Alt Bant (<={b_alt})')
        ax.axhspan(b_alt, b_ust, color='#00E676', alpha=0.16, label=f'Orta Bant ({b_alt + 1}-{b_ust - 1})')
        ax.axhspan(b_ust, y_max + 250, color='#FF1744', alpha=0.16, label=f'Üst Bant (>={b_ust})')

        x_vals = range(1, len(son_25) + 1)
        ax.plot(x_vals, y_vals, color='#94a3b8', linestyle='--', linewidth=1.4, alpha=0.8)
        nokta_renkleri = ['#00B0FF' if v <= b_alt else ('#00E676' if v < b_ust else '#FF1744') for v in y_vals]
        ax.scatter(x_vals, y_vals, color=nokta_renkleri, s=95, zorder=5, edgecolor='white', linewidth=1.1)

        offset = max(2, int((y_max - y_min) * 0.04))
        for i, txt in enumerate(y_vals):
            ax.annotate(txt, (x_vals[i], y_vals[i] + offset), color='white', ha='center', fontsize=8, fontweight='bold')

        ax.set_ylim(y_min, y_max)
        ax.set_xlim(0.5, len(son_25) + 0.5)
        ax.set_xticks(x_vals)
        ax.tick_params(colors='white', labelsize=8)
        ax.set_title(f"{secilen_oyun} — Son 25 Çekilişin 3 Bant Seyri & Markov Sarkaç Yönü", color='#00E5FF',
                     fontsize=10.5, fontweight='bold')
        for spine in ax.spines.values(): spine.set_color('#30363d')
        leg = ax.legend(loc='upper right', facecolor='#0d1117', edgecolor='#30363d', fontsize=8)
        for text in leg.get_texts(): text.set_color("white")
        plt.tight_layout()
        st.pyplot(fig)

    with col_oranlar:
        st.markdown("##### 📡 3x3 Markov & Sarkaç Bant İhtimalleri")
        st.markdown(f"<div class='bant-kart bant-ust'>🔴 ÜST BANT ({b_ust}+): %{ihtimaller['Ust']:.1f}</div>",
                    unsafe_allow_html=True)
        st.markdown(
            f"<div class='bant-kart bant-orta'>🟢 ORTA BANT ({b_alt + 1}-{b_ust - 1}): %{ihtimaller['Orta']:.1f}</div>",
            unsafe_allow_html=True)
        st.markdown(f"<div class='bant-kart bant-alt'>🔵 ALT BANT (<={b_alt}): %{ihtimaller['Alt']:.1f}</div>",
                    unsafe_allow_html=True)
        st.success(
            f"🎯 **1. Hedef:** `{bant_1} Bant` (%{ihtimaller[bant_1]:.1f})  \n🛡️ **2. Sigorta:** `{bant_2} Bant` (%{ihtimaller[bant_2]:.1f})")

    st.divider()

    # 3. BÖLÜM: KULLANICI SEÇİM PANELİ (HAVUZ SEÇİMİ + BANT SEÇİMİ + KOLON SAYISI - MADDE 2 & 3)
    st.markdown("#### ⚙️ Kupon Üretim Parametrelerini Belirleyin")
    col_u1, col_u2, col_u3 = st.columns([1.6, 1.4, 1])

    with col_u1:
        havuz_tercihi = st.selectbox(
            f"🧬 1. Oynamak İstediğiniz Gianella Havuzunu Seçin:",
            [
                f"🔥 Sadece Havuz A (Gelme Olasılığı En Yüksek {yari_havuz_boyutu}'lık Havuz - %{ol_a})",
                f"⚖️ Her İki Havuz (Havuz A + Havuz B Eşit Dağılımlı Çift Matris)",
                f"🎯 Her İki Havuz (Olasılık Ağırlıklı: %{ol_a} Havuz A / %{ol_b} Havuz B)",
                f"🪐 Sadece Havuz B (Simetrik Karşılık {yari_havuz_boyutu}'lık Havuz - %{ol_b})"
            ]
        )

    with col_u2:
        bant_haritasi = {
            f"🔵 Alt Bant ({aktif_cfg['kolon_bant_alt'][0]}-{aktif_cfg['kolon_bant_alt'][1]})": "Alt",
            f"🟢 Orta Bant ({aktif_cfg['kolon_bant_orta'][0]}-{aktif_cfg['kolon_bant_orta'][1]})": "Orta",
            f"🔴 Üst Bant ({aktif_cfg['kolon_bant_ust'][0]}-{aktif_cfg['kolon_bant_ust'][1]})": "Ust"
        }
        varsayilan_etiketler = [k for k, v in bant_haritasi.items() if v in [bant_1, bant_2]]
        secilen_bant_etiketleri = st.multiselect(
            "📡 2. Aktif Olacak Bantları Seçin (Birini, İkisini veya Tümünü):",
            options=list(bant_haritasi.keys()),
            default=varsayilan_etiketler,
            help="İstediğiniz tek bir bandı, iki bandı veya üçünü birden seçebilirsiniz. Boş bırakırsanız tüm bantlar serbest kalır."
        )
        aktif_bant_kodlari = [bant_haritasi[e] for e in secilen_bant_etiketleri] if secilen_bant_etiketleri else ["Alt", "Orta", "Ust"]

    with col_u3:
        kolon_adedi = int(st.number_input(
            "🔢 3. Kaç Kolon Oynamak İstiyorsunuz?",
            min_value=1, max_value=200, value=50, step=1,
            help="İstediğiniz kolon sayısını (Örn: 10, 25, 33, 50, 66) doğrudan yazabilirsiniz."
        ))

    # 4. BÖLÜM: 28 FİLTRELİ ÇİFT KADEMELİ HUNİ İLE OPTİMAL KOLON ÜRETİMİ (MADDE 4)
    if st.button(f"🚀 SEÇİLEN HAVUZ(LAR)DAN 28 FİLTRE İLE OPTİMAL {kolon_adedi} KOLON ÜRET", type="primary", use_container_width=True):
        start_t = time.time()
        with st.spinner(f"Seçilen Gianella havuz(lar)ı 28 Filtreli Çift Kademeli Huniden geçiriliyor ve {kolon_adedi} optimal kolon örülüyor..."):
            if "Sadece Havuz A" in havuz_tercihi:
                nihai_havuz, bankolar, diger_karanliklar, ek_tohum = gianella_havuzundan_kolon_uret(
                    h_a, kolon_adedi, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🎯 Havuz-A"
                )
            elif "Sadece Havuz B" in havuz_tercihi:
                nihai_havuz, bankolar, diger_karanliklar, ek_tohum = gianella_havuzundan_kolon_uret(
                    h_b, kolon_adedi, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🪐 Havuz-B"
                )
            elif "Eşit Dağılımlı" in havuz_tercihi:
                adet_a = kolon_adedi - (kolon_adedi // 2)
                adet_b = kolon_adedi // 2
                kol_a, b_a, hdg_a, ek_tohum = gianella_havuzundan_kolon_uret(
                    h_a, adet_a, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🎯 Havuz-A"
                )
                kol_b, b_b, hdg_b, _ = gianella_havuzundan_kolon_uret(
                    h_b, adet_b, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🪐 Havuz-B"
                )
                nihai_havuz = kol_a + kol_b
                bankolar = sorted(list(set(b_a + b_b)))
                diger_karanliklar = sorted(list(set(hdg_a + hdg_b)))
            else:
                # Olasılık Ağırlıklı İki Havuz Dağılımı
                adet_a = max(1, int(round(kolon_adedi * (ol_a / 100.0))))
                adet_b = max(0, kolon_adedi - adet_a)
                kol_a, b_a, hdg_a, ek_tohum = gianella_havuzundan_kolon_uret(
                    h_a, adet_a, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🎯 Havuz-A"
                )
                kol_b, b_b, hdg_b, _ = gianella_havuzundan_kolon_uret(
                    h_b, adet_b, aktif_bant_kodlari, aktif_cfg, aktif_paket,
                    mutlak_alan_aktif, esnek_tolerans_aktif, "🪐 Havuz-B"
                ) if adet_b > 0 else ([], [], [], {})
                nihai_havuz = kol_a + kol_b
                bankolar = sorted(list(set(b_a + b_b)))
                diger_karanliklar = sorted(list(set(hdg_a + hdg_b)))

            # Ekstra topları (Sayısal Joker/Süper veya Şans Topu +1) sırayla dengeli dağıt
            for idx, item in enumerate(nihai_havuz):
                item["ekstra"] = ekstra_top_hesapla(item["kolon"], aktif_cfg, ek_tohum, kolon_idx=idx)

        if nihai_havuz:
            st.session_state[f"v23_uretim_{aktif_cfg['kod']}"] = (
                nihai_havuz, bankolar, diger_karanliklar, ek_tohum, time.time() - start_t, havuz_tercihi
            )

    if f"v23_uretim_{aktif_cfg['kod']}" in st.session_state:
        havuz, bankolar, diger_karanliklar, ek_tohum, sure, secilen_mod_adi = st.session_state[f"v23_uretim_{aktif_cfg['kod']}"]
        banko_html = " ".join([f"<span class='top-banko'>{b:02d}</span>" for b in bankolar])
        kapsanan_farkli_sayi = len(set(n for item in havuz for n in item["kolon"]))
        ek_bilgi = f" | <b>Kapsanan Farklı Sayı:</b> {kapsanan_farkli_sayi}/{max_sayi} | <b>En Aç Dekad:</b> [{ek_tohum.get('ezik_dekad', '-')}]"
        if "arti_havuz" in ek_tohum:
            ek_bilgi += f" | <b style='color:#00E676;'>+1 Elit Havuz:</b> {ek_tohum['arti_havuz']}"

        st.markdown(f'''
        <div class="tohum-kutu">
            <div style="color:#00E5FF; font-weight:bold; font-size:14px; margin-bottom:6px;">
                🌌 V23.5 ÇİFT KADEMELİ 28 FİLTRE & MAX-DISPERSION OPTİMAL SET ({len(havuz)} Kolon — {sure:.2f} sn)
            </div>
            <div style="color:white; font-size:13.5px;">
                <b style="color:#E1BEE7;">Çekirdek Bankolar:</b> {banko_html} &nbsp;|&nbsp;
                <b style="color:#FF8A80;">Mıknatıslı Hedge:</b> {diger_karanliklar[:8]} {ek_bilgi}
            </div>
        </div>
        ''', unsafe_allow_html=True)

        for idx, item in enumerate(havuz, 1):
            baslik_str = f"{idx:02d}. {item['etiket']} (Top:{sum(item['kolon'])})"
            st.markdown(kolon_html_olustur(item["kolon"], baslik_str, bankolar, diger_karanliklar, item["ekstra"],
                                           item["is_gold"]), unsafe_allow_html=True)

        kupon_alt_aksiyon_paneli(havuz, secilen_oyun, secilen_mod_adi.split('(')[0].strip(), bankolar, diger_karanliklar,
                                 key_prefix=f"v23_{aktif_cfg['kod']}")

# =========================================================================
# SEKME 2: KUPON KASASI & OTOMATİK İKRAMİYE KONTROLÖRÜ
# =========================================================================
with tabs[1]:
    st.markdown("### 💾 Favori Kupon Kasası ve Otomatik İkramiye Kontrolü")
    kasa_verisi = kasayi_yukle()
    if not kasa_verisi:
        st.info("Kasanızda henüz kayıtlı kupon bulunmuyor. Üretim ekranından tek tıkla kaydedebilirsiniz.")
    else:
        kontrol_sonuc_girdi = st.text_input(
            "🎯 Çıkan Sonucu Girerek Kasadaki Tüm Kuponları Kontrol Et (Sayıları boşluk veya virgülle ayırın):",
            key="kasa_kontrol_v23")
        kontrol_sayilari = set(
            [int(s) for s in re.findall(r'\d+', kontrol_sonuc_girdi)]) if kontrol_sonuc_girdi else set()

        for kayit in kasa_verisi:
            with st.expander(f"📁 [{kayit['tarih']}] {kayit['oyun']} — {kayit['mod']} ({len(kayit['kolonlar'])} Kolon)",
                             expanded=True):
                if kontrol_sayilari:
                    isabet_sayaci = Counter(len(set(it["kolon"]) & kontrol_sayilari) for it in kayit["kolonlar"])
                    ozet_str = " | ".join(f"**{k} Bilen:** {v} adet" for k, v in sorted(isabet_sayaci.items(), reverse=True) if k >= 6 or k == 0)
                    if ozet_str:
                        st.success(f"🏆 **İkramiye Özeti:** {ozet_str}")
                for idx, item in enumerate(kayit["kolonlar"], 1):
                    k = item["kolon"]
                    eks = item.get("ekstra", {})
                    ortaklar = sorted(list(set(k) & kontrol_sayilari)) if kontrol_sayilari else []
                    etk = item.get("etiket", f"Kolon {idx:02d}")
                    b_str = f"{etk} ({sum(k)})" + (f" 🎯[{len(ortaklar)} Bindi!]" if kontrol_sayilari else "")
                    st.markdown(kolon_html_olustur(k, b_str, kayit.get("banko"), kayit.get("hedge"), eks,
                                                   item.get("is_gold", False)), unsafe_allow_html=True)
                if st.button(f"🗑️ Bu Kuponu Sil", key=f"del_{kayit['id']}"):
                    kasadan_sil(kayit["id"])
                    st.rerun()

# =========================================================================
# SEKME 3: HIZLI BACKTEST SİMÜLASYONU (GIANELLA SARKAÇ vs RASTGELE)
# =========================================================================
with tabs[2]:
    st.markdown(f"### 🧪 {secilen_oyun} — Dinamik Gianella (Son 80 Çekiliş) & 28 Filtre vs Rastgele Testi")
    col_bt1, col_bt2, col_bt3 = st.columns(3)
    test_hafta = col_bt1.slider("Son Kaç Çekiliş Test Edilsin?", 5, 30, 15, step=5)
    hafta_kolon = col_bt2.slider("Her Çekiliş İçin Kolon Sayısı?", 10, 66, 25, step=5)
    bt_modu = col_bt3.selectbox("Backtest Havuz Stratejisi:", ["Sadece Baskıdaki Havuz A", "Her İki Havuz (A + B Eşit)"])

    if st.button("🚀 GIANELLA BACKTEST SİMÜLASYONUNU BAŞLAT", type="primary"):
        draws = aktif_paket["draws"]
        if len(draws) <= test_hafta + 85:
            st.error("Son 80 çekilişlik dinamik Gianella penceresi için yeterli arşiv verisi yok!")
        else:
            q_isabet, r_isabet = Counter(), Counter()
            havuz_a_ustun_sayisi = 0
            prog = st.progress(0.0)

            for i in range(test_hafta):
                hedef_idx = len(draws) - test_hafta + i
                gercek = set(draws[hedef_idx])
                gecmis_80 = draws[hedef_idx - 80:hedef_idx]

                # O çekiliş öncesindeki son 80 çekilişe göre Dinamik Gianella Havuz A'yı oluştur
                sayac_80 = Counter(num for d in gecmis_80 for num in d if 1 <= num <= max_sayi)
                havuz_a_bt = []
                for d_idx in range((max_sayi - 1) // 10 + 1):
                    d_sayilar = [n for n in range(d_idx * 10 + 1, min(max_sayi + 1, (d_idx + 1) * 10 + 1))]
                    sirali_d = sorted(d_sayilar, key=lambda x: sayac_80.get(x, 0))
                    havuz_a_bt.extend(sirali_d[:len(d_sayilar) // 2])
                havuz_b_bt = list(set(range(1, max_sayi + 1)) - set(havuz_a_bt))

                # Gerçek çekilişte Havuz A mı daha çok top yakaladı?
                if len(set(havuz_a_bt) & gercek) >= len(set(havuz_b_bt) & gercek):
                    havuz_a_ustun_sayisi += 1

                q_aday = []
                aktif_bt_havuz = havuz_a_bt if "Sadece" in bt_modu else list(range(1, max_sayi + 1))
                for _ in range(8000):
                    if len(q_aday) >= hafta_kolon * 2:
                        break
                    aday = sorted(random.sample(aktif_bt_havuz, k_boyut))
                    if cift_kademeli_28_filtre_denetimi(aday, aktif_cfg, aktif_paket, mode="mod5",
                                                        esnek_tolerans=True, tek_havuz_modu=True):
                        q_aday.append({"kolon": aday})

                q_sec = [x["kolon"] for x in optimal_dagilim_sec(q_aday, hafta_kolon)]
                while len(q_sec) < hafta_kolon:
                    q_sec.append(sorted(random.sample(aktif_bt_havuz, k_boyut)))
                r_sec = [sorted(random.sample(range(1, max_sayi + 1), k_boyut)) for _ in range(hafta_kolon)]

                for k in q_sec: q_isabet[len(set(k) & gercek)] += 1
                for k in r_sec: r_isabet[len(set(k) & gercek)] += 1
                prog.progress((i + 1) / test_hafta)

            st.success(
                f"✅ Simülasyon Tamamlandı! Test edilen {test_hafta} çekilişin **{havuz_a_ustun_sayisi} tanesinde (%{havuz_a_ustun_sayisi / test_hafta * 100:.1f})** Dinamik Havuz A en az Havuz B kadar veya daha fazla top yakaladı!")
            bt_t = [{"İsabet Kategorisi": f"{b} Bilen Kolon", "🎯 Quant V23.5 (Gianella + 28 Filtre)": q_isabet.get(b, 0),
                     "🎲 Rastgele (Sen Seç)": r_isabet.get(b, 0)} for b in [0] + list(range(2, k_boyut + 1))]
            st.dataframe(pd.DataFrame(bt_t), use_container_width=True, hide_index=True)
