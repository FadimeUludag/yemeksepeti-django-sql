Create DATABASE YemekSepetiDb;
GO
use YemekSepetiDb;
GO


--kullanýcý bilgilerini tutacak bir tablo oluþturuyoruz
Create table tbl_Kullanicilar(
	KullaniciID int primary key identity(1,1), --kullaniciID sini sistem otomatik versin ,identity ile 1 den baþlayýp 1 er 1 er versin
	AdSoyad nvarchar(100) not null, --isim soyisim alaný boþ býrakýlmasýn diye
	Eposta nvarchar(100) unique not null, --ayný maille birden fazla giriþ yapýlmasýn diye unique kullandým
	Sifre nvarchar(50) not null, -- þifre boþ olamaz
	TelefonNo nvarchar(11), -- telefon isteðe baðlý 
	Adres nvarchar(300), --adres alýyoruz
	Rol int not null default 3,-- herkes default olarak müþteri olrak baþlasýn,o yüzden default 3 yaptým
	KayitTarihi datetime default getdate(), -- kayýt olunan andaki tarihi ve saati almasý için
	AktifMi bit default 1 --Müþteriyi silmek yerine pasife çekmek için,0 yaptýðýmýzda müþteri yok sayýlýr
	);

	--kategoriler için tablo
create table tbl_Kategoriler(
	KategoriID int primary key identity(1,1),
	KategoriAdi nvarchar(50) not null,
	AktifMi bit default 1 --kategori o an müþterilere görünsün mü?
);

	-- restoran bilgilerini tutmak için tablo
Create table tbl_Restoranlar(
	RestoranID int primary key identity(1,1), -- Restoranlarý birbirinden ayýrt etmek için benzersiz bir numara, sistem bu numarayý otomatik versin ben elle girmeyeyim
	RestoranAdi nvarchar(100) not null,--restoran adý boþ olmamalý
	Aciklama nvarchar(max), --açýklama için sýnýr olmasýn diye max yaptým
	MinTutar decimal(10,2) not null default 0, -- firma minimum sepet tutarýný boþ býrakýrsa default olarak 0 olsun, decimal ile de küsüratlý sayýlarda sýkýntý çýkmaz
	SahipID int not null, --restoran hangi kullanýcýya ait,bunu belirten id
	AktifMi bit not null default 1, -- restoraný silmek istersek 0 yaparýz
	foreign key (SahipID) references tbl_Kullanicilar(KullaniciID) --restoranýn sahibi mutlaka kullancýlar tablosunda kayýtlý biri olmalý.ShipID KullaniciID ile eþleþmezse olmayan bir kiþiye restoran açamayacaðýmýz için iþlem iptal edilir.
	);


	--yemeklerin listesi
create table tbl_Yemekler(
	YemekID int primary key identity(1,1),-- Her yemeðin bir ID'si olsun, yapacaðým iþlemler için bu id yi kullanýrým
	YemekAdi nvarchar(100) not null, --yemek adý girilmeli,boþ býrakýlmamalý
	Fiyat decimal (10, 2) not null, --fiyat girilmeli
	Icerik nvarchar (250), --içinde ne var ne yok yazsýnlar
	AktifMi bit default 1, --yemek þuan satýlýyor mu
	RestoranID int not null, --hangi dükkanýn yemeði
	KategoriID int,
	foreign key (RestoranID) references tbl_Restoranlar(RestoranID), -- bu yemek hangi dükkana ait? mutlaka restoranlar tablosundaki geçerli bir id ile eþleþmeli
	foreign key (KategoriID) references tbl_Kategoriler(KategoriID) --bu yemek hangi kategoriye ait,kategori tablosundaki id ile eþleþmeli
	);

--sipariþleri kim ,ne zaman, hangi dükkandan istemiþ
create table tbl_Siparisler(
	SiparisID int primary key identity(1,1),
	Tarih Datetime default getdate(), --sipariþ verildiðinde o anki tarih ve saati otomatik almalý
	ToplamTutar decimal (10,2),
	Durum nvarchar(50) default 'Hazýrlanýyor', --sipariþ verildiði anda durum 'hazýrlanýyor' olsun
	MusteriID int not null, --sipariþi veren
	RestoranID int not null, -- sipariþi alan
	foreign key (MusteriID) references tbl_Kullanicilar(KullaniciID),-- müþteri,kullanicilar tablosuna kayýtlý kullanýcý olmalý
	foreign key (RestoranID) references tbl_Restoranlar(RestoranID) --restoran id si de eþleþmeli
	);

create table tbl_SiparisDetay (
	DetayID int primary key identity(1,1),
	SiparisID int not null,
	YemekID int not null, --hangi yemek
	Adet int not null, --kaç adet,mutlaka deðer girilmeli
	BirimFiyat decimal(10,2), -- o anki fiyat
	foreign key (SiparisID) REFERENCES tbl_Siparisler(SiparisID), 
	foreign key (YemekID) references tbl_Yemekler(YemekID) --tablodan yemek id doðrulamasý
);
 
--yemeklere yapýlan yorumlarýn iþleyiþi için tablo
create table tbl_Yorumlar(
	YorumID int primary key identity(1,1),
	YorumMetni nvarchar(500), --yorum yazmasý için alan
	Puan int, --puan verebilsin diye
	Tarih Datetime default getdate(), --yorum yapýlan anýn tarihi ve saati
	MusteriID int not null, --yorum yapan müþteri
	RestoranID int not null, --yorum yapýlan dükkan
	SiparisID int not null,
	AktifMi bit default 1, --yorum silebilmek için (uygunsuz yorumlar vs)
	foreign key (MusteriID) references tbl_Kullanicilar(KullaniciID), --yorumu yapan kiþi kullanýcý olarak kayýtlý olmalý
	foreign key (RestoranID) references tbl_Restoranlar(RestoranID), -- yorum yapýlan dükkanýn id si ile eþleþmeli
	foreign key (SiparisID) references tbl_Siparisler(SiparisID) --siparis id kontrolü yapýyoruz ki sipariþ vermeden yorum yapamasýn
);


