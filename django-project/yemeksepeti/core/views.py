from django.http import HttpResponse
from django.shortcuts import render, redirect
import pyodbc
from django.contrib import messages


def get_connection():
    # SQL Server bağlantısı
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=.;"
        "DATABASE=YemekSepetiDb;"
        "Trusted_Connection=yes;"
        "Encrypt=no;"
    )


# ANA SAYFA–RESTORAN LİSTESİ

# giriş yapan kullanıcılar için
# aktif restoranları listeleyen ana sayfadır.
# Kategori filtresi varsa sonuçlar ona göre gelir
def ana_sayfa(request):
    # giriş yapılmamışsa login'e yönlendir
    if "kullanici_id" not in request.session:
        return redirect("login")

    # kategori filtresi
    kategori_id = request.GET.get("kategori")  # filtre için

    conn = get_connection()
    cursor = conn.cursor()

    # Dropdown menü için kategorileri çekiyoruz
    cursor.execute("""
        SELECT KategoriID, KategoriAdi
        FROM tbl_Kategoriler
        WHERE AktifMi = 1
    """)
    kategoriler = cursor.fetchall()

    # kategori filtresi varsa sp ile(seçili kategoriyi) yoksa view ile(tüm restoranları) listele
    if kategori_id and kategori_id != "":
        cursor.execute(
            "EXEC dbo.sp_AnaSayfaRestoranListele @KategoriID = ?", (int(kategori_id),))
    else:
        cursor.execute(
            "EXEC dbo.sp_AnaSayfaRestoranListele @KategoriID = NULL")
    rows = cursor.fetchall()
    conn.close()

    # template tarafında daha rahat kullanmak için
    # kategorileri dictionary listesine çeviriyoruz
    kategoriler_liste = []
    for k in kategoriler:
        kategoriler_liste.append({
            "id": k[0],
            "ad": k[1],
            "secili": (str(k[0]) == str(kategori_id))
        })

    # restoran isimlerine göre sabit görsel eşleştirmesi yapıyoruz
    image_map = {
        "lezzetduragi": "lezzetduragi.jpg",
        "anadolusofrasi": "anadolusofrasi.jpg",
        "ustakebapci": "kebap.jpg",
        "dominospizza": "pizza.jpg",
        "burgerlab": "burger.jpg",
        "cicekevyemekleri": "cicekevyemekleri.jpg",
        "sokaklezzetleri": "sokaklezzetleri.jpg",
        "kozocakbasi": "koz.jpg",
        "gurmetatlar": "gurme.jpg",
        "sefinyeri": "sefinyeri.jpg",
    }

    restoranlar = []
    # SP’den gelen satırları template’in beklediği formata dönüştürüyoruz
    for row in rows:
        r_ad_clean = (
            row[1]
            .lower()
            .replace(" ", "")
            .replace("ç", "c")
            .replace("ğ", "g")
            .replace("ı", "i")
            .replace("ö", "o")
            .replace("ş", "s")
            .replace("ü", "u")
        )
        image = image_map.get(r_ad_clean, "default.jpg")

        # restoranların ayrıntılı listelenmesi için
        restoranlar.append({
            "RestoranID": row[0],
            "RestoranAdi": row[1],
            "MinTutar": row[2],
            "Aciklama": row[3],
            "Puan": row[4] if row[4] else 0,
            "YorumSayisi": row[5] if row[5] else 0,
            "AktifYemekSayisi": row[6] if row[6] else 0,
            "image": image
        })

    return render(request, "home.html", {
        "restoranlar": restoranlar,
        "kategoriler": kategoriler_liste
    })


# RESTORAN MENÜ SAYFASI

