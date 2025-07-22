from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course, SabotageRecord, CourseSchedule

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class CourseForm(forms.ModelForm):
    weekly_classes = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        label='週のコマ数',
        help_text='一週間に何回授業があるかを入力してください（1-10）'
    )
    
    class Meta:
        model = Course
        fields = ['name', 'total_time_block', 'need_percent']
        labels = {
            'name': '授業名',
            'total_time_block': '総コマ数',
            'need_percent': '必要出席率（%）'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: データベース基礎'
            }),
            'total_time_block': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 15',
                'min': '1'
            }),
            'need_percent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '例: 70',
                'min': '0',
                'max': '100',
                'step': '0.1',
                'value': '80'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルト値を設定
        if not self.instance.pk:  # 新規作成時のみ
            self.fields['need_percent'].initial = 80
        
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width: 100%; padding: 10px; border: 1px solid #dee2e6; border-radius: 0px; font-size: 14px; box-sizing: border-box;'

class CourseScheduleForm(forms.ModelForm):
    class Meta:
        model = CourseSchedule
        fields = ['weekday', 'period']
        labels = {
            'weekday': '曜日',
            'period': '時限'
        }
        widgets = {
            'weekday': forms.Select(attrs={
                'class': 'form-control'
            }),
            'period': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width: 100%; padding: 10px; border: 1px solid #dee2e6; border-radius: 0px; font-size: 14px; box-sizing: border-box;'

class SabotageRecordForm(forms.ModelForm):
    class Meta:
        model = SabotageRecord
        fields = ['date', 'absence_type', 'note']
        labels = {
            'date': '日付',
            'absence_type': '欠席種別',
            'note': 'メモ'
        }
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'absence_type': forms.Select(
                choices=[
                    ('サボり', 'サボり'),
                    ('病欠', '病欠'),
                    ('忌引', '忌引'),
                    ('その他', 'その他')
                ],
                attrs={'class': 'form-control'}
            ),
            'note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '任意'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['style'] = 'width: 100%; padding: 10px; border: 1px solid #dee2e6; border-radius: 0px; font-size: 14px; box-sizing: border-box;'
