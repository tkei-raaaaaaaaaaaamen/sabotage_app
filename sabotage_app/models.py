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

# 授業のスケジュール（曜日・時限）
class CourseSchedule(models.Model):
    WEEKDAY_CHOICES = [
        ('monday', '月曜日'),
        ('tuesday', '火曜日'),
        ('wednesday', '水曜日'),
        ('thursday', '木曜日'),
        ('friday', '金曜日'),
    ]
    
    PERIOD_CHOICES = [
        (1, '1限'),
        (2, '2限'),
        (3, '3限'),
        (4, '4限'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.CharField(max_length=10, choices=WEEKDAY_CHOICES, verbose_name="曜日")
    period = models.IntegerField(choices=PERIOD_CHOICES, verbose_name="時限")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['weekday', 'period']
        unique_together = ('course', 'weekday', 'period')  # 同じ授業が同じ時間に重複しないように
        
    def __str__(self):
        return f"{self.course.name} ({self.get_weekday_display()}{self.period}限)"

class SabotageRecord(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sabotagerecord')
    date = models.DateField()
    absence_type = models.CharField(max_length=10)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
         return f"{self.course.name} - {self.date}"   
    
    
    
    