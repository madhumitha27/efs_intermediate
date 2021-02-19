from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .utils import render_to_pdf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer


now = timezone.now()
def home(request):
   return render(request, 'portfolio/home.html',
                 {'portfolio': home})

class CustomerList(APIView):

    def get(self,request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)

class CustomerByNumber(APIView):

    def get(self, request, pk, format=None):
        try:
            person = Customer.objects.get(cust_number=pk)
            serializer = CustomerSerializer(person)
            return Response(serializer.data)
        except:
             return Response(status=status.HTTP_400_BAD_REQUEST)

@login_required
def customer_list(request):
    user = User.objects.get(pk=request.user.id)
   # if (user.groups.filter(name="customer").exists()):
      #  print('here')
      #  count = Customer.objects.filter(name_id=request.user.id).count()
      #  if (count == 0):
        #    nurse = Customer.objects.create(name_id=request.user.id, email=request.user.email)
        #cust = Customer.objects.get(pk=request.user.username)
        #return render(request, 'portfolio/accountprofile.html', {'customer': cust})

    #else:
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',
                 {'customers': customer})

def register(request):
    print("entered into register view method")
    if request.method == 'POST':
        print("entered into register view method entered if method")
        form = RegisterForm(request.POST)
        if form.is_valid():
            userObj =form.save()
            my_group = Group.objects.get(name=form.cleaned_data['group'])
            mygroupStr=str(my_group)
            if (mygroupStr == "advisor"):
                print("advisor...")
                userObj.is_staff=True
                userObj.is_superuser = True
            else:
                print("customer....")
            userObj.groups.add(my_group)
            userObj.save()
            return render(request,
                          'registration/registerdone.html',
                          {'form': form})
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})

