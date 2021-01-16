from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
import bcrypt, random
from .models import *
from django.db.models import Q
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.conf import settings 
from django.core.mail import send_mail

# Create your views here.

##PAGE RENDERS
def index(request):
    return render(request, "index.html")

def login_reg(request):
    return render(request, "logandreg.html")

def home(request):
    if 'user_id' not in request.session:
        return redirect("/")
    context ={
        'page_name': "Home",
        'recents': Image.objects.filter(name__startswith="recent"),
        'trending': Image.objects.filter(name__startswith="trending"),
        'all_cards': Image.objects.filter(name__startswith="all")
    }
    return render(request, "home.html", context)

def recent(request):
    user = get_user(request)
    cards = Image.objects.filter(Q(uploaded_by=None, name__startswith="recent") | Q(uploaded_by=user))
    context ={
        'page_name': "Recent",
        'cards': cards,
    }
    return render(request, 'base_card.html', context)

def trending(request):
    user = get_user(request)
    cards = Image.objects.filter(Q(uploaded_by=None, name__startswith="trending" )| Q(uploaded_by=user))
    context ={
        'page_name': "Trending",
        'cards': cards,
    }
    return render(request, 'base_card.html', context)
     
def a_z(request):
    user = get_user(request)
    cards = Image.objects.filter(Q(uploaded_by=None) | Q(uploaded_by=user))
    context ={
        'page_name': "A-Z",
        'cards': cards,
    }
    return render(request, 'base_card.html', context)

def my_cards(request):
    this_user = get_user(request)
    cards = Card.objects.filter(creator=this_user)
    context ={
        'page_name': "My Previous Cards",
        'cards': cards,
        'mycards': True,
    }
    return render(request, 'base_card.html', context)

def create(request):
    context={
        'songs': Audio.objects.all(),
    }
    return render(request, 'create.html', context)

def granted(request, item_id):
    wish_granted = Card.objects.get(id=item_id)
    wish_granted.granted =  True
    wish_granted.save()
    return redirect('/create')

def image_details(request, img_id):
    context={
        'card': Image.objects.get(id=img_id),
        'specific': True,
        'songs': Audio.objects.all(),
        
    }
    return render(request, 'create.html', context)

def search(request):
    if request.method=="POST":
        # get search text
        stext = request.POST['search']
        print(f"search text: {stext}")

        # add check for no text or only whitespace, if so, return to page
        user = get_user(request)
        # search the DB using filter
        cards = Image.objects.filter(Q(uploaded_by=None, name__icontains=stext )| Q(uploaded_by=user, name__icontains=stext))
        print(f"query set: {cards}")
        # print(f"1st image name: {qs[0].name}")

        # return the query set, for now
        # this_user = get_user(request)
        context ={
            'page_name': f" {stext} Cards",
            'cards': cards,
        }
        return render(request, 'base_card.html', context)

    # not a POST request,  send em back home
    return redirect('/')

def edit_card(request, card_id):
    card = Card.objects.get(id=card_id)
    context = {
        'edit': True,
        'card': card.images.first(),
        'this_card': card,
        'specific': True,
        'songs': Audio.objects.all(),
    }
    return render (request, 'create.html', context)

def update_card(request, card_id):
    if request.method == "POST":
        card = Card.objects.get(id=card_id)
        if request.FILES:
            image_id = upload_image(request)
            img = Image.objects.get(id=image_id)
            old_image = card.images.first()
            card.images.remove(old_image)
            card.images.add(img)
            print(f'image_id created was {image_id}')
        card.message = request.POST['greet_text']
        if 'song_id' in request.POST:
            print(f"song id is {request.POST['song_id']}")
            card.audio = Audio.objects.get(id=request.POST['song_id'])
        card.save()
        return redirect (f'/view_card/{card.id}')
    return redirect ('/')

def test(request):
    return render (request, 'test2.html')

def review(request, img_id):
    image_id = img_id
    this_user = get_user(request)
    if request.method == 'POST':
        if request.FILES:
            image_id = upload_image(request)
            print(f'image_id created was {image_id}')
        gText = request.POST['greet_text']
        # Create a Card
        cName = 'temp'
        cCreator = get_user(request)
        cMessage = gText
        cCard = Card.objects.create(name=cName, creator=cCreator, message=cMessage)
        print(f"card id: {cCard.id}")
        if 'song_id' in request.POST:
            print(f"song id is {request.POST['song_id']}")
            cCard.audio = Audio.objects.get(id=request.POST['song_id'])
        cCard.save()
        # add the Image to the Card
        cImage = Image.objects.get(id=image_id)
        cCard.images.add(cImage)
        context={
            'user': this_user,
            'visitor': False,
            'image': cCard.images.first(),
            'card': cCard,
            'comments': cCard.comments.all(),
        }
    return render(request, 'review.html', context)

def visitor_card(request, unique, card_id):
    this_card = Card.objects.filter(unique_id=unique, id=card_id)
    if len(this_card)==0:
        return HttpResponse("Invalid Link")
    this_card = this_card[0]
    cImage = this_card.images.first()
    this_card.viewed = True
    this_card.save()
    context ={
        'visitor': True,
        'image': cImage,
        'card': this_card,
        'comments': this_card.comments.all(),
    }
    return render (request, 'review.html', context)

