# User Management System - Updated Documentation

## Overview
The user management system has been updated with simplified user types and partner assignment features.

## Key Changes

### 1. User Type Simplification
- **Removed**: Admin user type
- **Kept**: Partner user type only
- All users in the system are now Partners
- Simplified user creation and management

### 2. Partner Assignment to Rentals and Expenses
- **Rental Model**: Added `user` field (ForeignKey to User)
  - Tracks which partner is responsible for each rental
  - Optional field (can be null/blank)
  - Dropdown selection in rental form

- **Expense Model**: Added `user` field (ForeignKey to User)
  - Tracks which partner is responsible for each expense
  - Optional field (can be null/blank)
  - Dropdown selection in expense form

### 3. Month/Year Filters on Vehicle Details Page
- **Already Implemented**: Month and year filters are working
- **Features**:
  - Month buttons (Jan-Dec) for quick selection
  - Year dropdown (2020 to current+2 years)
  - Filters the monthly summary table dynamically
  - Default: Current month and year selected
  - Real-time filtering without page reload

## Database Changes

### Models Updated:
1. **UserProfile**
   - Simplified to only support 'partner' user type
   - Removed USER_TYPE_CHOICES
   - All users automatically get 'partner' type

2. **Rental**
   - Added: `user` field (ForeignKey to User, nullable)
   - Help text: "Partner responsible for this rental"

3. **Expense**
   - Added: `user` field (ForeignKey to User, nullable)
   - Help text: "Partner responsible for this expense"

### Migrations Applied:
- `0003_expense_user_rental_user_alter_userprofile_user_type.py`

## Forms Updated

### RentalForm
- Added `user` field as ModelChoiceField
- Shows all active users in dropdown
- Label: "Select Partner (Optional)"
- Appears first in the form

### ExpenseForm
- Added `user` field as ModelChoiceField
- Shows all active users in dropdown
- Label: "Select Partner (Optional)"
- Appears first in the form

### UserCreateForm & UserEditForm
- Removed `user_type` field
- All users are automatically set as partners
- Simplified user creation process

## UI Updates

### User List Page
- **Stats Cards**: Now shows:
  1. Total Partners
  2. Active Partners
  3. Inactive Partners
- **Role Column**: Shows "Partner" badge for all users
- **Removed**: Admin/Partner distinction
- **Kept**: All modern styling and responsive design

### Forms
- **Partner Dropdown**: Added to rental and expense forms
- **Modern Design**: Maintained professional styling
- **Responsive**: Works on all screen sizes

## Vehicle Details Page Filters

### Month Filter
- 12 month buttons (Jan-Dec)
- Click to select month
- Active month highlighted
- Default: Current month

### Year Filter
- Dropdown with years from 2020 to current+2
- Default: Current year
- Changes filter dynamically

### Monthly Summary Table
- Filtered by selected month and year
- Shows: Month, Revenue, Expenses, Profit
- Empty state when no data for selected period
- Smooth filtering without page reload

## Usage

### Adding a Rental with Partner Assignment
1. Go to Vehicle Details page
2. Click "Add Rental"
3. Select partner from dropdown (optional)
4. Fill in rental details
5. Save

### Adding an Expense with Partner Assignment
1. Go to Vehicle Details page
2. Click "Add Expense"
3. Select partner from dropdown (optional)
4. Fill in expense details
5. Save

### Filtering Vehicle Data by Month/Year
1. Go to Vehicle Details page
2. Click desired month button
3. Select year from dropdown
4. View filtered monthly summary

### Creating a New Partner
1. Go to Users page
2. Click "Add New User"
3. Fill in details (username, email, name, password)
4. User is automatically created as Partner
5. No need to select user type

## Technical Notes

- All users have `is_staff=False` and `is_superuser=False`
- Partner assignment is optional on rentals and expenses
- Existing rentals/expenses without assigned partners will show as unassigned
- Month/year filters use JavaScript for instant filtering
- No page reload required for filtering

## Benefits

1. **Simplified User Management**: No confusion between admin/partner
2. **Better Tracking**: Know which partner handled each rental/expense
3. **Flexible Filtering**: Quick access to specific month/year data
4. **Optional Assignment**: Partners can be assigned or left blank
5. **Clean UI**: Modern, professional interface maintained
