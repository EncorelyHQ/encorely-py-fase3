"""
Seed de demostración para la exposición.

Crea un administrador y tres usuarios de ejemplo, y registra swipes RIGHT
suficientes para desbloquear el Radar (>= 25) y calcular el ADN musical de cada uno.
Es idempotente: se puede ejecutar varias veces sin duplicar datos.

    python manage.py seed_demo
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.chat.models import ChatRoom, Message
from apps.matches.models import Friendship, FriendshipStatus
from apps.matches.services import MatchService
from apps.music.models import Song, Swipe, SwipeType

User = get_user_model()

DEMO_PASSWORD = "Encorely2026!"

DEMO_USERS = [
    {
        "username": "camilo",
        "email": "camilo@encorely.com",
        "display_name": "Camilo R.",
        "city": "Medellín",
        "concert_mood": "moshpit",
    },
    {
        "username": "juandiego",
        "email": "juandiego@encorely.com",
        "display_name": "Juan Diego",
        "city": "Bogotá",
        "concert_mood": "front_row",
    },
    {
        "username": "emmanuel",
        "email": "emmanuel@encorely.com",
        "display_name": "Emmanuel",
        "city": "Cali",
        "concert_mood": "vip",
    },
]

SWIPES_TO_UNLOCK_RADAR = 26

# Catálogo extra para garantizar canciones suficientes (>= 26) y desbloquear el Radar.
# Cada tupla: (título, artista, energy, danceability, valence, tempo) en rango [0, 1].
EXTRA_SONGS = [
    ("Blinding Lights", "The Weeknd", 0.80, 0.51, 0.33, 0.69),
    ("Levitating", "Dua Lipa", 0.83, 0.70, 0.91, 0.60),
    ("Bad Guy", "Billie Eilish", 0.43, 0.70, 0.56, 0.55),
    ("Watermelon Sugar", "Harry Styles", 0.82, 0.55, 0.56, 0.39),
    ("Don't Start Now", "Dua Lipa", 0.79, 0.79, 0.68, 0.55),
    ("Peaches", "Justin Bieber", 0.70, 0.68, 0.46, 0.45),
    ("Montero", "Lil Nas X", 0.62, 0.61, 0.76, 0.71),
    ("Good 4 U", "Olivia Rodrigo", 0.66, 0.56, 0.69, 0.83),
    ("Stay", "The Kid LAROI", 0.76, 0.59, 0.48, 0.85),
    ("Industry Baby", "Lil Nas X", 0.70, 0.74, 0.89, 0.62),
    ("Shivers", "Ed Sheeran", 0.86, 0.79, 0.82, 0.71),
    ("Easy On Me", "Adele", 0.27, 0.60, 0.13, 0.57),
    ("Cold Heart", "Elton John", 0.79, 0.80, 0.94, 0.51),
    ("abcdefu", "GAYLE", 0.54, 0.69, 0.41, 0.61),
    ("Heat Waves", "Glass Animals", 0.53, 0.76, 0.53, 0.40),
    ("Enemy", "Imagine Dragons", 0.74, 0.57, 0.50, 0.77),
    ("Ghost", "Justin Bieber", 0.71, 0.61, 0.66, 0.61),
    ("Woman", "Doja Cat", 0.55, 0.82, 0.57, 0.51),
    ("Happier Than Ever", "Billie Eilish", 0.30, 0.33, 0.22, 0.45),
    ("Beggin'", "Måneskin", 0.80, 0.71, 0.59, 0.65),
    ("Flowers", "Miley Cyrus", 0.68, 0.71, 0.65, 0.59),
    ("Anti-Hero", "Taylor Swift", 0.64, 0.64, 0.53, 0.49),
    ("As It Was", "Harry Styles", 0.73, 0.52, 0.66, 0.69),
    ("Unholy", "Sam Smith", 0.47, 0.71, 0.24, 0.66),
    ("Calm Down", "Rema", 0.66, 0.80, 0.80, 0.54),
    ("Kill Bill", "SZA", 0.55, 0.64, 0.42, 0.44),
    ("Creepin'", "Metro Boomin", 0.62, 0.72, 0.50, 0.49),
    ("Die For You", "The Weeknd", 0.62, 0.58, 0.51, 0.67),
    ("La Bachata", "Manuel Turizo", 0.70, 0.85, 0.78, 0.51),
    ("Tití Me Preguntó", "Bad Bunny", 0.72, 0.65, 0.40, 0.71),
    ("Me Porto Bonito", "Bad Bunny", 0.70, 0.91, 0.42, 0.46),
    ("Quevedo: BZRP Vol. 52", "Bizarrap", 0.62, 0.62, 0.55, 0.64),
    ("Ojitos Lindos", "Bad Bunny", 0.57, 0.62, 0.56, 0.55),
    ("Despechá", "Rosalía", 0.78, 0.81, 0.84, 0.65),
    ("Tacones Rojos", "Sebastián Yatra", 0.83, 0.73, 0.88, 0.62),
    ("Pepas", "Farruko", 0.92, 0.74, 0.50, 0.92),
    ("Vampire", "Olivia Rodrigo", 0.53, 0.51, 0.36, 0.48),
    ("Seven", "Jung Kook", 0.79, 0.79, 0.75, 0.62),
    ("Paint The Town Red", "Doja Cat", 0.61, 0.87, 0.70, 0.50),
    ("Dance The Night", "Dua Lipa", 0.83, 0.67, 0.78, 0.55),
    ("What Was I Made For?", "Billie Eilish", 0.18, 0.33, 0.20, 0.40),
    ("Sunflower", "Post Malone", 0.48, 0.76, 0.91, 0.65),
    ("Circles", "Post Malone", 0.76, 0.70, 0.55, 0.48),
    ("Save Your Tears", "The Weeknd", 0.83, 0.68, 0.64, 0.59),
    ("Starboy", "The Weeknd", 0.59, 0.68, 0.49, 0.62),
    ("Believer", "Imagine Dragons", 0.78, 0.77, 0.67, 0.62),
    ("Shape of You", "Ed Sheeran", 0.65, 0.83, 0.93, 0.48),
    ("Blank Space", "Taylor Swift", 0.70, 0.76, 0.57, 0.48),
]


class Command(BaseCommand):
    help = "Crea el admin + 3 usuarios demo con swipes para la exposición (idempotente)."

    def handle(self, *args, **options):
        self._ensure_songs()
        self._seed_events()
        self._upsert_admin()

        songs = list(Song.objects.all()[:SWIPES_TO_UNLOCK_RADAR])
        for data in DEMO_USERS:
            self._upsert_user(data, songs)

        self._seed_accepted_match("camilo", "juandiego")

        self.stdout.write(self.style.SUCCESS("\nSeed de demostración completado."))

    def _seed_events(self) -> None:
        """Carga el catálogo de eventos desde el fixture (idempotente por pk)."""
        fixture = settings.BASE_DIR / "fixtures" / "events.json"
        if fixture.exists():
            call_command("loaddata", str(fixture), verbosity=0)
            self.stdout.write(self.style.SUCCESS("Eventos   -> cargados desde fixture"))

    def _seed_accepted_match(self, username_a: str, username_b: str) -> None:
        """Crea un match ACEPTADO entre dos usuarios (genera sala de chat) + mensajes."""
        try:
            ua = User.objects.get(username=username_a)
            ub = User.objects.get(username=username_b)
        except User.DoesNotExist:
            return

        # El modelo exige user_source.id < user_target.id para un par único.
        source, target = (ua, ub) if ua.id < ub.id else (ub, ua)
        friendship, _ = Friendship.objects.update_or_create(
            user_source=source,
            user_target=target,
            defaults={
                "status": FriendshipStatus.ACCEPTED,
                "matched_at": timezone.now(),
                "compatibility_score": MatchService.pair_score(source, target),
            },
        )
        # El signal de chat crea la sala al aceptar; aseguramos su existencia.
        room, _ = ChatRoom.objects.get_or_create(friendship=friendship)

        if not room.messages.exists():
            Message.objects.create(room=room, sender=source, content="¡Hola! Hicimos match musical 🙌")
            Message.objects.create(room=room, sender=target, content="¡Brutal! ¿Vas a algún concierto pronto?")
        self.stdout.write(
            self.style.SUCCESS(f"Match     -> {username_a} ↔ {username_b} aceptado (sala #{room.id})")
        )

    def _ensure_songs(self) -> None:
        """Garantiza al menos 26 canciones para que se pueda desbloquear el Radar."""
        for title, artist, energy, dance, valence, tempo in EXTRA_SONGS:
            Song.objects.get_or_create(
                title=title,
                artist_name=artist,
                defaults={
                    "energy": energy,
                    "danceability": dance,
                    "valence": valence,
                    "tempo": tempo,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Canciones -> {Song.objects.count()} en catálogo"))

    def _upsert_admin(self) -> None:
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@encorely.com", "display_name": "Administrador"},
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password(DEMO_PASSWORD)
        admin.save()
        self.stdout.write(self.style.SUCCESS(f"Admin     -> admin / {DEMO_PASSWORD}"))

    def _upsert_user(self, data: dict, songs: list[Song]) -> None:
        username = data["username"]
        user, _ = User.objects.get_or_create(username=username)
        for field, value in data.items():
            setattr(user, field, value)
        user.set_password(DEMO_PASSWORD)
        user.save()

        # El signal post_save de Swipe incrementa swipe_count y recalcula el ADN.
        for song in songs:
            Swipe.objects.get_or_create(
                user=user, song=song, defaults={"type": SwipeType.RIGHT}
            )

        user.refresh_from_db()
        self.stdout.write(
            self.style.SUCCESS(
                f"Usuario   -> {username} / {DEMO_PASSWORD}  ({user.swipe_count} swipes)"
            )
        )
