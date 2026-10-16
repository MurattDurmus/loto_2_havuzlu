import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import os
from collections import Counter
import datetime
from scipy.spatial.distance import euclidean
import networkx as nx
from itertools import combinations

# =========================================================================
# SAYFA AYARLARI VE ŞIK TASARIM (CSS)
# =========================================================================
st.set_page_config(page_title="Süper Loto AI Quant Terminali Supreme", page_icon="🌌", layout="wide")

st.markdown('''
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 1.05rem; font-weight: bold;}
    .bant-kutu {padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 6px solid;}
    .bant-ust {background-color: #2b1114; border-color: #FF1744;}
    .bant-orta {background-color: #122919; border-color: #00E676;}
    .bant-alt {background-color: #111d2b; border-color: #00B0FF;}
    .sayi-rozet {display: inline-block; background-color: rgba(255,255,255,0.1); padding: 5px 10px; border-radius: 5px; margin: 3px; font-weight: bold;}

    .kolon-satir {
        display: flex; align-items: center; background-color: #1E1E1E; 
        padding: 8px 15px; border-radius: 6px; margin-bottom: 6px;
        border: 1px solid #333;
    }
    .kolon-baslik {width: 170px; font-weight: bold; color: #aaa; font-size: 14px;}
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
    .top-gold {
        display: inline-block; width: 32px; height: 32px; line-height: 32px; 
        border-radius: 50%; background-color: #FFD600; color: black; 
        text-align: center; font-weight: bold; font-size: 15px; margin-right: 6px;
        box-shadow: 0 0 12px #FFD600; border: 1px solid #FFF59D;
    }
    .tahlil-basarili {color: #00E676; font-weight: bold;}
    .tahlil-hatali {color: #FF1744; font-weight: bold; text-decoration: line-through;}
    </style>
''', unsafe_allow_html=True)

# =========================================================================
# SABİTLER VE KLASİK VERİ OKUMA
# =========================================================================
ASAL_SAYILAR = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59}


def onluk_grup_bul(n): return (n - 1) // 10


def kitle_cekimi_hesapla(df):
    if df is None or len(df) == 0: return set(), set()
    tum_sayilar = df[['T1', 'T2', 'T3', 'T4', 'T5', 'T6']].values.flatten()
    frekanslar = pd.Series(tum_sayilar).value_counts()
    tum_havuz = pd.Series(0, index=np.arange(1, 61))
    frekanslar = frekanslar.add(tum_havuz, fill_value=0).astype(int).sort_values(ascending=False)
    return set(frekanslar.head(15).index), set(frekanslar.tail(15).index)


@st.cache_data
def get_veri_ve_fizik_parametreleri():
    dosya_adi = 'Super_Loto_2020.csv'
    if not os.path.exists(dosya_adi):
        return None, None, None, None, None, None, None
    try:
        # Veri Yükleme
        df = pd.read_csv(dosya_adi, delimiter='\t' if '\t' in open(dosya_adi).readline() else ';')
        if len(df.columns) <= 1: df = pd.read_csv(dosya_adi, delimiter=',')

        # Sütun dönüşümleri
        if 'Tarih' in df.columns:
            df['Tarih'] = pd.to_datetime(df['Tarih'], format='mixed', dayfirst=True)
        cols = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        df = df.dropna(subset=cols)
        for col in cols: df[col] = df[col].astype(int)
        df['Toplam'] = df[cols].sum(axis=1)

        # Kronolojik sıra: En son çekiliş en sonda olacak
        if 'Tarih' in df.columns:
            df = df.sort_values('Tarih').reset_index(drop=True)
        else:
            df = df.iloc[::-1].reset_index(drop=True)

        draws = df[cols].values.tolist()
        num_draws = len(draws)

        # 1. İSİNG MODELİ (Manyetik Spinler)
        all_numbers = [num for draw in draws for num in draw]
        counts = Counter(all_numbers)
        median_freq = np.median(list(counts.values())) if counts else 0
        spins = {i: 1 if counts.get(i, 0) > median_freq else -1 for i in range(1, 61)}

        # 2. PERKOLASYON (Karanlık Madde Ağı)
        pair_counts = Counter()
        for draw in draws:
            pair_counts.update(combinations(sorted(draw), 2))
        perc_thresh = int(np.percentile(list(pair_counts.values()), 95)) if pair_counts else 13

        # 3. FAZ GEÇİŞİ (Tc Eşiği Bankoları)
        appearances = {i: [] for i in range(1, 61)}
        for idx, draw in enumerate(draws):
            for num in draw: appearances[num].append(idx)

        all_gaps = []
        for num, app in appearances.items():
            if len(app) > 1: all_gaps.extend(np.diff(app))
        t_c_95 = np.percentile(all_gaps, 95) if all_gaps else 29

        current_sleep = {num: (num_draws - 1) - (app[-1] if len(app) > 0 else 0) for num, app in appearances.items()}
        faz_bankolari = [k for k, v in current_sleep.items() if v >= t_c_95]

        # Zirveler ve Vadiler
        zirveler, vadiler = kitle_cekimi_hesapla(df)

        return df, zirveler, vadiler, spins, pair_counts, perc_thresh, faz_bankolari
    except Exception as e:
        st.error(f"Veri yüklenirken hata oluştu: {e}")
        return None, None, None, None, None, None, None


df_global, global_zirveler, global_vadiler, spins_global, pair_counts_global, perc_thresh_global, faz_bankolari_global = get_veri_ve_fizik_parametreleri()

