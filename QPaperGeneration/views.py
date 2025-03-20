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
            "questions": questionandanswers,
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
    title = request.POST["heading"]
    subTitle = request.POST["extradetails"]
    marksboxcheck = request.POST["marksboxcheck"]
    topics = request.POST.getlist('topics')
    topics = [eval(i) for i in topics]
    cos = request.POST.getlist('cos')
    cos = [eval(i) for i in cos]

    twomqs = []
    sevmqs = []
    tens = []
    for topic in topics:
        tins = QPattern.objects.filter(marks=2).filter(topic=Topic.objects.filter(id=topic).first())
        sins = QPattern.objects.filter(marks=5).filter(topic=Topic.objects.filter(id=topic).first())
        tensa = QPattern.objects.filter(marks=10).filter(topic=Topic.objects.filter(id=topic).first())
        for tin in tins:
            twomqs.append(tin.question)
        for sin in sins:
            sevmqs.append(sin.question)
        for ten in tensa:
            tens.append(ten.question)

    # Prepare the questions based on the new format
    qLines = []
    i = 1
    
    print("number of 2 marks questions: ", len(twomqs))
    print("number of 5 marks questions: ", len(sevmqs))
    print("number of 10 marks questions: ", len(tens))

    if request.POST["ptype"] == '1':
        # IA Paper - Q1: Any five questions (2 marks each), Q2: Any one question (5 marks), Q3: Any one question (5 marks)
        qLines.append("Time : 1 Hour")
        qLines.append("Max Marks : 20")
        qLines.append("")
        qLines.append("1. Attempt the following questions:")
        qLines.append("2. Avoid using any unfair means during the paper.")
        qLines.append("")

        # Q1: Any five questions from 6 (2 marks each)
        qLines.append("Question 1 : Any five questions - 2 marks each")
        qLines.append(f"(Choose 5 from the following 6 questions)")
        twolist = random.sample(twomqs, 6)
        for tq in twolist:
            qLines.append(f"Q.{i} " + tq)
            i += 1

        qLines.append("")  # Add spacing

        # Q2: Any one question from 2 (5 marks)
        sevlist = random.sample(sevmqs, 4)
        qLines.append("Question 2 : Any one question - 5 marks")
        qLines.append(f"(Choose 1 from the following 2 questions)")
        
        qLines.append(f"Q.{i} " + sevlist[0])
        qLines.append(f"Q.{i} " + sevlist[1])
        i += 1

        qLines.append("")  # Add spacing

        # Q3: Any one question from 2 (5 marks)
        qLines.append("Question 3 : Any one question - 5 marks")
        qLines.append(f"(Choose 1 from the following {len(sevmqs)} questions)")
        qLines.append(f"Q.{i} " + sevlist[2])
        qLines.append(f"Q.{i} " + sevlist[3])
        i += 1
    
    if request.POST["ptype"] == '2':  # Assuming 'ptype == 2' is for Semester papers
        qLines.append("Time : 3 Hours")
        qLines.append("Max Marks : 100")
        qLines.append("")
        qLines.append("1. Answer all questions.")
        qLines.append("2. All questions carry equal marks.")
        qLines.append("3. Attempt any 3 questions from Q2 to Q6.")
        qLines.append("4. Avoid using any unfair means during the paper.")
        qLines.append("")

        # Q1: Compulsory question (5 marks each)
        qLines.append("Question 1 : Compulsory questions - 5 marks each")
        comp_qs = random.sample(sevmqs, 4)  # Select 4 compulsory questions (5 marks each)
        for tq in comp_qs:
            qLines.append(f"Q.{i} " + tq)
            i += 1

        qLines.append("")  # Add spacing

        # Q2-Q6: Each worth 20 marks (2 sub-questions for 10 marks each)
        main_qs = random.sample(tens, 10)
        qLines.append("Question 2 : Answer both sub-questions (10 marks each) - Total 20 marks")
        qLines.append(f"Q.{i} " + main_qs[0])  # Sub-question 1
        qLines.append(f"Q.{i+1} " + main_qs[1])  # Sub-question 2
        i += 2

        qLines.append("")

        qLines.append("Question 3 : Answer both sub-questions (10 marks each) - Total 20 marks")
        qLines.append(f"Q.{i} " + main_qs[2])  # Sub-question 1
        qLines.append(f"Q.{i+1} " + main_qs[3])  # Sub-question 2
        i += 2

        qLines.append("")

        qLines.append("Question 4 : Answer both sub-questions (10 marks each) - Total 20 marks")
        qLines.append(f"Q.{i} " + main_qs[4])  # Sub-question 1
        qLines.append(f"Q.{i+1} " + main_qs[5])  # Sub-question 2
        i += 2

        qLines.append("")

        qLines.append("Question 5 : Answer both sub-questions (10 marks each) - Total 20 marks")
        qLines.append(f"Q.{i} " + main_qs[6])  # Sub-question 1
        qLines.append(f"Q.{i+1} " + main_qs[7])  # Sub-question 2
        i += 2

        qLines.append("")

        qLines.append("Question 6 : Answer both sub-questions (10 marks each) - Total 20 marks")
        qLines.append(f"Q.{i} " + main_qs[8])  # Sub-question 1
        qLines.append(f"Q.{i+1} " + main_qs[9])  # Sub-question 2
        i += 2

        qLines.append("")

    # Generate PDF
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