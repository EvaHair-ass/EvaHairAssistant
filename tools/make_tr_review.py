"""Собирает тексты турецкой страницы для проверки носителем из тех же данных, что и сайт."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_landing as B
t = B.TEXTS["tr"]; a = t["ac"]
L = ["# Melaymade: турецкие тексты посадочной страницы (для проверки носителем)\n",
 "Пояснение для носителя (на турецком): Bu metinler, el işi (handmade) ustaları için hazırlanan bir uygulamanın tanıtım sayfasına aittir. Lütfen doğallık ve doğruluk açısından kontrol eder misin? Üslup: «siz». Terimler: Malzeme Stoku, Maliyet Hesaplama, Fiyatlandırma. Marka adı: Melaymade (tek kelime). Başlıklar kasıtlı olarak cesur ve duygusal yazıldı; doğal ve şık duruyor mu, daha iyi bir söyleyiş var mı? Düzeltmeleri madde madde yazman yeterli, teşekkürler!\n",
 "Особенно важно проверить: заголовки (они смелые и образные) и раздел «Akademi».\n",
 "## Başlık ve giriş",
 f"- Sayfa başlığı: {t['title']}\n- Açıklama: {t['desc']}\n- Menü: {' | '.join(t['nav'])} | {t['login']}",
 f"- Etiket: {a['pill']}\n- Üst yazı: {t['kicker']}\n- Ana başlık: {t['h1'].replace('*','')}\n- Alt başlık: {t['sub']}\n- Düğmeler: {t['cta']} | {t['cta2']}\n- Not: {t['note']}\n",
 f"## {t['how_title']}"]
L += [f"{i}. **{x}**. {y}" for i, (x, y) in enumerate(t["steps"], 1)]
c = t["cr"]; h = t["sh"]
L += ["", f"## {h['title']} (yeni bölüm)", f"- Üst yazı: {h['kick']}\n- Giriş: {h['lead']}\n- Başlıklar: " + " | ".join(h["names"]) + f"\n- Not: {h['note']}\n", f"## {c['title']} (yeni bölüm)", f"- Üst yazı: {c['kick']}\n- Giriş: {c['lead']}\n- Etiketler: " + " | ".join(c["items"]) + f"\n- Alt not: {c['foot']}\n", f"## {c['yt']} (yeni bölüm)", f"- Üst yazı: {c['yk']}\n- Giriş: {c['yl']}"]
L += [f"- **{x}**. {y}" for _, x, y in c["yi"]]
L += ["", "## Akademi (yeni bölüm)",
 f"- Rozet: {a['ac_badge']}\n- Ana başlık: **{a['ac_big']}**\n- Alt başlık: {a['ac_h']}\n- Giriş: {a['ac_lead']}\n- Düğme: {a['ac_cta']}\n", f"### {a['pain_title']}"]
L += [f"- **{q}**\n  {x}" for q, x in a["pains"]]
L += ["", "### Akademi özellikleri"]
L += [f"- [{a['b_ok'] if st == 'ok' else a['b_soon']}] **{ti}**. {tx}" for ic, ti, tx, st in a["ac_cards"]]
L += [f"\n### {a['road_kick']}\n- **{a['road_title']}**\n  {a['road_text']}\n- Dürüst not: {a['ac_note']}\n", f"## {t['feat_title']}"]
L += [f"- **{x}**. {y}" for ic, x, y in t["features"]]
L += [f"\n## {t['gal_title']}", "- Altyazılar: " + " | ".join(t["gal"]) + f"\n- Not: {t['ui_note']}\n", f"## {t['faq_title']}"]
L += [f"- **{q}**\n  {x}" for q, x in t["faq"]]
L += [f"\n## Son çağrı\n- **{t['final_title']}**\n- {t['final_text']}\n- Düğme: {t['final_cta']}\n- Alt bilgi: {t['footer']}"]
(pathlib.Path(__file__).parent.parent / "тексты_страницы_для_проверки_TR.md").write_text("\n".join(L) + "\n", encoding="utf-8")
