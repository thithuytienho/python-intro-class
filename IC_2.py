########################################
# Faker I.C.2 # Thi Thuy Tien Ho, 2026 #
#--------------------------------------#
# thithuytienho@usf.edu # (C)     2026 #
#--------------------------------------#
# Creates synthetic patient data       #
# using the Faker lib and random #s    #
#                                      #
# For research and educational use     #
# only, not for clinical decisions.    #
########################################

# Import libs
import json
import os
from faker import Faker
from anonymate.anonymizer import Anonymizer
from cryptography.fernet import Fernet

# Load or create a persistent encryption key
KEY_FILE ="encryption key"

if os.path.exists(KEY_FILE):
      with open(KEY_FILE, "rb") as f:
            encryption_key = f.read()
else:
      encryption_key = Fernet.generate_key()
      with open(KEY_FILE, "wb") as f:
            f.write(encryption_key)

# Initialize the Faker engine and Anonymizer engine
fake = Faker()
anonymizer = Anonymizer(encryption_key=encryption_key)

# Prompt user for data length
length = int(input("Enter the desired number of synthetic patient datasets you would like:"))

# Initialize Data Variable
data =[]

# Call faker_len function to generate names
for _ in range(length):
      data.append(fake.profile())

# Print data to terminal
print("Unencrypted Data:")
print(data)

# Turn data into a string
data_str = json.dumps (data, default=str)

# Run anonymizer
secure_data = anonymizer.encrypt_text(data_str)

# Show Encrypted data to User
print("Encrypted Data:")
print(secure_data)

# Create boolean question function for file write
def write_to_file_question(question:str) -> bool:
    while True:
          write_decision = input(f"{question} (y/n): ").strip().lower()
          if write_decision in ("y", "yes"):
                return True
          if write_decision in ("n", "no"):
                return False

          print("Invalid input. Please enter 'y' or 'n'.")

# Ask if they would like to write data to file
write_bool = write_to_file_question("Would you like to write this data to file?")

# Write Data if/else logic
if write_bool == True:
      custom_name = input("Enter the name for the file. (no special characters):")

      file_name = (f"{custom_name}.txt")

      with open (file_name, "w", encoding="utf-8") as file:
            file.write(secure_data)

      print(f"Saved to {file_name}")
else:
      print("Data not saved. All data will be lost when application is closed.")


