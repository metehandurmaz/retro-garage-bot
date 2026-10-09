# Retro Garage bot

Lisansı açık klasik araba videolarını bulur, 1080x1920 Shorts'a çevirir ve YouTube kanalına günde 3 tane yükler. Başlık, açıklama ve etiketleri kendisi doldurur.

- Kaynaklar: Pixabay, Wikimedia Commons, Internet Archive. Pexels anahtarı `.env` içine yazılırsa o da kullanılır.
- Yalnızca Pixabay/Pexels lisansı, kamu malı, CC0 ve CC BY kabul edilir. CC BY-SA, NC, ND ve lisanssız klipler elenir.
- Sessiz kliplere `music/bed.mp3` eklenir. Motor sesi olan kliplere müzik eklenmez.
- Aynı klip iki kez yüklenmez (`data/seen.sqlite`).

## Hikâyeli Shorts

Günün 1. ve 3. yüklemesi hikâyeli video, 2. yüklemesi klip olur. Hikâyeli video: Türkçe yapay zekâ seslendirmesi (`edge-tts`), tek kelimelik sarı altyazı (Anton yazı tipi, OFL) ve Wikimedia Commons'taki lisanslı fotoğraflardan hızlı kesmeler.

- Hikâyeler `src/stories.py` içinde. Yeni hikâye eklemek için listeye bir `_s(...)` satırı eklemek yeterli.
- Deneme: `python -m src.story_video --id mustang-1964` (yüklemez, `out/` içine yazar).
- Hikâyeler bitince bot sadece klip yüklemeye devam eder.

## Otomatik güncelleme

Zamanlanmış görev her çalışmada önce `scripts/update.ps1` ile GitHub'daki son kodu çeker, sonra yükleme yapar. `.env`, `secrets/`, `data/`, `music/` ve `logs/` repoda olmadığı için güncellemeden etkilenmez. Güncelleme kaydı: `logs/update.log`.

Eski bir kurulumu bu moda geçirmek için sunucuda yönetici PowerShell'e bir kez yapıştır:

```powershell
[Net.ServicePointManager]::SecurityProtocol='Tls12'; iex (irm https://raw.githubusercontent.com/metehandurmaz/retro-garage-bot/main/scripts/bootstrap.ps1)
```

## Windows sunucuya kurulum

1. Sunucuya Uzak Masaüstü ile bağlan.
2. [python.org](https://www.python.org/downloads/) adresinden Python 3.12 veya üstünü kur. Kurulumda **Add python.exe to PATH** kutusunu işaretle.
3. Bu klasörü sunucuya kopyala, örneğin `C:\retro-garage-bot`.
4. PowerShell'i o klasörde aç:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
   ```

   Bu betik Python paketlerini ve `ffmpeg`'i kurar.
5. Dosyaları yerleştir:
   - Google Cloud'dan indirdiğin OAuth JSON dosyası: `secrets\client_secret.json`
   - Müzik: `music\bed.mp3`
   - `.env` içine `PIXABAY_API_KEY` değerini yaz.
6. YouTube iznini bir kez ver. Tarayıcı açılır, Retro Garage kanalının Google hesabıyla gir:

   ```powershell
   .\.venv\Scripts\python.exe -m src.authorize
   ```

   "Google bu uygulamayı doğrulamadı" uyarısı çıkarsa **Gelişmiş → devam et** de. Bu senin kendi uygulaman.
7. Yüklemeden deneme yap. Videolar ve başlıklar `out\` klasörüne yazılır:

   ```powershell
   .\.venv\Scripts\python.exe -m src.main --dry-run --count 2
   ```

8. Tek bir gerçek yükleme dene:

   ```powershell
   .\.venv\Scripts\python.exe -m src.main --count 1
   ```

9. Zamanlayıcıyı kur. Her gün 10:00, 15:00 ve 20:00'de birer video yükler:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\install_task.ps1
   ```

   Saatleri değiştirmek için: `-Times "09:00","14:00","21:00"`.

Kayıtlar `logs\bot.log` dosyasında.

## Google Cloud tarafında iki önemli ayar

- **Uygulamayı yayına al.** Google Auth Platform → Audience → **Publish app**. Uygulama "Testing" durumunda kalırsa izin 7 günde bir düşer ve bot yükleyemez.
- **API denetimi.** Google, doğrulanmamış projelerden API ile yüklenen videoları "özel" olarak kilitleyebilir. İlk yükleme özel görünürse [YouTube API denetim formunu](https://support.google.com/youtube/contact/yt_api_form) doldur. Onay gelene kadar videolar özel kalabilir.

## Ayarlar (`.env`)

| Ayar | Anlamı |
| --- | --- |
| `DAILY_LIMIT` | Günde en fazla kaç video (varsayılan 3) |
| `VIDEOS_PER_RUN` | Her çalışmada kaç video (varsayılan 1) |
| `PRIVACY_STATUS` | `public`, `unlisted` veya `private` |
| `MUSIC_CREDIT` | Müzik atıf istiyorsa açıklamaya yazılacak satır |
| `SILENCE_DB` | Bu seviyenin altındaki klipler sessiz sayılır (varsayılan -45) |
