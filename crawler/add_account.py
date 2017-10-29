from pymongo import MongoClient

class AddAccount():
    def add_account(self,coll ,id , email, password):
        post = {'_id':id,'email':email,'password':password}
        coll.insert_one(post)

client = MongoClient("localhost")
db = client.email_account
coll = db.linkedin_account
acc = AddAccount()
email = ['ma.xiang@yandex.com']
password = 'industry123'
for i in range(len(email)):
    acc.add_account(coll,i+1,email[i],password)

