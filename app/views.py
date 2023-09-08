
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import forms,models
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import datetime,timedelta,date
from django.core.mail import send_mail
from LMS.settings import EMAIL_HOST_USER
from .models import * 


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/index.html')

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/studentclick.html')

#for showing signup/login button for teacher
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')

def adminsignup_view(request):
    form=forms.AdminSigupForm()
    if request.method=='POST':
        form=forms.AdminSigupForm(request.POST)
        if form.is_valid():
            user=form.save()
            user.set_password(user.password)
            user.save()


            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)

            return HttpResponseRedirect('adminlogin')
    return render(request,'library/adminsignup.html',{'form':form})

def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')
    else:
        return render(request,'library/studentafterlogin.html')

def studentsignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            user2=f2.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)

def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    #now it is empty book form for sending to html
    form=forms.BookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.BookForm(request.POST)
        if form.is_valid():
            user=form.save()
            return render(request,'library/bookadded.html')
    return render(request,'library/addbook.html',{'form':form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books=Book.objects.all()
    return render(request,'library/viewbook.html',{'books':books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form=forms.IssuedBookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.IssuedBookForm(request.POST)
        if form.is_valid():
            obj=IssuedBook()
            obj.enrollment=request.POST.get('enrollment2')
            obj.name=request.POST.get('name2')
            name=request.POST.get('name2')
            obj1=Book.objects.get(name=name)
            obj1.available_copies = int(obj1.available_copies) - 1
            obj.save()
            obj1.save()
            return render(request,'library/bookissued.html')
    return render(request,'library/issuebook.html',{'form':form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students=StudentExtra.objects.all()
    return render(request,'library/viewstudent.html',{'students':students})

@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student=StudentExtra.objects.filter(user_id=request.user.id)
    issuedbook=IssuedBook.objects.filter(enrollment=student[0].enrollment)

    li1=[]

    li2=[]
    for ib in issuedbook:
        books=Book.objects.filter(name=ib.name)
        for book in books:
            t=(request.user,student[0].enrollment,student[0].branch,book.name,book.author)
            li1.append(t)
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        print(date.today())
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10
        t=(issdate,expdate,fine)
        li2.append(t)

    return render(request,'library/viewissuedbookbystudent.html',{'li1':li1,'li2':li2})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def returnissuedbookbystudent(request):
    form=forms.ReturnBookForm()
    if request.method=='POST':
        #now this form have data from html
        form=forms.ReturnBookForm(request.POST)
        if form.is_valid():
            e=request.POST.get('enrollment3')
            Name=request.POST.get('name3')
            obj = IssuedBook.objects.filter(name=Name).filter(enrollment=e)
            name=request.POST.get('name3')
            obj1=Book.objects.get(name=name)
            obj1.available_copies = int(obj1.available_copies) + 1
            obj.delete()
            obj1.save()
            return render(request,'library/bookreturned.html')
    return render(request,'library/returnissuedbookbystudent.html',{'form':form})