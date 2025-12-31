#!/bin/bash

# Renkler
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}====== SANTA 2024: ADAPTIVE OPTIMIZER BAŞLATILIYOR ======${NC}"
echo "Hedef: 70.920 ve altı (Antarktika)"
echo "Çıkmak için: Ctrl+C"
echo "---------------------------------------------------------"

# Çalışma dizinine git
cd "$(dirname "$0")"

# Gerekli dosyaların varlığını kontrol et
if [ ! -f "adaptive_continuous_optimizer.py" ] || [ ! -f "ultimate_optimizer_serial" ] || [ ! -f "verify_score" ]; then
    echo -e "${RED}HATA: Gerekli dosyalar (py, cpp exe) bulunamadı!${NC}"
    echo "Lütfen 'adaptive_continuous_optimizer.py', 'ultimate_optimizer_serial' ve 'verify_score' dosyalarının bu klasörde olduğundan emin ol."
    exit 1
fi

# Sonsuz döngü (Çökse bile tekrar başlar)
while true; do
    echo -e "${GREEN}>> Optimizer Başlatılıyor...${NC}"
    
    # Python scriptini çalıştır (-u ile anlık çıktı)
    python3 -u adaptive_continuous_optimizer.py
    
    # Eğer script bir şekilde durursa (hata vs), kullanıcıya bilgi ver ve tekrar başlat
    EXIT_CODE=$?
    echo -e "${RED}>> Script durdu (Kod: $EXIT_CODE). 3 saniye içinde yeniden başlatılıyor...${NC}"
    sleep 3
done
