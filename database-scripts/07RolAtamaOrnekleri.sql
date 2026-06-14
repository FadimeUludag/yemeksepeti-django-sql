use YemekSepetiDb
go 

-- fadime kullanýcýsýný admin (Rol = 1) yap
UPDATE tbl_Kullanicilar
SET Rol = 1
WHERE Eposta = 'fadime@gmail.com';

-- ateþ kullanýcýsýný firma (Rol = 2) yap
UPDATE tbl_Kullanicilar
SET Rol = 2
WHERE Eposta = 'ates@gmail.com';


-- Sunum ve test sýrasýnda iþlem kolaylýðý saðlamak için
-- tüm restoranlar tek bir firma hesabýna atadým.
-- Ama sistem çoklu firma yapýsýný destekliyor.Ýsteðe baðlý olarak
--her restorana farklý firma da atanabilir.
UPDATE tbl_Restoranlar
SET SahipID = 4;
