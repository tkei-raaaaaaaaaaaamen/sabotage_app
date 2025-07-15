from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# 授業の総コマ数、必要出席率
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="授業名")
    total_time_block = models.IntegerField(verbose_name="総コマ数")
    need_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="必要出席率")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
class SabotageRecord(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sabotagerecord')
    date = models.DateField()
    absence_type = models.CharField(max_length=10)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
         return f"{self.course.name} - {self.date}"   
    
    
    
    