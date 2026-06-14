USE YemekSepetiDb;
GO

-- Kullanýcý Kaydý
--Kullanýcýdan bilgileri alsýn ve veritabanýna 'Müþteri' (Rol=3) olarak kaydetsin
create procedure sp_KullaniciKayit
    
    --kayýtta lazým olacak veriler için dýþardan gelen parametreler
    @AdSoyad nvarchar(100),
    @Eposta nvarchar(100),
    @Sifre nvarchar(50),
    @Telefon nvarchar(11),
    @Adres nvarchar(300)
as
begin
--gelen verileri tabloya ekliyoruz
    insert into tbl_Kullanicilar (AdSoyad,Eposta,Sifre,TelefonNo,Adres, Rol,AktifMi)
--rol alanýna varsayýlan olarak 3(müþteri) atýyoruz
    values (@AdSoyad,@Eposta,@Sifre,@Telefon,@Adres, 3,1)
end
go


--Kullanýcý giriþi
create procedure sp_KullaniciGiris
    @Eposta nvarchar(100),
    @Sifre nvarchar(50)
as
begin
    select KullaniciID, AdSoyad, Rol 
    FROM tbl_Kullanicilar 
    WHERE Eposta = @Eposta 
    AND Sifre = @Sifre --E-posta ve þifre  kontrolü yapar.Eþleþirse ID, isim ve rol bilgisini döndürür.
    AND AktifMi = 1 -- Sadece aktif kullanýcýlar,silinenler(AktifMi = 0) giriþ yapamaz
end
go

--anasayfada kategoriye göre restoranlarý listeleyen sp
alter procedure sp_AnaSayfaRestoranListele
    @KategoriID int = null
as
begin
    select distinct
        v.RestoranID,
        v.RestoranAdi,
        v.MinTutar,
        v.Aciklama,
        v.OrtalamaPuan,
        v.YorumSayisi,
        v.AktifYemekSayisi

    -- ana sayfada gösterilecek restoran özet bilgileri view üzerinden alýnýyor
    from vw_AnaSayfaRestoranOzet v 
    join tbl_Yemekler y 
        on v.RestoranID = y.RestoranID
    where y.AktifMi = 1
      and (
            @KategoriID IS NULL
            OR y.KategoriID = @KategoriID
          )
end
go


--restorana týklayýnca menü getirir
create procedure sp_RestoranMenusuGetir
    @RestoranID int 
as
begin
    select 
        y.YemekID, 
        y.YemekAdi, 
        y.Fiyat, 
        y.Icerik,
        k.KategoriAdi
    from tbl_Yemekler y
    left join tbl_Kategoriler k ON y.KategoriID=k.KategoriID
    where y.RestoranID = @RestoranID 
        AND y.AktifMi = 1 --sadece aktif yemekler sipariþ verilebilsin
    ORDER BY k.KategoriAdi --kategorilere göre sýralý gelsin
end
go

--yorumlarý görüntülemek için
alter procedure sp_RestoranYorumlariGetir
    @RestoranID int
as
begin
    select
        y.YorumID,          -- silme için gerekli
        y.MusteriID,
        k.AdSoyad,
        y.YorumMetni,
        y.Puan,
        y.Tarih      
    from tbl_Yorumlar y
    join tbl_Kullanicilar k on k.KullaniciID= y.MusteriID  -- Yazan kiþinin ismini bulmak için birleþtiriyoruz,yazan kiþi kulanýcýlar tablosunda yoksa o yorumu getirmiyoruz
    where y.RestoranID = @RestoranID --ayný restorana yapýlan tüm yorumlarý listelemek için
      and y.AktifMi = 1 -- silinmiþ yorumlarý getirme
    ORDER BY y.Tarih desc; -- en yeni yorum en baþta gözüksün
end
go


  --yorum silmek için
create procedure sp_YorumSil
    @YorumID int
as
begin
    update tbl_Yorumlar
    set AktifMi = 0 
    where YorumID = @YorumID
end
go

--yorumlar istendiðinde geri aktif edilebilsin diye
create procedure sp_YorumAktifEt
    @YorumID int
as
begin
    update tbl_Yorumlar
    set AktifMi = 1
    where YorumID = @YorumID
end
go      


--kullanýcýya kullanýcý ya da firma rolü verebilmek için
create procedure sp_KullaniciRolGuncelle
    @KullaniciID int,
    @YeniRol int
