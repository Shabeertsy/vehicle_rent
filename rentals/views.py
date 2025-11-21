from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Vehicle, Rental, Expense
from .forms import VehicleForm, RentalForm, ExpenseForm, UserCreateForm, UserEditForm
import pandas as pd
from datetime import datetime, date

def dashboard(request):
    # Overall Analytics
    total_income = Rental.objects.aggregate(Sum('total_amount_received'))['total_amount_received__sum'] or 0
    total_expense = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_income - total_expense
    active_vehicles_count = Vehicle.objects.count()

    # Monthly Data for Graph and Table
    # Group rentals by month
    rentals_by_month = Rental.objects.annotate(month=TruncMonth('date_out')).values('month').annotate(income=Sum('total_amount_received')).order_by('month')
    
    # Group expenses by month
    expenses_by_month = Expense.objects.annotate(month=TruncMonth('date')).values('month').annotate(expense=Sum('amount')).order_by('month')

    # Merge data
    monthly_data = {}
    
    for r in rentals_by_month:
        month = r['month'].strftime('%B %Y')
        if month not in monthly_data:
            monthly_data[month] = {'month': month, 'income': 0, 'expense': 0, 'profit': 0}
        monthly_data[month]['income'] += float(r['income'])

    for e in expenses_by_month:
        month = e['month'].strftime('%B %Y')
        if month not in monthly_data:
            monthly_data[month] = {'month': month, 'income': 0, 'expense': 0, 'profit': 0}
        monthly_data[month]['expense'] += float(e['expense'])

    # Calculate profit for each month
    final_monthly_data = []
    for month, data in monthly_data.items():
        data['profit'] = data['income'] - data['expense']
        final_monthly_data.append(data)
    
    # Sort by date (parsing the month string back to date for sorting)
    final_monthly_data.sort(key=lambda x: datetime.strptime(x['month'], '%B %Y'))

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'profit': profit,
        'active_vehicles_count': active_vehicles_count,
        'monthly_data': final_monthly_data,
    }
    return render(request, 'dashboard.html', context)

