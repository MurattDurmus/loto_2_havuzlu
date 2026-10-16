import streamlit as st
import random
import time
import pandas as pd
import numpy as np
import os
from collections import Counter
import datetime
import matplotlib.pyplot as plt

# =========================================================================
# SAYFA AYARLARI VE ŞIK TASARIM (CSS)
# =========================================================================
st.set_page_config(page_title="On Numara AI Quant Terminali", page_icon="🎱", layout="wide")

st.markdown('''
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {font-size: 1.05rem; font-weight: bold;}
    .bant-kutu {padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 8px solid;}
    .bant-ust {background-color: #2b1114; border-color: #FF1744;}
    .bant-merkez {background-color: #122919; border-color: #00E676;}
    .bant-alt {background-color: #111d2b; border-color: #00B0FF;}
    .uyari-rozet {
        background-color: #FF9800; color: black; padding: 4px 10px; 
        border-radius: 5px; font-size: 13px; font-weight: bold; 
        margin-left: 15px; display: inline-block; box-shadow: 0 0 10px rgba(255,152,0,0.5);
    }
    .kolon-satir {
        display: flex; align-items: center; background-color: #1E1E1E; 
        padding: 8px 15px; border-radius: 6px; margin-bottom: 6px; border: 1px solid #333;
    }
    .kolon-baslik {width: 140px; font-weight: bold; color: #aaa; font-size: 14px;}
    .top-standart {
        display: inline-block; width: 30px; height: 30px; line-height: 30px; 
        border-radius: 50%; background-color: #9C27B0; color: white; 
        text-align: center; font-weight: bold; font-size: 14px; margin-right: 4px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    .top-cekirdek {
        display: inline-block; width: 22px; height: 22px; line-height: 22px; 
        border-radius: 50%; background-color: #424242; color: #00E676; 
        text-align: center; font-weight: bold; font-size: 11px; margin-right: 2px;
    }
    .top-karadelik {
        display: inline-block; width: 22px; height: 22px; line-height: 22px; 
        border-radius: 50%; background-color: #FF1744; color: white; 
        text-align: center; font-weight: bold; font-size: 11px; margin-right: 2px;
        box-shadow: 0 0 8px #FF1744;
    }
    .tahlil-basarili {color: #00E676; font-weight: bold;}
    .tahlil-hatali {color: #FF1744; font-weight: bold; text-decoration: line-through;}
    </style>
''', unsafe_allow_html=True)


# =========================================================================
# SABİTLER VE VERİ OKUMA
# =========================================================================
@st.cache_data
def get_veri():
    if not os.path.exists('On_Numara_Kusursuz.csv'): return None
    df = pd.read_csv('On_Numara_Kusursuz.csv', delimiter='\t')
    cols = [f'T{i}' for i in range(1, 23)]
    df['Toplam'] = df[cols].sum(axis=1)
    return df


df_global = get_veri()


# =========================================================================
# %33 EŞİT İHTİMALLİ 3 BANT RADARI VE UYARI MOTORU
# =========================================================================
def bant_ihtimal_hesapla(df):
    if df is None or len(df) < 20: return None, None, None, 0, None

    def get_bant(t):
        if t <= 850:
            return 'Alt'
        elif 851 <= t <= 932:
            return 'Orta'
        else:
            return 'Ust'

    df_temp = df.copy()
    df_temp['Bant'] = df_temp['Toplam'].apply(get_bant)
    son_20_list = df_temp.tail(20)['Bant'].tolist()

    counts = Counter(son_20_list)
    # Temel olasılıklar tam %33.33'tür
    base_p = {'Alt': 33.33, 'Orta': 33.33, 'Ust': 33.33}
    expected = {'Alt': 6.66, 'Orta': 6.66, 'Ust': 6.66}  # 20 çekilişte beklenen adet

    diff = {k: expected[k] - counts.get(k, 0) for k in base_p}

    son_bantlar = son_20_list[::-1]
    aktif_seri_bandi = son_bantlar[0]
    seri_sayisi = 0
    for b in son_bantlar:
        if b == aktif_seri_bandi:
            seri_sayisi += 1
        else:
            break

    raw_p = {k: max(5, base_p[k] + diff[k] * 4.0) for k in base_p}

    if seri_sayisi >= 2 and aktif_seri_bandi in raw_p:
        raw_p[aktif_seri_bandi] = max(5, raw_p[aktif_seri_bandi] - (seri_sayisi * 5))

    total_raw = sum(raw_p.values())
    final_p = {k: (v / total_raw) * 100 for k, v in raw_p.items()}

    return max(final_p, key=final_p.get), final_p, aktif_seri_bandi, seri_sayisi, df_temp


