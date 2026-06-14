YEMEKSEPETİ SİPARİŞ SİSTEMİ
Veritabanı Projesi

1. PROJE HAKKINDA GENEL BİLGİ

Bu proje, kullanıcıların restoranları görüntüleyebildiği, sepete ürün ekleyebildiği ve yemekleri online olarak sipariş verebildiği; firmaların gelen siparişleri onaylayabildiği, sipariş durumlarını güncelleyebildiği ve yapılan yorumları görüntüleyebildiği; adminlerin ise tüm sistemi kontrol edebildiği web tabanlı bir uygulamadır.

Proje, Microsoft SQL Server üzerinde oluşturulan bir veritabanı ve
Django framework kullanılarak geliştirilen bir web uygulamasından
oluşmaktadır.

Sipariş toplam tutarı, yorum kontrolleri ve bazı iş kuralları
veritabanı tarafında (trigger ve stored procedure) sağlanmaktadır.


2. GEREKLİ KURULUMLAR

- Python 3.x
- Django
- Microsoft SQL Server
- SQL Server Management Studio (SSMS)
- pyodbc(SQL Server bağlantısı için)
- HTML / CSS (Bootstrap kullanılmıştır)
- JavaScript (sepette adet artırma/azaltma gibi basit işlemler için)
- Visual Studio Code (kod editörü olarak kullanılmıştır)


3. PROJE KLASÖR YAPISI

Projede iki ana bölüm bulunmaktadır:

1) Veritabanı dosyaları
   - Tablolar (CREATE TABLE)
   - Stored Procedure (SP)
   - Trigger (TRG)
   - Function
   - View
   - Test verileri ve rol atama örnekleri

2) Django Web Uygulaması
   - views.py
   - urls.py
   - templates klasörü (HTML dosyaları)
   - static klasörü (CSS / görseller)





4. VERİTABANI KURULUMU

4.1 Bilgisayarda Microsoft SQL Server ve
    SQL Server Management Studio (SSMS) kurulu olmalıdır.
4.2 SQL Server Management Studio (SSMS) açılır.
4.3 Microsoft SQL Server üzerinde "YemeksepetiDb" adlı veritabanı oluşturulur.

4.4 Proje klasörü içinde bulunan SQL dosyaları
   çalıştırılarak:

   1) 01_Tables.sql
   2) 02_StoredProcedures.sql
   3) 03_Triggers.sql
   4) 04_Functions.sql
   5) 05_Views.sql
   6) 06_TestData.sql
   7) 07RolAtamaOrnekleri.sql

   SQL Server üzerine eklenir.

4.5 Veritabanı bağlantısı, Django projesinde pyodbc kullanılarak SQL Server’a    bağlanacak şekilde ayarlanmıştır.


5. DJANGO UYGULAMASINI ÇALIŞTIRMA

Proje sanal ortam (venv) kullanılarak geliştirilmiştir.
Sanal ortam kullanılması önerilir.

5.1 SANAL ORTAM KULLANARAK ÇALIŞTIRMA 

5.1.1 Proje klasörüne girilir.
5.1.2 Sanal ortam oluşturulur:

   python -m venv venv

5.1.3 Sanal ortam aktif edilir:

   Windows:
   venv\Scripts\activate

5.1.4 Gerekli paketler kurulur:

   pip install django pyodbc

5.1.5 Django sunucusu başlatılır:

   python manage.py runserver

Django sunucusu çalıştırıldıktan sonra uygulamaya tarayıcıdan
aşağıdaki adresler üzerinden erişilebilir.

Ana Sayfa (Restoran Listesi):
http://127.0.0.1:8000/

Giriş Sayfası:
http://127.0.0.1:8000/login/

Kayıt Sayfası:
http://127.0.0.1:8000/register/


Not:
Admin ve firma panellerine erişim, kullanıcı rolüne göre
kontrol edilmektedir. Yetkisi olmayan kullanıcılar
bu sayfalara erişemez.


6. UYGULAMAYA GİRİŞ VE ROLLER

Sistemde 3 farklı rol bulunmaktadır:

- Admin (Rol = 1)
- Firma (Rol = 2)
- Müşteri (Rol = 3)

Projeyi kolayca inceleyebilmek için örnek admin ve firma
hesapları test verileri ile birlikte oluşturulmuştur.

Admin Giriş Bilgileri:
E-posta : fadime@gmail.com
Şifre   : fadime

Firma Giriş Bilgileri:
E-posta : ates@gmail.com
Şifre   : ateşsu

Müşteri kullanıcıları sistem üzerinden kayıt olabilir.

Not:
Kolay test edebilmek için tüm restoranlar tek bir firmaya atanmıştır.
isteğe bağlı olarak her bir restoran farklı firmalara atanabilir.


7. ÖNEMLİ NOTLAR

- Sipariş toplam tutarı, veritabanındaki trigger’lar ile otomatik hesaplanmaktadır.
- Bir sipariş teslim edilmeden yorum yapılamaz.
- Aynı sipariş için birden fazla aktif yorum eklenemez.
- Sipariş verildiğinde ürünler sipariş tablolarına aktarılır.
- Bu kontroller trigger ve stored procedure seviyesinde sağlanmıştır.
- Django tarafı bu veritabanı kurallarına göre çalışmaktadır.