as
begin
    UPDATE tbl_Kullanicilar
    set Rol = @YeniRol
    where KullaniciID = @KullaniciID
end
go


--Kategori tanýmlama (tatlý,ev yemeði vs)
create procedure sp_KategoriEkle
    @KategoriAdi nvarchar(50)
as
begin
    insert into tbl_Kategoriler(KategoriAdi,AktifMi)
    values(@KategoriAdi,1)
end
go


--yemek firmasý eklemek için kullanýyoruz
create procedure sp_RestoranEkle
    @RestoranAdi nvarchar(100),
    @Aciklama nvarchar(max),
    @MinTutar decimal(10,2),
    @SahipID int --restoraný hangi kullanýcýnýn yönettiði (foreign key)
as 
begin
--Restoranlar tablosuna veri ekliyoruz
    insert into tbl_Restoranlar (RestoranAdi, Aciklama, MinTutar, SahipID,AktifMi)
    VALUES (@RestoranAdi, @Aciklama, @MinTutar, @SahipID,1)
end
go


--NOT:
--Bu Stored Procedure ler, veritabaný bakým ve test amaçlý olarak hazýrlanmýþtýr.
--Projede ilgili iþlem Django tarafýnda doðrudan UPDATE sorgularý ile
--yapýldýðý için aktif olarak çaðrýlmamaktadýr.

--Ancak ayný iþlemin veritabaný tarafýnda merkezi ve tekrar kullanýlabilir
--bir þekilde yapýlabilmesi amacýyla SP olarak da tanýmlanmýþtýr.
--SSMS üzerinden baðýmsýz olarak çalýþtýrýlabilir durumdadýr.
create procedure sp_KullaniciSil
    @KullaniciID int
as 
begin
    update tbl_Kullanicilar SET AktifMi = 0 --kullanici silme iþlemi,AktifMi kolonunu set ile 0 olarak update ederek siliyoruz
    where KullaniciID = @KullaniciID
end
go


--Kategori Sil
create procedure sp_KategoriSil
    @KategriID int
as
begin
    update tbl_Kategoriler
    set AktifMi=0
    where KategoriID=@KategriID
end 
go



create procedure sp_RestoranSil
    @RestoranID int
as
begin
    update tbl_Restoranlar SET AktifMi = 0 --restoran silme iþlemi
    where RestoranID = @RestoranID
end
go

create procedure sp_RestoranAktifEt
    @RestoranID int
as
begin
    update tbl_Restoranlar SET AktifMi = 1 --restoraný geri aktif etme
    where RestoranID = @RestoranID
end
go


-- Yemek ekleme(firma paneli)
-- Restoranýn kendi menüsüne yeni bir ürün eklemesini saðlar.
create procedure sp_YemekEkle
    @YemekAdi nvarchar(100),
    @Fiyat decimal(10,2),
    @Icerik nvarchar(250),
    @RestoranID int,
    @KategoriID int
as
begin
    insert into tbl_Yemekler (YemekAdi, Fiyat, Icerik, RestoranID,KategoriID, AktifMi)
    values (@YemekAdi, @Fiyat, @Icerik, @RestoranID,@KategoriID, 1)
end
go


--yemek silme iþlemi
create procedure sp_YemekSil
    @YemekID int
as
begin
    update tbl_Yemekler set AktifMi=0
    where YemekID=@YemekID
end
go





--sepet onayi
create procedure sp_SiparisOlustur
    @MusteriID int,
    @RestoranID int,
    @YeniSiparisID int output --@YeniSiparisID parametresi dýþarýya sipraiþ numarasý verecek
as
begin
    insert into tbl_Siparisler (MusteriID, RestoranID, ToplamTutar, Durum, Tarih)
    values (@MusteriID, @RestoranID,0,'Hazýrlanýyor', GETDATE());
    set @YeniSiparisID = SCOPE_IDENTITY(); --en son oluþturulan sipariþin numarasýný (ID) tutmak için SCOPE_IDENTITY() kullanýyoruz
end
go


--sipariþ durumunu güncelle
create procedure sp_SiparisDurumGuncelle
    @SiparisID int,
    @YeniDurum nvarchar(50)
as
begin
    update tbl_Siparisler
    set Durum=@YeniDurum --sipariþin durumunu yeni gelen durumla deðiþtiriyoruz
    where SiparisID=@SiparisID
end
go