# Seçilen restoranın menüsünü ve kategorilere göre
# listelenmiş yemeklerini gösterir.
def restoran_menu(request, restoran_id):
    # Kullanıcı giriş kontrolü
    if "kullanici_id" not in request.session:
        return redirect("login")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # restoran bilgisini çekiyoruz
        cursor.execute("""
            select RestoranID, RestoranAdi, Aciklama, MinTutar
            from tbl_Restoranlar
            where RestoranID = ? and AktifMi = 1
        """, (restoran_id),)

        restoran = cursor.fetchone()
        if not restoran:
            return HttpResponse("restoran bulunamadı")

        # Template için okunabilir hale getiriyoruz
        restaurant = {
            "RestoranID": restoran[0],
            "RestoranAdi": restoran[1],
            "Aciklama": restoran[2],
            "MinTutar": restoran[3],
        }

        # restoran menüsü için yazdığımız sp yi kullanıyoruz
        cursor.execute(
            "exec dbo.sp_RestoranMenusuGetir @RestoranID = ?",
            restoran_id
        )
        rows = cursor.fetchall()
        conn.close()

        menu_items = []
        for r in rows:
            menu_items.append({
                "YemekID": r[0],
                "YemekAdi": r[1],
                "Fiyat": r[2],
                "Icerik": r[3],
                "KategoriAdi": r[4],
            })

        sepet = request.session.get("sepet", {})
        urunler = sepet.get("urunler", {})

        return render(request, "menu.html", {
            "restaurant": restaurant,
            "menu_items": menu_items,
            "sepet_urunler": urunler
        })

    except Exception as e:
        return HttpResponse(f"hata: {e}")


# KULLANICI GİRİŞİ

# Kullanıcının e-posta ve şifre bilgileri
# sp üzerinden kontrol ediliyor
# Rol bilgisine göre ilgili panele yönlendirme yapılıyor
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # sp ile kullanıcı giriş kontrolü
            cursor.execute(
                "exec dbo.sp_KullaniciGiris ?, ?",
                email, password
            )

            user = cursor.fetchone()
            conn.close()

            # kullanıcı bulunduysa session bilgileri atanıyor
            if user:
                request.session["kullanici_id"] = user[0]
                request.session["adsoyad"] = user[1]
                request.session["rol"] = user[2]

                # rolüne göre yönlendirme yapıyoruz
                if user:
                    if user[2] == 1:      # ADMIN
                        return redirect("admin_panel")
                    elif user[2] == 2:    # FIRMA
                        return redirect("firma_panel")
                    else:                 # KULLANICI
                        return redirect("home")
                # hatalı giriş
                else:
                    return render(request, "login.html", {
                        "error": "E-posta veya şifre hatalı"
                    })

        except Exception as e:
            return HttpResponse(f"hata: {e}")

    return render(request, "login.html")


# KAYIT

# Kullanıcı kayıt işlemini SP ile yapıyoruz
# Aynı e-posta ile aktif kayıt varsa engelliyoruz
def register_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        district = request.POST.get("district", "").strip()

        # Şifre kontrolü
        if password != password_confirm:
            return render(request, "register.html", {
                "error": "Şifreler eşleşmiyor."
            })

        # Ad Soyad birleştirme
        adsoyad = f"{first_name} {last_name}".strip()
        # Adresi tek string haline getiriyoruz
        full_address = f"{address} / {district} / {city}".strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Aynı e-posta ile aktif kullanıcı varsa yeni kaydı engelliyoruz
            cursor.execute(
                "SELECT 1 FROM tbl_Kullanicilar WHERE Eposta = ? AND AktifMi=1",
                email
            )
            if cursor.fetchone():
                conn.close()
                return render(request, "register.html", {
                    "error": "Bu e-posta ile zaten kayıt var."
                })

            # sp ile kayıt
            cursor.execute(
                "EXEC dbo.sp_KullaniciKayit ?, ?, ?, ?, ?",
                adsoyad, email, password, phone, full_address
            )
            conn.commit()
            conn.close()

            return redirect("login")

        except Exception as e:
            return HttpResponse(f"hata: {e}")

    return render(request, "register.html")


# ÇIKIŞ
# kullanıcıyı sistemden çıkarır ve sessionı temizler.
def logout_view(request):
    request.session.flush()
    return redirect("login")


