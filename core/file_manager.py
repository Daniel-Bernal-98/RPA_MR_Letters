import os

def save_file(pdf_path, patient, date_of_service_, claim_number):
    try:
        output_dir = "./Processed_Claims" #Directory to save organized files
        patient_dir = os.path.join(output_dir, patient) #Create patient directory
        
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir) #Create directory if it doesn't exist

        new_file_name = f"{patient}_{date_of_service_}_{claim_number}.pdf" #Create new file name
        final_dir = os.path.join(patient_dir, new_file_name) #Create final directory for the file

        os.rename(pdf_path, final_dir) #Move and rename the file

        return f"File organized successfully: {new_file_name}" #Return success message
    
    except Exception as e:
        #return an error message if something goes wrong
        return f"Error processing file: {os.path.basename(pdf_path)} - {str(e)}"