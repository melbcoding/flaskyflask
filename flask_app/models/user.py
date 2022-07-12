from flask_app.config.mysqlconnection import connectToMySQL
import re
EMAIL_REGEX =  re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash
from datetime import date

class User:
    db = "Poke_DB"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.alias = data['alias']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.poke_count = data['poke_count']
        self.total_count = 0
        self.poker_list = []

# create user
    @classmethod
    def save(cls, form_data):
        query = "INSERT INTO users (name,alias,email,password) VALUES(%(name)s,%(alias)s,%(email)s,%(password)s);"
        return connectToMySQL(cls.db).query_db(query, form_data)

# read by email
    @classmethod
    def get_email(cls, form_data):
        query = "SELECT users.*, SUM(pokes.poke_count) as poke_count FROM users LEFT JOIN pokes ON pokes.user_id = users.id WHERE users.email = %(email)s GROUP BY users.id;"
        results = connectToMySQL(cls.db).query_db(query, form_data)
        if len(results) < 1:
            return False
        return cls(results[0])

# read one user with total pokes count
    @classmethod
    def get_by_id(cls,form_data):
        print(form_data)
        query= "SELECT users.*, SUM(pokes.poke_count) as poke_count FROM users LEFT JOIN pokes ON pokes.user_id = users.id WHERE users.id = %(id)s GROUP BY users.id;"
        results = connectToMySQL(cls.db).query_db(query,form_data)
        one_user= cls(results[0])
        if results[0]['poke_count'] == None:
            one_user.poke_count=0
            return one_user
        return one_user

# read one complete user with pokers/pokes
    @classmethod
    def get_ONE_user_with_pokes(cls, data):
        query="SELECT users.id, users2.id, pokes.poke_count FROM users LEFT JOIN pokes on users.id = pokes.user_id LEFT JOIN users as users2 on pokes.poker_id = users2.id WHERE users.id = %(id)s ORDER BY pokes.poke_count DESC;"
        results= connectToMySQL(cls.db).query_db(query, data)
        user_id= {"id": results[0]['id']}
        one_user=cls.get_by_id(user_id)
        if len(results) <= 1:
            return one_user
        for row in results:
            poker_data= {
                "id" : row['users2.id'],
            }
            poker_info = cls.get_by_id(poker_data)
            poker_info.poke_count = row['poke_count']
            one_user.poker_list.append(poker_info)
        return one_user
    
    #read all pokers
    @classmethod
    def get_all_pokers(cls):
        query = "SELECT users.id from users;"
        results = connectToMySQL(cls.db).query_db(query)
        user_list= []
        for row in results:
            user_id= {"id" : row['id']}
            user_info= cls.get_by_id(user_id)
            user_list.append(user_info)
        return user_list
    # create poke
    @classmethod
    def start_pokin(cls, data):
        query="INSERT INTO pokes(user_id, poker_id, poke_count) VALUES(%(user_id)s, %(poker_id)s, 1);"
        return connectToMySQL(cls.db).query_db(query, data)

    # update poke
    @classmethod
    def add_poke(cls, data):
        query= "UPDATE pokes SET poke_count = poke_count + 1 WHERE pokes.user_id = %(user_id)s and pokes.poker_id= %(poker_id)s;"
        return connectToMySQL(cls.db).query_db(query, data)


    @staticmethod
    def check_pokes(data):
        is_valid= True
        query="SELECT * FROM pokes WHERE pokes.user_id = %(user_id)s and pokes.poker_id = %(poker_id)s;"
        results= connectToMySQL(User.db).query_db(query, data)
        if len(results) < 1:
            is_valid= False
            return is_valid
        return is_valid

    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(User.db).query_db(query,user)
        if len(results)>= 1:
            flash("Email already taken, please use another!")
            is_valid= False
        if not EMAIL_REGEX.match(user['email']):
            flash("invalid email!")
            is_valid= False
        if len(user['name']) < 3:
            flash("Name must be at least 3 characters","register")
            is_valid= False
        if len(user['alias']) < 3:
            flash("Last name must be at least 3 characters","register")
            is_valid= False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters","register")
            is_valid= False
        if user['password'] != user['confirm']:
            flash("Passwords don't match","register")
            is_valid = False
        if user['dob'] == '':
            flash("You must be 16 years or older to join", "register")
            is_valid= False
        if user['dob']:
            current_year = date.today().year
            dateOfBirth = user['dob']
            splitDate= dateOfBirth.split('-')
            print(splitDate)
            bdayYear= int(splitDate[0])
            age = current_year - bdayYear
            print(f'You are {age} years old.')
            if age < 16:
                flash('YOU are under the age of 16, YOU SHALL NOT PASS!', "register")
                is_valid= False
        return is_valid

    