# ADMİN PANELİ
def admin_panel(request):
    # sadece admin girebilsin
    if "kullanici_id" not in request.session or request.session.get("rol") != 1:
        return redirect("login")

    mesaj = ""

    # Admin panelde form işlemleri POST ile gelyor, action alanına göre ayrıştırılıyor
    if request.method == "POST":
        action = request.POST.get("action")

        conn = get_connection()
        cursor = conn.cursor()

     # kullanıcı işlemleri
        # kullanıcı pasife al (sp ile)
        if action == "kullanici_sil":
            kid = request.POST.get("kullanici_id")
            cursor.execute("EXEC sp_KullaniciSil ?", kid)
            mesaj = "Kullanıcı pasife alındı."

        # kullanıcının aktiflik pasiflik değişimi
        elif action == "kullanici_toggle":
            kid = int(request.POST.get("kullanici_id"))
            aktif = request.POST.get("aktif")  # True / False string

            # admin kendi hesabını kapamasın
            if kid == request.session["kullanici_id"]:
                messages.error(request, "Admin kendi hesabını pasife alamaz.")
            else:
                yeni_durum = 0 if aktif == "True" else 1
                cursor.execute("""
                    UPDATE tbl_Kullanicilar
                    SET AktifMi = ?
                    WHERE KullaniciID = ?
                """, yeni_durum, kid)

                mesaj = "Kullanıcı durumu güncellendi."

        # rol değiştirme
        elif action == "rol_degistir":
            kid = int(request.POST.get("kullanici_id"))
            rol = int(request.POST.get("rol"))

            # admin kendi rolünü değiştiremez
            if kid == request.session["kullanici_id"]:
                messages.error(request, "Admin kendi rolünü değiştiremez.")
            else:
                cursor.execute(
                    "EXEC sp_KullaniciRolGuncelle ?, ?",
                    kid, rol
                )
                mesaj = "Kullanıcı rolü güncellendi."

        # restoran işlemleri

        # sp ile restoran ekleme
        elif action == "restoran_ekle":
            cursor.execute(
                "EXEC sp_RestoranEkle ?, ?, ?, ?",
                request.POST.get("restoran_adi"),
                request.POST.get("aciklama"),
                request.POST.get("min_tutar"),
                request.POST.get("sahip_id"),
            )
            mesaj = "Restoran eklendi."

        # restoran aktiflik pasiflik değişimi
        # (data base tarafında restoran pasif olunca yemekleri de pasif yapan trigger var)
        elif action == "restoran_toggle":
            rid = int(request.POST.get("restoran_id"))
            aktif = request.POST.get("aktif")

            yeni_durum = 0 if aktif == "True" else 1

            cursor.execute("""
                UPDATE tbl_Restoranlar
                SET AktifMi = ?
                WHERE RestoranID = ?
            """, yeni_durum, rid)

            mesaj = "Restoran durumu güncellendi."

        # kategori işlemleri

        # sp ile kategori ekle
        elif action == "kategori_ekle":
            cursor.execute(
                "EXEC sp_KategoriEkle ?",
                request.POST.get("kategori_adi"),
            )
            mesaj = "Kategori eklendi."

        # kategori aktif pasif yapma işlemi
        elif action == "kategori_toggle":
            kid = int(request.POST.get("kategori_id"))
            aktif = request.POST.get("aktif")

            yeni_durum = 0 if aktif == "True" else 1

            cursor.execute("""
                UPDATE tbl_Kategoriler
                SET AktifMi = ?
                WHERE KategoriID = ?
            """, yeni_durum, kid)

            mesaj = "Kategori durumu güncellendi."

        conn.commit()
        conn.close()

    # panel ilk açıldığında listelemeler yapılır (kullanıcılar,restoranlar,kategoriler)
    conn = get_connection()
    cursor = conn.cursor()

    # kullanıcılar
    cursor.execute("""
        SELECT KullaniciID, AdSoyad, Eposta, Rol, AktifMi
        FROM tbl_Kullanicilar
    """)
    kullanicilar = cursor.fetchall()

    # Template’de rahat göstermek için kullanıcıları dictionary yapısına çeviriyoruz
    kullanicilar_liste = []
    for k in kullanicilar:
        kullanicilar_liste.append({
            "id": k[0],
            "ad": k[1],
            "eposta": k[2],
            "rol": k[3],
            "aktif": k[4],
            "is_admin": k[3] == 1,
            "is_musteri": k[3] == 3,
            "is_firma": k[3] == 2,
        })

    # restoranlar
    cursor.execute("""
        SELECT RestoranID, RestoranAdi, AktifMi
        FROM tbl_Restoranlar
    """)
    restoranlar = cursor.fetchall()

    # kategoriler
    cursor.execute("""
        SELECT KategoriID, KategoriAdi, AktifMi
        FROM tbl_Kategoriler
    """)
    kategoriler = cursor.fetchall()

    conn.close()

    return render(request, "admin_panel.html", {
        "mesaj": mesaj,
        "kullanicilar": kullanicilar_liste,
        "restoranlar": restoranlar,
        "kategoriler": kategoriler
    })