def view_card(request, card_id):
    if confirm_session(request):
        this_user = get_user(request)
    cCard = Card.objects.get(id=card_id)        
    context={
        'user': this_user,
        'image': cCard.images.first() ,
        'card': cCard,
        'comments': cCard.comments.all(),
    }
    return render(request, 'review.html', context)


##CREATE DATA    
def register(request):
    if request.method=="POST":
        errors = User.objects.validate(request.POST)
        if errors:
            for error in errors:
                messages.error(request, errors[error])
            return redirect('/login_reg')

        # password encrypt
        user_pw = request.POST['pw']
        hash_pw = bcrypt.hashpw(user_pw.encode(), bcrypt.gensalt()).decode()

        # create the new user
        new_user = User.objects.create(first_name=request.POST['f_n'], last_name=request.POST['l_n'], email=request.POST['email'], password=hash_pw)
        print(f"first_name:{request.POST['f_n']}, last_name:{request.POST['l_n']}, email:{request.POST['email']}, password:{request.POST['pw']}, (hash: {hash_pw}).")

        # store user info in session
        request.session['user_id'] = new_user.id
        request.session['user_name'] = f"{new_user.first_name} {new_user.last_name}"

        return redirect('/home')

    # was not a post request, send user back to home page
    return redirect('/')

def upload_image(request):
    if request.method == 'POST':
        this_user = get_user(request)
        file = request.FILES
        media = file.get('media')
        this_media = Image()
        this_media.img = media
        this_media.name = media.name
        this_media.uploaded_by = this_user
        this_media.save()
    return this_media.id 

def upload_video(request):
    if request.method == 'POST':
        this_user = get_user(request)
        file = request.FILES
        media = file.get('video')
        this_media = Video()
        this_media.vid = media
        this_media.name = media.name
        this_media.uploaded_by = this_user
        this_media.save()
    return this_media.id 

def upload_audio(request):
    if request.method == 'POST':
        this_user = get_user(request)
        file = request.FILES
        media = file.get('audio')
        this_media = Audio()
        this_media.aud = media
        this_media.name = media.name
        this_media.uploaded_by = this_user
        this_media.save()
    return this_media.pk 
        
def send_email(request, card_id):
    if request.method == "POST":
        this_user = get_user(request)
        this_card = Card.objects.get(id=card_id)
        img = this_card.images.first()
        if this_card.receiver_email:
            new_card = this_card
            new_card.pk = None
            new_card.save()
            new_card.unique_id = random.randint(10000, 99999)
            new_card.images.add(img)
            new_card.save()
            this_card = new_card
        else:
            this_card.receiver_name = request.POST['name']
            this_card.receiver_email = request.POST['email']
        this_card.save()
        link=f"www.holidaygreetingscards.com/view_card/{this_card.unique_id}/{this_card.id}"
        subject = request.POST['subject']
        message = f"{request.POST['name']}, You have greeting card waiting for you from {this_user.first_name}. \n Click link to see card: {link}"
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [request.POST['email']]
        send_mail(subject, message, email_from, recipient_list ) 
        messages.success(request, "Your holiday greeting has been sent!")
        return redirect (f'/view_card/{this_card.id}')
    return redirect ('/')

# Create comments on view page
def create_comm(request):
    if request.method=='POST':
        this_card = Card.objects.get(id=request.POST['card_id'])
        this_comment = Comment.objects.create(content=request.POST['contents'], card=this_card)
        if logged_user(request):
            this_user = get_user(request)
            this_comment.poster = f'{this_user.first_name} {this_user.last_name}'
            this_comment.save()
            return redirect (f'/view_card/{this_card.id}')
        this_comment.poster = f'{this_card.receiver_name}'
        this_comment.save()
        return redirect(f'/view_card/{this_card.unique_id}/{this_card.id}')
    return redirect('/')

##ACTIONS
def login(request):
    if request.method == 'POST':
        # see if email is in the DB
        logged_user = User.objects.filter(email=request.POST['email'])
        if logged_user:
            logged_user = logged_user[0]    # strip the curlies 
            # compare the passwords
            if bcrypt.checkpw(request.POST['pw'].encode(), logged_user.password.encode()):
                request.session['user_id'] = logged_user.id
                request.session['user_name'] = f"{logged_user.first_name} {logged_user.last_name}"
                return redirect('/home')
            else:
                # bad password
                messages.error(request, "Incorrect password")
                return redirect('/login_reg')
        else: 
            # didn't find user in the database
            messages.error(request, "Email address is not registered")
            return redirect('/login_reg')

    # was not a post request, send user back to home page
    return redirect('/')


def logout(request):
    request.session.flush()
    return redirect('/')

def get_user(request):
    return User.objects.get(id=request.session['user_id'])

def confirm_session(request):
    if 'user_id' in request.session:
        return True
    return redirect('/')

def logged_user(request):
    if 'user_id' in request.session:
        return True
    return False
    # Add Likes to the view page

def add_like(request, card_id):
    this_card = Card.objects.get(id=card_id)
    this_card.likes += 1
    this_card.save()
    if logged_user(request):
        this_card.user_likes.add(get_user(request))
        return redirect(f'/view_card/{this_card.id}')
    return redirect(f'/view_card/{this_card.unique_id}/{this_card.id}')