if 'ozel_havuz' not in st.session_state:
    st.session_state.ozel_havuz = "5, 6, 7, 8, 15, 20, 35, 37, 43, 44, 48, 56, 57, 59, 60"


# =========================================================================
# YARDIMCI FİZİK KURALLARI (SAW VE PERKOLASYON)
# =========================================================================
def get_coord(num):
    num -= 1
    return (num % 10, num // 10)


def calc_walk_len(kolon):
    s_k = sorted(kolon)
    return sum(euclidean(get_coord(s_k[i]), get_coord(s_k[i + 1])) for i in range(5))


def is_percolated(kolon):
    if not pair_counts_global: return False
    subG = nx.Graph()
    subG.add_nodes_from(kolon)
    valid_edges = [(u, v) for u, v in combinations(kolon, 2) if pair_counts_global[(u, v)] >= perc_thresh_global]
    subG.add_edges_from(valid_edges)
    return nx.is_connected(subG)


def kuantum_fizik_denetimi(kolon):
    """İsing Manyetizması ve SAW Polimer Yürüyüşü Denetimi"""
    # 1. Manyetizma
    if spins_global:
        manyetik_enerji = sum(spins_global[num] for num in kolon)
        if manyetik_enerji not in [-2, 0, 2]: return False

    # 2. Polimer Uzunluğu (SAW)
    walk_len = calc_walk_len(kolon)
    if not (13.0 <= walk_len <= 23.0): return False

    # 3. Faz Bankosu (Garantisi)
    if faz_bankolari_global and not any(num in faz_bankolari_global for num in kolon):
        return False

    return True


# =========================================================================
# BANT İHTİMAL RADARI
# =========================================================================
def bant_ihtimal_hesapla(df):
    if df is None or len(df) < 20: return None, None

    def get_bant(t):
        return 'Alt' if t <= 166 else ('Ust' if t >= 201 else 'Orta')

    df_temp = df.copy()
    df_temp['Bant'] = df_temp['Toplam'].apply(get_bant)
    son_20 = df_temp.tail(20).reset_index(drop=True)
    counts = son_20['Bant'].value_counts()
    actual = {'Alt': counts.get('Alt', 0), 'Orta': counts.get('Orta', 0), 'Ust': counts.get('Ust', 0)}
    expected = {'Alt': 6.66, 'Orta': 6.66, 'Ust': 6.66}
    diff = {k: expected[k] - actual[k] for k in expected}
    son_bantlar = son_20['Bant'].tolist()[::-1]
    aktif_seri_bandi = son_bantlar[0]
    seri_sayisi = sum(1 for b in son_bantlar if b == aktif_seri_bandi)
    if not all(b == aktif_seri_bandi for b in son_bantlar[:seri_sayisi]):
        seri_sayisi = 0
        for b in son_bantlar:
            if b == aktif_seri_bandi:
                seri_sayisi += 1
            else:
                break
    raw_p = {k: max(5, 33.33 + diff[k] * 3.0) for k in expected}
    if seri_sayisi >= 3: raw_p[aktif_seri_bandi] = max(5, raw_p[aktif_seri_bandi] - (seri_sayisi * 3))
    total_raw = sum(raw_p.values())
    final_p = {k: (v / total_raw) * 100 for k, v in raw_p.items()}
    return max(final_p, key=final_p.get), final_p


# =========================================================================
# 🧠 YAPAY ZEKA DİNAMİK ÖĞRENME (Aylık Trend Analizi)
# =========================================================================
AI_LOG_FILE = 'ai_loss_log.csv'

SINIRLAR = {
    'mod4': {'H1': (35, 67), 'H2': (116, 148), 'fraktal': (2.04, 3.44), 'sapma': 15, 'mat1': (1.33, 2.15),
             'mat2': (2.00, 6.75), 'bosluk': 20},
    'mod5': {'H1': (23, 87), 'H2': (96, 160), 'fraktal': (1.65, 5.05), 'sapma': 24, 'mat1': (1.17, 3.17),
             'mat2': (1.45, 16.0), 'bosluk': 26}
}
ai_mesaji = ""


def log_sonuc_kaydet(sayilar, H1, H2, fraktal, sapma, mat1, mat2, bosluk):
    df_log = pd.DataFrame([{
        'Tarih': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Kolon': str(sayilar),
        'H1': H1, 'H2': H2, 'Fraktal': round(fraktal, 2),
        'Sapma': sapma, 'Mat1': round(mat1, 2), 'Mat2': round(mat2, 2), 'Bosluk': bosluk
    }])
    if not os.path.exists(AI_LOG_FILE):
        df_log.to_csv(AI_LOG_FILE, index=False)
    else:
        df_log.to_csv(AI_LOG_FILE, mode='a', header=False, index=False)


def dinamik_sinir_guncelle():
    global SINIRLAR, ai_mesaji
    if not os.path.exists(AI_LOG_FILE): return
    try:
        df_log = pd.read_csv(AI_LOG_FILE)
        if len(df_log) >= 5:
            son_trend = df_log.tail(10)
            trend_H1_mean = son_trend['H1'].mean()
            trend_H2_mean = son_trend['H2'].mean()
            trend_H1_std = max(5, son_trend['H1'].std())
            trend_H2_std = max(10, son_trend['H2'].std())

            yeni_H1_min = max(20, int((SINIRLAR['mod4']['H1'][0] + (trend_H1_mean - trend_H1_std)) / 2))
            yeni_H1_max = min(80, int((SINIRLAR['mod4']['H1'][1] + (trend_H1_mean + trend_H1_std)) / 2))
            yeni_H2_min = max(90, int((SINIRLAR['mod4']['H2'][0] + (trend_H2_mean - trend_H2_std)) / 2))
            yeni_H2_max = min(170, int((SINIRLAR['mod4']['H2'][1] + (trend_H2_mean + trend_H2_std)) / 2))

            SINIRLAR['mod4']['H1'] = (yeni_H1_min, yeni_H1_max)
            SINIRLAR['mod4']['H2'] = (yeni_H2_min, yeni_H2_max)
            SINIRLAR['mod5']['H1'] = (max(15, yeni_H1_min - 10), min(95, yeni_H1_max + 10))
            SINIRLAR['mod5']['H2'] = (max(80, yeni_H2_min - 15), min(180, yeni_H2_max + 15))

            ai_mesaji = f"*(🤖 AI Trend Optimizasyonu Aktif: Mod 4 H1 sınırı [{yeni_H1_min}-{yeni_H1_max}], H2 sınırı [{yeni_H2_min}-{yeni_H2_max}] olarak güncellendi!)*"
    except Exception as e:
        pass


dinamik_sinir_guncelle()


# =========================================================================
# GENEL KURALLAR VE DENETİM MOTORLARI
# =========================================================================
def genel_kural_denetimi(kolon, df_gecmis=None, zirveler=set(), vadiler=set(), hedefler=None, altin_kesi_aktif=True):
    toplam = sum(kolon)
    if hedefler:
        if not any(h_min <= toplam <= h_max for (h_min, h_max) in hedefler): return False
    elif altin_kesi_aktif:
        if not (145 <= toplam <= 221): return False

    if sum(1 for n in kolon if n % 2 != 0) not in [2, 3, 4]: return False
    bosluklar = [(kolon[i + 1] - kolon[i] - 1) for i in range(5)]
    if bosluklar.count(0) > 1 or (0 in bosluklar and 1 in bosluklar): return False
    if sum(bosluklar) >= 41 and max(bosluklar) <= 17: return False
    if sum(bosluklar) <= 40 and max(bosluklar) >= 18: return False
    if not (kolon[0] < 21 and kolon[-1] > 39): return False
    if (6 - len(set(onluk_grup_bul(n) for n in kolon))) not in [2, 3]: return False
    if not (25 <= sum(sum(int(d) for d in str(n)) for n in kolon) <= 55): return False
    if kolon[1] > 34 or kolon[4] < 26: return False
    if max(Counter([n % 10 for n in kolon]).values()) > 2: return False
    if not (7.00 <= np.std(kolon) <= 23.50): return False
    if sum(1 for n in kolon if 21 <= n <= 40) not in [2, 3]: return False
    if sum(1 for n in kolon if n in ASAL_SAYILAR) not in [1, 2]: return False
    if not (35 <= kolon[5] - kolon[0] <= 55): return False
    if zirveler and sum(1 for n in kolon if n in zirveler) > 2: return False
    if vadiler and sum(1 for n in kolon if n in vadiler) < 1: return False
    return True


def kusursuz_mu(kolon, df_gecmis=None, zirveler=set(), vadiler=set(), altin_kesi_aktif=True):
    if not genel_kural_denetimi(kolon, df_gecmis, zirveler, vadiler, altin_kesi_aktif=altin_kesi_aktif): return False
    dusuk_sayisi = sum(1 for n in kolon if n <= 30)
    if dusuk_sayisi not in [2, 3, 4]: return False
    return True


def quant_kalibre_kusursuz_mu(kolon, hedef_toplam, df_gecmis=None, zirveler=set(), vadiler=set()):
    if sum(kolon) != hedef_toplam: return False
    if not genel_kural_denetimi(kolon, df_gecmis, zirveler, vadiler, altin_kesi_aktif=False): return False
    bant = 'Alt' if hedef_toplam <= 166 else ('Ust' if hedef_toplam >= 201 else 'Orta')
    dusuk_sayisi = sum(1 for n in kolon if n <= 30)
    if bant == 'Alt' and not (3 <= dusuk_sayisi <= 6): return False
    if bant == 'Orta' and not (2 <= dusuk_sayisi <= 4): return False
    if bant == 'Ust' and not (0 <= dusuk_sayisi <= 3): return False
    return True


def kolon_kotaya_uygun_mu(kolon, kota_tipi):
    tek_sayisi = sum(1 for n in kolon if n % 2 != 0)
    bosluklar = [(kolon[i + 1] - kolon[i] - 1) for i in range(5)]
    has_0 = 0 in bosluklar
    has_1 = 1 in bosluklar
    if kota_tipi == "Tip1_Asimetrik_Uyumlu" and (tek_sayisi in [2, 4] and (has_0 or has_1)):
        return True
    elif kota_tipi == "Tip2_Simetrik_Dar" and (tek_sayisi == 3 and sum(bosluklar) <= 40 and has_0):
        return True
    elif kota_tipi == "Tip3_Daginik_Sniper" and (not has_0 and not has_1):
        return True
    return False


def optimal_dagilim_sec(gecerli_kolonlar, hedef_sayi):
    if len(gecerli_kolonlar) <= hedef_sayi: return gecerli_kolonlar
    secilenler = [gecerli_kolonlar.pop(random.randint(0, len(gecerli_kolonlar) - 1))]
    while len(secilenler) < hedef_sayi:
        en_iyi_aday, en_dusuk_ortak = None, 999
        for aday in gecerli_kolonlar:
            max_ortak = max(len(set(aday) & set(secilen)) for secilen in secilenler)
            if max_ortak < en_dusuk_ortak:
                en_dusuk_ortak, en_iyi_aday = max_ortak, aday
        secilenler.append(en_iyi_aday)
        gecerli_kolonlar.remove(en_iyi_aday)
    return secilenler


# =========================================================================
# DİNAMİK YAPAY ZEKA SİMETRİ MOTORLARI (SINIRLAR DİNAMİKTİR)
# =========================================================================
def fraktal_simetri_denetimi_kati(kolon):
    s = SINIRLAR['mod4']
    T1, T2, T3, T4, T5, T6 = kolon
    H1, H2 = T1 + T2 + T3, T4 + T5 + T6
    if not (s['H1'][0] <= H1 <= s['H1'][1]): return False
    if not (s['H2'][0] <= H2 <= s['H2'][1]): return False

    y1, y2, y3 = T1 + T6, T2 + T5, T3 + T4
    if max([y1, y2, y3]) - min([y1, y2, y3]) > s['sapma']: return False

    dis, orta, cekirdek = T6 - T1, T5 - T2, T4 - T3
    if cekirdek == 0 or orta == 0: return False
    if not (s['mat1'][0] <= dis / orta <= s['mat1'][1]): return False
    if not (s['mat2'][0] <= orta / cekirdek <= s['mat2'][1]): return False

    if max([T2 - T1, T3 - T2, T4 - T3, T5 - T4, T6 - T5]) > s['bosluk']: return False
    if H1 == 0 or not (s['fraktal'][0] <= H2 / H1 <= s['fraktal'][1]): return False
    return True


def fraktal_simetri_denetimi_esnek(kolon):
    s = SINIRLAR['mod5']
    T1, T2, T3, T4, T5, T6 = kolon
    H1, H2 = T1 + T2 + T3, T4 + T5 + T6
    if not (s['H1'][0] <= H1 <= s['H1'][1]): return False
    if not (s['H2'][0] <= H2 <= s['H2'][1]): return False

    y1, y2, y3 = T1 + T6, T2 + T5, T3 + T4
    if max([y1, y2, y3]) - min([y1, y2, y3]) > s['sapma']: return False

    dis, orta, cekirdek = T6 - T1, T5 - T2, T4 - T3
    if cekirdek == 0 or orta == 0: return False
    if not (s['mat1'][0] <= dis / orta <= s['mat1'][1]): return False
    if not (s['mat2'][0] <= orta / cekirdek <= s['mat2'][1]): return False

    if max([T2 - T1, T3 - T2, T4 - T3, T5 - T4, T6 - T5]) > s['bosluk']: return False
    if H1 == 0 or not (s['fraktal'][0] <= H2 / H1 <= s['fraktal'][1]): return False
    return True


# =========================================================================
# KUANTUM ÇEKİRDEK MOTORU
# =========================================================================
def dinamik_kuantum_rezonans(df):
    max_idx = len(df) - 1
    timelines = {
        'Kronolojik': [set(df.iloc[max_idx - l][['T1', 'T2', 'T3', 'T4', 'T5', 'T6']]) for l in range(1, 16) if
                       max_idx - l >= 0],
        'Fibonacci': [set(df.iloc[max_idx - l][['T1', 'T2', 'T3', 'T4', 'T5', 'T6']]) for l in
                      [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987][:15] if max_idx - l >= 0],
        'Kadim_19': [set(df.iloc[max_idx - l][['T1', 'T2', 'T3', 'T4', 'T5', 'T6']]) for l in
                     [i * 19 for i in range(1, 16)] if max_idx - l >= 0],
        'Laplace': [set(df.iloc[max_idx - l][['T1', 'T2', 'T3', 'T4', 'T5', 'T6']]) for l in
                    [2 ** n for n in range(0, 15)] if max_idx - l >= 0]
    }

    decade_counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    all_cold = []
    for name, seq in timelines.items():
        seen = set()
        for d in seq:
            seen.update(d)
            for num in d: decade_counts[onluk_grup_bul(num)] += 1
        all_cold.extend(list(set(range(1, 61)) - seen))

    cold_counts = Counter(all_cold)
    if cold_counts:
        max_basinc = max(cold_counts.values())
        karanlik_sayilar = [num for num, count in cold_counts.items() if count == max_basinc]
    else:
        max_basinc, karanlik_sayilar = 0, []

    en_ezik = min(decade_counts, key=decade_counts.get)
    return karanlik_sayilar, list(range(en_ezik * 10 + 1, en_ezik * 10 + 11)), max_basinc


# =========================================================================
# ANA ARAYÜZ (SEKMELER)
# =========================================================================
st.title("🎯 Süper Loto AI Quant Terminali Supreme")
st.caption("Veritabanı: Super_Loto_2020.csv | Mod 4 & 5 Kuantum Fizik Kuralları Aktif (İsing, SAW, Perkolasyon)")
if ai_mesaji: st.markdown(f"<span style='color:#00B0FF; font-weight:bold;'>{ai_mesaji}</span>", unsafe_allow_html=True)

tabs = st.tabs(["🏛️ Klasik", "🚀 Quant V2", "🌌 Mod 3", "🎯 Mod 4 (KATI)", "🪐 Mod 5 (ESNEK)", "🧠 AI Tahlil & Evrim"])

en_iyi_bant, ihtimaller = bant_ihtimal_hesapla(df_global)

# -------------------------------------------------------------------------
# SEKME 1: KLASİK ANALİZ
# -------------------------------------------------------------------------
with tabs[0]:
    st.markdown("### 🏛️ Klasik Kuantum Filtresi (Mod 1 ve Mod 2)")
    strateji = st.radio("Uygulanacak Modu Seçin:",
                        ["Mod 1: Tüm Sayılardan Kusursuz DNA Süz", "Mod 2: Kombinatoryal Kapsama (Özel Havuz)"],
                        key='klasik_strat')
    havuz_girdisi = ""
    if "Mod 2" in strateji: havuz_girdisi = st.text_input("Havuz Sayıları:", value=st.session_state.ozel_havuz)
    kolon_sayisi_klasik = st.number_input("Üretilecek Kolon Sayısı:", min_value=1, max_value=200, value=10,
                                          key='k_klasik')

    if st.button("🚀 KUPONLARI ÜRET (KLASİK)", type="secondary"):
        start_t = time.time()
        havuz, cop = [], 0
        h_sayilar = list(set([int(s.strip()) for s in havuz_girdisi.split(',')])) if "Mod 2" in strateji else range(1,
                                                                                                                    61)

        with st.spinner("Taranıyor..."):
            for _ in range(4000000):
                if len(havuz) >= (kolon_sayisi_klasik * 5): break
                aday = sorted(random.sample(h_sayilar, 6))
                if aday not in havuz:
                    if kusursuz_mu(aday, df_global, global_zirveler, global_vadiler):
                        havuz.append(aday)
                    else:
                        cop += 1
            nihai = optimal_dagilim_sec(havuz, kolon_sayisi_klasik)

        if nihai:
            st.success(f"🎯 Tamamlandı! Kolon: {len(nihai)} | Çöp: {cop:,} | Süre: {time.time() - start_t:.2f}s")
            for i, k in enumerate(nihai, 1):
                h = "".join([f"<div class='top-standart'>{n:02d}</div>" for n in k])
                st.markdown(
                    f"<div class='kolon-satir'><div class='kolon-baslik'>Klasik Kolon {i}</div><div>{h}</div></div>",
                    unsafe_allow_html=True)

# -------------------------------------------------------------------------
# SEKME 2: QUANT V2.0
# -------------------------------------------------------------------------
with tabs[1]:
    if df_global is not None and ihtimaller:
        st.markdown("### 📡 Canlı Bant Basınç Radarı")
        st.markdown(f'''
        <div class="bant-kutu bant-ust"><h4 style='margin-top:0;'>🔴 ÜST BANT (201-260) — <span style='color:#FF1744;'>İhtimal: %{ihtimaller['Ust']:.1f}</span></h4></div>
        <div class="bant-kutu bant-orta"><h4 style='margin-top:0;'>🟢 ORTA BANT (167-200) — <span style='color:#00E676;'>İhtimal: %{ihtimaller['Orta']:.1f}</span></h4></div>
        <div class="bant-kutu bant-alt"><h4 style='margin-top:0;'>🔵 ALT BANT (106-166) — <span style='color:#00B0FF;'>İhtimal: %{ihtimaller['Alt']:.1f}</span></h4></div>
        ''', unsafe_allow_html=True)
        st.divider()

        st.markdown("### 🚀 Quant V2.0 - Tam Kalibre Kotalı Üretici")
        secilen_bant = st.radio("Bandı Seçin:", ["🔵 Alt Bant", "🟢 Orta Bant", "🔴 Üst Bant"], horizontal=True)
        kolon_sayisi = st.slider("Kaç Kolon Üretilsin?", 10, 50, 10, step=10)

        if st.button("🔥 Dağılım Kotalı Kolonları Üret", type="primary", key='btn_uret'):
            current_date = datetime.datetime.now()


            def get_hedefler(alt_sinir, ust_sinir):
                bolge = df_global[(df_global['Toplam'] >= alt_sinir) & (df_global['Toplam'] <= ust_sinir)].copy()
                stats = bolge.groupby('Toplam').agg(Frekans=('Tarih', 'count'),
                                                    Son_Cikis=('Tarih', 'max')).reset_index()
                stats['Gecikme_Gun'] = (current_date - stats['Son_Cikis']).dt.days

                def agirlik_hesapla(x):
                    if x <= 166:
                        return 0.1 + 0.9 * ((x - 106) / 60)
                    elif x >= 201:
                        return 0.1 + 0.9 * ((260 - x) / 59)
                    else:
                        return 1.0 - 0.15 * (abs(x - 183) / 17)

                stats['Kalibre_Basinc'] = (stats['Frekans'] * stats['Gecikme_Gun']) * stats['Toplam'].apply(
                    agirlik_hesapla)
                return stats.sort_values('Kalibre_Basinc', ascending=False).head(3)['Toplam'].tolist()


            hedef_listesi = get_hedefler(106, 166) if "Alt" in secilen_bant else (
                get_hedefler(167, 200) if "Orta" in secilen_bant else get_hedefler(201, 260))

            k1, k2, k3 = int(kolon_sayisi * 0.5), int(kolon_sayisi * 0.3), kolon_sayisi - int(kolon_sayisi * 0.5) - int(
                kolon_sayisi * 0.3)
            kotalar = (["Tip1_Asimetrik"] * k1 + ["Tip2_Simetrik"] * k2 + ["Tip3_Daginik"] * k3)

            uretilenler = []
            with st.spinner("Taranıyor..."):
                for i, kota in enumerate(kotalar):
                    h_toplam = hedef_listesi[i % len(hedef_listesi)]
                    kolon = None
                    for _ in range(1500000):
                        aday = sorted(random.sample(range(1, 61), 6))
                        if quant_kalibre_kusursuz_mu(aday, h_toplam, df_global, global_zirveler,
                                                     global_vadiler) and kolon_kotaya_uygun_mu(aday, kota):
                            kolon = aday
                            break
                    if not kolon:
                        for _ in range(500000):
                            aday = sorted(random.sample(range(1, 61), 6))
                            if quant_kalibre_kusursuz_mu(aday, h_toplam, df_global, global_zirveler, global_vadiler):
                                kolon = aday
                                kota += " (Serbest)"
                                break
                    uretilenler.append((kolon, h_toplam, kota))

            for i, (k, hedef, tip) in enumerate(uretilenler):
                if k:
                    h = "".join([f"<div class='top-standart'>{n:02d}</div>" for n in k])
                    st.markdown(
                        f"<div class='kolon-satir'><div class='kolon-baslik'>Kota: {tip.split('_')[0]} (Puan:{hedef})</div><div>{h}</div></div>",
                        unsafe_allow_html=True)
                else:
                    st.warning(f"Kolon {i + 1} bulunamadı.")

# -------------------------------------------------------------------------
# SEKME 3: MOD 3 - KOZMİK AĞ
# -------------------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🌌 Mod 3: 12 Boyutlu Kozmik Ağ")
    if df_global is not None:
        if st.button("🔮 12 BOYUTLU AĞI TARAT", type="primary", use_container_width=True):
            start_t = time.time()
            with st.spinner("Taranıyor..."):
                karanliklar, ezik_havuz, basinc = dinamik_kuantum_rezonans(df_global)
            sec_k = min(2, len(karanliklar))
            aktif_k = random.sample(karanliklar, sec_k) if sec_k > 0 else []
            kalan = list(set(range(1, 61)) - set(aktif_k))

            havuz, cop = [], 0
            with st.spinner("Simüle Ediliyor..."):
                for _ in range(8000000):
                    if len(havuz) >= 10: break
                    aday = sorted(aktif_k + random.sample(kalan, 6 - sec_k))

                    if len(set(aday) & set(ezik_havuz)) < 2: cop += 1; continue
                    if kusursuz_mu(aday, df_global, global_zirveler, global_vadiler):
                        havuz.append(aday)
                    else:
                        cop += 1

            if havuz:
                st.success(f"🌌 Tamamlandı! Kolon: {len(havuz)} | Çöp: {cop:,}")
                for i, k in enumerate(havuz, 1):
                    h = "".join(
                        [f"<div class='{'top-karanlik' if n in aktif_k else 'top-standart'}'>{n:02d}</div>" for n in k])
                    st.markdown(
                        f"<div class='kolon-satir'><div class='kolon-baslik'>Mod 3 Kolon {i}</div><div>{h}</div></div>",
                        unsafe_allow_html=True)

# -------------------------------------------------------------------------
# SEKME 4: YENİ MOD 4 (KATI KANUNLAR + KUANTUM FİZİĞİ)
# -------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 🎯 Mod 4: Ultra Sniper (AI Sınırları & Kuantum Kuralları)")
    radar_teklif_4 = False
    if ihtimaller:
        radar_teklif_4 = st.checkbox(f"Radar Önerisini ({en_iyi_bant}) Kabul Et", key="r4")

    if st.button("🔮 KATI KOLONLARI ÜRET", type="primary", key="btn_m4"):
        start_t = time.time()
        hedef_araliklar = [(106, 166)] if radar_teklif_4 and en_iyi_bant == 'Alt' else (
            [(167, 200)] if radar_teklif_4 and en_iyi_bant == 'Orta' else (
                [(201, 260)] if radar_teklif_4 else [(145, 221)]))
        hedef_metni = "Radar Kilitli" if radar_teklif_4 else "Altın Kesi"

        karanliklar, ezik_havuz, basinc = dinamik_kuantum_rezonans(df_global)

        # Faz bankosu garantisi
        zorunlu_bankolar = []
        if faz_bankolari_global:
            zorunlu_bankolar.append(random.choice(faz_bankolari_global))

        sec_k = min(2, len(karanliklar))
        aktif_k = list(set(random.sample(karanliklar, sec_k) + zorunlu_bankolar))
        kalan = list(set(range(1, 61)) - set(aktif_k))

        havuz, cop = [], 0
        with st.spinner("Kuantum Süzgeci Taranıyor (İsing, SAW, Perkolasyon)..."):
            for _ in range(15000000):
                if len(havuz) >= 10: break

                # Rastgele aday oluştururken aktif_k (kara delikler ve faz bankoları) dahil edilir.
                # Eğer aktif_k havuzu 6'dan büyükse sınırlandırıyoruz
                orneklem_boyutu = max(0, 6 - len(aktif_k))
                aday = sorted(aktif_k[:6] + random.sample(kalan, orneklem_boyutu))

                if len(set(aday) & set(ezik_havuz)) < 2: cop += 1; continue

                if genel_kural_denetimi(aday, df_global, global_zirveler, global_vadiler, hedefler=hedef_araliklar):
                    if fraktal_simetri_denetimi_kati(aday):
                        if kuantum_fizik_denetimi(aday):
                            is_gold = is_percolated(aday)
                            havuz.append({"kolon": aday, "is_gold": is_gold})
                            continue
                cop += 1

        if havuz:
            st.success(
                f"🎯 Tamamlandı! Kolon: {len(havuz)} | Çöp: {cop:,} | Süre: {time.time() - start_t:.2f}s | Hedef: {hedef_metni}")
            for i, data in enumerate(havuz, 1):
                k, is_gold = data["kolon"], data["is_gold"]

                h = ""
                for n in k:
                    if n in faz_bankolari_global:
                        h += f"<div class='top-karanlik' title='Faz Bankosu'>{n:02d}</div>"
                    elif is_gold:
                        h += f"<div class='top-gold' title='Perkolasyon'>{n:02d}</div>"
                    else:
                        h += f"<div class='top-standart'>{n:02d}</div>"

                rozet = "<span style='color:#FFD600; font-weight:bold;'>💎 ALTIN KOLON</span>" if is_gold else ""
                st.markdown(
                    f"<div class='kolon-satir'><div class='kolon-baslik'>Mod 4 (Puan:{sum(k)})</div><div>{h}</div><div style='margin-left:auto;'>{rozet}</div></div>",
                    unsafe_allow_html=True)
        else:
            st.warning("Katı kurallar çok sert geldi, olasılık bulunamadı.")

# -------------------------------------------------------------------------
# SEKME 5: YENİ MOD 5 (ESNEK KANUNLAR + KUANTUM FİZİĞİ)
# -------------------------------------------------------------------------
with tabs[4]:
    st.markdown("### 🪐 Mod 5: Esnek Simetri (AI Sınırları & Kuantum Kuralları)")
    radar_teklif_5 = False
    if ihtimaller:
        radar_teklif_5 = st.checkbox(f"Radar Önerisini ({en_iyi_bant}) Kabul Et", key="r5")

    if st.button("🔮 ESNEK KOLONLARI ÜRET", type="primary", key="btn_m5"):
        start_t = time.time()
        hedef_araliklar = [(106, 166)] if radar_teklif_5 and en_iyi_bant == 'Alt' else (
            [(167, 200)] if radar_teklif_5 and en_iyi_bant == 'Orta' else (
                [(201, 260)] if radar_teklif_5 else [(145, 221)]))
        hedef_metni = "Radar Kilitli" if radar_teklif_5 else "Altın Kesi"

        karanliklar, ezik_havuz, basinc = dinamik_kuantum_rezonans(df_global)

        zorunlu_bankolar = []
        if faz_bankolari_global:
            zorunlu_bankolar.append(random.choice(faz_bankolari_global))

        sec_k = min(2, len(karanliklar))
        aktif_k = list(set(random.sample(karanliklar, sec_k) + zorunlu_bankolar))
        kalan = list(set(range(1, 61)) - set(aktif_k))

        havuz, cop = [], 0
        with st.spinner("Kuantum Süzgeci Taranıyor (İsing, SAW, Perkolasyon)..."):
            for _ in range(10000000):
                if len(havuz) >= 10: break

                orneklem_boyutu = max(0, 6 - len(aktif_k))
                aday = sorted(aktif_k[:6] + random.sample(kalan, orneklem_boyutu))

                if len(set(aday) & set(ezik_havuz)) < 2: cop += 1; continue

                if genel_kural_denetimi(aday, df_global, global_zirveler, global_vadiler, hedefler=hedef_araliklar):
                    if fraktal_simetri_denetimi_esnek(aday):
                        if kuantum_fizik_denetimi(aday):
                            is_gold = is_percolated(aday)
                            havuz.append({"kolon": aday, "is_gold": is_gold})
                            continue
                cop += 1

        if havuz:
            st.success(
                f"🪐 Tamamlandı! Kolon: {len(havuz)} | Çöp: {cop:,} | Süre: {time.time() - start_t:.2f}s | Hedef: {hedef_metni}")
            for i, data in enumerate(havuz, 1):
                k, is_gold = data["kolon"], data["is_gold"]
                h = ""
                for n in k:
                    if n in faz_bankolari_global:
                        h += f"<div class='top-karanlik' title='Faz Bankosu'>{n:02d}</div>"
                    elif is_gold:
                        h += f"<div class='top-gold' title='Perkolasyon'>{n:02d}</div>"
                    else:
                        h += f"<div class='top-standart'>{n:02d}</div>"

                rozet = "<span style='color:#FFD600; font-weight:bold;'>💎 ALTIN KOLON</span>" if is_gold else ""
                st.markdown(
                    f"<div class='kolon-satir'><div class='kolon-baslik'>Mod 5 (Puan:{sum(k)})</div><div>{h}</div><div style='margin-left:auto;'>{rozet}</div></div>",
                    unsafe_allow_html=True)
        else:
            st.warning("Bulunamadı, tekrar deneyin.")

# -------------------------------------------------------------------------
# SEKME 6: 🧠 YAPAY ZEKA TAHLİLİ VE ÖĞRENME (KUANTUM DESTEKLİ)
# -------------------------------------------------------------------------
with tabs[5]:
    st.markdown("### 🧠 AI Karne, Kuantum Röntgen ve Öğrenme Modülü")
    st.info(
        "Çıkan sonuçları girin. Hem AI sınır trendleri güncellenecek, hem de kolonun Kuantum Fizik analizleri yapılacaktır.")

    tahlil_girdi = st.text_input("Çekiliş Sonucunu Girin (Aralarında virgül veya boşluk ile):",
                                 placeholder="Örn: 16, 18, 22, 31, 37, 55")

    if st.button("🔍 ÇEKİLİŞİ RÖNTGENLE VE VERİTABANINA KAYDET", type="primary"):
        try:
            import re

            sayilar = sorted([int(s) for s in re.findall(r'\d+', tahlil_girdi)])
            if len(sayilar) != 6 or not all(1 <= n <= 60 for n in sayilar):
                st.error("Lütfen 1-60 arasında tam 6 sayı girin.")
            else:
                T1, T2, T3, T4, T5, T6 = sayilar
                toplam = sum(sayilar)
                H1, H2 = T1 + T2 + T3, T4 + T5 + T6
                fraktal = H2 / H1 if H1 > 0 else 0
                y1, y2, y3 = T1 + T6, T2 + T5, T3 + T4
                sapma = max([y1, y2, y3]) - min([y1, y2, y3])
                dis, orta, cekirdek = T6 - T1, T5 - T2, T4 - T3
                mat1 = dis / (orta if orta > 0 else 1)
                mat2 = orta / (cekirdek if cekirdek > 0 else 1)
                max_f = max([T2 - T1, T3 - T2, T4 - T3, T5 - T4, T6 - T5])

                # Kuantum Hesaplamaları
                manyetik_enerji = sum(spins_global.get(num, 0) for num in sayilar) if spins_global else 0
                walk_len = calc_walk_len(sayilar)
                is_gold = is_percolated(sayilar)

                # VERİ TABANINA KAYIT
                log_sonuc_kaydet(sayilar, H1, H2, fraktal, sapma, mat1, mat2, max_f)

                st.markdown(f"#### 📊 Analiz Edilen Kolon: {sayilar}")
                st.success(
                    "✅ Çekiliş sonuçları yapay zekanın öğrenme veri tabanına (ai_loss_log.csv) başarıyla kaydedildi!")

                s = SINIRLAR['mod4']
                rapor = []

                # Klasik AI Sınırları
                rapor.append(("Altın Kesi Toplam Puanı (145-221)", 145 <= toplam <= 221, f"Toplam: {toplam}"))
                rapor.append(
                    ("H1 (AI Dinamik Basınç: {} - {})".format(s['H1'][0], s['H1'][1]), s['H1'][0] <= H1 <= s['H1'][1],
                     f"H1: {H1}"))
                rapor.append(
                    ("H2 (AI Dinamik Basınç: {} - {})".format(s['H2'][0], s['H2'][1]), s['H2'][0] <= H2 <= s['H2'][1],
                     f"H2: {H2}"))
                rapor.append(("Fraktal Oran Sabiti ({:.2f} - {:.2f})".format(s['fraktal'][0], s['fraktal'][1]),
                              s['fraktal'][0] <= fraktal <= s['fraktal'][1], f"Oran: {fraktal:.2f}"))
                rapor.append(
                    ("Yörünge Simetrisi (Max Sapma: {})".format(s['sapma']), sapma <= s['sapma'], f"Sapma: {sapma}"))
                rapor.append(("Matruşka Dış Kafes Oranı ({:.2f} - {:.2f})".format(s['mat1'][0], s['mat1'][1]),
                              s['mat1'][0] <= mat1 <= s['mat1'][1], f"Oran: {mat1:.2f}"))
                rapor.append(("Kuantum Sıçraması (Max Boşluk: {})".format(s['bosluk']), max_f <= s['bosluk'],
                              f"Maks Boşluk: {max_f}"))

                # Kuantum Fizik Sınırları
                rapor.append(("Manyetik Nötralizasyon (İsing Spin)", manyetik_enerji in [-2, 0, 2],
                              f"Enerji: {manyetik_enerji} (Sadece 0 veya +/- 2 kabul edilir)"))
                rapor.append(("Kendinden Kaçınan Yürüyüş (SAW Uzunluğu)", 13.0 <= walk_len <= 23.0,
                              f"Mesafe: {walk_len:.2f} (İdeal: 13-23 birim)"))
                rapor.append(("Karanlık Madde Ağı (Perkolasyon)", is_gold,
                              f"Durum: {'Geçerli (Altın Kolon!)' if is_gold else 'Bağlar Zayıf (Koptu)'}"))

                gecen_sayisi = sum(1 for r in rapor if r[1])
                st.progress(gecen_sayisi / len(rapor))
                st.markdown(f"**Karne Notu: {gecen_sayisi} / {len(rapor)} Kuraldan Geçti**")

                for isim, durum, aciklama in rapor:
                    if durum:
                        st.markdown(f"✅ <span class='tahlil-basarili'>{isim}</span> ➔ {aciklama}",
                                    unsafe_allow_html=True)
                    else:
                        if "Karanlık Madde" in isim:
                            st.markdown(
                                f"⚠️ <span style='color:#FF9800; font-weight:bold;'>{isim}</span> ➔ <span style='color:gray'>Uyarı ({aciklama})</span>",
                                unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f"❌ <span class='tahlil-hatali'>{isim}</span> ➔ <span style='color:gray'>ÇUVALLADI ({aciklama})</span>",
                                unsafe_allow_html=True)

                if gecen_sayisi >= len(rapor) - 2:
                    st.success("🤖 AI Çıkarımı: Kusursuz! Çekiliş Mod 4 ve Kuantum Fizik yasalarına tam oturdu.")
                else:
                    st.error(
                        "🤖 AI Çıkarımı: Sınırlar zorlandı. Sistem bu sapmaları öğrenip bir sonraki çekilişte sınırlarını esnetecektir.")

        except Exception as e:
            st.error(f"Lütfen sayıları doğru formatta girin. Hata: {e}")