# FİRMA PANELİ
def firma_panel(request):

    if "kullanici_id" not in request.session or request.session.get("rol") != 2:
        return redirect("login")

    firma_id = request.session["kullanici_id"]

    if request.method == "POST":
        action = request.POST.get("action")

        conn = get_connection()
        cursor = conn.cursor()

        # sipariş durumları
        # onaylandı durumu
        if action == "siparis_onayla":
            siparis_id = request.POST.get("siparis_id")

            # sadece firmanın kendisine ait restoranların siparişleri güncellenebiliyor
            cursor.execute("""
                UPDATE tbl_Siparisler
                SET Durum = 'Onaylandı'
                WHERE SiparisID = ?
                    AND RestoranID IN (
                        SELECT RestoranID
                        FROM tbl_Restoranlar
                        WHERE SahipID = ?   
                    )
            """, siparis_id, firma_id)

        # sipariş iptal durumu
        elif action == "siparis_iptal":
            siparis_id = request.POST.get("siparis_id")

            cursor.execute("""
                UPDATE tbl_Siparisler
                SET Durum = 'İptal'
                WHERE SiparisID = ?
                    AND RestoranID IN (
                        SELECT RestoranID
                        FROM tbl_Restoranlar
                        WHERE SahipID = ?
                    )
            """, siparis_id, firma_id)

        # teslim edildi durumu
        elif action == "siparis_teslim":
            siparis_id = request.POST.get("siparis_id")

            # durum teslim edildi olunca data base tarafında teslim tarihi trigger ile yazılıyor
            cursor.execute("""
                UPDATE tbl_Siparisler
                SET Durum = 'Teslim Edildi'
                WHERE SiparisID = ?
                AND RestoranID IN (
                    SELECT RestoranID
                    FROM tbl_Restoranlar
                    WHERE SahipID = ?
                )
            """, siparis_id, firma_id)

        elif action == "yorum_pasif":
            # sp ile yorum pasife alma
            yorum_id = request.POST.get("yorum_id")
            cursor.execute("EXEC sp_YorumSil ?", yorum_id)

        elif action == "yorum_aktif":
            # sp ile yorum aktif etme
            yorum_id = request.POST.get("yorum_id")
            cursor.execute("EXEC sp_YorumAktifEt ?", yorum_id)

        conn.commit()
        conn.close()

    # firma panel listeleri (restoranlar,yorumlar,siparişler)
    conn = get_connection()
    cursor = conn.cursor()

    # firmanın restoranları
    cursor.execute("""
        SELECT RestoranID, RestoranAdi
        FROM tbl_Restoranlar
        WHERE SahipID = ? AND AktifMi = 1
    """, firma_id)
    restoranlar = cursor.fetchall()

   # Yorumlar
    cursor.execute("""
        SELECT 
            y.YorumID,
            r.RestoranAdi,
            y.YorumMetni,
            y.Puan,
            y.AktifMi
        FROM tbl_Yorumlar y
        JOIN tbl_Restoranlar r ON y.RestoranID = r.RestoranID
        WHERE r.SahipID = ?
        ORDER BY y.Tarih desc
    """, firma_id)

    yorumlar = cursor.fetchall()

    # firmaya gelen siparişler
    cursor.execute("""
        SELECT s.SiparisID, r.RestoranAdi, s.Durum
        FROM tbl_Siparisler s
        JOIN tbl_Restoranlar r ON s.RestoranID = r.RestoranID
        WHERE r.SahipID = ?
    """, firma_id)
    siparisler = cursor.fetchall()

    conn.close()

    return render(request, "firma_panel.html", {
        "restoranlar": restoranlar,
        "yorumlar": yorumlar,
        "siparisler": siparisler

    })


# ARAMA

