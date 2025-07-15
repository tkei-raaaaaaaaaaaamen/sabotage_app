from django.contrib import admin
from .models import Course, SabotageRecord

# Register your models here.

# SabotageRecordをCourseの詳細画面でインライン表示
class SabotageRecordInline(admin.TabularInline):
    model = SabotageRecord
    extra = 0  # 空のフォームを表示しない
    fields = ['date', 'absence_type', 'note']
    readonly_fields = ['created_at']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'total_time_block', 'need_percent', 'created_at']
    list_filter = ['user', 'created_at', 'need_percent']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SabotageRecordInline]
    
    fieldsets = (
        ('基本情報', {
            'fields': ('user', 'name')
        }),
        ('授業設定', {
            'fields': ('total_time_block', 'need_percent')
        }),
        ('タイムスタンプ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SabotageRecord)
class SabotageRecordAdmin(admin.ModelAdmin):
    list_display = ['course', 'date', 'absence_type', 'created_at']
    list_filter = ['course', 'date', 'absence_type', 'created_at']
    search_fields = ['course__name', 'note']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('欠席情報', {
            'fields': ('course', 'date', 'absence_type')
        }),
        ('メモ', {
            'fields': ('note',)
        }),
        ('タイムスタンプ', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
