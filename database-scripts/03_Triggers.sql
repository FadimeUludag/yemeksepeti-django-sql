use YemekSepetiDb
go

-- sipariþe yeni bir yemek eklendiðinde toplam tutarý
-- her seferinde elle hesaplamamak için yazdýðým trigger
create trigger trg_SiparisToplamGuncelle
--bu trigger sipariþe yemek eklenince çalýþacak
--o yüzden Sipariþ Detay tablosuna baðlanýyoruz
on tbl_SiparisDetay 
after insert --önce yemek eklensin sonra toplam hesaplansýn 
as
begin
    --update ile sipariþler tablosundaki ToplamTutar alanýný güncelliyoruz
	update s
	set ToplamTutar=(
        -- Ayný sipariþe ait tüm yemeklerin
        -- adet * birim fiyat toplamýný hesaplýyoruz
		select SUM(sd.Adet * sd.BirimFiyat)
        from tbl_SiparisDetay sd
        where sd.SiparisID = s.SiparisID
    )
    -- inserted tablosu, az önce yemek eklenen
    -- sipariþlerin ID’lerini tutar
    -- INNER JOIN ile sadece bu sipariþleri güncelliyoruz
    from tbl_Siparisler s
    INNER JOIN inserted i ON s.SiparisID = i.SiparisID
end
go

-- sipariþe yemek eklenirken fiyatla oynanmasýný engellemek için yazdým
-- yemeðin fiyatýný ekleme anýnda Yemekler tablosundan alýyorum
-- böylece fiyat sonradan deðiþse bile eski sipariþ etkilenmiyor
create trigger trg_BirimFiyatSabitle 
on tbl_SiparisDetay
instead of insert -- insert tabloya gitmesin ve önce trigger çalýþsýn diye
as
begin
    -- Burada sipariþ detay tablosuna eklemeyi ben kontrol ediyorum
    -- Kullanýcýnýn girdiði BirimFiyat'ý dikkate almýyorum
    insert into tbl_SiparisDetay (SiparisID, YemekID, Adet, BirimFiyat)
    SELECT 
        i.SiparisID,
        i.YemekID,
        i.Adet,
        y.Fiyat --yemeðin sistemde kayýtlý olan fiyatýný alýyorum
    -- eklenen yemeðin fiyatýný almak için yemekler tablosu ile eþleþtiriyorum
    from inserted i
    inner join tbl_Yemekler y ON i.YemekID = y.YemekID
    where y.AktifMi = 1   --sadece aktif yemekler
end
go

--ALTER TABLE komutunu tekrar çalýþtýrdýðýmda hata almamak için
--if COL_LENGTH() is null kontrolü ekledim
if COL_LENGTH('tbl_Siparisler', 'TeslimTarihi') is null
begin
    
    --tbl_Siparisler tablosuna
    --TeslimTarihi adýnda
    --tarih–saat tutan yeni sütun ekliyoruz
    alter table tbl_Siparisler
    add TeslimTarihi datetime
    end
go

--yemek teslim edildiði anýn tarih ve saatini kaydetmek için yazdýðým trigger
create trigger trg_TeslimTarihiYaz
on tbl_Siparisler
after update -- güncelleme yapýldýktan sonra trigger çalýþsýn diye
as
begin
    -- durumu "Teslim Edildi" olan sipariþler için
    --tablonun yeni sütunu olan TeslimTarihi'ne
    --o anýn tarih ve saatini atýyoruz
    update tbl_Siparisler
    set TeslimTarihi = GETDATE()
    -- sadece az önce güncellenen ve daha önce teslim tarihi verilmemiþ
    --sipariþler kontrol ediliyor
    where SiparisID IN (select SiparisID from inserted)
      AND Durum = 'Teslim Edildi'
      AND TeslimTarihi IS NULL
END
GO


--restoran pasif duruma getirilirse otomatik
--olarak yemekler de pasif olsun diye yazdýðým trigger
create trigger trg_RestoranPasifYemekPasif
on tbl_Restoranlar
after update --deðiþiklik yapýldýktan sonra trigger çalýþsýn diye
as
begin
    update y 
    set y.AktifMi = 0
    -- pasif yapýlan restoranýn yemeklerini bulmak için
    from tbl_Yemekler y
    inner join inserted i on y.RestoranID = i.RestoranID
    --güncelleme iþlemi restoran pasif olduðunda yapýlsýn
    where i.AktifMi = 0
        AND y.AktifMi=1
end
go

--restoran geri aktif duruma getirilirse otomatik
--olarak yemekler de aktif olsun diye yazdýðým trigger
create trigger trg_RestoranAktifYemekAktif
on tbl_Restoranlar
after update --deðiþiklik yapýldýktan sonra trigger çalýþsýn diye
as
begin
    set nocount on;

    --restoran aktif olduysa
    update y 
    set y.AktifMi = i.AktifMi
    from tbl_Yemekler y
    join inserted i on y.RestoranID = i.RestoranID
    join deleted d on d.RestoranID=i.RestoranID
    where d.AktifMi = 0
        AND i.AktifMi=1
end
go


-- sipariþ teslim edilmeden yorum yapýlmasýný engelleyen trigger
create or alter trigger trg_YorumSiparisKontrol
on tbl_Yorumlar
after insert
as
begin

    set nocount on;

    --Eklenmek istenen yorumlar arasýnda,sipraiþi tesim edilmemiþ olan 
    --kullanýcý var mý kontrol etmek için if exists kullanýyoruz
    if exists(
    select 1
    from inserted i --eklenmek istenen yorumlar

    left join tbl_Siparisler s
        --yorumdaki kullanýcý ve restoran için
        --Durum= 'Teslim Edildi' mi diye bakýyoruz
        on s.SiparisID = i.SiparisID
        and s.MusteriID = i.MusteriID
        and s.RestoranID = i.RestoranID
        AND s.Durum = 'Teslim Edildi'
    
    --eðer sipariþ bulunmazsa left join sonucu null olur
    where s.SiparisID is null

    )
    begin
        --sipariþ teslim edilmediyse yorum ekleme ve kullanýcýya hata mesajý gönder
        raiserror(
            'Teslim edilmiþ sipariþ olmadan yorum yapýlamaz.',
            16,1
        );
        ROLLBACK TRANSACTION;
        return;
    end

    -- ayný sipariþ için birden fazla aktif yorum engeli
    if exists(
        select 1
        from tbl_Yorumlar y
        join inserted i on y.SiparisID=i.SiparisID
        where y.AktifMi=1
            and y.YorumID<>i.YorumID
    )
    begin
        raiserror('Bu sipariþ için zaten aktif bir yorum bulunmaktadýr.',16, 1);
        rollback transaction;
        return;
    end;
end;
go

    