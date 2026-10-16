import pandas as pd
import requests

print("🛰️ Lotobil sunucusuna bağlanılıyor...")
url = "https://lotobil.com/On-Numara-Butun-Sonuc-Listesi"

# Sitenin bot olduğumuzu anlamaması için standart bir Chrome tarayıcı kimliği gönderiyoruz
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Sayfadaki tüm tabloları pandas ile çek
    tablolar = pd.read_html(response.text)

    # En çok satırı olan tabloyu seç (Tüm çekilişlerin olduğu ana tablo)
    ana_tablo = max(tablolar, key=len)

    print(f"✅ Tablo bulundu! Toplam {len(ana_tablo)} satır çekiliş verisi çekildi.")

    # Veriyi CSV olarak kaydet (Algoritmamıza uygun olması için sekme boşluklu kaydediyoruz)
    dosya_adi = "On_Numara_Ham.csv"
    ana_tablo.to_csv(dosya_adi, sep='\t', index=False)
    print(f"📁 Veri başarıyla '{dosya_adi}' olarak kaydedildi!")

    # Sütun yapılarını görmek için ilk 3 satırı yazdır
    print("\nVerinin Başlıkları ve İlk Satırı:")
    print(ana_tablo.head(1))

except Exception as e:
    print(f"❌ Bir hata oluştu: {e}")