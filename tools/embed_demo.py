#!/usr/bin/env python3
"""Собирает prototype/demo-photos.js из jpg-файлов в prototype/demo_photos/ (имя файла = ключ).
Фото подгружаются приложением только когда пользователь жмёт «Загрузить учебные примеры»."""
import base64, json, pathlib
R = pathlib.Path(__file__).resolve().parent.parent / "prototype"
d = {p.stem: "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() for p in sorted((R / "demo_photos").glob("*.jpg"))}
(R / "demo-photos.js").write_text("window.DEMO_PH=" + json.dumps(d) + ";\n", encoding="utf-8")
print("demo-photos.js:", len(d), "фото,", round((R / "demo-photos.js").stat().st_size / 1024), "КБ")