# Vehicle Views
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    rentals = vehicle.rentals.all().order_by('-date_out')
    expenses = vehicle.expenses.all().order_by('-date')
    
    total_revenue = rentals.aggregate(Sum('total_amount_received'))['total_amount_received__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_revenue - total_expense
    
    # Monthly breakdown for this vehicle (income, expense, profit per month) including all months
    # Rentals grouped by month
    rentals_by_month = rentals.annotate(month=TruncMonth('date_out')).values('month').annotate(income=Sum('total_amount_received')).order_by('month')
    # Expenses grouped by month
    expenses_by_month = expenses.annotate(month=TruncMonth('date')).values('month').annotate(expense=Sum('amount')).order_by('month')

    # Figure out the month range present in rentals/expenses
    min_month = None
    max_month = None

    for queryset in [rentals_by_month, expenses_by_month]:
        for d in queryset:
            if d['month']:
                if not min_month or d['month'] < min_month:
                    min_month = d['month']
                if not max_month or d['month'] > max_month:
                    max_month = d['month']

    if not min_month or not max_month:
        today = date.today().replace(day=1)
        min_month = max_month = today

    # Build a list of all months from min_month to max_month
    current = min_month.replace(day=1)
    months = []
    while current <= max_month:
        months.append(current)
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # Prepare lookups
    rental_map = {r['month']: float(r['income'] or 0) for r in rentals_by_month if r['month']}
    expense_map = {e['month']: float(e['expense'] or 0) for e in expenses_by_month if e['month']}

    monthly_data = []
    for month_dt in months:
        income = rental_map.get(month_dt, 0)
        expense = expense_map.get(month_dt, 0)
        profit_val = income - expense
        monthly_data.append({
            'month': month_dt,  # Pass the date object directly
            'income': income, 
            'expense': expense, 
            'profit': profit_val
        })

    # Pass months (as list of date objects) to the front end, so template can access all months explicitly.
    context = {
        'vehicle': vehicle,
        'rentals': rentals,
        'expenses': expenses,
        'total_revenue': total_revenue,
        'total_expense': total_expense,
        'profit': profit,
        'monthly_data': monthly_data,
        'all_months': months,   # <<<This is the additional context variable
    }
    return render(request, 'vehicle_detail.html', context)

def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle created successfully.')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'form.html', {'form': form, 'title': 'Add Vehicle'})

def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('vehicle_detail', pk=pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'form.html', {'form': form, 'title': 'Edit Vehicle'})

def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully.')
        return redirect('vehicle_list')
    return render(request, 'confirm_delete.html', {'object': vehicle})

# Rental Views
def rental_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.vehicle = vehicle
            rental.save()
            messages.success(request, 'Rental added successfully.')
            return redirect('vehicle_detail', pk=vehicle_id)
    else:
        form = RentalForm()
    return render(request, 'form.html', {'form': form, 'title': f'Add Rental for {vehicle.name}'})

def rental_edit(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rental updated successfully.')
            return redirect('vehicle_detail', pk=rental.vehicle.id)
    else:
        form = RentalForm(instance=rental)
    return render(request, 'form.html', {'form': form, 'title': 'Edit Rental'})

def rental_delete(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    vehicle_id = rental.vehicle.id
    if request.method == 'POST':
        rental.delete()
        messages.success(request, 'Rental deleted successfully.')
        return redirect('vehicle_detail', pk=vehicle_id)
    return render(request, 'confirm_delete.html', {'object': rental})

# Expense Views
def expense_create(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.vehicle = vehicle
            expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('vehicle_detail', pk=vehicle_id)
    else:
        form = ExpenseForm()
    return render(request, 'form.html', {'form': form, 'title': f'Add Expense for {vehicle.name}'})

def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('vehicle_detail', pk=expense.vehicle.id)
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'form.html', {'form': form, 'title': 'Edit Expense'})

def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    vehicle_id = expense.vehicle.id
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('vehicle_detail', pk=vehicle_id)
    return render(request, 'confirm_delete.html', {'object': expense})

# Excel Import
def import_data(request):
    vehicles = Vehicle.objects.all()
    import_errors = []
    selected_vehicle_id = None

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        vehicle_id = request.POST.get('vehicle_id')
        selected_vehicle_id = vehicle_id

        if not vehicle_id:
            messages.error(request, 'Please select a vehicle.')
            return render(request, 'import.html', {'vehicles': vehicles, 'import_errors': import_errors, 'selected_vehicle_id': selected_vehicle_id})

        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

        try:
            # Try to read the Excel file from the beginning each time
            # For seekability, use InMemoryUploadedFile, so read into BytesIO if needed
            from io import BytesIO
            excel_data = excel_file.read()
            # Reset pointer for every read_excel
            def get_excel_stream():
                return BytesIO(excel_data)

            header_row_index = 0
            found_header = False

            # Step 1: Find the header row
            df_temp = pd.read_excel(get_excel_stream(), header=None, nrows=20)
            for i, row in df_temp.iterrows():
                row_values = [str(val).strip().upper() for val in row.values]
                if 'DATE OUT' in row_values and 'CUSTOMER' in row_values:
                    header_row_index = i
                    found_header = True
                    break

            if not found_header:
                messages.warning(request, "Could not find 'DATE OUT' header row. Please check file format.")
                return render(request, 'import.html', {'vehicles': vehicles, 'import_errors': ['Header row not found (DATE OUT, CUSTOMER)'], 'selected_vehicle_id': selected_vehicle_id})

            # Step 2: Read the full file with the correct header
            df = pd.read_excel(get_excel_stream(), header=header_row_index)

            # Normalize column names
            df.columns = [str(col).strip().upper() for col in df.columns]

            rental_success_count = 0
            expense_success_count = 0

            for index, row in df.iterrows():
                # --- Process Rental ---
                try:
                    date_out_raw = row.get('DATE OUT')
                    customer_raw = row.get('CUSTOMER')

                    if pd.notna(date_out_raw) and pd.notna(customer_raw):
                        # Parse Date Out
                        date_out = None
                        try:
                            if isinstance(date_out_raw, str):
                                date_out = pd.to_datetime(date_out_raw, dayfirst=True, errors='coerce').date()
                            elif hasattr(date_out_raw, 'date'):
                                date_out = date_out_raw.date()
                            elif isinstance(date_out_raw, pd.Timestamp):
                                date_out = date_out_raw.date()
                        except Exception as e:
                            date_out = None

                        if date_out:
                            rental = Rental(
                                vehicle=vehicle,
                                date_out=date_out,
                                customer_name=str(customer_raw).strip(),
                                destination=row.get('DESTINATION'),
                                customer_id=row.get('CUSTOMER ID')
                            )
                            # Contact No (sometimes ; at end)
                            rental.contact_no = row.get('CONTACT NO;') or row.get('CONTACT NO')
                            rental.care_of = row.get('C/O')

                            # Time Out
                            time_out_raw = row.get('TIME OUT')
                            rental.time_out = None
                            if pd.notna(time_out_raw):
                                try:
                                    if hasattr(time_out_raw, 'time'):
                                        rental.time_out = time_out_raw
                                    elif isinstance(time_out_raw, str):
                                        parsed_time = pd.to_datetime(time_out_raw, errors='coerce')
                                        if not pd.isna(parsed_time):
                                            rental.time_out = parsed_time.time()
                                except: pass

                            # Date In
                            date_in_raw = row.get('DATE IN')
                            rental.date_in = None
                            if pd.notna(date_in_raw):
                                try:
                                    if hasattr(date_in_raw, 'date'):
                                        rental.date_in = date_in_raw.date()
                                    elif isinstance(date_in_raw, str):
                                        rental.date_in = pd.to_datetime(date_in_raw, dayfirst=True, errors='coerce').date()
                                except: pass

                            # Time In
                            time_in_raw = row.get('TIME IN')
                            rental.time_in = None
                            if pd.notna(time_in_raw):
                                try:
                                    if hasattr(time_in_raw, 'time'):
                                        rental.time_in = time_in_raw
                                    elif isinstance(time_in_raw, str):
                                        parsed_time = pd.to_datetime(time_in_raw, errors='coerce')
                                        if not pd.isna(parsed_time):
                                            rental.time_in = parsed_time.time()
                                except: pass

                            # Numeric fields
                            rental.days_of_rent = pd.to_numeric(row.get('DAYS OF RENT'), errors='coerce')
                            if pd.isna(rental.days_of_rent): rental.days_of_rent = 0
                            rental.rent_per_day = pd.to_numeric(row.get('RENT/DAY'), errors='coerce')
                            if pd.isna(rental.rent_per_day): rental.rent_per_day = 0
                            adv_amt = None
                            if 'ADV; AMOUNT' in df.columns:
                                adv_amt = row.get('ADV; AMOUNT')
                            if adv_amt is None and 'ADV AMOUNT' in df.columns:
                                adv_amt = row.get('ADV AMOUNT')
                            rental.advance_amount = pd.to_numeric(adv_amt, errors='coerce')
                            if pd.isna(rental.advance_amount): rental.advance_amount = 0

                            rental.starting_km = pd.to_numeric(row.get('STARTING KM'), errors='coerce')
                            if pd.isna(rental.starting_km): rental.starting_km = None
                            rental.ending_km = pd.to_numeric(row.get('ENDING KM'), errors='coerce')
                            if pd.isna(rental.ending_km): rental.ending_km = None
                            rental.total_amount_received = pd.to_numeric(row.get('TOTAL AMOUNT RECEIVED'), errors='coerce')
                            if pd.isna(rental.total_amount_received): rental.total_amount_received = 0

                            rental.save()
                            rental_success_count += 1

                except Exception as e:
                    import_errors.append(f"Rental Row {index+1}: {e}")

                # --- Process Expense ---
                try:
                    particulars = row.get('PARTICULARS')
                    amount = row.get('AMOUNT')

                    if pd.notna(particulars) and pd.notna(amount):
                        # Expense Date
                        date_val_raw = row.get('DATE')
                        expense_date = timezone.now().date()
                        if pd.notna(date_val_raw):
                            try:
                                if hasattr(date_val_raw, 'date'):
                                    expense_date = date_val_raw.date()
                                elif isinstance(date_val_raw, str):
                                    date_parsed = pd.to_datetime(date_val_raw, dayfirst=True, errors='coerce')
                                    if not pd.isna(date_parsed):
                                        expense_date = date_parsed.date()
                            except: pass

                        # Handle C/O for expense rows (C/O.1 or fallback if no CUSTOMER)
                        care_of_expense = None
                        if 'C/O.1' in df.columns:
                            care_of_expense = row.get('C/O.1')
                        if not care_of_expense and 'C/O' in df.columns and pd.isna(row.get('CUSTOMER')):
                            care_of_expense = row.get('C/O')

                        expense_amount = pd.to_numeric(amount, errors='coerce')
                        if pd.isna(expense_amount): expense_amount = 0

                        expense = Expense(
                            vehicle=vehicle,
                            date=expense_date,
                            particulars=particulars,
                            place=row.get('PLACE'),
                            care_of=care_of_expense,
                            amount=expense_amount
                        )
                        expense.save()
                        expense_success_count += 1

                except Exception as e:
                    import_errors.append(f"Expense Row {index+1}: {e}")

            msg = []
            if rental_success_count > 0:
                msg.append(f'{rental_success_count} rentals')
            if expense_success_count > 0:
                msg.append(f'{expense_success_count} expenses')
            if msg:
                messages.success(request, f"Successfully imported: {', '.join(msg)}.")
            else:
                if not found_header:
                    messages.warning(request, "Could not find 'DATE OUT' header row. Please check file format.")
                else:
                    messages.warning(request, 'No records were imported. Please check the file format and ensure data exists.')
            if import_errors:
                messages.error(request, f"Some rows were skipped due to errors. See details below.")
                return render(request, 'import.html', {'vehicles': vehicles, 'import_errors': import_errors, 'selected_vehicle_id': selected_vehicle_id})
        except Exception as e:
            import_errors.append(str(e))
            messages.error(request, f'Error importing file: {str(e)}')
            return render(request, 'import.html', {'vehicles': vehicles, 'import_errors': import_errors, 'selected_vehicle_id': selected_vehicle_id})

        return redirect('vehicle_detail', pk=vehicle_id)

    if request.method == 'GET':
        selected_vehicle_id = request.GET.get('vehicle_id')

    return render(request, 'import.html', {'vehicles': vehicles, 'import_errors': import_errors, 'selected_vehicle_id': selected_vehicle_id})


# User Management Views
def user_list(request):
    """Display list of all users"""
    users = User.objects.all().order_by('-date_joined')
    active_count = users.filter(is_active=True).count()
    inactive_count = users.filter(is_active=False).count()
    
    context = {
        'users': users,
        'active_count': active_count,
        'inactive_count': inactive_count,
    }
    return render(request, 'user_list.html', context)

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    # Get filter year, default to current year
    current_year = datetime.now().year
    selected_year = request.GET.get('year', current_year)
    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = current_year

    # Filter rentals and expenses by user and year
    rentals = Rental.objects.filter(user=user, date_out__year=selected_year).order_by('-date_out')
    expenses = Expense.objects.filter(user=user, date__year=selected_year).order_by('-date')

    # Calculate totals for the selected year
    total_income = rentals.aggregate(Sum('total_amount_received'))['total_amount_received__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    profit = total_income - total_expense

    # Monthly breakdown
    monthly_data = {}
    
    # Process rentals
    rentals_by_month = rentals.annotate(month=TruncMonth('date_out')).values('month').annotate(income=Sum('total_amount_received')).order_by('month')
    for r in rentals_by_month:
        month_name = r['month'].strftime('%B')
        if month_name not in monthly_data:
            monthly_data[month_name] = {'month': month_name, 'income': 0, 'expense': 0}
        monthly_data[month_name]['income'] = float(r['income'])

    # Process expenses
    expenses_by_month = expenses.annotate(month=TruncMonth('date')).values('month').annotate(expense=Sum('amount')).order_by('month')
    for e in expenses_by_month:
        month_name = e['month'].strftime('%B')
        if month_name not in monthly_data:
            monthly_data[month_name] = {'month': month_name, 'income': 0, 'expense': 0}
        monthly_data[month_name]['expense'] = float(e['expense'])

    # Calculate profit for each month and sort
    final_monthly_data = []
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    for month in months_order:
        if month in monthly_data:
            data = monthly_data[month]
            data['profit'] = data['income'] - data['expense']
            final_monthly_data.append(data)

    # Get available years for filter
    rental_years = Rental.objects.filter(user=user).dates('date_out', 'year')
    expense_years = Expense.objects.filter(user=user).dates('date', 'year')
    available_years = sorted(list(set([d.year for d in rental_years] + [d.year for d in expense_years] + [current_year])), reverse=True)

    context = {
        'user_obj': user,
        'rentals': rentals,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'profit': profit,
        'monthly_data': final_monthly_data,
        'selected_year': selected_year,
        'available_years': available_years,
    }
    return render(request, 'user_detail.html', context)

def user_create(request):
    """Create a new user"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'form.html', {'form': form, 'title': 'Add User'})

def user_edit(request, pk):
    """Edit an existing user"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('user_list')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'form.html', {'form': form, 'title': f'Edit User: {user.username}'})

def user_delete(request, pk):
    """Delete a user"""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('user_list')
    return render(request, 'confirm_delete.html', {'object': user, 'object_type': 'user'})