# Kullanıcı yemek adı,restoran adı,kategori adına göre arama yapabiliyor
def arama(request):
    if "kullanici_id" not in request.session:
        return redirect("login")

    # aranacak kelimeyi alıyoruz
    kelime = request.GET.get("q", "").strip()

    # boş arama yapılırsa ana sayfaya dönüyoruz
    if not kelime:
        return redirect("home")

    conn = get_connection()
    cursor = conn.cursor()

    # Sonuçlarda restoranın ortalama puanını ve yorum sayısını fonksiyonlar ile gösteriyoruz
    cursor.execute("""
        SELECT 
            y.YemekID, 
            y.YemekAdi, 
            y.Fiyat, 
            r.RestoranAdi, 
            r.RestoranID,
            k.KategoriAdi,
            dbo.fn_RestoranOrtalamaPuan(r.RestoranID) AS OrtalamaPuan,
            dbo.fn_RestoranYorumSayisi(r.RestoranID) AS YorumSayisi
        FROM tbl_Yemekler y
        JOIN tbl_Restoranlar r ON y.RestoranID = r.RestoranID
        JOIN tbl_Kategoriler k ON y.KategoriID = k.KategoriID
        WHERE y.AktifMi = 1 AND r.AktifMi = 1
          AND (
               y.YemekAdi LIKE ? 
               OR r.RestoranAdi LIKE ? 
               OR k.KategoriAdi LIKE ?
          )
    """, (f"%{kelime}%", f"%{kelime}%", f"%{kelime}%"))

    gelen_kayitlar = cursor.fetchall()
    conn.close()

    return render(request, "arama.html", {
        "q": kelime,
        "sonuclar": gelen_kayitlar
    })


# SEPET İŞLEMLERİ

# SEPETE EKLE
# sepette sadece bir restorana ait ürün olabiliyor
# başka restorandan ürün eklemek isterse kullanıcıdan sepeti boşaltması isteniyor
def sepete_ekle(request):
    if "kullanici_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("home")

    yemek_id = request.POST.get("yemek_id")
    adet = int(request.POST.get("adet", 1))

    if not yemek_id:
        return redirect("home")

    conn = get_connection()
    cursor = conn.cursor()

    # yemek aktif mi,restoran aktif mi bu yemeğin restoranı ne
    cursor.execute("""
        SELECT y.RestoranID
        FROM tbl_Yemekler y
        JOIN tbl_Restoranlar r ON y.RestoranID = r.RestoranID
        WHERE y.YemekID = ? AND y.AktifMi = 1 AND r.AktifMi = 1
    """, yemek_id)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return redirect("home")

    restoran_id = row[0]
    sepet = request.session.get("sepet")

    # sepet yoksa oluştur
    if not sepet:
        sepet = {
            "restoran_id": restoran_id,
            "urunler": {}
        }

    # ürün sepetteki restorana mı ait kontrolü
    if sepet["restoran_id"] != restoran_id:
        messages.error(
            request, "Sepetinizde başka bir restorana ait ürünler var. Lütfen önce sepetinizi boşaltın.")
        return redirect(request.META.get("HTTP_REFERER", "home"))

    # session json anahtarları string olduğu için yemek_id yi stringe çeviriyoruz
    yemek_id = str(yemek_id)
    sepet["urunler"][yemek_id] = sepet["urunler"].get(yemek_id, 0) + adet

    request.session["sepet"] = sepet
    request.session.modified = True

    messages.success(request, "Ürün sepete eklendi.")
    return redirect(request.META.get("HTTP_REFERER", "home"))


