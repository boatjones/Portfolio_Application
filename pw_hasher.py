import streamlit_authenticator as stauth

# Input your new password
passwords = ['passord_to_hash']  # replace 'your_new_password' with the actual password

# Hash the password
hashed_passwords = stauth.Hasher(passwords).generate()

# Print the hashed password
print(hashed_passwords)

