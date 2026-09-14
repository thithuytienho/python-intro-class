#Blood Pressure Screening
#Classify each patients BP and count the number of patients in each category (Normal, Elevated, High Blood Pressure)
    #Normal: Systolic below 120 AND Diastolic below 80
    #Elevated: Systolic 120-129 AND Diastolic below 80
    #High Blood Pressure: Systolic 130 or above OR Diastolic 80 or above
# 1. Print each patients name and BP classification.
# 2. Print the total number of patients in each category
names = ["Alice","Bob","Charlie", "David", "Eva", "Fern"]
systolic = [118, 125, 135,140, 128, 115]
Diastolic = [75, 78, 85, 90, 79, 70]

normal_count = 0
elevated_count = 0
high_BP_count = 0

#Classify each patient and count them
for i in range(len(names)):
    # Classify based on systolic and diastolic readings
    if systolic[i] <120 and Diastolic[i] < 80:
        classification = "Normal"
        normal_count = normal_count + 1
    elif 120 <= systolic[i] <= 129 and Diastolic[i] < 80:
        classification = "elevated"
        elevated_count = elevated_count + 1
    else:
        classification = "High Blood Pressure"
        high_BP_count = high_BP_count + 1
    print(f"{names[i]}: {classification}")

#Print results
print(f"/nTotal number of patients in each category:")
print(f"Normal: {normal_count}")
print(f"Elevated: {elevated_count}")
print(f"High Blood Pressure: {high_BP_count}")