# SEPETİM
# Sepet sadece giriş yapan kullanıcıya gösterilir
def sepetim(request):
    if "kullanici_id" not in request.session:
        return redirect("login")

    sepet = request.session.get("sepet")

    # Sepet yoksa boş sepet ekranı
    if not sepet or not sepet.get("urunler"):
        return render(request, "sepet.html", {"urunler": [], "toplam": 0})

    urunler_dict = sepet["urunler"]
    if not urunler_dict:
        return render(request, "sepet.html", {"urunler": [], "toplam": 0})

    # sql IN sorgusu için placeholder listesi oluşturuyoruz: ?, ?, ?
    ids = list(urunler_dict.keys())
    placeholders = ",".join(["?"] * len(ids))

    conn = get_connection()
    cursor = conn.cursor()

    # sepetteki ürünlerin temel bilgisini db den çekiyoruz
    cursor.execute(f"""
        SELECT y.YemekID, y.YemekAdi, y.Fiyat, y.RestoranID, r.RestoranAdi
        FROM tbl_Yemekler y
        JOIN tbl_Restoranlar r ON y.RestoranID = r.RestoranID
        WHERE y.YemekID IN ({placeholders})
    """, ids)

    rows = cursor.fetchall()

    urunler = []
    toplam = 0

    # her ürün için adet * fiyat hesabı yapıyoruz
    for r in rows:
        yemek_id = str(r[0])
        adet = urunler_dict.get(yemek_id, 0)
        ara_toplam = float(r[2]) * int(adet)
        toplam += ara_toplam

        urunler.append({
            "YemekID": r[0],
            "YemekAdi": r[1],
            "BirimFiyat": r[2],
            "Adet": adet,
            "AraToplam": ara_toplam,
        })

    # restoran adı ve min tutarı alıyoruz
    cursor.execute("""
        SELECT RestoranAdi,MinTutar
        FROM tbl_Restoranlar
        WHERE RestoranID = ?
       """, sepet["restoran_id"])

    restoran = cursor.fetchone()
    conn.close()

    if restoran:
        restoran_adi_raw = restoran[0]
        min_tutar = restoran[1]
    else:
        restoran_adi_raw = "Restoran"
        min_tutar = 0

    # restoran görseli için yine isim temizleme
    key = (
        restoran_adi_raw
        .lower()
        .replace(" ", "")
        .replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("ö", "o")
        .replace("ş", "s")
        .replace("ü", "u")
    )

    image_map = {
        "lezzetduragi": "lezzetduragi.jpg",
        "anadolusofrasi": "anadolusofrasi.jpg",
        "ustakebapci": "kebap.jpg",
        "dominospizza": "pizza.jpg",
        "burgerlab": "burger.jpg",
        "cicekevyemekleri": "cicekevyemekleri.jpg",
        "sokaklezzetleri": "sokaklezzetleri.jpg",
        "kozocakbasi": "koz.jpg",
        "gurmetatlar": "gurme.jpg",
        "sefinyeri": "sefinyeri.jpg",
    }

    restoran_image = image_map.get(key)

    return render(request, "sepet.html", {
        "urunler": urunler,
        "toplam": toplam,
        "restoran_adi": restoran_adi_raw,
        "restoran_image": restoran_image,
        "min_tutar": min_tutar,
    })


# SEPET ARTIR
def sepet_artir(request):
    # sepet işlemleri sadece giriş yapan kullanıcıya açık
    if "kullanici_id" not in request.session:
        return redirect("login")
    if request.method != "POST":
        return redirect("sepet")

    yemek_id = str(request.POST.get("yemek_id"))
    sepet = request.session.get("sepet", {})
    urunler = sepet.get("urunler", {})

    # ürün varsa adeti bir artır
    if yemek_id in urunler:
        urunler[yemek_id] += 1

    request.session["sepet"] = sepet
    return redirect("sepet")


# SEPET AZALT
def sepet_azalt(request):
    if "kullanici_id" not in request.session:
        return redirect("login")
    if request.method != "POST":
        return redirect("sepet")

    yemek_id = str(request.POST.get("yemek_id"))
    sepet = request.session.get("sepet", {})
    urunler = sepet.get("urunler", {})

    # ürün varsa adet azaltılır,0 olursa listeden silinir
    if yemek_id in urunler:
        urunler[yemek_id] -= 1
        if urunler[yemek_id] <= 0:
            del urunler[yemek_id]

    # sepet boşaldıysa sessiondan sepeti kaldırıyoruz
    if not urunler:
        del request.session["sepet"]
        return redirect("sepet")

    request.session["sepet"] = sepet
    return redirect("sepet")


