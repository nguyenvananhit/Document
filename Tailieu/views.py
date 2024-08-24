from django.shortcuts import render, redirect
from pymongo import MongoClient
from .models import User
from django.contrib import messages
from pymongo import MongoClient
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def get_mongo_client():
    """Kết nối đến MongoDB và trả về client."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        print("Kết nối đến MongoDB thành công!")
        return client
    except Exception as e:
        print(f"Lỗi khi kết nối đến MongoDB: {e}")
        raise

def get_database(collection_name):
    """Lấy dữ liệu từ một collection cụ thể trong MongoDB."""
    client = get_mongo_client()
    db = client['QLTLDB']  # Replace with your actual database name
    collection = db[collection_name]  # Access the specified collection
    data_cursor = collection.find()  # Fetch all documents from the collection
    data = list(data_cursor)  # Convert cursor to list
    return data



   

def display_data(request):

    return render(request, 'Tailieu/list.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Connect to MongoDB and access the users collection
        client = get_mongo_client()
        db = client['QLTLDB']  # Replace with your actual database name
        users_collection = db['users']  # Access the 'users' collection

        # Check if the user exists and the password matches
        user = users_collection.find_one({"email": email, "password": password})

        if user:
            # User found, handle successful login
            request.session['user_id'] = str(user['id'])  # Store user ID in session
            request.session['user_email'] = user['email']  # Store user email in session
            return JsonResponse({'message': 'Login successful!', 'redirect': '/home/'})
        else:
            # User not found or password incorrect
            return JsonResponse({'message': 'Invalid email or password.'})

    # For GET requests or if login fails, render the login page with user data
    users_data = get_database('users')
    return render(request, 'Tailieu/login.html', {'data': users_data})
def document(request):
    data = get_database()
    return render(request, 'Tailieu/document.html')

def home(request):
   # Kiểm tra nếu không có thông tin email trong session, chuyển hướng đến trang đăng nhập
    if 'user_email' not in request.session:
        return redirect('login')  # Chuyển hướng đến trang đăng nhập

    user_email = request.session.get('user_email')

    # Fetch document statistics
    incoming_docs = get_database('incoming_documents')
    outgoing_docs = get_database('outgoing_documents')
    internal_docs = get_database('internal_documents')
    contracts = get_database('contracts')

    return render(request, 'Tailieu/home.html', {
        'user_email': user_email,
        'incoming_docs_count': len(incoming_docs),
        'outgoing_docs_count': len(outgoing_docs),
        'internal_docs_count': len(internal_docs),
        'contracts_count': len(contracts),
    })
def incoming_documents_view(request):
    incoming_docs = get_database('incoming_documents')
    return render(request, 'Tailieu/incoming_documents.html', {'documents': incoming_docs})

def outgoing_documents_view(request):
    outgoing_docs = get_database('outgoing_documents')
    return render(request, 'Tailieu/outgoing_documents.html', {'documents': outgoing_docs})

def internal_documents_view(request):
    internal_docs = get_database('internal_documents')
    return render(request, 'Tailieu/internal_documents.html', {'documents': internal_docs})

def contracts_view(request):
    contracts = get_database('contracts')
    return render(request, 'Tailieu/contracts.html', {'documents': contracts})

from django.core.files.storage import FileSystemStorage

def upload_document_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES['document']

        # Save the file
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_url = fs.url(filename)

        # Store document details in MongoDB
        client = get_mongo_client()
        db = client['QLTLDB']
        collection = db['incoming_documents']  # Update with your desired collection
        collection.insert_one({
            'title': title,
            'file_url': file_url,
            'date_received': datetime.now(),  # Update as needed
            'sender': request.session.get('user_email')  # Example field
        })

        return render(request, 'Tailieu/upload_document.html', {'success': True})

    return render(request, 'Tailieu/upload_document.html')


def search_documents_view(request):
    # Handle document search
    if request.method == 'GET':
        query = request.GET.get('query')
        # Perform search in MongoDB
        results = get_database('documents').find({'title': {'$regex': query, '$options': 'i'}})
        return render(request, 'Tailieu/search_documents.html', {'results': list(results)})
    return render(request, 'Tailieu/search_documents.html')

def view_documents_view(request):
    # View all documents
    documents = get_database('documents')
    return render(request, 'Tailieu/view_documents.html', {'documents': documents})

def logout(request):
    # Gọi phương thức logout của Django để đăng xuất và xoá session
    request.session.flush() 
    
    # Chuyển hướng người dùng đến trang đăng nhập hoặc trang chủ sau khi đăng xuất
    return redirect('login')  # Hoặc redirect('home') nếu bạn muốn chuyển hướng đến trang chính


from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def get_next_sequence(name):
    client = get_mongo_client()
    db = client['QLTLDB']
    counters = db['counters']
    counter = counters.find_one_and_update(
        {'_id': name},
        {'$inc': {'sequence_value': 1}},
        return_document=True,
        upsert=True
    )
    return counter['sequence_value']
def add_incoming_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date_received = request.POST.get('date_received')
        sender = request.POST.get('sender')
        file = request.FILES.get('file')

        if file:
            doc_id = get_next_sequence('incoming_documents')
            # Save the file
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            # Store document details in MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['QLTLDB']
            collection = db['incoming_documents']
            collection.insert_one({
                'id': doc_id,
                'title': title,
                'file_url': file_url,
                'date_received': date_received,
                'sender': sender
            })

            return render(request, 'Tailieu/add_incoming_document.html', {'success': True})

        else:
            return render(request, 'Tailieu/add_incoming_document.html', {'error': 'No file uploaded.'})

    return render(request, 'Tailieu/add_incoming_document.html')


def edit_incoming_document(request, id):
    client = get_mongo_client()
    db = client['QLTLDB']  # Replace with your actual database name
    incomming_collection = db['incoming_documents']  # Access the 'users' collection

    document = incomming_collection.find_one({'id': id})

    
    if request.method == 'POST':
        title = request.POST.get('title')
        date_received = request.POST.get('date_received')
        sender = request.POST.get('sender')
        file = request.FILES.get('file')
        if file:
            # Save the new file
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            # Update file URL in the document
            incomming_collection.update_one({'id': id}, {'$set': {'file_url': file_url}})
        else:
            file_url = document['file_url']  # Retain existing file URL if no new file is uploaded
        
        # Update document details
        incomming_collection.update_one({'id': id}, {
            '$set': {
                'title': title,
                'date_received': date_received,
                'sender': sender
            }
        })
        messages.success(request, 'Tài liệu đã được cập nhật.')
        return redirect('incoming_documents')

    return render(request, 'Tailieu/edit_incoming_document.html', {'document': document})
from django.http import Http404
def delete_incoming_document(request, id):
      # Kết nối đến collection
    client = get_mongo_client()
    db = client['QLTLDB']  # Replace with your actual database name
    incomming_collection =db['incoming_documents']

    # Tìm và xóa tài liệu dựa trên id
    result = incomming_collection.delete_one({'id': id})

    # Nếu không xóa được tài liệu (tài liệu không tồn tại), ném lỗi 404
    if result.deleted_count == 0:
        raise Http404("Tài liệu không tồn tại")

    # Thông báo thành công và chuyển hướng về trang danh sách tài liệu
    messages.success(request, 'Tài liệu đã được xóa thành công.')
    return redirect('incoming_documents')

from django.shortcuts import render
from pymongo import MongoClient
from datetime import datetime
import pytz
from datetime import datetime, timedelta
from django.shortcuts import render
from django.db.models import Q


from django.shortcuts import render
from pymongo import MongoClient
from datetime import datetime, timedelta

def search_incoming_documents(request):
    # Kết nối đến MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']  # Thay đổi tên cơ sở dữ liệu theo nhu cầu
    collection = db['incoming_documents']

    # Lấy các tham số từ yêu cầu
    query = request.GET.get('search', '')
    sender = request.GET.get('sender', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Xây dựng truy vấn
    filter_criteria = {}

    if query:
        filter_criteria['title'] = {'$regex': query, '$options': 'i'}
    
    if sender:
        filter_criteria['sender'] = {'$regex': sender, '$options': 'i'}

    

    # Thực hiện truy vấn
    documents = list(collection.find(filter_criteria))

    return render(request, 'Tailieu/incoming_documents.html', {
        'documents': documents,
        'query': query,
        'sender': sender,
        'start_date': start_date,
        'end_date': end_date
    })




# Out Document 
def add_outgoing_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date_sent = request.POST.get('date_sent')
        receiver = request.POST.get('receiver')
        file = request.FILES.get('file')

        if file:
            doc_id = get_next_sequence('outgoing_documents')
            # Save the file
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            # Store document details in MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['QLTLDB']
            collection = db['outgoing_documents']
            collection.insert_one({
                'id': doc_id,
                'title': title,
                'file_url': file_url,
                'date_sent': date_sent,
                'receiver': receiver
            })

            return render(request, 'Tailieu/add_outgoing_document.html', {'success': True})

        else:
            return render(request, 'Tailieu/add_outgoing_document.html', {'error': 'No file uploaded.'})

    return render(request, 'Tailieu/add_outgoing_document.html')

def edit_outgoing_document(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    outgoing_collection = db['outgoing_documents']

    document = outgoing_collection.find_one({'id': id})

    if request.method == 'POST':
        title = request.POST.get('title')
        date_sent = request.POST.get('date_sent')
        receiver = request.POST.get('receiver')
        file = request.FILES.get('file')

        if file:
            # Save the new file
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            # Update file URL in the document
            outgoing_collection.update_one({'id': id}, {'$set': {'file_url': file_url}})
        else:
            file_url = document['file_url']  # Retain existing file URL if no new file is uploaded

        # Update document details
        outgoing_collection.update_one({'id': id}, {
            '$set': {
                'title': title,
                'date_sent': date_sent,
                'receiver': receiver
            }
        })
        messages.success(request, 'Tài liệu đã được cập nhật.')
        return redirect('outgoing_documents')

    return render(request, 'Tailieu/edit_outgoing_document.html', {'document': document})

def delete_outgoing_document(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    outgoing_collection = db['outgoing_documents']

    # Tìm và xóa tài liệu dựa trên id
    result = outgoing_collection.delete_one({'id': id})

    # Nếu không xóa được tài liệu (tài liệu không tồn tại), ném lỗi 404
    if result.deleted_count == 0:
        raise Http404("Tài liệu không tồn tại")

    # Thông báo thành công và chuyển hướng về trang danh sách tài liệu
    messages.success(request, 'Tài liệu đã được xóa thành công.')
    return redirect('outgoing_documents')
def search_outgoing_documents(request):
    # Kết nối đến MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['outgoing_documents']

    # Lấy các tham số từ yêu cầu
    query = request.GET.get('search', '')
    receiver = request.GET.get('receiver', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # Xây dựng truy vấn
    filter_criteria = {}

    if query:
        filter_criteria['title'] = {'$regex': query, '$options': 'i'}
    
    if receiver:
        filter_criteria['receiver'] = {'$regex': receiver, '$options': 'i'}

    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            filter_criteria['date_sent'] = {'$gte': start_date_obj}
        except ValueError:
            filter_criteria['date_sent'] = {'$gte': datetime.min}

    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            if 'date_sent' in filter_criteria:
                filter_criteria['date_sent']['$lte'] = end_date_obj
            else:
                filter_criteria['date_sent'] = {'$lte': end_date_obj}
        except ValueError:
            filter_criteria['date_sent'] = {'$lte': datetime.max}

    # Thực hiện truy vấn
    documents = list(collection.find(filter_criteria))

    return render(request, 'Tailieu/outgoing_documents.html', {
        'documents': documents,
        'query': query,
        'receiver': receiver,
        'start_date': start_date,
        'end_date': end_date
    })

# list_internal_documents 

def list_internal_documents(request):
    # Kết nối đến MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['internal_documents']
    
    # Lấy tất cả tài liệu từ collection
    documents = list(collection.find())
    
    return render(request, 'Tailieu/internal_documents.html', {
        'documents': documents
    })


def add_internal_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date_received = request.POST.get('date_received')
        department = request.POST.get('department')
        status = request.POST.get('status')
        file = request.FILES.get('file')

        if file:
            doc_id = get_next_sequence('internal_documents')
            # Save the file
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)

            # Store document details in MongoDB
            client = MongoClient('mongodb://localhost:27017/')
            db = client['QLTLDB']
            collection = db['internal_documents']
            collection.insert_one({
                'id': doc_id,
                'title': title,
                'file_url': file_url,
                'date_received': date_received,
                'department': department,
                'status': status
            })

            messages.success(request, 'Tài liệu đã được thêm thành công.')
            return redirect('list_internal_documents')

        else:
            messages.error(request, 'Chưa tải lên file.')
            return render(request, 'Tailieu/add_internal_document.html')

    return render(request, 'Tailieu/add_internal_document.html')


def edit_internal_document(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['internal_documents']
    document = collection.find_one({'id': id})

    if request.method == 'POST':
        title = request.POST.get('title')
        date_received = request.POST.get('date_received')
        department = request.POST.get('department')
        status = request.POST.get('status')
        file = request.FILES.get('file')
        
        if file:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            collection.update_one({'id': id}, {'$set': {'file_url': file_url}})
        else:
            file_url = document['file_url']  # Retain existing file URL if no new file is uploaded
        
        collection.update_one({'id': id}, {
            '$set': {
                'title': title,
                'date_received': date_received,
                'department': department,
                'status': status
            }
        })
        messages.success(request, 'Tài liệu đã được cập nhật.')
        return redirect('list_internal_documents')

    return render(request, 'Tailieu/edit_internal_document.html', {'document': document})



def delete_internal_document(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['internal_documents']

    result = collection.delete_one({'id': id})

    if result.deleted_count == 0:
        raise Http404("Tài liệu không tồn tại")

    messages.success(request, 'Tài liệu đã được xóa thành công.')
    return redirect('list_internal_documents')


# User 


def list_users(request):
    # Kết nối đến MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['users']
    
    # Lấy tất cả người dùng từ collection
    users = list(collection.find())
    
    return render(request, 'Tailieu/users.html', {
        'users': users
    })
from django.contrib.auth.hashers import make_password

def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        status = request.POST.get('status')

        # Mã hóa mật khẩu
        hashed_password =password
        doc_id = get_next_sequence('internal_documents')
        # Store user details in MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['QLTLDB']
        collection = db['users']
        collection.insert_one({
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': role,
            'status': status,
            'id': doc_id
        })

        messages.success(request, 'Người dùng đã được thêm thành công.')
        return redirect('list_users')

    return render(request, 'Tailieu/add_user.html')
from django.shortcuts import render, redirect
from pymongo import MongoClient
from django.contrib import messages
from django.contrib.auth.hashers import make_password

def edit_user(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['users']
    user = collection.find_one({'id': id})

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        status = request.POST.get('status')

        # Mã hóa mật khẩu nếu được cung cấp
        if password:
            hashed_password = make_password(password)
        else:
            hashed_password = user['password']

        collection.update_one({'id': id}, {
            '$set': {
                'username': username,
                'email': email,
                'password': hashed_password,
                'role': role,
                'status': status
                
            }
        })
        messages.success(request, 'Người dùng đã được cập nhật.')
        return redirect('list_users')

    return render(request, 'Tailieu/edit_user.html', {'user': user})

from django.shortcuts import redirect
from pymongo import MongoClient
from django.http import Http404
from django.contrib import messages

def delete_user(request, id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['users']

    result = collection.delete_one({'id': id})

    if result.deleted_count == 0:
        raise Http404("Người dùng không tồn tại")

    messages.success(request, 'Người dùng đã được xóa thành công.')
    return redirect('list_users')


# Contracts 
# Lấy danh sách nhân viên
def get_users():
    client = get_mongo_client()
    db = client['QLTLDB']
    users_collection = db['users']
    return list(users_collection.find())

# list_internal_documents 

from pymongo import MongoClient
from django.shortcuts import render

def list_contracts(request):
    try:
        # Kết nối đến MongoDB
        client = get_mongo_client()
       
        db = client['QLTLDB']  # Thay đổi tên cơ sở dữ liệu nếu cần
        contracts_collection = db['contracts']  # Thay đổi tên collection nếu cần

        # Lấy danh sách hợp đồng
        contracts = list(contracts_collection.find())
        
        # In thông tin debug
        print(f"Retrieved contracts: {contracts}")

    except Exception as e:
        # In lỗi nếu có
        print(f"Error fetching contracts: {e}")
        contracts = []

    return render(request, 'Tailieu/contracts.html', {'contracts': contracts})

   

      
def add_contract(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        document_id = request.POST.get('document_id')  # Assume you have a way to get associated document
        responsible_user_id = request.POST.get('responsible_user_id')
        file = request.FILES.get('file')

        if file:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
        else:
            file_url = ''

        client = get_mongo_client()
        db = client['QLTLDB']
        contracts_collection = db['contracts']
        doc_id = get_next_sequence('internal_documents')
        contracts_collection.insert_one({
            'id': doc_id,
            'title': title,
            'start_date': start_date,
            'end_date': end_date,
            'document_id': document_id,
            'responsible_user_id': responsible_user_id,
            'file_url': file_url,
            
        })

        messages.success(request, 'Hợp đồng đã được thêm.')
        return redirect('list_contracts')

    users = get_users()
    return render(request, 'Tailieu/add_contract.html', {'users': users})

from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from pymongo import MongoClient
from django.http import HttpResponse
from django.contrib import messages
def edit_contract(request, id):
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['QLTLDB']
    collection = db['contracts']

    # Retrieve the contract by ID
    contract = collection.find_one({'id': id})

    if not contract:
        return HttpResponse("Contract not found")

    if request.method == 'POST':
        title = request.POST.get('title')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        document_id = request.POST.get('document_id')
        responsible_user_id = request.POST.get('responsible_user_id')
        file = request.FILES.get('file')

        # Handle file upload
        fs = FileSystemStorage()
        if file:
            filename = fs.save(file.name, file)
            file_url = fs.url(filename)
            # Update the contract with the new file URL
            collection.update_one({'id': id}, {'$set': {'file_url': file_url}})

        # Update the contract details
        collection.update_one({'id': id}, {
            '$set': {
                'title': title,
                'start_date': start_date,
                'end_date': end_date,
                'document_id': document_id,
                'responsible_user_id': responsible_user_id
            }
        })
        messages.success(request, 'Contract updated successfully.')
        return redirect('contracts')

    return render(request, 'Tailieu/edit_contract.html', {
        'contract': contract
    })
def delete_contract(request, id):
    client = get_mongo_client()
    db = client['QLTLDB']
    contracts_collection = db['contracts']

    result = contracts_collection.delete_one({'_id': id})

    if result.deleted_count == 0:
        raise Http404("Hợp đồng không tồn tại")

    messages.success(request, 'Hợp đồng đã được xóa thành công.')
    return redirect('list_contracts')


from django.http import HttpResponse

# Profile 
def profile(request):
    if 'user_id' in request.session:
        user_id = request.session.get('user_id')
        
        # Kết nối đến MongoDB
        client = get_mongo_client()
        db = client['QLTLDB']
        users_collection = db['users']
        
        user = users_collection.find_one({'_id': user_id})

        if user:
            # Truyền dữ liệu đến template
            return render(request, 'profile.html', {
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'status': user['status']
            })
        else:
            return HttpResponse("User not found")

    return redirect('login')

def about(request):
    return render(request, 'Tailieu/about.html')
