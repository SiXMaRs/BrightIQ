from django.db import models

# Create your models here.
class SklearnModel(models.Model):
    name = models.CharField(max_length=300)
    file = models.FileField(upload_to='models/', blank=True, null=True)
    def __str__(self):
        return self.name
    def rain(self):
        pass
    def predict(self):
        pass