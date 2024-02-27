from django.shortcuts import render,redirect
from .forms import TrainingForm
import jsonlines
import os
import time
import csv
from openai import OpenAI
from django.conf import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def create_fine_tuning_file(file_path):
    print("Processing fine tuning file " + file_path)
    file = client.File.create(
        file=open(file_path, "rb"),
        purpose='fine-tune'
    )

    # Get the file ID
    file_id = file['id']

    # Check the file's status
    status = file['status']

    while status != 'processed':
        print(f"File status: {status}. Waiting for the file to be processed...")
        time.sleep(10)  # Wait for 10 seconds
        file_response = client.File.retrieve(file_id)
        status = file_response['status']
        print(file_response)
    fine_tuning_response = client.FineTuningJob.create(training_file=file_id, model="gpt-3.5-turbo")
    print(fine_tuning_response)
    return fine_tuning_response

def fine_tune_model(fine_tuning_file):
    print("Starting fine tuning job with ID: " + fine_tuning_file['id'])
    if fine_tuning_file['status'] == 'processed':
        fine_tuning_response = client.FineTuningJob.create(
            training_file=fine_tuning_file['id'],
            model="gpt-3.5-turbo"
        )
        print(fine_tuning_response['id'])

def load_csv_finetuning(csv_file, output_path):
    # Open the CSV file for reading
    with open(csv_file, 'r', newline='') as csv_file_object:
        csv_reader = csv.reader(csv_file_object)

        # Open the JSONL file for writing
        with jsonlines.open(output_path, mode='w') as jsonl_file:
            for row in csv_reader:
                system = row[0]
                values = [{"role": "system", "content": system}]
                odd = True
                for value in row[1:]:
                    if odd:
                        if len(value) > 0:
                            values.append({"role": "user", "content": value})
                        odd = False
                    else:
                        if len(value) > 0:
                            values.append({"role": "assistant", "content": value})
                        odd = True
                json_data = {"messages":values}
                jsonl_file.write(json_data)


def admin_interface(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            uploaded_file = request.FILES['file']
            # Get the file name

            file_name = uploaded_file.name
            file_name= file_name.split(".")[0].replace(" ","_")+"."+file_name.split(".")[1]
            path=os.path.join(settings.TRAIN_FOLDER,file_name)
            opath=os.path.join(settings.TRAIN_FOLDER,file_name.split(".")[0]+".jsonl")
            load_csv_finetuning(path, opath)
            print(path)
            print(opath)
            form = TrainingForm()
    else:
        form = TrainingForm()
    return render(request, 'training.html', {'form': form})