def returnPDF(pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_of_initial_stock_value = 0
    sum_current_stocks_value = 0
    sum_of_initial_stock_value_INR = 0
    sum_current_stocks_value_INR = 0

    sum_current_investment_value = 0
    sum_of_initial_investment_value = 0
    sum_current_investment_value_INR = 0
    sum_of_initial_investment_value_INR = 0

    stock_result = 0
    stock_result_INR = 0
    investment_result=0
    investment_result_INR=0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        print('stock-',stock)
        ccValue=stock.current_stock_value()
        print('ccValue->',ccValue)
        sum_current_stocks_value += ccValue
        sum_of_initial_stock_value += stock.initial_stock_value()
    stock_result = sum_current_stocks_value - sum_of_initial_stock_value
    # COnverting Stocks to INR
    sum_of_initial_stock_value_INR = float(sum_current_stocks_value) * stock.currency_rate()
    sum_current_stocks_value_INR = float(sum_of_initial_stock_value) * stock.currency_rate()
    stock_result_INR = float(stock_result) * stock.currency_rate()

    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    investment_result = sum_current_investment_value - sum_of_initial_investment_value
    # COnverting Investments to INR
    sum_current_investment_value_INR = float(sum_current_investment_value) * stock.currency_rate()
    sum_of_initial_investment_value_INR = float(sum_of_initial_investment_value) * stock.currency_rate()
    investment_result_INR = float(investment_result) * stock.currency_rate()

    context = {'customers': customers, 'investments': investments, 'stocks': stocks,
               # 'sum_acquired_value': sum_acquired_value,
               # 'sum_recent_value': sum_recent_value, # 'overall_investment_results':overall_investment_results,
               'investment_result': investment_result,'investment_result_INR': investment_result_INR,
               'stock_result': stock_result,'stock_result_INR': stock_result_INR,
               'sum_current_investment_value': sum_current_investment_value,
               'sum_of_initial_investment_value': sum_of_initial_investment_value,
               'sum_current_investment_value_INR': sum_current_investment_value_INR,
               'sum_of_initial_investment_value_INR': sum_of_initial_investment_value_INR,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value,
               'sum_of_initial_stock_value_INR': sum_of_initial_stock_value_INR,
               'sum_current_stocks_value_INR': sum_current_stocks_value_INR
               }

    template = get_template('portfolio/DownloadPortfolio.html')
    print('Value-->', pk)
    pdf = render_to_pdf('portfolio/DownloadPortfolio.html', context)

    return pdf

def download_portfolio(request,pk):
       pdf= returnPDF(pk)
       response = HttpResponse(pdf, content_type='application/pdf')
       response['Content-Disposition'] = 'attachment; filename="report.pdf"'

       p = canvas.Canvas ( pdf )
       p.setFont ( "Times-Roman" , 55 )
       p.showPage ( )
       p.save ( )
       return response

def sendemailpdf(request,pk):
    customer = get_object_or_404(Customer, pk=pk)
    pdf = returnPDF(pk)
    cusEmail=customer.email
    sendEmail(pdf,cusEmail)

    return render(request, 'portfolio/emailsuccess.html')

def sendEmail(pdf,email):
     subject = "Application List "
     content = {}
     from_email = settings.EMAIL_HOST_USER
     message = EmailMultiAlternatives(subject=subject, body="Welcome.. Please find the attached portfolio pdf", from_email=from_email,
                                      to=[email], )
     #html_template = get_template("portfolio/DownloadPortfolio.html").render(context=content)
     #message.attach_alternative(html_template, "text/html")
     message.attach('Applications.pdf', pdf, 'application/pdf')
     message.send()

@login_required
def customer_edit(request, pk):
   customer = get_object_or_404(Customer, pk=pk)
   if request.method == "POST":
       # update
       form = CustomerForm(request.POST, instance=customer)
       if form.is_valid():
           customer = form.save(commit=False)
           customer.updated_date = timezone.now()
           customer.save()
           customer = Customer.objects.filter(created_date__lte=timezone.now())
           return render(request, 'portfolio/customer_list.html',
                         {'customers': customer})
   else:
        # edit
       form = CustomerForm(instance=customer)
   return render(request, 'portfolio/customer_edit.html', {'form': form})

@login_required
def customer_delete(request, pk):
   customer = get_object_or_404(Customer, pk=pk)
   customer.delete()
   return redirect('portfolio:customer_list')

@login_required
def stock_delete(request, pk):
   stock = get_object_or_404(Stock, pk=pk)
   stock.delete()
   return redirect('portfolio:stock_list')

@login_required
def investment_delete(request, pk):
   investment = get_object_or_404(Investment, pk=pk)
   investment.delete()
   return redirect('portfolio:investment_list')

@login_required
def stock_list(request):
   stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
   return render(request, 'portfolio/stock_list.html', {'stocks': stocks})

@login_required
def investment_list(request):
   investments = Investment.objects.filter(acquired_date__lte=timezone.now())
   return render(request, 'portfolio/investment_list.html', {'investments': investments})

@login_required
def stock_new(request):
   if request.method == "POST":
       form = StockForm(request.POST)
       if form.is_valid():
           stock = form.save(commit=False)
           stock.created_date = timezone.now()
           stock.save()
           stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
           return render(request, 'portfolio/stock_list.html',
                         {'stocks': stocks})
   else:
       form = StockForm()
       # print("Else")
   return render(request, 'portfolio/stock_new.html', {'form': form})

@login_required
def investment_new(request):
   if request.method == "POST":
       form = InvestmentForm(request.POST)
       if form.is_valid():
           investment = form.save(commit=False)
           investment.created_date = timezone.now()
           investment.save()
           investments = Investment.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/investment_list.html',
                         {'investments': investments})
   else:
       form = InvestmentForm()
       # print("Else")
   return render(request, 'portfolio/investment_new.html', {'form': form})

@login_required
def stock_edit(request, pk):
   stock = get_object_or_404(Stock, pk=pk)
   if request.method == "POST":
       form = StockForm(request.POST, instance=stock)
       if form.is_valid():
           stock = form.save()
           # stock.customer = stock.id
           stock.updated_date = timezone.now()
           stock.save()
           stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
           return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
   else:
       # print("else")
       form = StockForm(instance=stock)
   return render(request, 'portfolio/stock_edit.html', {'form': form})

