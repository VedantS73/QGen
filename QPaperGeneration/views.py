import random
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas

from QPaperGeneration.models import User, QPattern, Subject, Topic

 # Create your views here.

@login_required(login_url='login')
def index(request):
    return render(request, "index.html",{
        "subjects":Subject.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "login.html")

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def myquestions(request):
    if request.method == "POST":
        user = request.user
        subject = request.POST["subject"]
        topic = request.POST["topic"]
        marks = request.POST["marks"]
        difficulty = request.POST["difficulty"]
        question = request.POST["question"]
        answer = request.POST["answer"]

        cursub, subcr = Subject.objects.get_or_create(name=subject)
        curtop, topcr = Topic.objects.get_or_create(name=topic,sub=cursub)
        qamodel = QPattern.objects.create(user=user, topic=curtop, subject=cursub,question=question, answer=answer, marks=marks, difficulty=difficulty)
        qamodel.save()
        return HttpResponseRedirect(reverse("myquestions"))
    elif request.method == "GET":
        questionandanswers = QPattern.objects.all()
        qa = Paginator(questionandanswers, 10)
        page_obj = qa.get_page(1)
        return render(request, "myquestions.html",{
            "questions": page_obj,
        })
    else:
        HttpResponseRedirect("FORBIDDEN")

def papergen1(request):
    if request.method == "POST":
        checkboxstatus = False
        if request.POST.get('marksboxcheck',False) == 'on':
            checkboxstatus = True
        return render(request, "index2.html",{
            "heading": request.POST["heading"],
            "extradetails": request.POST["extradetails"],
            "marksboxcheck": checkboxstatus,
            # "diffslider": request.POST["diffslider"],
            "ptype": request.POST["ptype"],
            "subsel": request.POST["subsel"],
            "topics": Topic.objects.filter(sub=Subject.objects.get(pk=request.POST["subsel"]))
        })
    else:
        HttpResponseRedirect("FORBIDDEN")

def papergen2(request):
    title=request.POST["heading"]
    subTitle=request.POST["extradetails"]
    marksboxcheck = request.POST["marksboxcheck"]
    # diffslider = request.POST["diffslider"]
    # print(diffslider)
    # qLines = ["Name :","Roll No :", "Class :","Subject :","Obtained Marks: ","Total Marks:"]
    qLines = []
    topics = request.POST.getlist('topics')
    topics = [eval(i) for i in topics]
    print(topics)
    cos = request.POST.getlist('cos')
    cos = [eval(i) for i in cos]
    print(cos)
    twomqs = []
    sevmqs = []
    for topic in topics:
        tins = QPattern.objects.filter(marks=2).filter(topic=Topic.objects.filter(id=topic).first()).filter(co__in=cos)
        sins = QPattern.objects.filter(marks=7).filter(topic=Topic.objects.filter(id=topic).first()).filter(co__in=cos)
        for tin in tins:
            twomqs.append(tin.question)
        for sin in sins:
            sevmqs.append(sin.question)
    # random.choice(topics)
    i=1
    if request.POST["ptype"] == '1':
        qLines.append("Time : 1 Hour")
        qLines.append("Max Marks : 20")
        qLines.append("")
        qLines.append("")
        qLines.append("1. Attempt both the questions to get full marks.")
        qLines.append("2. Avoid using any unfair means during the paper.")
        qLines.append("")
        qLines.append("")
        qLines.append("Question 1 :  2marks × 3 = 6marks  (Attempt all 3)")
        qLines.append("")
        twolist = random.sample(twomqs,3)
        for tq in twolist:
                qLines.append(f"Q.{i} " + tq)
                i=i+1
        i=1
        qLines.append(" ")
        qLines.append("")
        qLines.append("Question 2 :  7marks × 2 = 14marks  (Attempt any 2)")
        qLines.append("")
        sevlist = random.sample(sevmqs,3)
        for tq in sevlist:
                qLines.append(f"Q.{i} " + tq)
                i=i+1
    elif request.POST["ptype"] == '2':
        qLines.append("Time : 1 Hour")
        qLines.append("Max Marks : 20")
        qLines.append("")
        qLines.append("")
        qLines.append("1. Question No 1 is compulsory")
        qLines.append("2. Answer any three from the remaining")
        qLines.append("2. Avoid using any unfair means during the paper.")
        qLines.append("")
        qLines.append("")
        qLines.append("Question 1 :  Answer any four from the following -- 20marks")
        twolist = random.sample(twomqs,5)
        for tq in twolist:
                qLines.append(f"Q.{i} " + tq)
                twomqs.remove(tq)
                i=i+1
        i=1
        qLines.append(" ")
        qLines.append("Question 2 :  Answer any two from the following -- 20marks")
        sevlist = random.sample(sevmqs,3)
        for tq in sevlist:
                qLines.append(f"Q.{i} " + tq)
                sevmqs.remove(tq)
                i=i+1
        i=1
        qLines.append(" ")
        qLines.append("Question 3 :  Answer any four from the following -- 20marks")
        sevlist = random.sample(twomqs,6)
        for tq in sevlist:
                qLines.append(f"Q.{i} " + tq)
                twomqs.remove(tq)
                i=i+1
        i=1
        qLines.append(" ")
        qLines.append("Question 4 :  Answer any two from the following -- 20marks")
        sevlist = random.sample(sevmqs,3)
        for tq in sevlist:
                qLines.append(f"Q.{i} " + tq)
                sevmqs.remove(tq)
                i=i+1
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Times-Roman", 24)
    p.setTitle(title)
    p.drawCentredString(300, 770, title)
    p.setFont("Times-Roman", 16)
    p.drawCentredString(290, 720, subTitle)
    p.line(30, 710, 550, 710)
    p.setFont("Times-Roman", 12)
    text = p.beginText(40, 680)
    for line in qLines:
        text.textLine(line)
    p.drawText(text)
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='PdfGenerated.pdf')
