from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PLANT_FAMILY_CHOICES = [
    ('cactus', 'Cactus & Succulents'),
    ('tropical', 'Tropical Foliage'),
    ('ferns', 'Ferns & Leafy Greens'),
    ('flowering', 'Flowering Plants'),
    ('palms', 'Palms & Trees'),
    ('air', 'Air Plants & Moss'),
    ('other', 'Other'),
]

CARE_TYPE_CHOICES = [
    ('water', 'Watered'),
    ('sunlight', 'Sunlight'),
]

WATER_THRESHOLDS = {
    'cactus':    (14, 21),
    'tropical':  (3, 6),
    'ferns':     (2, 4),
    'flowering': (3, 5),
    'palms':     (5, 10),
    'air':       (7, 12),
    'other':     (3, 6),
}

SUN_THRESHOLDS = {
    'cactus':    (7, 14),
    'tropical':  (3, 6),
    'ferns':     (3, 6),
    'flowering': (2, 4),
    'palms':     (4, 8),
    'air':       (5, 10),
    'other':     (3, 6),
}

OVERWATER_THRESHOLDS = {
    'cactus':    7,
    'tropical':  2,
    'ferns':     1,
    'flowering': 2,
    'palms':     3,
    'air':       4,
    'other':     2,
}

OVERSUN_THRESHOLDS = {
    'cactus':    1,
    'tropical':  2,
    'ferns':     1,
    'flowering': 2,
    'palms':     2,
    'air':       2,
    'other':     2,
}


class Plant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant_family = models.CharField(max_length=50, choices=PLANT_FAMILY_CHOICES)
    nickname = models.CharField(max_length=100, blank=True)
    variety = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname if self.nickname else self.get_plant_family_display()

    def get_water_status(self):
        logs = self.carelog_set.filter(care_type='water').order_by('-date_logged')
        last_water = logs.first()
        if not last_water:
            return 'very_thirsty'
        days_since = (timezone.now() - last_water.date_logged).days
        happy_threshold, sad_threshold = WATER_THRESHOLDS.get(self.plant_family, (3, 6))
        overwater_threshold = OVERWATER_THRESHOLDS.get(self.plant_family, 2)
        log_list = list(logs)
        for i in range(len(log_list) - 1):
            days_between = (log_list[i].date_logged - log_list[i + 1].date_logged).days
            if days_between < overwater_threshold:
                return 'overwatered'
        if days_since <= happy_threshold:
            return 'happy'
        elif days_since <= sad_threshold:
            return 'thirsty'
        else:
            return 'very_thirsty'

    def get_sun_status(self):
        logs = self.carelog_set.filter(care_type='sunlight').order_by('-date_logged')
        last_sun = logs.first()
        if not last_sun:
            return 'very_dark'
        days_since = (timezone.now() - last_sun.date_logged).days
        happy_threshold, sad_threshold = SUN_THRESHOLDS.get(self.plant_family, (3, 6))
        oversun_threshold = OVERSUN_THRESHOLDS.get(self.plant_family, 2)
        log_list = list(logs)
        for i in range(len(log_list) - 1):
            days_between = (log_list[i].date_logged - log_list[i + 1].date_logged).days
            if days_between < oversun_threshold:
                return 'too_much_sun'
        if days_since <= happy_threshold:
            return 'happy'
        elif days_since <= sad_threshold:
            return 'needs_sun'
        else:
            return 'very_dark'

    def get_mood(self):
        water = self.get_water_status()
        sun = self.get_sun_status()
        if water == 'overwatered' and sun == 'too_much_sun':
            return 'neglected'
        elif water == 'overwatered':
            return 'overwatered'
        elif sun == 'too_much_sun':
            return 'too_much_sun'
        elif water == 'happy' and sun == 'happy':
            return 'thriving'
        elif water == 'very_thirsty' and sun == 'very_dark':
            return 'neglected'
        elif water == 'very_thirsty':
            return 'very_thirsty'
        elif water == 'thirsty':
            return 'thirsty'
        elif sun == 'very_dark':
            return 'very_dark'
        elif sun == 'needs_sun':
            return 'needs_sun'
        else:
            return 'happy'

    def last_watered(self):
        log = self.carelog_set.filter(care_type='water').order_by('-date_logged').first()
        return log.date_logged if log else None

    def last_sunlight(self):
        log = self.carelog_set.filter(care_type='sunlight').order_by('-date_logged').first()
        return log.date_logged if log else None


class CareLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    care_type = models.CharField(max_length=20, choices=CARE_TYPE_CHOICES)
    date_logged = models.DateTimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_care_type_display()} - {self.plant}"