@login_required
def investment_edit(request, pk):
   investment = get_object_or_404(Investment, pk=pk)
   if request.method == "POST":
       form = InvestmentForm(request.POST, instance=investment)
       if form.is_valid():
           investment = form.save()
           # stock.customer = stock.id
           investment.updated_date = timezone.now()
           investment.save()
           investments = Investment.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/investment_list.html', {'investments': investments})
   else:
       # print("else")
       form = InvestmentForm(instance=investment)
   return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def portfolio(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_of_initial_stock_value = 0
    sum_current_stocks_value = 0
    sum_of_initial_stock_value_INR = 0
    sum_current_stocks_value_INR = 0

    sum_current_investment_value = 0
    sum_of_initial_investment_value = 0
    sum_current_investment_value_INR = 0
    sum_of_initial_investment_value_INR = 0

    stock_result = 0
    stock_result_INR = 0
    investment_result = 0
    investment_result_INR = 0

    sum_portfolio_intial_investments=0
    sum_portfolio_intial_investments_INR = 0
    sum_portfolio_current_investments = 0
    sum_portfolio_current_investments_INR= 0
    grand_total_results=0
    grand_total_results_INR = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()
    stock_result = sum_current_stocks_value - sum_of_initial_stock_value
    # COnverting Stocks to INR
    sum_of_initial_stock_value_INR = float(sum_current_stocks_value) * stock.currency_rate()
    sum_current_stocks_value_INR = float(sum_of_initial_stock_value) * stock.currency_rate()
    stock_result_INR = float(stock_result) * stock.currency_rate()

    for investment in investments:
        sum_current_investment_value += investment.recent_value
        sum_of_initial_investment_value += investment.acquired_value

    investment_result = sum_current_investment_value - sum_of_initial_investment_value
    # COnverting Investments to INR
    sum_current_investment_value_INR = float(sum_current_investment_value) * stock.currency_rate()
    sum_of_initial_investment_value_INR = float(sum_of_initial_investment_value) * stock.currency_rate()
    investment_result_INR = float(investment_result) * stock.currency_rate()

    sum_portfolio_intial_investments = float(sum_of_initial_stock_value) + float(sum_of_initial_investment_value)
    sum_portfolio_intial_investments_INR = float(sum_portfolio_intial_investments) * stock.currency_rate()
    sum_portfolio_current_investments = float(sum_current_stocks_value) + float(sum_current_investment_value)
    sum_portfolio_current_investments_INR =float(sum_portfolio_current_investments) * stock.currency_rate()
    grand_total_results = float(stock_result) + float(investment_result)
    grand_total_results_INR = float(grand_total_results) * stock.currency_rate()

    return render(request, 'portfolio/portfolio.html', {'customers': customers, 'investments': investments, 'stocks': stocks,
               # 'sum_acquired_value': sum_acquired_value,
               # 'sum_recent_value': sum_recent_value, # 'overall_investment_results':overall_investment_results,
               'investment_result': investment_result, 'investment_result_INR': investment_result_INR,
               'stock_result': stock_result, 'stock_result_INR': stock_result_INR,
               'sum_current_investment_value': sum_current_investment_value,
               'sum_of_initial_investment_value': sum_of_initial_investment_value,
               'sum_current_investment_value_INR': sum_current_investment_value_INR,
               'sum_of_initial_investment_value_INR': sum_of_initial_investment_value_INR,
               'sum_current_stocks_value': sum_current_stocks_value,
               'sum_of_initial_stock_value': sum_of_initial_stock_value,
               'sum_of_initial_stock_value_INR': sum_of_initial_stock_value_INR,
               'sum_current_stocks_value_INR': sum_current_stocks_value_INR,
                                                        'sum_portfolio_intial_investments': sum_portfolio_intial_investments,
                                                        'sum_portfolio_intial_investments_INR': sum_portfolio_intial_investments_INR,
                                                        'sum_portfolio_current_investments': sum_portfolio_current_investments,
                                                        'sum_portfolio_current_investments_INR': sum_portfolio_current_investments_INR,
                                                        'grand_total_results': grand_total_results,
                                                        'grand_total_results_INR': grand_total_results_INR
                                                        })

