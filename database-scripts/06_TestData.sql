use YemekSepetiDb
go

--Kategoriler
exec sp_KategoriEkle N'Pizza';
exec sp_KategoriEkle N'Kebap';
exec sp_KategoriEkle N'Burger';
exec sp_KategoriEkle N'Tatlý';
exec sp_KategoriEkle N'Ýçecek';
exec sp_KategoriEkle N'Ev Yemeði';

--KategoriID’leri 
--en son eklenen aktif kaydý tutmak için top 1 kullandým
declare @PizzaID int = (select top 1 KategoriID from tbl_Kategoriler where KategoriAdi = N'Pizza'  AND AktifMi=1 ORDER BY KategoriID desc);
declare @KebapID int = (select top  1 KategoriID from tbl_Kategoriler where KategoriAdi = N'Kebap'  AND AktifMi=1 ORDER BY KategoriID desc);
declare @BurgerID int = (select top  1 KategoriID from tbl_Kategoriler where KategoriAdi = N'Burger' AND AktifMi=1 ORDER BY KategoriID desc);
declare @TatliID int = (Select top  1 KategoriID from tbl_Kategoriler where KategoriAdi = N'Tatlý'  AND AktifMi=1 ORDER BY KategoriID desc);
declare @IcecekID int = (select top  1 KategoriID from tbl_Kategoriler where KategoriAdi = N'Ýçecek' AND AktifMi=1 ORDER BY KategoriID desc);
declare @EvYemekID int =(select top 1 KategoriID from tbl_Kategoriler where KategoriAdi=N'Ev Yemeði'  and AktifMi=1 order by KategoriID desc);


--SahipID leri
declare @SahipID int =(select top 1 KullaniciID     --sistemde kullanýcý yoksa
                       from tbl_Kullanicilar        --baþlangýçta iþlemleri test edebilmek için
                       where AktifMi=1              --örnek bir kullanýcý ekleniyor
                       order by KullaniciID);

if @SahipID is null
begin
    exec sp_KullaniciKayit
        @AdSoyad =N'Test Kullanýcý',
        @Eposta  =N'test@test.com',
        @Sifre   =N'1234',
        @Telefon =N'05000000000',
        @Adres   =N'test adres';

    set @SahipID =(select top 1 KullaniciID 
                   from tbl_Kullanicilar 
                   where AktifMi=1 
                   order by KullaniciID desc);
end


--restoranlar
exec sp_RestoranEkle N'Lezzet Duraðý',N'Ev Yemekleri',90, @SahipID;
exec sp_RestoranEkle N'Anadolu Sofrasý',N'Ev Yemekleri',100,@SahipID;
exec sp_RestoranEkle N'Usta Kebapçý',N'Kebap Çeþitleri',150,@SahipID;
exec sp_RestoranEkle N'Dominos Pizza',N'Pizza ve Ýçecekler',120,@SahipID;
exec sp_RestoranEkle N'Burger Lab',N'Burger Menüler',140,@SahipID;
exec sp_RestoranEkle N'Çiçek Ev Yemekleri',N'Günlük Ev Yemekleri',80,@SahipID;
exec sp_RestoranEkle N'Sokak Lezzetleri',N'Hýzlý Yemekler',110,@SahipID;
exec sp_RestoranEkle N'Köz Ocakbaþý',N'Izgara Ürünler',160,@SahipID;
exec sp_RestoranEkle N'Gurme Tatlar',N'Özel Tarifler',180,@SahipID;
exec sp_RestoranEkle N'Þefin Yeri',N'Karýþýk Menüler',130,@SahipID;




--RestoranID leri
declare @LezzetID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Lezzet Duraðý'and AktifMi=1 order by RestoranID desc);
declare @AnadoluID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Anadolu Sofrasý'and AktifMi=1 order by RestoranID desc);
declare @UstaID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Usta Kebapçý'and AktifMi=1 order by RestoranID desc);
declare @DominosID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Dominos Pizza'and AktifMi=1 order by RestoranID desc);
declare @BurgerRID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Burger Lab' and AktifMi=1 order by RestoranID desc);
declare @ÇiçekEvID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Çiçek Ev Yemekleri' and AktifMi=1 order by RestoranID desc);
declare @SokakID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Sokak Lezzetleri'and AktifMi=1 order by RestoranID desc);
declare @KözID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Köz Ocakbaþý'and AktifMi=1 order by RestoranID desc);
declare @GurmeID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Gurme Tatlar'and AktifMi=1 order by RestoranID desc);
declare @SefID int =(select top 1 RestoranID from tbl_Restoranlar where RestoranAdi=N'Þefin Yeri'and AktifMi=1 order by RestoranID desc);



