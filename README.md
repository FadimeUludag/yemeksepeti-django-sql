# Yemeksepeti Sipariş Sistemi

## Proje Hakkında

Bu proje, kullanıcıların restoranları görüntüleyebildiği, sepete ürün ekleyebildiği ve online sipariş verebildiği; firmaların gelen siparişleri yönetebildiği ve yorumları görüntüleyebildiği; yöneticilerin ise sistemi kontrol edebildiği web tabanlı bir uygulamadır.

Proje, **Microsoft SQL Server** üzerinde oluşturulan bir veritabanı ve **Django** framework'ü kullanılarak geliştirilen bir web uygulamasından oluşmaktadır.

Sipariş toplam tutarı hesaplama, yorum kontrolü ve çeşitli iş kuralları veritabanı tarafında **Stored Procedure** ve **Trigger** yapıları kullanılarak gerçekleştirilmiştir.

---

## Kullanılan Teknolojiler

* Python
* Django
* Microsoft SQL Server (MSSQL)
* SQL Server Management Studio (SSMS)
* pyodbc
* HTML
* CSS (Bootstrap)
* JavaScript
* Visual Studio Code

---

## Proje Özellikleri

### Müşteri

* Kullanıcı kayıt ve giriş sistemi
* Restoran listeleme
* Menü görüntüleme
* Sepete ürün ekleme ve çıkarma
* Sipariş oluşturma
* Sipariş geçmişini görüntüleme
* Sipariş sonrası yorum yapabilme

### Firma

* Gelen siparişleri görüntüleme
* Sipariş durumlarını güncelleme
* Restoran yorumlarını görüntüleme

### Admin

* Sistem yönetimi
* Kullanıcı ve firma işlemlerini kontrol etme

---

## Proje Yapısı

### Veritabanı Bölümü

* Tablolar (CREATE TABLE)
* Stored Procedures
* Triggers
* Functions
* Views
* Test Verileri
* Rol Atama Örnekleri

### Django Uygulaması

* Views
* URL Yapıları
* Templates
* Static Dosyalar
* Kullanıcı Yönetimi
* Sipariş Sistemi

---

## Veritabanı Kurulumu

1. Microsoft SQL Server ve SQL Server Management Studio (SSMS) kurulur.
2. `YemeksepetiDb` isimli veritabanı oluşturulur.
3. Aşağıdaki SQL dosyaları sırasıyla çalıştırılır:

```sql
01_Tables.sql
02_StoredProcedures.sql
03_Triggers.sql
04_Functions.sql
05_Views.sql
06_TestData.sql
07RolAtamaOrnekleri.sql
```

4. Django uygulaması, `pyodbc` kullanılarak SQL Server'a bağlanacak şekilde yapılandırılmıştır.

---

## Uygulamayı Çalıştırma

### Sanal Ortam Oluşturma

```bash
python -m venv venv
```

### Sanal Ortamı Aktifleştirme

```bash
venv\Scripts\activate
```

### Gerekli Paketleri Kurma

```bash
pip install -r requirements.txt
```

### Sunucuyu Başlatma

```bash
python manage.py runserver
```

---

## Erişim Adresleri

Ana Sayfa:

```text
http://127.0.0.1:8000/
```

Giriş Sayfası:

```text
http://127.0.0.1:8000/login/
```

Kayıt Sayfası:

```text
http://127.0.0.1:8000/register/
```

---

## Kullanıcı Rolleri

Sistemde üç farklı rol bulunmaktadır:

* Admin
* Firma
* Müşteri

Müşteri kullanıcıları sistem üzerinden kayıt olabilir.

---

## Veritabanı Kuralları

* Sipariş toplam tutarı trigger'lar ile otomatik hesaplanır.
* Sipariş teslim edilmeden yorum yapılamaz.
* Aynı sipariş için birden fazla aktif yorum oluşturulamaz.
* Sipariş verildiğinde ürünler ilgili sipariş tablolarına aktarılır.
* İş kurallarının önemli bir kısmı veritabanı seviyesinde uygulanmaktadır.

---

## Not

Bu proje, Veritabanı Yönetim Sistemleri dersi kapsamında geliştirilmiş olup Django ve MSSQL entegrasyonu kullanılarak hazırlanmıştır.
