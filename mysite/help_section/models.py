from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Facility(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_postal_code = models.CharField(max_length=20, blank=True, null=True)
    address_city = models.CharField(max_length=100, blank=True, null=True)
    full_address_text_detail = models.TextField(blank=True, null=True)
    hyperreal_link = models.URLField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    voivodeship = models.CharField(max_length=100, blank=True, null=True)
    number_of_places = models.IntegerField(blank=True, null=True)
    addiction_types_text = models.TextField(blank=True, null=True)
    program_lengths_text = models.TextField(blank=True, null=True)
    therapy_types_text = models.TextField(blank=True, null=True)
    facility_type_text = models.TextField(blank=True, null=True)
    psychotherapy_types_text = models.TextField(blank=True, null=True)
    counseling_types_text = models.TextField(blank=True, null=True)
    other_activities_text = models.TextField(blank=True, null=True)
    last_updated_hyperreal_text = models.CharField(max_length=50, blank=True, null=True)
    # Współrzędne geograficzne
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Nowe relacje many-to-many:
    addiction_types = models.ManyToManyField('AddictionType', blank=True, related_name='facilities')
    facility_types = models.ManyToManyField('FacilityType', blank=True, related_name='facilities')
    voivodeships = models.ManyToManyField('Voivodeship', blank=True, related_name='facilities')
    program_lengths = models.ManyToManyField('ProgramLength', blank=True, related_name='facilities')
    therapy_types = models.ManyToManyField('TherapyType', blank=True, related_name='facilities')
    psychotherapy_types = models.ManyToManyField('PsychotherapyType', blank=True, related_name='facilities')
    counseling_types = models.ManyToManyField('CounselingType', blank=True, related_name='facilities')
    legal_issues = models.ManyToManyField('LegalIssue', blank=True, related_name='facilities')
    other_actions = models.ManyToManyField('AdditionalActivity', blank=True, related_name='facilities')
    age_gender_groups = models.ManyToManyField('AgeGenderGroup', blank=True, related_name='facilities')

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            queryset = Facility.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = Facility.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Placówka"
        verbose_name_plural = "Placówki"

class Comment(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        author = self.author
        author_name = author.username if hasattr(author, 'username') else str(author)
        return f'Komentarz dodany przez {author_name} do {self.facility.name}'

    class Meta:
        verbose_name = "Komentarz"
        verbose_name_plural = "Komentarze"
        ordering = ['-created_at']

class RatingCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoria oceny"
        verbose_name_plural = "Kategorie ocen"

class FacilityRating(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='ratings')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(RatingCategory, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('facility', 'author', 'category')
        verbose_name = "Ocena placówki"
        verbose_name_plural = "Oceny placówek"

    def __str__(self):
        author = self.author
        author_name = author.username if hasattr(author, 'username') else str(author)
        return f'{self.facility.name} - {self.category.name}: {self.value} (przez {author_name})'

# --- KATEGORIE I KLASYFIKACJE ---
class AddictionType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Rodzaj uzależnienia"
        verbose_name_plural = "Rodzaje uzależnień"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class FacilityType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Typ placówki"
        verbose_name_plural = "Typy placówek"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class Voivodeship(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Województwo"
        verbose_name_plural = "Województwa"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class ProgramLength(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Długość programu"
        verbose_name_plural = "Długości programów"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class TherapyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Rodzaj terapii"
        verbose_name_plural = "Rodzaje terapii"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class PsychotherapyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Psychoterapia"
        verbose_name_plural = "Psychoterapie"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class CounselingType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Poradnictwo"
        verbose_name_plural = "Poradnictwa"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class LegalIssue(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Kłopot z prawem"
        verbose_name_plural = "Kłopoty z prawem"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class AdditionalActivity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Działanie dodatkowe"
        verbose_name_plural = "Działania dodatkowe"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class AgeGenderGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    def __str__(self): return self.name
    class Meta:
        verbose_name = "Grupa wiekowa/płeć"
        verbose_name_plural = "Grupy wiekowe/płci"

    @property
    def display_name(self):
        return self.name.split(' | Hyperreal [H]elp - chcemy pomóc')[0] if self.name else ''

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletter"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('new_facility', 'Nowa placówka'),
        ('facility_update', 'Aktualizacja placówki'),
        ('new_comment', 'Nowy komentarz'),
        ('new_rating', 'Nowa ocena'),
        ('system', 'Powiadomienie systemowe'),
        ('newsletter', 'Newsletter'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Niski'),
        ('medium', 'Średni'),
        ('high', 'Wysoki'),
        ('urgent', 'Pilny'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)  # For non-registered users
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        recipient = self.user.username if self.user else self.email
        return f'{self.title} - {recipient}'
    
    class Meta:
        verbose_name = "Powiadomienie"
        verbose_name_plural = "Powiadomienia"
        ordering = ['-created_at']

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    new_facilities = models.BooleanField(default=True)
    facility_updates = models.BooleanField(default=False)
    new_comments = models.BooleanField(default=False)
    new_ratings = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Preferencje powiadomień - {self.user.username}'
    
    class Meta:
        verbose_name = "Preferencje powiadomień"
        verbose_name_plural = "Preferencje powiadomień"
