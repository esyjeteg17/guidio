import shutil
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from apps.fonts.models import Font


DATA_DIR = Path(settings.BASE_DIR) / "apps" / "fonts" / "data"
ARCHIVES_DIR = DATA_DIR / "font_archives"
TARGET_DIR = Path(settings.MEDIA_ROOT) / "fonts"


# Соответствие: имя архива → (название шрифта в БД, имя файла внутри zip для regular)
ARCHIVE_MAP: dict[str, tuple[str, str]] = {
    "Arial.zip": ("Arial", "arialmt.ttf"),
    "Arial Black.zip": ("Arial Black", "arial_black.ttf"),
    "Bookman Old Style.zip": ("Bookman Old Style", "bookmanoldstyle.ttf"),
    "Century Gothic.zip": ("Century Gothic", "centurygothic.ttf"),
    "Courier New Cyr.zip": ("Courier New", "couriercyrps.ttf"),
    "Georgia.zip": ("Georgia", "georgia.ttf"),
    "KZ Times New Roman.zip": ("Times New Roman", "kztimesnewroman.ttf"),
    "Lucida Console.zip": ("Lucida Console", "lucidaconsole.ttf"),
    "Microsoft Sans Serif.zip": ("MS Sans Serif", "microsoftsansserif.ttf"),
    "ms-reference-serif.zip": ("MS Serif", "MSReferenceSerif.ttf"),
    "Ouroboros.zip": ("Ouroboros", "ouroboros_regular.ttf"),
    "Outward.zip": ("Outward", "outward-block.ttf"),
    "Palatino Linotype.zip": ("Palatino Linotype", "palatinolinotype_roman.ttf"),
    "Tahoma.zip": ("Tahoma", "tahoma.ttf"),
    "Trebuchet MS.zip": ("Trebuchet MS", "trebuchetms.ttf"),
    "Verdana.zip": ("Verdana", "Verdana.ttf"),
    "hyperlegible-sans.zip": ("Hyperlegible Sans", "otf/HyperlegibleSans-Regular.otf"),
    "impact-cufonfonts-webfont.zip": ("Impact", "impact.woff"),
    "murmure-main.zip": ("Murmure", "murmure-main/fonts/le-murmure.ttf"),
    "bebas-neue.zip": ("Bebas Neue", "BebasNeue-Regular.ttf"),
    "droidsansmono.zip": ("Droid Sans Mono", "droidsansmono/DroidSansMono.ttf"),
    "pilowlava.zip": ("Pilowlava", "pilowlava-master/Fonts/Pilowlava-Regular.otf"),
}


def slugify(name: str) -> str:
    return name.lower().replace(" ", "_")


class Command(BaseCommand):
    help = "Распаковывает архивы шрифтов в media/fonts/ и привязывает к Font.file"

    def handle(self, *args, **options):
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        ok, missing_archives, missing_files, missing_fonts = 0, [], [], []

        for archive_name, (font_name, internal_path) in ARCHIVE_MAP.items():
            archive_path = ARCHIVES_DIR / archive_name
            if not archive_path.exists():
                missing_archives.append(archive_name)
                continue

            font = Font.objects.filter(name=font_name).first()
            if not font:
                missing_fonts.append(font_name)
                continue

            try:
                with zipfile.ZipFile(archive_path) as zf:
                    try:
                        member = zf.getinfo(internal_path)
                    except KeyError:
                        missing_files.append(f"{archive_name}:{internal_path}")
                        continue

                    suffix = Path(internal_path).suffix
                    out_dir = TARGET_DIR / slugify(font_name)
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_name = f"{slugify(font_name)}{suffix}"
                    out_path = out_dir / out_name

                    with zf.open(member) as src, open(out_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                relative = out_path.relative_to(settings.MEDIA_ROOT)
                font.file.name = str(relative)
                font.save(update_fields=["file"])
                ok += 1
                self.stdout.write(f"  ✓ {font_name} ← {archive_name}")
            except zipfile.BadZipFile:
                missing_files.append(f"{archive_name} (bad zip)")

        self.stdout.write(self.style.SUCCESS(f"\nРаспаковано шрифтов: {ok}"))
        if missing_archives:
            self.stdout.write(
                self.style.WARNING(f"Нет архивов: {missing_archives}")
            )
        if missing_files:
            self.stdout.write(
                self.style.WARNING(f"Нет файлов в архивах: {missing_files}")
            )
        if missing_fonts:
            self.stdout.write(
                self.style.WARNING(f"Нет таких шрифтов в БД: {missing_fonts}")
            )
