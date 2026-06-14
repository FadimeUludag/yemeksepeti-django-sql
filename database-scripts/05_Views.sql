use YemekSepetiDb
go

-- ana sayfada kullanýlacak restoran özet bilgilerini
-- raporlama amacýyla döndüren view
create view vw_AnaSayfaRestoranOzet
as
select
    --restoranýn temel bilgileri
    r.RestoranID,
    r.RestoranAdi,
    r.MinTutar,
    r.Aciklama,

    --restoranýn ortalama puanýný hesaplayan fonksiyon
    dbo.fn_RestoranOrtalamaPuan(r.RestoranID) as OrtalamaPuan,

    --restorana yapýlan toplam yorum sayýsýný hesaplayan fonksiyon
    dbo.fn_RestoranYorumSayisi(r.RestoranID) as YorumSayisi,

    --restoranda aktif olarak satýlan yemek sayýsýný hesaplayan fonksiyon
    dbo.fn_RestoranAktifYemekSayisi(r.RestoranID) as AktifYemekSayisi

from tbl_Restoranlar r
where r.AktifMi = 1 -- sadece aktif restoranlar listelensin
go