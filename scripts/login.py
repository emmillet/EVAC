from django.contrib.auth.models import User

# Create user and save to the database
user = User.objects.create_user('userid', 'firstname', 'lastname', 'dob', 'address', 'city', 'myemail@crazymail.com', 'phonenumber', 
'quarstipend', 'totalstipend','quarhours', 'totalhours','mypassword')