# SEPET SİL
def sepet_sil(request):
    if "kullanici_id" not in request.session:
        return redirect("login")
    if request.method != "POST":
        return redirect("sepet")

    yemek_id = str(request.POST.get("yemek_id"))
    sepet = request.session.get("sepet", {})
    urunler = sepet.get("urunler", {})

    # direkt sepeti sil
    if yemek_id in urunler:
        del urunler[yemek_id]

    # sepet boşaldıysa sessiondan kaldır
    if not urunler:
        del request.session["sepet"]
        return redirect("sepet")

    request.session["sepet"] = sepet
    return redirect("sepet")


# SİPARİŞ VER
# tbl_Siparisler kaydı açılır
# tbl_SiparisDetay kayıtları eklenir
# BirimFiyat ve ToplamTutar yazdığım triggerlarla otomatik hesaplanır
# trg_BirimFiyatSabitle gerçek fiyatı yazar
# trg_SiparisToplamGuncelle toplam tutarı hesaplar
def siparis_ver(request):
    if "kullanici_id" not in request.session:
        return redirect("login")

    if request.method != "POST":
        return redirect("sepet")

    sepet = request.session.get("sepet")
    if not sepet or not sepet.get("urunler"):
        return redirect("sepet")

    musteri_id = request.session["kullanici_id"]
    restoran_id = sepet["restoran_id"]
    urunler = sepet["urunler"]

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Siparişi oluşturuyoruz
        # ToplamTutar başlangıçta 0
        cursor.execute("""
            INSERT INTO tbl_Siparisler (MusteriID, RestoranID, ToplamTutar, Durum)
            OUTPUT INSERTED.SiparisID
            VALUES (?, ?, ?, ?)
        """, musteri_id, restoran_id, 0, 'Hazırlanıyor')

        siparis_id = cursor.fetchone()[0]

        # sipariş detaylarını ekliyoruz
        # birim fiyatı 0 gönderiyoruz,birim fiyat triggerı gerçek fiyatı yazacak
        for yemek_id, adet in urunler.items():
            cursor.execute("""
                INSERT INTO tbl_SiparisDetay (SiparisID, YemekID, Adet, BirimFiyat)
                VALUES (?, ?, ?, ?)
            """, siparis_id, yemek_id, adet, 0)

        conn.commit()

        # sipariş tamamlanınca sepeti temizliyoruz
        del request.session["sepet"]
        messages.success(request, "Siparişiniz başarıyla alındı.")

    except Exception as e:
        conn.rollback()  # hata olursa işlemleri geri alıyoruz ki sipariş yarım kalmasın
        messages.error(
            request, f"Sipariş oluşturulurken bir hata oluştu: {str(e)}")
        return redirect("sepet")
    finally:
        conn.close()

    return redirect("home")