# =========================================================================
# ÇOKLU EVRENLER VE KARA DELİK ALGORİTMASI
# =========================================================================
def dinamik_kuantum_rezonans(df):
    if df is None: return [], 0
    max_idx = len(df) - 1
    cols = [f'T{i}' for i in range(1, 23)]

    timelines = {
        'Kronolojik': [set(df.iloc[max_idx - l][cols]) for l in range(1, 11) if max_idx - l >= 0],
        'Fibonacci': [set(df.iloc[max_idx - l][cols]) for l in [1, 2, 3, 5, 8, 13, 21, 34, 55, 89][:10] if
                      max_idx - l >= 0],
        'Kadim_19': [set(df.iloc[max_idx - l][cols]) for l in [i * 19 for i in range(1, 11)] if max_idx - l >= 0],
        'Asal_Uzay': [set(df.iloc[max_idx - l][cols]) for l in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][:10] if
                      max_idx - l >= 0]
    }

    all_cold = []
    for name, seq in timelines.items():
        seen = set()
        for d in seq: seen.update(d)
        all_cold.extend(list(set(range(1, 81)) - seen))

    cold_counts = Counter(all_cold)
    if cold_counts:
        max_basinc = max(cold_counts.values())
        karanlik_sayilar = [num for num, count in cold_counts.items() if count == max_basinc]
    else:
        max_basinc, karanlik_sayilar = 0, []

    return karanlik_sayilar, max_basinc


# =========================================================================
# YAPAY ZEKA DİNAMİK ÖĞRENME (AI LOGGING)
# =========================================================================
AI_LOG_FILE = 'on_numara_ai_log.csv'

SINIRLAR = {
    'mod4': {'H1': (193, 265), 'H2': (620, 695), 'fraktal': (2.55, 3.28), 'sapma': 17, 'mat1': (1.71, 2.18),
             'mat2': (8.17, 27.0), 'bosluk': 12},
    'mod5': {'H1': (161, 308), 'H2': (581, 728), 'fraktal': (2.25, 3.88), 'sapma': 23, 'mat1': (1.53, 2.54),
             'mat2': (4.89, 41.0), 'bosluk': 14}
}
ai_mesaji = ""


