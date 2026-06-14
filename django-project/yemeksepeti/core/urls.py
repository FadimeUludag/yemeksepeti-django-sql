from django.contrib import admin

# view fonksiyonları
from django.urls import path
from core.views import ana_sayfa, restoran_menu, login_view, register_view, logout_view
from core.views import admin_panel, firma_panel
from core.views import arama, siparis_ver, siparislerim
from core.views import (sepetim, sepete_ekle,
                        sepet_artir, sepet_azalt, sepet_sil)
from core.views import restoran_yorumlari, yorum_yap, yorum_sil


urlpatterns = [
    # django admin paneli
    path('admin/', admin.site.urls),

    # ana sayfa (restoran listesi)
    path('', ana_sayfa, name='home'),

    # restoran menü
    path('restoran/<int:restoran_id>/', restoran_menu, name='restoran_menu'),

    # login
    path('login/', login_view, name='login'),

    # register
    path('register/', register_view, name='register'),

    # logout
    path('logout/', logout_view, name='logout'),

    # admin
    path("admin-panel/", admin_panel, name="admin_panel"),

    # firma
    path("firma/", firma_panel, name="firma_panel"),

    # arama
    path("arama/", arama, name="arama"),

    # sipariş verme
    path("siparis-ver/", siparis_ver, name="siparis_ver"),

    # siparişlerim
    path("siparislerim/", siparislerim, name="siparislerim"),

    # sepet
    path("sepet/", sepetim, name="sepet"),
    path("sepete-ekle/", sepete_ekle, name="sepete_ekle"),
    path("sepet-artir/", sepet_artir, name="sepet_artir"),
    path("sepet-azalt/", sepet_azalt, name="sepet_azalt"),
    path("sepet-sil/", sepet_sil, name="sepet_sil"),

    # yorumlar
    path("restoran/<int:restoran_id>/yorumlar/",
         restoran_yorumlari, name="restoran_yorumlari"),
    path("siparis/<int:siparis_id>/yorum-yap/",
         yorum_yap, name="yorum_yap"),
    path("yorum/<int:yorum_id>/sil/", yorum_sil, name="yorum_sil"),





]
