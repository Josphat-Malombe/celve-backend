from django.db import models
from django.utils.text import slugify
from django.db import IntegrityError, transaction
from uuid import uuid4


# Create your models here.



class Post(models.Model):
    title=models.CharField(max_length=255)
    slug=models.SlugField(max_length=255,unique=True,blank=True)
    content=models.TextField()
    author=models.ForeignKey('core.User', on_delete=models.CASCADE)
    published=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['published']),
        ]



    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True) or str(uuid4())[:8]
            slug = base_slug
            i = 1

            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug

        attempts = 0
        while True:
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                break
            except IntegrityError:
                attempts += 1
                if attempts > 5:
                    raise
 
                self.slug = f"{base_slug}-{uuid4().hex[:6]}"

    def __str__(self):
        return (self.title[:50] + '...') if len(self.title) > 50 else self.title
