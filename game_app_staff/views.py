from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Staff,Game
from  game_app_user.models import CustomUser,Purchase
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


# Create your views here.

def staff_home(request):
    return render(request,'staff_home.html')

def staff_register(request):
    if request.method == "POST":
        username=request.POST.get("username")
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        email=request.POST.get("email")
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")


        if CustomUser.objects.filter(email=email).exists():
            messages.error(request,"Email Already Taken !!")
            return redirect("staff_register")
        if len(password)<5:
            messages.error(request,"Password Contain More than 5 charachter !!")
            return redirect("staff_register")
        if confirm_password!=password:
            messages.error(request,"Confirm password Didnt match !!")
            return redirect("staff_register")
        
        user=CustomUser.objects.create_user(username=username,email=email,first_name=first_name,last_name=last_name,password=password)
        user.save()

        Staff.objects.create(user=user)

        messages.success(request,f"{ user.username } register successfully ")
        return redirect("staff_login")
    return render(request,"staff_register.html")

def staff_login(request):
    if request.method == "POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        try:
            user_obj = CustomUser.objects.get(email=email)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            messages.error(request, "Not a register Staff !!")
            return redirect("staff_register")

        # Authenticate using username
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # Ensure the user has a staff profile
            if hasattr(user, 'staff_profile') and user.staff_profile.is_staff_member:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect("staff_home")
            else:
                messages.error(request, "You do not have staff access.")
                return redirect("staff_login")
        else:
            messages.error(request, "Invalid email or password!")
            return redirect("staff_login")
    return render(request,"staff_login.html")

def staff_logout(request):
    logout(request)
    return redirect('index')


@login_required
def staff_profile(request):
    if request.method == "POST":
        user=request.user
        if "staff_profile" in request.POST:
            user.username=request.POST.get('username',user.username)
            user.first_name=request.POST.get('first_name',user.first_name)
            user.last_name=request.POST.get('last_name',user.last_name)
            user.email=request.POST.get('email',user.email)
            user.save()
            
            messages.success(request, "Profile updated successfully!")
        elif "staff_password" in request.POST:
            current_password=request.POST.get("current_password")
            new_password=request.POST.get("new_password")
            confirm_pass=request.POST.get("confirm_pass")

            if  not user.check_password(current_password):
                messages.error(request, "Current password is incorrect!")
            elif confirm_pass!=new_password:
                messages.error(request, "New passwords do not match!")
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request,user)
                messages.success(request, "Password changed successfully!")

        return redirect('staff_profile') 
    
    return render(request, 'staff_profile.html')

@login_required
def staff_game_list(request):
    games=Game.objects.all().order_by('-created_at')
    return render(request,'staff_game_list.html',{'games':games})

@login_required
def add_game(request):
    if request.method == "POST":
        name=request.POST.get("name")
        category=request.POST.get('category')
        price=request.POST.get('price') if category == 'Premium' else 0
        description=request.POST.get("description")
        file=request.POST.get('file')
        image=request.FILES.get('image')

        Game.objects.create(name=name,category=category,image=image,file=file,price=price,description=description)
        return redirect('game_list')

    return render(request, 'add_game.html')

@login_required
def edit_game(request,game_id):
    games=get_object_or_404(Game,id=game_id)
    if request.method == "POST":
        games.name=request.POST.get('name')
        games.price=request.POST.get("price")
        if 'image' in request.FILES:
            games.image = request.FILES.get('image')

        # Handle File Upload or URL
        if 'file' in request.POST:
            games.file = request.POST.get('file')
        games.description=request.POST.get('description')
        games.category=request.POST.get('category')
        games.save()
        messages.success(request,"Edited Successfully")
        return redirect('game_list')
    return render(request,'edit_game.html',{'games':games})


@login_required
def staff_dashboard(request):
    games = Game.objects.all()
    purchases = Purchase.objects.filter(payment_status='Pending') 
    return render(request,'staff_dashboard.html', {'games': games, 'purchases': purchases})

@login_required
def manage_purchase(request):
    purchases=Purchase.objects.filter(payment_status='Pending')
    return render(request, 'manage_purchase.html', {'purchases': purchases})

@login_required
def approve_purchase(request,purchase_id):
    purchases=Purchase.objects.get(id=purchase_id)
    purchases.payment_status="Approved"
    purchases.save()
    messages.success(request, f"Purchase approved for { purchases.user.username }.")
    return redirect('manage_purchase')

@login_required
def reject_purchase(request,purchase_id):
    purchases=Purchase.objects.get(id=purchase_id)
    purchases.payment_status = "Rejected"
    purchases.save()
    messages.warning(request, f"Purchase rejected for { purchases.user.username }.")
    return redirect('manage_purchase')