def log_sonuc_kaydet(sayilar, Tpl, H1, H2, fraktal, sapma, mat1, mat2, bosluk):
    df_log = pd.DataFrame([{
        'Tarih': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Kolon': str(sayilar), 'Toplam': Tpl, 'H1': H1, 'H2': H2, 'Fraktal': round(fraktal, 2),
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
            trend = df_log.tail(10)
            t_H1, t_H2 = trend['H1'].mean(), trend['H2'].mean()
            std_H1, std_H2 = max(10, trend['H1'].std()), max(15, trend['H2'].std())

            y_H1_min, y_H1_max = int((SINIRLAR['mod4']['H1'][0] + (t_H1 - std_H1)) / 2), int(
                (SINIRLAR['mod4']['H1'][1] + (t_H1 + std_H1)) / 2)
            y_H2_min, y_H2_max = int((SINIRLAR['mod4']['H2'][0] + (t_H2 - std_H2)) / 2), int(
                (SINIRLAR['mod4']['H2'][1] + (t_H2 + std_H2)) / 2)

            SINIRLAR['mod4']['H1'] = (y_H1_min, y_H1_max)
            SINIRLAR['mod4']['H2'] = (y_H2_min, y_H2_max)
            SINIRLAR['mod5']['H1'] = (y_H1_min - 20, y_H1_max + 20)
            SINIRLAR['mod5']['H2'] = (y_H2_min - 30, y_H2_max + 30)
            ai_mesaji = f"*(🤖 AI Trend Optimizasyonu Aktif! H1:{y_H1_min}-{y_H1_max} | H2:{y_H2_min}-{y_H2_max})*"
    except:
        pass


dinamik_sinir_guncelle()


# =========================================================================
# ON NUMARA KATI & ESNEK SİMETRİ MOTORLARI
# =========================================================================
def on_numara_denetim(kolon_22, mod='mod4', hedef_toplam=None):
    s = SINIRLAR[mod]
    toplam = sum(kolon_22)

    if hedef_toplam and not (hedef_toplam[0] <= toplam <= hedef_toplam[1]): return False
    if not (9 <= sum(1 for n in kolon_22 if n % 2 != 0) <= 13): return False

    H1, H2 = sum(kolon_22[:11]), sum(kolon_22[11:])
    if not (s['H1'][0] <= H1 <= s['H1'][1]) or not (s['H2'][0] <= H2 <= s['H2'][1]): return False

    fraktal = H2 / H1 if H1 > 0 else 0
    if not (s['fraktal'][0] <= fraktal <= s['fraktal'][1]): return False

    sapma = max([kolon_22[i] + kolon_22[21 - i] for i in range(11)]) - min(
        [kolon_22[i] + kolon_22[21 - i] for i in range(11)])
    if sapma > s['sapma']: return False

    dis, orta, cekirdek = kolon_22[21] - kolon_22[0], kolon_22[16] - kolon_22[5], kolon_22[11] - kolon_22[10]
    if cekirdek == 0 or orta == 0: return False
    if not (s['mat1'][0] <= dis / orta <= s['mat1'][1]) or not (
            s['mat2'][0] <= orta / cekirdek <= s['mat2'][1]): return False

    if max([kolon_22[i + 1] - kolon_22[i] for i in range(21)]) > s['bosluk']: return False

    return True


def kupon_olustur(cekirdek_22, adet=5):
    kuponlar = []
    for _ in range(adet):
        for _ in range(200):
            aday_10 = sorted(random.sample(cekirdek_22, 10))
            if 4 <= sum(1 for x in aday_10 if x % 2 != 0) <= 6 and 350 <= sum(aday_10) <= 500:
                kuponlar.append(aday_10)
                break
    return kuponlar


# =========================================================================
# ANA ARAYÜZ
# =========================================================================
st.title("🎱 On Numara AI Quant Terminali Supreme")
st.caption("Veritabanı: On_Numara_Kusursuz.csv | Kozmik Ağ + %33.3 Eşit İhtimalli Bant Radarı Aktif")
if ai_mesaji: st.markdown(f"<span style='color:#00B0FF; font-weight:bold;'>{ai_mesaji}</span>", unsafe_allow_html=True)

tabs = st.tabs(["🚀 Eşit Bant Radarı & Grafikler", "🎯 Mod 4 (KATI)", "🪐 Mod 5 (ESNEK)", "🧠 AI Tahlil & Log"])

en_iyi_bant, ihtimaller, aktif_seri_bandi, seri_sayisi, df_temp = bant_ihtimal_hesapla(df_global)
karadelikler, basinc = dinamik_kuantum_rezonans(df_global)

# -------------------------------------------------------------------------
# SEKME 1: BANT RADARI VE KÜTLEÇEKİM GRAFİĞİ
# -------------------------------------------------------------------------
with tabs[0]:
    if df_global is None:
        st.error("Veritabanı bulunamadı!")
    elif ihtimaller:
        st.markdown("### 📡 3'lü Eşit İhtimalli Kuantum Bant Sistemi (Aktif Radar)")


        def get_warning(band_name):
            if aktif_seri_bandi == band_name and seri_sayisi >= 2:
                return f"<div class='uyari-rozet'>⚠️ {seri_sayisi} KEZ ÜST ÜSTE GELDİ! (İhtimal Düştü)</div>"
            return ""


        st.markdown(f'''
        <div class="bant-kutu bant-ust">
            <h4 style="margin:0;">🔴 ÜST BANT (>932) — İhtimal: %{ihtimaller['Ust']:.1f} {get_warning('Ust')}</h4>
            <span style="color:#aaa; font-size:13px; font-weight:normal;">Doğal olasılık: %33.33 | AI hesaplamasıyla gecikme bazlı güncel ihtimal.</span>
        </div>
        <div class="bant-kutu bant-merkez">
            <h4 style="margin:0;">🟢 ORTA BANT (851 - 932) — İhtimal: %{ihtimaller['Orta']:.1f} {get_warning('Orta')}</h4>
            <span style="color:#aaa; font-size:13px; font-weight:normal;">Doğal olasılık: %33.33 | AI hesaplamasıyla gecikme bazlı güncel ihtimal.</span>
        </div>
        <div class="bant-kutu bant-alt">
            <h4 style="margin:0;">🔵 ALT BANT (<851) — İhtimal: %{ihtimaller['Alt']:.1f} {get_warning('Alt')}</h4>
            <span style="color:#aaa; font-size:13px; font-weight:normal;">Doğal olasılık: %33.33 | AI hesaplamasıyla gecikme bazlı güncel ihtimal.</span>
        </div>
        ''', unsafe_allow_html=True)

        k_html = "".join([f"<span class='top-karadelik'>{n:02d}</span>" for n in karadelikler])
        st.markdown(
            f"**🌌 12 Boyutlu Çoklu Evren Analizi:** {len(karadelikler)} adet Kara Delik bulundu (Basınç: {basinc}): {k_html if k_html else 'Yok'}",
            unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 Son 30 Çekilişin KütleÇekim (Toplam Puan) Grafiği")

        try:
            fig, ax = plt.subplots(figsize=(12, 4.5))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#0e1117')

            son_30 = df_temp.tail(30).reset_index(drop=True)

            # Eşit %33 Koridorlarını Çiz
            ax.axhspan(933, max(1100, son_30['Toplam'].max() + 50), color='#FF1744', alpha=0.15,
                       label='Üst Bant (>932)')
            ax.axhspan(851, 932, color='#00E676', alpha=0.15, label='Orta Bant (851-932)')
            ax.axhspan(min(600, son_30['Toplam'].min() - 50), 850, color='#00B0FF', alpha=0.15, label='Alt Bant (<851)')

            ax.plot(son_30.index, son_30['Toplam'], marker='o', color='#FFA000', linewidth=2, markersize=7)

            ax.set_title("Terminalin Toplam Puan Dalgalanması (%33 Eşit Dağılım)", color='white', pad=15)
            ax.set_xlabel("Son 30 Çekiliş (Eskiden Yeniye)", color='white')
            ax.set_ylabel("KütleÇekim Puanı", color='white')
            ax.tick_params(colors='white')
            ax.grid(axis='y', alpha=0.15, linestyle='--')
            ax.legend(facecolor='#1E1E1E', edgecolor='white', labelcolor='white', loc='upper left')

            st.pyplot(fig)
        except Exception as e:
            st.error("Grafik oluşturulamadı.")

# -------------------------------------------------------------------------
# SEKME 2 & 3: MOD 4 VE MOD 5 KUPON ÜRETİMİ
# -------------------------------------------------------------------------
for i, mod_adi, tab_ref in [(1, 'mod4', tabs[1]), (2, 'mod5', tabs[2])]:
    with tab_ref:
        mod_label = "KATI (Mod 4)" if mod_adi == 'mod4' else "ESNEK (Mod 5)"
        st.markdown(f"### {'🎯' if mod_adi == 'mod4' else '🪐'} {mod_label} Çekirdek Simülasyonu")

        radar_teklif = False
        if ihtimaller:
            radar_teklif = st.checkbox(f"Radar Önerisini ({en_iyi_bant} Bant) Kabul Et", key=f"r_{mod_adi}")

        kolon_sayisi = st.slider("Üretilecek 10'luk Bilet Sayısı:", 5, 20, 5, key=f"slider_{mod_adi}")

        if st.button(f"🔮 ÇEKİRDEK VE BİLETLERİ ÜRET ({mod_label})", type="primary", key=f"btn_{mod_adi}"):
            start_t = time.time()

            if radar_teklif:
                if en_iyi_bant == 'Alt':
                    hedef = (10, 850)
                elif en_iyi_bant == 'Orta':
                    hedef = (851, 932)
                else:
                    hedef = (933, 1700)
                hedef_m = f"{en_iyi_bant} Bant Kilitli"
            else:
                hedef = (10, 1700)
                hedef_m = "Tüm Evren"

            sec_k = min(3, len(karadelikler))
            aktif_k = random.sample(karadelikler, sec_k) if sec_k > 0 else []
            kalan_sayilar = list(set(range(1, 81)) - set(aktif_k))

            cekirdek = None
            cop = 0
            with st.spinner("Evren Taranıyor... Kara Delikler Entegre Ediliyor..."):
                for _ in range(5000000):
                    aday_22 = sorted(aktif_k + random.sample(kalan_sayilar, 22 - sec_k))
                    if on_numara_denetim(aday_22, mod=mod_adi, hedef_toplam=hedef):
                        cekirdek = aday_22
                        break
                    else:
                        cop += 1

            if cekirdek:
                st.success(
                    f"✅ 22'lik Kusursuz Çekirdek Bulundu! Çöp: {cop:,} | Süre: {time.time() - start_t:.2f}s | Hedef: {hedef_m}")
                c_html = "".join(
                    [f"<div class='{'top-karadelik' if n in aktif_k else 'top-cekirdek'}'>{n:02d}</div>" for n in
                     cekirdek])
                st.markdown(
                    f"<div style='background-color:#000; padding:10px; border-radius:5px;'><b>🧬 22'lik Kaynak Çekirdek:</b><br>{c_html}</div>",
                    unsafe_allow_html=True)
                st.divider()

                biletler = kupon_olustur(cekirdek, adet=kolon_sayisi)
                st.markdown("#### 🎫 Oynanabilir 10'luk Biletleriniz:")
                for idx, b in enumerate(biletler, 1):
                    b_html = "".join(
                        [f"<div class='{'top-karadelik' if n in aktif_k else 'top-standart'}'>{n:02d}</div>" for n in
                         b])
                    st.markdown(
                        f"<div class='kolon-satir'><div class='kolon-baslik'>Bilet {idx}</div><div>{b_html}</div></div>",
                        unsafe_allow_html=True)
            else:
                st.warning("Kurallar zorlayıcı oldu, çekirdek bulunamadı. Tekrar deneyin.")

# -------------------------------------------------------------------------
# SEKME 4: 🧠 YAPAY ZEKA TAHLİLİ
# -------------------------------------------------------------------------
with tabs[3]:
    st.markdown("### 🧠 AI Karne ve Veritabanı Öğrenme Modülü")
    tahlil_girdi = st.text_input("Gerçekleşen 22 Sayıyı Girin:")

    if st.button("🔍 22'LİK KÜTLEYİ RÖNTGENLE", type="primary"):
        import re

        sayilar = sorted([int(s) for s in re.findall(r'\d+', tahlil_girdi)])
        if len(sayilar) != 22 or not all(1 <= n <= 80 for n in sayilar):
            st.error("Lütfen 1-80 arasında tam 22 adet sayı girin.")
        else:
            Tpl = sum(sayilar)
            H1, H2 = sum(sayilar[:11]), sum(sayilar[11:])
            fraktal = H2 / H1 if H1 > 0 else 0
            yorungeler = [sayilar[i] + sayilar[21 - i] for i in range(11)]
            sapma = max(yorungeler) - min(yorungeler)
            dis, orta, cekirdek = sayilar[21] - sayilar[0], sayilar[16] - sayilar[5], sayilar[11] - sayilar[10]
            mat1 = dis / (orta if orta > 0 else 1)
            mat2 = orta / (cekirdek if cekirdek > 0 else 1)
            bosluk = max([sayilar[i + 1] - sayilar[i] for i in range(21)])

            log_sonuc_kaydet(sayilar, Tpl, H1, H2, fraktal, sapma, mat1, mat2, bosluk)
            st.success("✅ Log başarıyla AI veri tabanına eklendi!")

            s = SINIRLAR['mod4']
            rapor = []
            rapor.append(
                ("H1 (AI Dinamik Basınç: {} - {})".format(s['H1'][0], s['H1'][1]), s['H1'][0] <= H1 <= s['H1'][1],
                 f"H1: {H1}"))
            rapor.append(
                ("H2 (AI Dinamik Basınç: {} - {})".format(s['H2'][0], s['H2'][1]), s['H2'][0] <= H2 <= s['H2'][1],
                 f"H2: {H2}"))
            rapor.append(("Fraktal Oran ({:.2f} - {:.2f})".format(s['fraktal'][0], s['fraktal'][1]),
                          s['fraktal'][0] <= fraktal <= s['fraktal'][1], f"Oran: {fraktal:.2f}"))
            rapor.append(
                ("Yörünge Simetrisi (Max Sapma: {})".format(s['sapma']), sapma <= s['sapma'], f"Sapma: {sapma}"))
            rapor.append(("Matruşka Dış Kafes ({:.2f} - {:.2f})".format(s['mat1'][0], s['mat1'][1]),
                          s['mat1'][0] <= mat1 <= s['mat1'][1], f"Oran: {mat1:.2f}"))
            rapor.append(("Kuantum Sıçraması (Max Boşluk: {})".format(s['bosluk']), bosluk <= s['bosluk'],
                          f"Maks Boşluk: {bosluk}"))

            gecen = sum(1 for r in rapor if r[1])
            st.progress(gecen / len(rapor))
            for isim, durum, aciklama in rapor:
                if durum:
                    st.markdown(f"✅ <span class='tahlil-basarili'>{isim}</span> ➔ {aciklama}", unsafe_allow_html=True)
                else:
                    st.markdown(
                        f"❌ <span class='tahlil-hatali'>{isim}</span> ➔ <span style='color:gray'>ÇUVALLADI ({aciklama})</span>",
                        unsafe_allow_html=True)