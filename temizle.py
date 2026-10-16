import pandas as pd
import numpy as np

print("Veri temizliği başlatılıyor...")

# 1. Ham veriyi oku ve gereksiz başlıkları atla
temiz_veriler = []
with open('OnNumara.csv', 'r', encoding='utf-8') as f:
    for satir in f:
        satir = satir.strip()
        if not satir or satir.startswith('202') or satir.startswith('199') or satir.startswith('Hft'):
            continue
        parcalar = satir.split(';')
        if len(parcalar) >= 23:
            temiz_veriler.append(parcalar[:23])

df = pd.DataFrame(temiz_veriler, columns=['Hft'] + [f'T{i}' for i in range(1, 23)])

# 2. Tüm verileri sayısal formata (integer) çevir
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna().astype(int)

# 3. Her çekilişi küçükten büyüğe yatay olarak sırala
sayi_sutunlari = [f'T{i}' for i in range(1, 23)]
df[sayi_sutunlari] = np.sort(df[sayi_sutunlari].values, axis=1)

# 4. Hatalı çekilişleri (80'den büyük sayı içerenler veya aynı sayının 2 kez yazıldığı satırlar) sil
gecerli_satirlar = []
for idx, row in df.iterrows():
    degerler = row[sayi_sutunlari].values
    if len(set(degerler)) == 22 and max(degerler) <= 80:
        gecerli_satirlar.append(True)
    else:
        gecerli_satirlar.append(False)

df_kusursuz = df[gecerli_satirlar].copy()

# 5. Kusursuz dosyayı Streamlit'in okuyacağı formatta kaydet
df_kusursuz.to_csv('On_Numara_Kusursuz.csv', sep='\t', index=False)
print(f"✅ İşlem tamam! {len(df_kusursuz)} adet kusursuz çekiliş 'On_Numara_Kusursuz.csv' olarak kaydedildi.")