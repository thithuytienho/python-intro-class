########################################
# Faker LAB.3 # Thi Thuy Tien Ho, 2026 #
#--------------------------------------#
# thihthuytienho@usf.edu # (C) 2026    #
########################################

# Import libs
import json
from anonymate.anonymizer import Anonymizer
from cryptography.fernet import Fernet

#Create encryption key
encryption_key = Fernet.generate_key()

# Initialize the Anonymizer engine
anonymizer = Anonymizer(encryption_key =encryption_key)

# For five patient profiles
profiles = [
    {
        "name": "Oscar Newman",
        "sex": "M",
        "blood_group": "B+",
        "Birthdate": "1927-01-19",
    },
    {
        "name": "Jeremy Wilson",
        "sex": "M",
        "blood_group": "A-",
        "Birthdate": "1996-10-12",

    },
    {
        "name": "Kenneth Rhodes",
        "sex": "M",
        "blood_group": "A-",
        "Birthdate": "2003-06-15",
    },
    {
        "name": "Nicole Richardson",
        "sex": "F",
        "blood_group": "AB+",
        "Birthdate": "2003-09-07",
    },
    {
        "name": "Gary Gamble",
        "sex": "M",
        "blood_group":"A+",
        "Birthdate": "1968-08-19",
    }
]

# Ask user to select a profile
profile_number = int(input("Enter profile number (1-5): "))
profile = profiles[profile_number - 1]

# Ask the user which profile specific they want
choice = input("Enter profile specific (name, DoB, sex, blood_group):").strip().lower()

#Get the requested information
if choice == "name":
    print(f"Name: {profile['name']}")
elif choice == "dob":
    print(f"DoB: {profile['Birthdate']}")
elif choice =="sex":
    print(f"Sex: {profile['sex']}")
elif choice =="blood_group":
    print(f"Blood Group: {profile['blood_group']}")
else:
    print( "Invalid choice")

# Ask user if they want to encrypt the data
encrypt_choice = input ("Would you like to encrypt the data? (y/n):"). strip().lower()

if encrypt_choice == "y" or encrypt_choice == "yes":

    # Turn profile into a string
    data_str = json.dumps(profile, default=str)

    #Run anonymizer
    secure_data = anonymizer.encrypt_text(data_str)

    #Show encrypted data to User
    print("Encrypted data:")
    print(secure_data)
else:
    print("Unencrypted data.")
