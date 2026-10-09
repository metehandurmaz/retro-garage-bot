from dataclasses import dataclass


@dataclass(frozen=True)
class Story:
    id: str
    title: str
    text: str
    image_queries: tuple[str, ...]
    must_contain: tuple[str, ...]
    hashtags: tuple[str, ...]
    max_year: int | None = None
    exclude: tuple[str, ...] = ()


def _s(id, title, text, queries, must_contain, *tags, max_year=None, exclude=()):
    queries = (queries,) if isinstance(queries, str) else tuple(queries)
    return Story(id, title, " ".join(text.split()), queries, must_contain,
                 ("#shorts", "#klasikaraba", *tags, "#classiccars"), max_year, tuple(exclude))


STORIES = [
    _s("mustang-1964", "Bu Araba İlk Gün 22 Bin Sipariş Aldı! 😲 1964 Ford Mustang", """
        Bu araba tanıtıldığı ilk gün tam 22 bin sipariş aldı. Yıl 1964, adı Ford Mustang.
        Ford bir yılda yüz bin tane satmayı umuyordu. Ama ilk yılında 400 binden fazla sattı.
        Ve iki yıl dolmadan, bir milyonuncu Mustang banttan indi.
    """, "1965 Ford Mustang", ("mustang",), "#fordmustang", max_year=1970),

    _s("delorean", "Şirketi Battı, Sonra Dünyanın En Ünlü Arabası Oldu! DeLorean DMC-12", """
        Bu arabanın kaportası boyasız, paslanmaz çelikti. DeLorean DMC-12, Kuzey İrlanda'da üretildi
        ve kapıları martı kanadı gibi yukarı açılıyordu. Ama satışlar beklenenin çok altında kaldı.
        Şirket 1982'de battı, sadece 9 bin kadar üretildi. Üç yıl sonra bir film, onu dünyanın en ünlü arabası yaptı.
    """, "DeLorean DMC-12", ("delorean",), "#delorean", max_year=1983),

    _s("vw-beetle", "Bu Araba 65 Yıl Neredeyse Hiç Değişmedi! Volkswagen Beetle", """
        Bu araba tam 21 buçuk milyon kez üretildi. Volkswagen Beetle, 1930'larda Ferdinand Porsche tarafından tasarlandı.
        Adı Almanca'da halkın arabası demekti. Tasarımı neredeyse hiç değişmeden 65 yıl üretildi.
        Son klasik Beetle, 2003'te Meksika'da banttan indi.
    """, ("Volkswagen Beetle", "VW Käfer", "Volkswagen Type 1"), ("beetle", "käfer", "kafer"),
       "#vosvos", "#volkswagen", max_year=2003, exclude=("new beetle", "a5", "2012", "2019")),

    _s("ford-model-t", "12 Saatlik İş 1,5 Saate İndi! Ford Model T", """
        1913'te Henry Ford, otomobil üretimini sonsuza dek değiştirdi. Yürüyen bant sayesinde
        bir arabanın yapımı 12 saatten bir buçuk saate indi. Ford Model T o kadar ucuzladı ki,
        onu yapan işçiler bile satın alabildi. 1927'ye kadar 15 milyondan fazla üretildi.
    """, "Ford Model T", ("model t",), "#fordmodelt", max_year=1927),

    _s("citroen-ds", "Patlak Lastiklerle Cumhurbaşkanını Kurtardı! Citroen DS", """
        1962'de Fransa Cumhurbaşkanı de Gaulle'ün arabası kurşun yağmuruna tutuldu. Lastikler patladı
        ama araba durmadı. Çünkü bu bir Citroen DS'ti. Hidropnömatik süspansiyonu sayesinde
        patlak lastiklerle kaçmayı başardı. De Gaulle hayatını bu arabaya borçluydu.
    """, ("Citroen DS", "Citroen DS 19", "Citroen DS 21"),
       ("citroën ds", "citroen ds", "ds 19", "ds19", "ds 21", "ds21", "ds 23", "ds23"), "#citroen", max_year=1975),

    _s("citroen-2cv", "Tasarım Şartı: Yumurtaları Kırmadan Tarladan Geçecek! Citroen 2CV", """
        Bu arabanın tasarım şartı çok garipti. Sürülmüş bir tarlada, sepet dolusu yumurtayı kırmadan taşıyacaktı.
        Citroen 2CV, Fransız köylüleri için yapıldı. Şapkalı bir adam bile içine rahatça sığmalıydı.
        42 yıl boyunca neredeyse 4 milyon tane üretildi.
    """, "Citroen 2CV", ("2cv",), "#citroen", max_year=1990),

    _s("mini", "Benzin Karneyle Satılınca Doğdu! Klasik Mini", """
        1956'da Süveyş krizi yüzünden İngiltere'de benzin karneyle satılıyordu. Bunun üzerine Alec Issigonis
        çok az yakan küçük bir araba tasarladı. Adı Mini'ydi. Boyu sadece üç metreydi ama dört kişi rahatça sığıyordu.
        Bu minik araba 1964'te Monte Carlo Rallisi'ni kazanarak herkesi şaşırttı.
    """, ("Morris Mini Minor", "Mini Cooper 1965"), ("mini",), "#mini", "#minicooper", max_year=1990),

    _s("mercedes-300sl", "Bu Kapılar Süs Değil, Zorunluluktu! Mercedes 300 SL", """
        Bu arabanın kapıları yukarı doğru açılıyordu ama bu bir süs değildi. Mercedes 300 SL'nin
        borulu şasisi kapı eşiklerini çok yükseltti, normal kapı takılamadı. Martı kanadı kapılar böyle doğdu.
        1954'te tanıtılan bu araba, benzinli direkt enjeksiyonlu ilk seri üretim otomobildi.
    """, "Mercedes-Benz 300 SL Gullwing", ("300 sl", "300sl"), "#mercedes", max_year=1963),

    _s("jaguar-e-type", "Enzo Ferrari Bile Hayran Kaldı! Jaguar E-Type", """
        Enzo Ferrari'nin bu araba için gelmiş geçmiş en güzel otomobil dediği anlatılır.
        Jaguar E-Type, 1961'de Cenevre'de tanıtıldı. Saatte 240 kilometreye ulaşabiliyordu
        ve fiyatı rakiplerinin çok altındaydı. Bugün New York Modern Sanat Müzesi'nde bile bir tane sergileniyor.
    """, ("Jaguar E-Type Series 1", "Jaguar XKE", "Jaguar E-Type"), ("e-type", "e type", "etype", "xke"),
       "#jaguar", max_year=1975),

    _s("lamborghini-miura", "Bir Traktörcü Ferrari'ye Kızınca Doğdu! Lamborghini Miura", """
        Ferruccio Lamborghini bir traktör üreticisiydi ve bir Ferrari'si vardı. Arabanın debriyajı sürekli bozuluyordu.
        Anlatılana göre şikâyet ettiğinde Enzo Ferrari ona, sen traktörlerine bak, dedi.
        Lamborghini de kendi spor arabasını yapmaya karar verdi. 1966'da çıkan Miura, ilk süper arabalardan biri oldu.
    """, "Lamborghini Miura", ("miura",), "#lamborghini", max_year=1973),

    _s("corvette-1953", "İlk Yıl Sadece 300 Tane Yapıldı! 1953 Chevrolet Corvette", """
        1953'te ilk Corvette'lerden sadece 300 tane üretildi. Hepsi beyazdı ve hepsinin içi kırmızıydı.
        Kaportası çelik değil, fiberglastı ve elle yapılıyordu.
        Bugün Corvette, Amerika'nın en uzun süredir üretilen spor arabası.
    """, "1953 Chevrolet Corvette", ("corvette",), "#corvette", "#chevrolet", max_year=1955),

    _s("porsche-911", "Bu Arabanın Asıl Adı 911 Değildi! Porsche 911", """
        Bu arabanın asıl adı 911 değil, 901'di. Porsche arabayı tanıttığında Peugeot itiraz etti.
        Çünkü Peugeot, ortasında sıfır olan üç haneli araba isimlerini kullanıyordu.
        Porsche de sıfırı bire çevirdi. Ve 911 efsanesi böyle başladı.
    """, "1967 Porsche 911", ("911",), "#porsche", "#porsche911", max_year=1973),

    _s("fiat-500", "Boyu 3 Metre Bile Değildi, İtalya'yı Tekerleğe Bindirdi! Fiat 500", """
        Bu arabanın boyu üç metreyi bile bulmuyordu. Fiat 500, 1957'de savaş sonrası İtalya için yapıldı.
        Ucuzdu, az yakıyordu ve dar sokaklara sığıyordu. 18 yılda yaklaşık 4 milyon tane üretildi
        ve İtalya'yı tekerlekler üzerine bindirdi.
    """, ("Fiat 500 F", "Fiat 500 L 1970", "Fiat Nuova 500"),
       ("500 f", "500f", "500 l", "500l", "nuova 500", "giardiniera", *(f"{y} fiat 500" for y in range(1957, 1976))),
       "#fiat500", "#fiat",
       max_year=1975, exclude=("topolino",)),

    _s("anadol", "Türkiye'nin İlk Seri Üretim Otomobili! Anadol", """
        Türkiye'nin ilk seri üretim otomobili, 1966'da Otosan fabrikasında banttan indi. Adı Anadol'du.
        Kaportası fiberglastı, motoru ise Ford'dan geliyordu.
        1984'e kadar binlerce Anadol üretildi ve bir neslin ilk arabası oldu.
    """, ("Anadol A1", "Anadol"), ("anadol",), "#anadol", "#yerliotomobil", exclude=("refik", "gerb")),

    _s("cadillac-1959", "Tarihin En Yüksek Arka Kanatları! 1959 Cadillac", """
        Bu arabanın arka kanatları otomobil tarihinin en yükseğiydi. 1959 Cadillac'ın tasarımı
        jet uçaklarından ve uzay çağından ilham aldı. Kanatların üstünde roket gibi duran çift stop lambaları vardı.
        Sonraki yıllarda kanatlar küçüldü ve bu moda sona erdi.
    """, "1959 Cadillac", ("1959 cadillac", "cadillac 1959", "59 cadillac", "1959 eldorado", "cadillac eldorado 1959"),
       "#cadillac"),

    _s("tucker-48", "Farı Direksiyonla Dönüyordu, Sadece 51 Tane Yapıldı! Tucker 48", """
        Bu arabanın ortasındaki üçüncü far, direksiyonla birlikte dönüyordu. Tucker 48, 1948'de
        zamanının çok ötesindeki güvenlik özellikleriyle tanıtıldı. Ama şirket dolandırıcılık davasıyla uğraşırken battı.
        Preston Tucker beraat etti, ama sadece 51 araba üretilebildi.
    """, "Tucker 48", ("tucker",), "#tucker"),

    _s("shelby-cobra", "İngiliz Arabaya Dev Amerikan Motoru! Shelby Cobra", """
        Bir Amerikalı yarışçı, küçük bir İngiliz spor arabasına dev bir Ford V8 motoru taktı.
        Adı Shelby Cobra oldu. Carroll Shelby'nin 1962'de yaptığı bu araba hafifti ve inanılmaz hızlıydı.
        Bugün dünyada en çok kopyası yapılan arabalardan biri.
    """, "Shelby Cobra", ("cobra",), "#shelby", "#cobra", max_year=1967, exclude=("mustang", "svt")),

    _s("charger-daytona", "Bu Kanat Yüzünden Yasaklandı! Dodge Charger Daytona", """
        Bu arabanın arkasındaki dev kanat süs değildi. Dodge Charger Daytona, NASCAR yarışları için yapıldı.
        1970'te Buddy Baker bu arabayla NASCAR'da ilk kez saatte 200 milin üzerine çıktı.
        Kanatlı arabalar o kadar hızlıydı ki kurallar değiştirildi ve pistlerden silindiler.
    """, "Dodge Charger Daytona", ("charger daytona",), "#dodge", "#musclecar", max_year=1970),

    _s("lancia-stratos", "Sadece Ralli Kazanmak İçin Doğdu! Lancia Stratos", """
        Bu araba, baştan sona ralli kazanmak için tasarlanan ilk otomobillerden biriydi.
        Lancia Stratos'un motoru bir Ferrari Dino'dan geliyordu.
        1974, 75 ve 76'da Dünya Ralli Şampiyonası'nı üst üste üç kez kazandı.
    """, ("Lancia Stratos HF", "Lancia Stratos"), ("stratos",), "#lancia", "#rally", max_year=1980),

    _s("toyota-2000gt", "James Bond İçin Tavanını Kestiler! Toyota 2000GT", """
        Bu araba bir James Bond filminde oynadı, ama önce tavanını kesmek gerekti.
        Sean Connery arabaya sığamayacak kadar uzundu. Toyota da film için iki tane üstü açık özel araba yaptı.
        Toyota 2000GT'den toplamda sadece 351 tane üretildi.
    """, "Toyota 2000GT", ("2000gt", "2000 gt"), "#toyota"),

    _s("bmw-isetta", "Kapısı Buzdolabı Gibi Önden Açılıyordu! BMW Isetta", """
        Bu arabanın kapısı önden, buzdolabı gibi açılıyordu. Direksiyon da kapıyla birlikte dışarı çıkıyordu.
        Tasarım aslında İtalyan buzdolabı üreticisi Iso'ya aitti. BMW lisansını aldı
        ve bu minik araba 1950'lerde zor günler geçiren BMW'yi ayakta tuttu.
    """, ("BMW Isetta 300", "Isetta"), ("isetta",), "#bmw", "#isetta"),

    _s("messerschmitt", "Uçak Yapmaları Yasaklanınca Araba Yaptılar! Messerschmitt KR200", """
        İkinci Dünya Savaşı'ndan sonra Messerschmitt'in uçak üretmesi yasaklandı.
        Şirket de uçak kokpitine benzeyen minik arabalar yapmaya başladı.
        KR200'de iki kişi uçaktaki gibi arka arkaya oturuyordu ve cam kubbe yana doğru açılıyordu.
    """, "Messerschmitt KR200", ("messerschmitt", "kr200", "kr 200"), "#messerschmitt"),

    _s("rolls-royce-silver-ghost", "1907'de 24 Bin Kilometre Durmadan Gitti! Rolls-Royce Silver Ghost", """
        1907'de bir otomobil, 24 bin kilometrelik bir dayanıklılık testine çıktı.
        Rolls-Royce Silver Ghost, neredeyse hiç arıza yapmadan bu yolu tamamladı.
        O dönem için inanılmaz olan bu başarı, Rolls-Royce'u dünyanın en iyi arabası ününe taşıdı.
    """, "Rolls-Royce Silver Ghost", ("silver ghost",), "#rollsroyce"),

    _s("pontiac-gto", "Kas Arabası Çılgınlığını Başlatan Araba! Pontiac GTO", """
        Kas arabası çılgınlığını başlatan araba buydu. 1964'te Pontiac mühendisleri orta boy bir arabaya
        dev bir V8 motor taktı. Bu fikrin arkasında, yıllar sonra DeLorean'ı yapacak olan John DeLorean vardı.
        Pontiac 5 bin tane satmayı umuyordu, ilk yıl 32 binden fazla sattı.
    """, ("Pontiac GTO 1967", "Pontiac GTO 1965"), ("gto",), "#pontiac", "#musclecar", max_year=1974),

    _s("ford-gt40", "Ferrari'ye Kızan Ford, Le Mans'ı Fethetti! Ford GT40", """
        1963'te Henry Ford ikinci, Ferrari'yi satın almak istedi ama anlaşma son anda bozuldu.
        Ford da Le Mans'ta Ferrari'yi yenecek bir araba yaptırdı. Adı GT40'tı.
        1966'da Le Mans'ta ilk üç sırayı alarak Ferrari'nin hükmünü bitirdi.
    """, "Ford GT40", ("gt40", "gt 40"), "#fordgt40", "#lemans", max_year=1969),

    _s("vw-bus", "63 Yıl Üretildi! Volkswagen Minibüs", """
        Bu minibüs ilk kez 1950'de üretildi ve üretimi ancak 2013'te sona erdi.
        Altmışlarda hippilerin simgesi olan Volkswagen Transporter, en son Brezilya'da üretiliyordu.
        Yeni güvenlik kuralları gelince 63 yıllık serüveni bitti.
    """, ("Volkswagen Type 2", "Volkswagen T1 Samba", "VW Bulli T1"),
       ("type 2", "transporter", "kombi", "t1", "t2", "bulli", "samba"), "#volkswagen", "#vwbus",
       max_year=1979, exclude=("t3", "t4", "t5", "t6", "t7")),

    _s("trabant", "Bu Arabayı Almak İçin 10 Yıl Beklenirdi! Trabant", """
        Doğu Almanya'da bu arabayı almak için on yıldan fazla beklenebiliyordu. Trabant'ın kaportası
        metal değil, pamuk atığı ve reçineden yapılan Duroplast'tı. Sıradan bir araba gibi görünse de
        üç milyondan fazla üretildi ve Berlin Duvarı'nın yıkılışının simgelerinden biri oldu.
    """, "Trabant 601", ("trabant",), "#trabant"),

    _s("lada-2101", "Bu Sovyet Arabası Aslında İtalyandı! Lada 2101", """
        Bu Sovyet arabası aslında bir İtalyandı. Lada 2101, Fiat 124'ün Rus kışlarına göre güçlendirilmiş hâliydi.
        Fiat, Togliatti şehrinde dev bir fabrika kurdu. 1970'te başlayan klasik Lada üretimi
        2012'ye kadar sürdü.
    """, "VAZ-2101 Lada", ("2101", "lada 1200", "zhiguli", "žiguli"), "#lada"),

    _s("land-rover-series1", "Kumsala Çizilen Bir Taslaktan Doğdu! Land Rover", """
        Anlatılana göre bu arabanın ilk taslağı bir kumsalda, kuma çizildi. Maurice Wilks,
        savaştan kalan Jeep'lerin yerine bir çiftlik aracı istiyordu. 1948'de çıkan Land Rover'ın kaportası alüminyumdu,
        çünkü savaş sonrası çelik karneyle dağıtılıyordu.
    """, "Land Rover Series I", ("series i", "series 1", "series one"), "#landrover", max_year=1958,
       exclude=("series ii", "series iii")),

    _s("willys-jeep", "Savaşı Kazandıran Araba! Willys Jeep", """
        İkinci Dünya Savaşı'nda bu araba her cephede görüldü. Willys MB Jeep'ten 640 bin kadar üretildi.
        Hafifti, dayanıklıydı ve her yere gidebiliyordu.
        Savaştan sonra sivil Jeep'lere dönüştü ve bütün arazi araçlarının atası oldu.
    """, "Willys MB jeep", ("willys",), "#jeep", "#willys", max_year=1955),

    _s("impala-1965", "Bir Yılda 1 Milyondan Fazla Sattı! 1965 Chevrolet Impala", """
        1965'te Amerika'da bir araba, tek bir yılda bir milyondan fazla sattı. Bu araba Chevrolet Impala'ydı.
        Uzun, alçak ve şık gövdesi onu herkesin hayali yaptı.
        Bu rekor, bugün hâlâ kırılamadı.
    """, "1965 Chevrolet Impala", ("impala",), "#impala", "#chevrolet", max_year=1966),

    _s("chrysler-airflow", "Zamanının Çok İlerisindeydi, Satmadı! Chrysler Airflow", """
        Bu araba rüzgâr tünelinde tasarlanan ilk seri üretim arabalardan biriydi.
        Chrysler Airflow, 1934'te aerodinamik gövdesiyle tanıtıldı. Ama halk bu tuhaf görünümü sevmedi
        ve satışlar çöktü. Bugün ise zamanının çok ötesinde bir tasarım olarak görülüyor.
    """, "Chrysler Airflow", ("airflow",), "#chrysler"),

    _s("volvo-p1800-irv", "Bu Arabayla 5 Milyon Kilometre Yapıldı! Volvo P1800", """
        Bir adam bu arabayla 5 milyon kilometreden fazla yol yaptı. Amerikalı öğretmen Irv Gordon,
        1966 model Volvo P1800'ünü sıfır aldı ve yıllarca her gün kullandı. Guinness rekorlar kitabına girdi.
        Bu mesafe, Ay'a altı kez gidip dönmeye yetiyor.
    """, "Volvo P1800", ("p1800", "p 1800"), "#volvo", max_year=1973),

    _s("corvair", "Bir Kitap Bu Arabayı Bitirdi! Chevrolet Corvair", """
        Bir kitap bu arabayı bitirdi. 1965'te Ralph Nader, Hiçbir Hızda Güvenli Değil adlı kitabını yayımladı.
        Kitabın ilk bölümü Chevrolet Corvair'in yol tutuşunu eleştiriyordu. Satışlar düştü,
        Amerika'da otomobil güvenliği kuralları ise tamamen değişti.
    """, "Chevrolet Corvair", ("corvair",), "#chevrolet", max_year=1969, exclude=("testudo",)),

    _s("datsun-240z", "Japonları Spor Arabada Ciddiye Aldıran Araba! Datsun 240Z", """
        1969'da Japonlar spor arabada ciddiye alınmıyordu. Sonra Datsun 240Z geldi.
        Avrupalı spor arabalar kadar hızlı ama onların çok altında bir fiyata satılıyordu.
        Amerika'da bekleme listeleri oluştu ve Japon spor arabası çağı başladı.
    """, "Datsun 240Z", ("240z", "240 z", "fairlady"), "#datsun", "#jdm", max_year=1978),

    _s("mercedes-pagoda", "Tavanı Bir Tapınağa Benziyordu! Mercedes Pagoda", """
        Bu arabanın sökülebilen tavanı ortadan çukurdu ve bir Uzak Doğu tapınağının çatısına benziyordu.
        Bu yüzden Mercedes 230 SL'ye Pagoda adı takıldı. 1963'te tanıtılan araba,
        kaza anında ezilerek enerjiyi emen gövde bölgelerine sahip ilk spor arabalardan biriydi.
    """, ("Mercedes-Benz W113 Pagode", "Mercedes 280 SL"), ("w113", "w 113", "pagode", "pagoda", "230 sl", "250 sl", "280 sl"),
       "#mercedes", max_year=1971),

    _s("ferrari-testarossa", "Adı İtalyanca 'Kızıl Kafa' Demek! Ferrari Testarossa", """
        Bu arabanın adı İtalyanca kızıl kafa demek. Ferrari Testarossa'nın motorundaki silindir kapakları
        kırmızıya boyanmıştı. Yanlardaki dev hava girişleri, arkadaki motora serin hava taşıyordu.
        1984'te çıktı ve seksenlerde neredeyse her gencin duvarındaki poster oldu.
    """, "Ferrari Testarossa", ("testarossa",), "#ferrari", max_year=1996, exclude=("250", "500 trc")),

    _s("lamborghini-countach", "Geri Giderken Kapıyı Açıp Eşiğe Oturuyorlardı! Lamborghini Countach", """
        Bu arabanın adı, İtalya'nın Piemonte şivesinde hayranlık ünlemi demek. Lamborghini Countach'ın
        arka görüşü o kadar kötüydü ki, sürücüler geri giderken makas kapıyı açıp eşiğe oturuyordu.
        1974'te çıktı ve süper araba denince akla gelen ilk şekil oldu.
    """, ("Lamborghini Countach", "Lamborghini Countach LP400", "Lamborghini Countach LP5000", "Countach 5000 Quattrovalvole"),
       ("countach",), "#lamborghini", max_year=1990, exclude=("lpi", "800-4")),

    _s("mercedes-w123", "2,7 Milyon Üretildi, Taksilerin Efsanesi Oldu! Mercedes W123", """
        Bu Mercedes'ten tam 2 milyon 700 bin tane üretildi. W123, 1976'da çıktı ve dünyanın dört bir yanında
        taksi olarak çalıştı. Motoru o kadar dayanıklıydı ki, yüz binlerce kilometreyi devirip hâlâ çalışanlar var.
        Mercedes'in sağlamlık efsanesi bu arabayla perçinlendi.
    """, ("Mercedes-Benz W123", "Mercedes W123 taxi"), ("w123", "w 123"), "#mercedes", "#w123", max_year=1986),

    _s("tofas-murat-124", "Rusya'da Lada, Türkiye'de Murat Oldu! Murat 124", """
        Aynı araba Rusya'da Lada, Türkiye'de Murat oldu. 1971'de Bursa'daki Tofaş fabrikasından çıkan ilk otomobil,
        Fiat 124'ün Türkiye'de üretilen hâli Murat 124'tü. Fiat 124, 1967'de Avrupa'da yılın otomobili seçilmişti.
        Murat 124, Türkiye'de milyonlarca insanın ilk arabası oldu.
    """, ("Fiat 124", "Tofaş Murat 124", "Fiat 124 1967", "Fiat 124 Berlina", "Fiat 124 Special"), ("fiat 124", "murat 124", "tofaş", "tofas"), "#murat124", "#tofas",
       max_year=1984, exclude=("spider", "spyder", "abarth", "2016", "2017", "2018", "2019", "2020")),

    _s("tofas-murat-131", "Şahin, Doğan, Kartal... Hepsi Bu Arabadan! Tofaş Murat 131", """
        Şahin, Doğan ve Kartal. Türkiye'nin yollarını yıllarca dolduran bu üç kardeşin atası aynı arabaydı.
        Tofaş, 1977'de Fiat 131'i Murat 131 adıyla üretmeye başladı. Sonra gövde yenilendi ve 1985'te Şahin doğdu.
        Bu aile tam 2002'ye kadar Bursa'da banttan inmeye devam etti.
    """, ("Fiat 131 Mirafiori", "Tofaş Şahin", "Tofas Dogan"), ("131", "şahin", "sahin", "doğan", "dogan", "kartal"),
       "#tofas", "#sahin", max_year=2002),

    _s("renault-12", "Bursa'da 29 Yıl Üretildi! Renault 12 Toros", """
        Bu araba Bursa'da tam 29 yıl üretildi. Oyak Renault, 1971'de Renault 12'yi Türkiye'de yapmaya başladı.
        Sağlam gövdesi ve geniş bagajıyla aileler onu çok sevdi. Station wagon modelinin adı ise Toros'tu.
        Son Renault 12, 2000 yılında banttan indi.
    """, "Renault 12", ("renault 12", "r12", "toros"), "#renault12", "#toros", max_year=2000),

    _s("chevrolet-bel-air-1957", "Her Kübik İnç İçin Bir Beygir! 1957 Chevrolet Bel Air", """
        1957 Chevrolet Bel Air, Amerika'nın en tanınan klasik arabalarından biri. O yıl Chevrolet,
        283 kübik inçlik V8 motora yakıt enjeksiyonu ekledi ve tam 283 beygir güç aldı.
        Her kübik inç için bir beygir, o dönem için inanılmaz bir rakamdı.
    """, "1957 Chevrolet Bel Air", ("bel air",), "#chevrolet", "#belair", max_year=1957),

    _s("aston-martin-db5", "Film Arabası 6,4 Milyon Dolara Satıldı! Aston Martin DB5", """
        Bu araba 1964'te bir James Bond filminde oynadı ve dünyanın en ünlü arabalarından biri oldu.
        Aston Martin DB5'in filmde kullanılan orijinallerinden biri, 2019'da açık artırmada
        6 milyon 385 bin dolara satıldı. Sinema tarihinin en pahalı arabalarından biri.
    """, ("Aston Martin DB5", "Aston Martin DB5 1964", "Aston Martin DB5 Vantage", "1965 Aston Martin DB5"), ("db5",),
       "#astonmartin", max_year=1965),

    _s("jaguar-d-type", "Le Mans'ı Üst Üste Üç Kez Kazandı! Jaguar D-Type", """
        Bu araba Le Mans 24 Saat yarışını üst üste üç kez kazandı. Jaguar D-Type, uçak teknolojisiyle yapılmıştı
        ve arkasındaki yüzgeç ona dengeyi veriyordu. 1955, 56 ve 57'de birinci oldu.
        1957'de ise ilk dört sırayı D-Type'lar aldı.
    """, "Jaguar D-Type", ("d-type", "d type", "dtype"), "#jaguar", "#lemans", max_year=1960),

    _s("bmw-2002-turbo", "Ön Tamponundaki Yazı Ters Yazılmıştı! BMW 2002 Turbo", """
        Bu arabanın ön tamponundaki turbo yazısı bilerek ters yazılmıştı. Öndeki sürücü dikiz aynasına baktığında
        düz okusun ve yol versin diye. BMW 2002 Turbo, 1973'te Avrupa'nın ilk turbolu seri üretim otomobillerindendi.
        Ama aynı yıl petrol krizi patladı ve sadece 1600 kadar üretildi.
    """, ("BMW 2002 Turbo", "BMW 2002 tii", "BMW 2002"), ("bmw 2002",), "#bmw", exclude=("1602",)),

    _s("chevrolet-camaro-1967", "Adının Anlamı: Mustang Yiyen Hayvan! 1967 Camaro", """
        Gazeteciler Chevrolet'ye Camaro ne demek diye sorduğunda, aldıkları cevap efsane oldu:
        Mustang yiyen, küçük ve vahşi bir hayvan. Chevrolet, Ford Mustang'in başarısına cevap olarak
        1967'de Camaro'yu çıkardı. Ve iki araba arasındaki kavga bugün hâlâ sürüyor.
    """, ("1967 Chevrolet Camaro", "1969 Chevrolet Camaro"), ("camaro",), "#camaro", "#chevrolet", max_year=1969),

    _s("plymouth-road-runner", "Korna Sesi İçin Çizgi Filme 50 Bin Dolar Ödendi! Plymouth Road Runner", """
        Bu arabanın kornası bip bip diye ötüyordu. Plymouth, Road Runner adını ve çizgi film kuşunun sesini
        kullanmak için Warner Bros'a 50 bin dolar ödedi. 1968'de çıkan araba ucuz ama çok güçlüydü
        ve beklenenin kat kat üstünde sattı.
    """, "Plymouth Road Runner", ("road runner", "roadrunner"), "#plymouth", "#musclecar", max_year=1975),

    _s("amc-gremlin", "1 Nisan'da Tanıtıldı, Şaka Sanıldı! AMC Gremlin", """
        Bu araba 1 Nisan 1970'te tanıtıldı ve birçok kişi şaka sandı. AMC Gremlin'in arkası sanki kesilmiş gibiydi.
        Ama Amerika'nın ilk küçük sınıf otomobillerinden biriydi ve benzin krizinde çok işe yaradı.
        Bugün en tuhaf görünen klasiklerden biri olarak seviliyor.
    """, "AMC Gremlin", ("gremlin",), "#amc", max_year=1978),

    _s("vw-karmann-ghia", "İtalyan Tasarım, Alman Usta, Beetle Şasisi! VW Karmann Ghia", """
        Bu araba İtalyan tasarımı, Alman ustalığı ve bir Beetle şasisinin birleşimiydi.
        Volkswagen Karmann Ghia'nın gövdesini İtalyan Ghia çizdi, Alman Karmann ise elle şekillendirdi.
        1955'ten 1974'e kadar 445 bin kadar üretildi.
    """, "Volkswagen Karmann Ghia", ("karmann", "ghia"), "#volkswagen", max_year=1974),

    _s("saab-92", "Uçak Üreticisinin Yaptığı İlk Araba! Saab 92", """
        Bu araba bir uçak fabrikasında doğdu. Savaş sonrası İsveçli uçak üreticisi Saab, otomobil yapmaya karar verdi.
        1949'da çıkan Saab 92'nin damla şeklindeki gövdesi, uçak mühendisleri tarafından tasarlanmıştı.
        Rüzgârı o kadar iyi yarıyordu ki, birçok modern arabadan daha aerodinamikti.
    """, ("Saab 92", "Saab 93", "Saab 96"), ("saab 92", "saab 93", "saab 96"), "#saab", max_year=1980),

    _s("audi-quattro", "Rallide Kuralları Yıkan Dört Çeker! Audi Quattro", """
        1980'de Audi, rallide her şeyi değiştirecek bir araba tanıttı. Quattro, dört çeker sistemi
        bir spor otomobilde kullanan ilk araçlardandı. Rakipler önce güldü, sonra tozunu yuttu.
        Audi, 1982 ve 1984'te Dünya Ralli Şampiyonası'nda markalar şampiyonu oldu.
    """, ("Audi Quattro 1980", "Audi Sport Quattro", "Audi Ur-Quattro"), ("quattro",), "#audi", "#rally",
       max_year=1991, exclude=("a4", "a6", "q5", "q7", "rs", "tt", "s4", "a8")),

    _s("ferrari-f40", "Enzo Ferrari'nin Onayladığı Son Araba! Ferrari F40", """
        Bu, Enzo Ferrari'nin onay verdiği son arabaydı. F40, Ferrari'nin 40. yılı için 1987'de yapıldı.
        Saatte 324 kilometreye çıkabiliyordu. Enzo Ferrari bir yıl sonra hayatını kaybetti.
        F40 bugün tüm zamanların en saf süper arabalarından biri sayılıyor.
    """, "Ferrari F40", ("f40",), "#ferrari", "#f40"),

    _s("cord-810", "Farları Gizlenen İlk Seri Üretim Araba! Cord 810", """
        1936'da bu arabanın farları kaportanın içine saklanabiliyordu. Cord 810, gizli farları olan
        ilk seri üretim otomobildi. Farlar, ön paneldeki küçük kollarla elle açılıyordu.
        Önden çekişliydi ve zamanının çok ötesindeydi ama şirket iki yıl sonra kapandı.
    """, ("Cord 810", "Cord 812"), ("cord",), "#cord", max_year=1937),

    _s("hudson-hornet", "Bir Animasyon Karakterine İlham Verdi! Hudson Hornet", """
        Ünlü bir animasyon filmindeki bilge yarış arabası Doc'un gerçek bir atası var: Hudson Hornet.
        Alçak gövdesi sayesinde virajlarda rakiplerinden çok daha iyi tutunuyordu.
        1951'den 1954'e kadar NASCAR pistlerine hükmetti.
    """, "Hudson Hornet", ("hornet",), "#hudson", max_year=1957),

    _s("benz-patent-motorwagen", "Dünyanın İlk Uzun Yolculuğunu Bir Kadın Yaptı! Benz Patent-Motorwagen", """
        Dünyanın ilk otomobilini Carl Benz yaptı, ama onu ünlü yapan eşi Bertha'ydı. 1888'de Bertha Benz,
        kocasına haber vermeden iki oğluyla birlikte 106 kilometre yol gitti. Yakıt bitince bir eczaneden benzin aldı.
        O eczane, tarihin ilk benzin istasyonu sayılıyor.
    """, "Benz Patent-Motorwagen", ("motorwagen", "motorwagon"), "#mercedes", "#benz", exclude=("drawing",)),

    _s("nissan-skyline-hakosuka", "Üç Yılda 50 Yarış Kazandı! Nissan Skyline GT-R Hakosuka", """
        Bu Japon sedan üç yıl içinde 50 yarış kazandı. 1969'da çıkan Nissan Skyline GT-R'ye,
        köşeli gövdesi yüzünden Japonca kutu Skyline anlamına gelen Hakosuka dendi.
        Bugünkü GT-R efsanesi tam olarak bu arabayla başladı.
    """, ("Nissan Skyline 2000GT-R", "Nissan Skyline KPGC10", "Skyline Hakosuka"), ("skyline", "hakosuka", "kpgc10"),
       "#nissan", "#skyline", "#jdm", max_year=1973),

    _s("mercedes-g-wagen", "Bir Şahın İsteğiyle Doğdu, 45 Yıldır Üretiliyor! Mercedes G-Class", """
        Anlatılana göre bu arabanın hikâyesi İran Şahı'nın bir isteğiyle başladı. Mercedes G-Serisi,
        1979'da askeri ve arazi aracı olarak tanıtıldı. Kutu gibi tasarımı neredeyse hiç değişmedi.
        Ve bugün hâlâ üretiliyor.
    """, ("Mercedes-Benz G-Class W460", "Mercedes W460", "Mercedes-Benz 230 GE"), ("w460", "w 460", "230 ge", "300 gd", "240 gd", "280 ge"),
       "#mercedes", "#gclass", max_year=1992),

    _s("range-rover-classic", "Louvre Müzesi'nde Sergilenen Araba! Range Rover", """
        Bu arazi aracı bir zamanlar Paris'teki Louvre Müzesi'nde sergilendi. 1970'te çıkan Range Rover,
        endüstriyel tasarımın örnek eseri olarak gösterildi. Hem çamurlu tarlada hem şehirde rahattı.
        Lüks arazi aracı fikri tam olarak bu arabayla başladı.
    """, ("Range Rover Classic", "Range Rover 1970"), ("range rover",), "#rangerover", "#landrover", max_year=1996,
       exclude=("sport", "evoque", "velar", "p38", "l322", "l405")),

    _s("renault-4", "8 Milyondan Fazla Üretildi! Renault 4", """
        Bu küçük araba 8 milyondan fazla üretildi. Renault 4, 1961'de çıktı ve tam 31 yıl üretimde kaldı.
        Vitesi ön panelden çıkan bir koldu, arka kapısı ise bir yük aracı gibi açılıyordu.
        Fransa'da ona hâlâ sevgiyle Quatrelle deniyor.
    """, "Renault 4", ("renault 4", "r4", "4l"), "#renault", max_year=1992),

    _s("corvette-1963-split-window", "Sadece Bir Yıl Üretilen Arka Cam! 1963 Corvette Stingray", """
        Bu arabanın arka camı ortadan ikiye bölünmüştü ve bu tasarım sadece bir yıl yaşadı.
        1963 Corvette Stingray'in tasarımcısı bu camı çok seviyordu, ama mühendisler arka görüşü kapattığını söyledi.
        Ertesi yıl cam tek parça yapıldı. Bugün bölünmüş camlı Stingray'ler en değerli Corvette'ler arasında.
    """, ("1963 Corvette Stingray split window", "1963 Chevrolet Corvette Sting Ray"),
       ("1963 corvette", "1963 chevrolet corvette", "corvette 1963", "'63 corvette", "'63 chevrolet corvette", "split window", "split-window"),
       "#corvette",
       max_year=1963),

    _s("bmw-507", "Elvis'in Arabasıydı, Sadece 252 Tane Yapıldı! BMW 507", """
        Bu arabadan sadece 252 tane üretildi ve biri Elvis Presley'indi. Elvis, Almanya'da askerlik yaparken
        beyaz bir BMW 507 aldı. Araba yıllar sonra bir ahırda bulundu ve BMW tarafından baştan sona yenilendi.
        BMW 507 bugün en değerli BMW'lerden biri.
    """, "BMW 507", ("507",), "#bmw", max_year=1959),

    _s("alfa-romeo-duetto", "27 Yıl Neredeyse Hiç Değişmedi! Alfa Romeo Spider", """
        Bu üstü açık İtalyan, 1967'de ünlü bir Hollywood filminde oynayınca bir anda dünya yıldızı oldu.
        Alfa Romeo Spider, 1966'da tanıtıldı ve tam 27 yıl üretildi.
        Zarif çizgileri sayesinde bugün hâlâ en çok sevilen klasik İtalyan arabalarından biri.
    """, ("Alfa Romeo Spider Duetto", "Alfa Romeo Spider 1966"), ("spider", "duetto"), "#alfaromeo", max_year=1993,
       exclude=("brera", "916", "124")),

    _s("ferrari-dino", "Enzo Ferrari Kaybettiği Oğlunun Adını Verdi! Ferrari Dino", """
        Enzo Ferrari, bu arabaya genç yaşta kaybettiği oğlunun adını verdi. Oğlu Alfredo'ya herkes Dino diyordu.
        Dino, babasıyla birlikte V6 motor fikri üzerinde çalışmıştı. Ferrari bu motorla yapılan küçük spor arabaya
        onun adını verdi. Dino 246, bugün en sevilen klasiklerden biri.
    """, ("Ferrari Dino 246 GT", "Dino 246 GT", "Dino 206 GT"), ("dino",), "#ferrari", "#dino", max_year=1974,
       exclude=("308", "gt4")),

    _s("de-tomaso-pantera", "Elvis Çalışmayınca Arabasını Vurdu! De Tomaso Pantera", """
        Anlatılana göre Elvis Presley, De Tomaso Pantera'sı bir gün çalışmayınca sinirlenip arabaya ateş etti.
        Bu İtalyan spor arabanın içinde Amerikan Ford V8 motoru vardı. 1971'den itibaren Amerika'da Ford bayileri satıyordu.
        Kurşun izli araba bugün bir müzede sergileniyor.
    """, "De Tomaso Pantera", ("pantera",), "#detomaso", max_year=1992),

    _s("chrysler-300-1955", "300 Beygirle Adını Aldı! 1955 Chrysler C-300", """
        Bu arabanın adı motorunun gücünden geliyor. 1955 Chrysler C-300, 300 beygir güç üreten
        ilk Amerikan seri üretim otomobillerindendi. Lüks bir sedan gibi görünüyordu ama
        aynı yıl NASCAR pistlerinde rakiplerine fark attı.
    """, ("Chrysler C-300 1955", "Chrysler 300B", "Chrysler 300 letter series"), ("c-300", "c300", "300b", "300c", "300 b", "300 c", "300d", "300f", "letter"),
       "#chrysler", max_year=1965),

    _s("toyota-land-cruiser-fj40", "Çöllerin Kralı: 25 Yıl Üretildi! Toyota Land Cruiser FJ40", """
        Bu araba çöllerde, ormanlarda ve dağlarda yıllarca durmadan çalıştı. Toyota Land Cruiser FJ40,
        1960'tan 1984'e kadar üretildi. O kadar dayanıklıydı ki Afrika ve Orta Doğu'da hâlâ binlercesi yolda.
        Toyota'nın dünya çapındaki ününde bu arabanın payı büyük.
    """, ("Toyota Land Cruiser FJ40", "Toyota FJ40"), ("fj40", "fj 40", "fj45", "bj40", "40 series"), "#toyota", "#landcruiser",
       max_year=1984),
]


def by_id(story_id: str) -> Story:
    for story in STORIES:
        if story.id == story_id:
            return story
    raise KeyError(story_id)
