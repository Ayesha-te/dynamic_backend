from django.db import models
from django.utils.text import slugify


class Blog(models.Model):
    BLOG_TYPE_CHOICES = (
        ('manual', 'Manual Blog'),
        ('pdf', 'PDF Blog'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    blog_type = models.CharField(max_length=10, choices=BLOG_TYPE_CHOICES, default='manual')
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='blogs/pdfs/', blank=True, null=True)
    pdf_thumbnail = models.ImageField(upload_to='blogs/pdf_thumbnails/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="blogs/images/", blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordering", "id"]

    def __str__(self):
        return f"Image for {self.blog.title}"
