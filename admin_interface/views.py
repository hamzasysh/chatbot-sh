from django.shortcuts import render
from .forms import TrainingForm
import jsonlines
import json
import os
import time
from django.http import JsonResponse
import csv
from openai import OpenAI
from django.conf import settings
from chat.models import Conversation, Message


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def create_fine_tuning_file(file_path):
    print("Processing fine tuning file " + file_path)
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose='fine-tune'
    )

    file_id = file.id

    status = file.status

    while status != 'processed':
        print(f"File status: {status}. Waiting for the file to be processed...")
        time.sleep(10)  # Wait for 10 seconds
        file_response = client.File.retrieve(file_id)
        status = file_response['status']
        print(file_response)
    return file

def fine_tune_model(fine_tuning_file):
    print("Starting fine tuning job with ID: " + fine_tuning_file.id)
    fine_tuning_response=None
    if fine_tuning_file.status == 'processed':
        fine_tuning_response = client.fine_tuning.jobs.create(
            training_file=fine_tuning_file.id,
            model="gpt-3.5-turbo"
        )
        print(fine_tuning_response.id)
    return fine_tuning_response.id

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



def load_db_conversations_in_csv(path):
    try:
        messages_with_conversation_details = Message.objects.select_related('conversation').all()
        cid = None
        conv = []

        with open(path, 'w',newline='') as csvfile:
            writer_object = csv.writer(csvfile)
            for i, message in enumerate(messages_with_conversation_details):
                if i == 0:
                    cid = message.conversation.session_id
                    conv.append(settings.SYSTEM_ROLE)
                    conv.append(message.text)
                elif cid != message.conversation.session_id:
                    writer_object.writerow(conv)
                    cid = message.conversation.session_id
                    conv.clear()
                    conv.append(settings.SYSTEM_ROLE)
                    conv.append(message.text)
                else:
                    conv.append(message.text)

            writer_object.writerow(conv)  

    except Exception as e:
        print(f"Error: {e}")

def merge_jsonl(file1, file2, output_file):
    with open(file1, 'r', encoding='utf-8') as f1, \
         open(file2, 'r', encoding='utf-8') as f2, \
         open(output_file, 'w', encoding='utf-8') as out_file:
        
        # Copy contents of file1 to output file
        for line in f1:
            out_file.write(line)
        
        # Copy contents of file2 to output file
        for line in f2:
            out_file.write(line)

    

def admin_interface(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name
            file_name= file_name.split(".")[0].replace(" ","_")+"."+file_name.split(".")[1]
            path=os.path.join(settings.TRAIN_FOLDER,file_name)
            opath=os.path.join(settings.TRAIN_FOLDER,file_name.split(".")[0]+".jsonl")
            dpath=os.path.join(settings.TRAIN_FOLDER,'db.csv')
            dopath=os.path.join(settings.TRAIN_FOLDER,"db.jsonl")
            mopath=os.path.join(settings.TRAIN_FOLDER,"main.jsonl")
            load_db_conversations_in_csv(dpath)
            load_csv_finetuning(path, opath)
            load_csv_finetuning(dpath, dopath)
            merge_jsonl(opath,dopath,mopath)
            #fine_tuning_file = create_fine_tuning_file(mopath)
            #id = fine_tune_model(fine_tuning_file)
            print(client.fine_tuning.jobs.list(limit=10))
            #model="ft:gpt-3.5-turbo:my-org:custom_suffix:id"
            success_message = "Training has completed successfully."
            print(path)
            print(opath)
            form = None  # Reset the form after successful submission
        else:
            success_message = "Training has failed"
            form=None
    else:
        form = TrainingForm()
        success_message = None
    return render(request, 'training.html', {'form': form, 'success_message': success_message})