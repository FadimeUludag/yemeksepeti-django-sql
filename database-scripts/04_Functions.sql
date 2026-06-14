use YemekSepetiDb
go


--Restoranýn ortalama puanýný hesaplayan fonksiyon
create function fn_RestoranOrtalamaPuan
(
    @RestoranID int --hangi restoranýn ortalamasý hesaplanacak
)
returns decimal(3,2) --ortalama puaný ondalýklý döndürebilmek için
as
begin
    -- ortalama puaný tutmak için deðiþken
    declare @OrtalamaPuan decimal(3,2)

    -- aktif yorumlarýn puan ortalamasýný alýyoruz
    select @OrtalamaPuan = AVG(CAST(Puan as decimal(3,2)))
    from tbl_Yorumlar
    where RestoranID = @RestoranID
      AND AktifMi = 1 --silinmiþ yorumlar alýnmasýn diye

     -- hesaplanan ortalama deðeri geri döndürüyoruz
    return isnull(@OrtalamaPuan,0)
end
go


--restorana yapýlan yorum sayýsýný veren fonksiyon
create function fn_RestoranYorumSayisi
(
    @RestoranID int -- yorum sayýsý hesaplanacak restoran
)
returns int -- toplam yorum sayýsý
as
begin
    -- Yorum sayýsýný tutmak için deðiþken
    declare @YorumSayisi int

    -- Aktif yorumlarý sayýyoruz
    select @YorumSayisi = COUNT(*)
    from tbl_Yorumlar
    where RestoranID = @RestoranID
      AND AktifMi = 1 -- silinen yorumlar dahil edilmez

    return @YorumSayisi -- yorum sayýsýný geri döndürüyoruz
end
go

--restoranda satýlan aktif yemek sayýsýný veren fonksiyon
create function fn_RestoranAktifYemekSayisi
(
    @RestoranID int  -- hangi restoranýn yemekleri sayýlacak
)
returns int -- aktif yemek sayýsý
as
begin
    -- Yemek sayýsýný tutmak için deðiþken
    declare @YemekSayisi int

    --yemekleri sayýyoruz
    select @YemekSayisi = COUNT(*)
    from tbl_Yemekler
    where RestoranID = @RestoranID
      AND AktifMi = 1 -- satýþý kapalý yemekler sayýlmaz

    return @YemekSayisi -- Hesaplanan yemek sayýsýný geri döndürüyoruz
end
go

