from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image
import os


def validate_profile_image(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError('Image file size must be under 5MB.')

    valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    FileExtensionValidator(valid_extensions)(value)

    try:
        with Image.open(value) as img:
            img.verify()
    except Exception:
        raise ValidationError('Upload a valid image file.')


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.ImageField(
        default = 'profile_pics/ADMIN.jpg',
        upload_to = 'profile_pics',
        validators=[validate_profile_image],
    )

    def __str__(self):
        return f'{self.user.username}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            # Ensure the file exists and is accessible
            if hasattr(self.image, 'path') and os.path.exists(self.image.path):
                # Use verify to quickly check image integrity; reopen afterwards
                with Image.open(self.image.path) as _img:
                    _img.verify()
                img = Image.open(self.image.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
        except Exception:
            # Don't let image processing errors break the entire request.
            # Keep the uploaded file as-is and fail gracefully.
            pass

    @property
    def image_url(self):
        """Return a safe URL for the profile image; falls back to admin default if needed."""
        try:
            # image.url raises ValueError if the file is missing, so guard it.
            return self.image.url
        except Exception:
            from django.conf import settings
            return settings.MEDIA_URL + 'profile_pics/ADMIN.jpg'