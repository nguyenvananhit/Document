from pymongo import MongoClient

def get_mongo_client():
    """Kết nối đến MongoDB và trả về client."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        print("Kết nối đến MongoDB thành công!")
        return client
    except Exception as e:
        print(f"Lỗi khi kết nối đến MongoDB: {e}")
        raise

def get_database(data):
    """Lấy dữ liệu từ MongoDB."""
    client = get_mongo_client()  # Use the function to get the MongoDB client
    db = client['test_database']  # Replace with your database name
    collection = db['test_collection']  # Replace with your collection name
    data_cursor = collection.find()  # Fetch all documents
    data = list(data_cursor)  # Convert cursor to list
    return data


