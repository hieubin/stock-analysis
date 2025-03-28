import hashlib

def generate_id(item):
    # Combine the most unique characteristics of the item into a string
    unique_string = str(item['ticker']) + str(item['isin']) + str(item['figi'])
    
    # Generate a hash of the unique string
    hash_object = hashlib.md5(unique_string.encode())
    
    # Return the hash as the "_id"
    return hash_object.hexdigest()
