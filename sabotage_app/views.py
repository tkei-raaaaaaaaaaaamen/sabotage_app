from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from .models import Course, SabotageRecord
from .forms import CustomUserCreationForm, CourseForm, SabotageRecordForm
# Create your views here.

@method_decorator(login_required, name='dispatch')
class IndexView(View):
    def get(self, request):
        # ログインユーザーの授業のみを取得
        courses = Course.objects.filter(user=request.user).order_by('-created_at')
        
        # 各授業の残り休める日数を計算
        courses_with_stats = []
        for course in courses:
            sabotage_records = SabotageRecord.objects.filter(course=course)
            
            # 計算ロジック
            total_classes = course.total_time_block
            required_attendance_rate = course.need_percent / 100
            required_attendance_count = total_classes * required_attendance_rate
            current_absence_count = sabotage_records.count()
            max_absence_count = total_classes - required_attendance_count
            remaining_absence_count = max_absence_count - current_absence_count
            
            courses_with_stats.append({
                'course': course,
                'current_absence_count': current_absence_count,
                'max_absence_count': int(max_absence_count),
                'remaining_absence_count': int(remaining_absence_count),
                'recent_records': sabotage_records.order_by('-date')[:3]  # 最近の3件
            })
        
        context = {
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
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'ログインしました。')
                return redirect('index')
            else:
                messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
        else:
            messages.error(request, 'ユーザー名とパスワードを入力してください。')
        
        return render(request, 'sabotage_app/login.html')
login_view = LoginView.as_view()

class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'ログアウトしました。')
        return redirect('login')
logout_view = LogoutView.as_view()

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
            username = form.cleaned_data.get('username')
            messages.success(request, f'アカウント「{username}」が作成されました。')
            return redirect('login')
        return render(request, 'sabotage_app/signup.html', {'form': form})
signup_view = SignupView.as_view()

@method_decorator(login_required, name='dispatch')
class AddAbsenceView(View):
    def post(self, request):
        course_id = request.POST.get('course_id')
        date = request.POST.get('date')
        absence_type = request.POST.get('absence_type')
        note = request.POST.get('note', '')
        
        if course_id and date and absence_type:
            course = get_object_or_404(Course, id=course_id, user=request.user)
            
            # 同じ日の記録があるかチェック
            existing_record = SabotageRecord.objects.filter(
                course=course, 
                date=date
            ).first()
            
            if existing_record:
                messages.error(request, f'{course.name}の{date}は既に記録されています。')
            else:
                SabotageRecord.objects.create(
                    course=course,
                    date=date,
                    absence_type=absence_type,
                    note=note
                )
                messages.success(request, f'{course.name}の欠席記録を追加しました。')
        else:
            messages.error(request, '必須項目を全て入力してください。')
        
        # リファラーから来た場合は元のページに戻る
        next_page = request.POST.get('next', 'index')
        if next_page == 'course_detail':
            return redirect('course_detail', course_id=course_id)
        return redirect('index')
add_absence_view = AddAbsenceView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseDetailView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        sabotage_records = SabotageRecord.objects.filter(course=course).order_by('-date')
        
        # 残り欠席可能回数を計算
        total_classes = course.total_time_block
        required_attendance_rate = course.need_percent / 100
        required_attendance_count = total_classes * required_attendance_rate
        current_absence_count = sabotage_records.count()
        max_absence_count = total_classes - required_attendance_count
        remaining_absence_count = max_absence_count - current_absence_count
        
        context = {
            'course': course,
            'sabotage_records': sabotage_records,
            'total_classes': total_classes,
            'required_attendance_rate': course.need_percent,
            'required_attendance_count': int(required_attendance_count),
            'current_absence_count': current_absence_count,
            'max_absence_count': int(max_absence_count),
            'remaining_absence_count': int(remaining_absence_count),
        }
        return render(request, "sabotage_app/course_detail.html", context)
course_detail_view = CourseDetailView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseCreateView(View):
    def get(self, request):
        form = CourseForm()
        return render(request, 'sabotage_app/course_create.html', {'form': form})
    
    def post(self, request):
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            messages.success(request, f'授業「{course.name}」を作成しました。')
            return redirect('index')
        return render(request, 'sabotage_app/course_create.html', {'form': form})
course_create_view = CourseCreateView.as_view()

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
            messages.success(request, f'授業「{course.name}」を更新しました。')
            return redirect('course_detail', course_id=course.id)
        return render(request, 'sabotage_app/course_edit.html', {'form': form, 'course': course})
course_edit_view = CourseEditView.as_view()

@method_decorator(login_required, name='dispatch')
class CourseDeleteView(View):
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, user=request.user)
        course_name = course.name
        course.delete()
        messages.success(request, f'授業「{course_name}」を削除しました。')
        return redirect('index')
course_delete_view = CourseDeleteView.as_view()

@method_decorator(login_required, name='dispatch')
class SabotageRecordEditView(View):
    def get(self, request, record_id):
        record = get_object_or_404(SabotageRecord, id=record_id, course__user=request.user)
        form = SabotageRecordForm(instance=record)
        return render(request, 'sabotage_app/record_edit.html', {'form': form, 'record': record})
    
    def post(self, request, record_id):
        record = get_object_or_404(SabotageRecord, id=record_id, course__user=request.user)
        form = SabotageRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, '欠席記録を更新しました。')
            return redirect('course_detail', course_id=record.course.id)
        return render(request, 'sabotage_app/record_edit.html', {'form': form, 'record': record})
record_edit_view = SabotageRecordEditView.as_view()

@method_decorator(login_required, name='dispatch')
class SabotageRecordDeleteView(View):
    def post(self, request, record_id):
        record = get_object_or_404(SabotageRecord, id=record_id, course__user=request.user)
        course_id = record.course.id
        record.delete()
        messages.success(request, '欠席記録を削除しました。')
        return redirect('course_detail', course_id=course_id)
record_delete_view = SabotageRecordDeleteView.as_view()