--yemekler

--lezzet duraðý (ev yemeði)
exec sp_YemekEkle N'ev köftesi',120, N'pilavlý', @LezzetID, @EvYemekID;
exec sp_YemekEkle N'nohut',90, N'sulu yemek', @LezzetID,@EvYemekID;
exec sp_YemekEkle N'ayran',25, N'300ml', @LezzetID, @IcecekID;


--anadolu sofrasý (ev yemeði)
exec sp_YemekEkle N'fasulye', 95, N'ev yapýmý', @AnadoluID, @EvYemekID;
exec sp_YemekEkle N'pilav', 40, N'sade',@AnadoluID, @EvYemekID;
exec sp_YemekEkle N'cacýk',30, N'soðuk',  @AnadoluID, @IcecekID;


--usta kebapçýsý (kebap)
exec sp_YemekEkle N'adana kebap',220, N'acýlý',@UstaID,@KebapID;
exec sp_YemekEkle N'urfa kebap',210, N'acýsýz',@UstaID,@KebapID;
exec sp_YemekEkle N'þalgam', 35, N'300ml', @UstaID,@IcecekID;


--Dominos Pizza (pizza)
exec sp_YemekEkle N'karýþýk pizza',180, N'orta boy',@DominosID, @PizzaID;
exec sp_YemekEkle N'margherita',160, N'peynirli', @DominosID,@PizzaID;
exec sp_YemekEkle N'cola',35, N'330ml', @DominosID, @IcecekID;


--burger lab (burger)
exec sp_YemekEkle N'cheeseburger',210, N'menü',@BurgerRID, @BurgerID;
exec sp_YemekEkle N'tavuk burger',180, N'soslu',@BurgerRID, @BurgerID;
exec sp_YemekEkle N'patates kýzartmasý', 60, N'orta boy', @BurgerRID, @BurgerID;


--çiçek ev yemekleri (ev yemeði)
exec sp_YemekEkle N'taze fasulye',95, N'zeytinyaðlý',@ÇiçekEvID,      @EvYemekID;
exec sp_YemekEkle N'karnýyarýk',130, N'patlýcanlý',@ÇiçekEvID,      @EvYemekID;
exec sp_YemekEkle N'yoðurt', 30, N'kase', @ÇiçekEvID,@IcecekID;


--sokak lezzetleri (burger / hýzlý)
exec sp_YemekEkle N'kumru',140, N'sucuklu', @SokakID,@BurgerID;
exec sp_YemekEkle N'kokoreç',160, N'yarým', @SokakID,@KebapID;
exec sp_YemekEkle N'gazoz',30, N'330ml',@SokakID,@IcecekID;


--köz ocakbaþý (ýzgara)
exec sp_YemekEkle N'ýzgara köfte', 190, N'ýzgara',@KözID,@KebapID;
exec sp_YemekEkle N'tavuk kanat',170, N'acýlý',@KözID,@KebapID;
exec sp_YemekEkle N'salata',45, N'mevsim',@KözID,@EvYemekID;


--gurme tatlar (karýþýk)
exec sp_YemekEkle N'özel soslu biftek',280, N'þef tarifi',@GurmeID,@KebapID;
exec sp_YemekEkle N'mantý',150, N'yoðurtlu', @GurmeID, @EvYemekID;
exec sp_YemekEkle N'limonata',35, N'ev yapýmý',@GurmeID,@IcecekID;


--þefin yeri (karýþýk)
exec sp_YemekEkle N'günün yemeði',160, N'deðiþken',@SefID,@EvYemekID;
exec sp_YemekEkle N'fýrýn makarna',140, N'kaþarlý', @SefID,@EvYemekID;
exec sp_YemekEkle N'sütlaç',90, N'tatlý', @SefID,@TatliID;


select * from vw_AnaSayfaRestoranOzet;
go