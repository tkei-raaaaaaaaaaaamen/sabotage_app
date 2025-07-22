from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Course, SabotageRecord, CourseSchedule
from .forms import CustomUserCreationForm, CourseForm, SabotageRecordForm, CourseScheduleForm
# Create your views here.

@method_decorator(login_required, name='dispatch')
class IndexView(View):
    def get(self, request):
        # 時間割の表示設定
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        weekday_names = {
            'monday': '月',
            'tuesday': '火',
            'wednesday': '水',
            'thursday': '木',
            'friday': '金'
        }
        periods = range(1, 5)  # 1-4限
        
        # ユーザーの全スケジュールを取得
        schedules = CourseSchedule.objects.filter(course__user=request.user).select_related('course')
        
        # 時間割テーブル用のデータ構造を作成
        timetable = {}
        for weekday in weekdays:
            timetable[weekday] = {}
            for period in periods:
                timetable[weekday][period] = None
        
        # 各授業の統計情報を計算してマップを作成
        course_stats_map = {}
        courses = Course.objects.filter(user=request.user)
        for course in courses:
            sabotage_records = SabotageRecord.objects.filter(course=course)
            
            # 計算ロジック
            total_classes = course.total_time_block
            required_attendance_rate = course.need_percent / 100
            required_attendance_count = total_classes * required_attendance_rate
            current_absence_count = sabotage_records.count()
            max_absence_count = total_classes - required_attendance_count
            remaining_absence_count = max_absence_count - current_absence_count
            
            course_stats_map[course.id] = {
                'current_absence_count': current_absence_count,
                'max_absence_count': int(max_absence_count),
                'remaining_absence_count': int(remaining_absence_count),
                'recent_records': sabotage_records.order_by('-date')[:3]
            }
        
        # スケジュールを時間割に配置（統計情報付き）
        for schedule in schedules:
            schedule.stats = course_stats_map.get(schedule.course.id, {
                'current_absence_count': 0,
                'max_absence_count': 0,
                'remaining_absence_count': 0,
                'recent_records': []
            })
            timetable[schedule.weekday][schedule.period] = schedule
        
        # 各授業の統計情報も計算
        courses_with_stats = []
        for course in courses:
            stats = course_stats_map.get(course.id, {})
            if stats:
                courses_with_stats.append({
                    'course': course,
                    **stats
                })
        
        context = {
            'timetable': timetable,
            'weekdays': weekdays,
            'weekday_names': weekday_names,
            'periods': periods,
            'courses_with_stats': courses_with_stats
        }
        return render(request, "sabotage_app/index.html", context)

index = IndexView.as_view()

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'sabotage_app/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('index')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
        
        return render(request, 'sabotage_app/login.html')

login_view = LoginView.as_view()

def logout_view(request):
    logout(request)
    return redirect('login')

class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        form = CustomUserCreationForm()
        return render(request, 'sabotage_app/signup.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
        return render(request, 'sabotage_app/signup.html', {'form': form})

signup = SignupView.as_view()

@method_decorator(login_required, name='dispatch')
class SabotageRecordEditView(View):
    def post(self, request):
        course_id = request.POST.get('course_id')
        action = request.POST.get('action')
        
        if course_id:
            course = get_object_or_404(Course, id=course_id, user=request.user)
            
            if action == 'absence':
                # 欠席記録を追加
                date = request.POST.get('date')
                absence_type = request.POST.get('absence_type', '公欠')
                note = request.POST.get('note', '')
                
                if date:
                    sabotage_record = SabotageRecord(
                        course=course,
                        date=date,
                        absence_type=absence_type,
                        note=note
                    )
                    sabotage_record.save()
                    messages.success(request, f'{course.name}の欠席記録を追加しました。')
            
            elif action == 'delete':
                # 欠席記録を削除
                record_id = request.POST.get('record_id')
                if record_id:
                    try:
                        record = SabotageRecord.objects.get(id=record_id, course__user=request.user)
                        record.delete()
                        messages.success(request, '欠席記録を削除しました。')
                    except SabotageRecord.DoesNotExist:
                        messages.error(request, '削除対象の記録が見つかりませんでした。')
            
            return redirect('course_detail', course_id=course_id)
        return redirect('index')

sabotage_record_edit = SabotageRecordEditView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseDetailView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        sabotage_records = SabotageRecord.objects.filter(course=course).order_by('-date')
        
        # 計算ロジック
        total_classes = course.total_time_block
        required_attendance_rate = course.need_percent / 100
        required_attendance_count = total_classes * required_attendance_rate
        current_absence_count = sabotage_records.count()
        max_absence_count = total_classes - required_attendance_count
        remaining_absence_count = max_absence_count - current_absence_count
        
        context = {
            'course': course,
            'sabotage_records': sabotage_records,
            'current_absence_count': current_absence_count,
            'max_absence_count': int(max_absence_count),
            'remaining_absence_count': int(remaining_absence_count),
            'total_classes': total_classes,
            'required_attendance_count': int(required_attendance_count),
        }
        return render(request, "sabotage_app/course_detail.html", context)

course_detail = CourseDetailView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseCreateView(View):
    def get(self, request):
        course_form = CourseForm()
        schedule_form = CourseScheduleForm()
        return render(request, 'sabotage_app/course_create.html', {
            'course_form': course_form,
            'schedule_form': schedule_form
        })
    
    def post(self, request):
        course_form = CourseForm(request.POST)
        
        if course_form.is_valid():
            weekly_classes = course_form.cleaned_data['weekly_classes']
            
            # 各スケジュールのデータを取得
            schedules_data = []
            valid_schedules = 0
            
            for i in range(weekly_classes):
                weekday = request.POST.get(f'weekday_{i}')
                period = request.POST.get(f'period_{i}')
                
                if weekday and period:
                    try:
                        period = int(period)
                        schedules_data.append({
                            'weekday': weekday,
                            'period': period
                        })
                        valid_schedules += 1
                    except ValueError:
                        pass
            
            # 有効なスケジュールが週のコマ数と一致するかチェック
            if valid_schedules == weekly_classes:
                # 授業を作成
                course = course_form.save(commit=False)
                course.user = request.user
                course.save()
                
                # スケジュールを作成
                for schedule_data in schedules_data:
                    CourseSchedule.objects.create(
                        course=course,
                        weekday=schedule_data['weekday'],
                        period=schedule_data['period']
                    )
                
                return redirect('index')
            else:
                messages.error(request, f'週のコマ数（{weekly_classes}）分のスケジュールを正しく入力してください。')
        
        schedule_form = CourseScheduleForm()
        return render(request, 'sabotage_app/course_create.html', {
            'course_form': course_form,
            'schedule_form': schedule_form
        })

course_create = CourseCreateView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseEditView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        form = CourseForm(instance=course)
        return render(request, 'sabotage_app/course_edit.html', {'form': form, 'course': course})
    
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_detail', course_id=course.id)
        return render(request, 'sabotage_app/course_edit.html', {'form': form, 'course': course})

course_edit = CourseEditView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseDeleteView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        course_name = course.name
        course.delete()
        return redirect('index')

course_delete = CourseDeleteView.as_view()