# SİPARİŞLERİM
# Kullanıcının geçmiş siparişlerini listeler
# siparişlerin durum,tarih bilgileri burada görünür
# sipariş durumu teslim edildi olduktan sonra kullanıcı yorum yapabilir
def siparislerim(request):
    if "kullanici_id" not in request.session:
        return redirect("login")

    musteri_id = request.session["kullanici_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            s.SiparisID,
            r.RestoranAdi,
            s.ToplamTutar,
            s.Durum,
            s.Tarih,
            s.TeslimTarihi
        FROM tbl_Siparisler s
        JOIN tbl_Restoranlar r ON s.RestoranID = r.RestoranID
        WHERE s.MusteriID = ?
        ORDER BY s.Tarih DESC
    """, musteri_id)

    siparisler = cursor.fetchall()
    conn.close()

    return render(request, "siparislerim.html", {
        "siparisler": siparisler
    })


# YORUMLAR
# restoranın yorumlarını gösterir
# ortalama puan ve yorum sayısı fonksiyonlarla hesaplanır
# sp ile aktif yoeumlar getirilir
def restoran_yorumlari(request, restoran_id):
    conn = get_connection()
    cursor = conn.cursor()

    # restoran bilgisi,ortalama puan ve yorum sayisi(fonksiyonlar ile)
    cursor.execute("""
        SELECT 
            r.RestoranAdi,
            dbo.fn_RestoranOrtalamaPuan(r.RestoranID),
            dbo.fn_RestoranYorumSayisi(r.RestoranID)
        FROM tbl_Restoranlar r
        WHERE r.RestoranID = ? AND r.AktifMi = 1
    """, (restoran_id,))

    restoran = cursor.fetchone()
    if not restoran:
        conn.close()
        return redirect("home")

    # sp ile yorumlar getirilir
    cursor.execute("EXEC sp_RestoranYorumlariGetir ?", (restoran_id,))
    yorumlar = cursor.fetchall()

    conn.close()

    return render(request, "restoran_yorumlari.html", {
        "restoran_adi": restoran[0],
        "ortalama_puan": restoran[1],
        "yorum_sayisi": restoran[2],
        "yorumlar": yorumlar,
        "aktif_kullanici": request.session["kullanici_id"]
    })


# YORUM YAPMA
# kullanıcı sadece teslim edilmiş sipariş için yorum yapabilir(trigger ile)
# aynı siparişe en fazla bir yorum yapabilir
def yorum_yap(request, siparis_id):
    if "kullanici_id" not in request.session:
        return redirect("login")

    musteri_id = request.session["kullanici_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # sipariş gerçekten bu kullanıcıya mı ait ve teslim edildi mi diye kontrol ediyoruz
    cursor.execute("""
        SELECT RestoranID
        FROM tbl_Siparisler
        WHERE SiparisID = ?
          AND MusteriID = ?
          AND Durum = 'Teslim Edildi'
    """, (siparis_id, musteri_id))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return redirect("siparislerim")

    restoran_id = row[0]

    if request.method == "POST":
        puan = request.POST.get("puan")
        yorum = request.POST.get("yorum")

        try:
            # yorum insert ediliyor
            # trigger burada tekrar kontrolleri yapacak
            cursor.execute("""
                INSERT INTO tbl_Yorumlar
                (SiparisID, MusteriID, RestoranID, YorumMetni, Puan, Tarih, AktifMi)
                VALUES (?, ?, ?, ?, ?, GETDATE(), 1)
            """, (siparis_id, musteri_id, restoran_id, yorum, puan))

            conn.commit()
            conn.close()

            messages.success(request, "Yorumunuz başarıyla eklendi.")
            return redirect("siparislerim")

        except pyodbc.Error as e:
            # trigger Raiserror üretirse buraya düşüyor
            conn.rollback()
            hata = str(e)

            # trigger mesajını yakalayıp kullanıcıya daha anlaşılır uyarı veriyoruz
            if "aktif bir yorum bulunmaktadır" in hata:
                messages.warning(
                    request,
                    "Bu sipariş için zaten aktif bir yorumunuz bulunmaktadır."
                )
            elif "Teslim edilmiş sipariş olmadan" in hata:
                messages.warning(
                    request,
                    "Teslim edilmemiş siparişler için yorum yapılamaz."
                )
            else:
                messages.error(
                    request,
                    "Yorum eklenirken bir hata oluştu."
                )

            conn.close()

    return render(request, "yorum_yap.html", {
        "siparis_id": siparis_id
    })


# YORUM SİLME
# kullanıcı sadece kendi yorumunu silebilir
# silme işlemini gerçek delete olarak değil de sp ile AktifMi=0 şeklinde yapıyoruz
def yorum_sil(request, yorum_id):
    if "kullanici_id" not in request.session:
        return redirect("login")

    musteri_id = request.session["kullanici_id"]

    conn = get_connection()
    cursor = conn.cursor()

    # yorum gerçekten bu kullanıcıya mı ait,aktif mi
    cursor.execute("""
        SELECT MusteriID, RestoranID
        FROM tbl_Yorumlar
        WHERE YorumID = ? AND AktifMi = 1
    """, (yorum_id,))

    yorum = cursor.fetchone()

    if not yorum:
        conn.close()
        messages.error(request, "Yorum bulunamadı.")
        return redirect("home")

    # başkasının yorumunu silmeye izin vermiyoruz
    if yorum[0] != musteri_id:
        conn.close()
        messages.error(request, "Bu yorumu silme yetkiniz yok.")
        return redirect("home")

    # sp ile yorum silme
    cursor.execute("EXEC sp_YorumSil ?", (yorum_id,))
    conn.commit()
    conn.close()

    messages.success(request, "Yorumunuz silindi.")
    return redirect("restoran_yorumlari", yorum[1])
