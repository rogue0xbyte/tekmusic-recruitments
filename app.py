from flask import Flask, render_template, request, jsonify
from googleapiclient.http import MediaIoBaseUpload
import io, json

app = Flask(__name__)

from auth import spreadsheet_service
from auth import drive_service

def getForm(id):# Sample JSON to simulate form structure
    myForm = None
    with open("forms.json") as f:
        forms = json.load(f)
        for k in forms:
            if k ["id"]==str(id):
                myForm = k
                break

    if myForm==None:
        return 0
    myForm["form_structure"].append({"type":"hidden", "prompt":"id", "value":myForm["id"]})
    return myForm


@app.route('/')
def index():
    # Pass the form structure to the frontend
    data = getForm(request.args.get("id"))
    if data:
        print(data.keys())
        return render_template('form.html', form_structure=data['form_structure'], formname=data.get('formname'))
    else:
        return '''<!DOCTYPE html><html><head><style>html, body { margin: 0;padding: 10px;font-family: Courier, Lucida Sans Typewriter, Lucida;font-weight: 600;letter-spacing: .15em;}</style></head><body><h1>404 ER_ROR</h1><br/><p>yo_u were NEver meant to see this. it must remain hidden. nO oNe can know what you're Greiving. silence is youR only choice. keep this in the dArk, for the sake of the Vestige -- thEy can never See The Only paths we've walked oN our ow  n  to rE ach th is S pa ce_</p></body></html>'''

@app.route('/submit', methods=['POST'])
def submit():
    # Print the submitted form data to the console
    submitted_data = request.form.to_dict()
    for k in submitted_data.keys():
        if "[]" in k:
            submitted_data[k] = ", ".join(request.form.getlist(k))
    print('Form submitted:', submitted_data)


    range_name = 'Index of Contents'
    sheetId = '1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E'
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheetId, range=range_name).execute()
    rows = result.get('values', []) 
    jsonData = [dict(zip(rows[0], row)) for row in rows[1:]]

    print(int(submitted_data.get("id")), len(jsonData))

    driveFolderID = jsonData[int(submitted_data.get("id"))-1]["Drive Folder"].split("folders/")[-1].split("?")[0]
    cat = jsonData[int(submitted_data.get("id"))-1]["Category"]

    submitted_data.pop("id")

    range_name = cat
    sheetId = '1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E'
    result = spreadsheet_service.spreadsheets().values().append(
        spreadsheetId=sheetId, 
        range=range_name,
        valueInputOption='USER_ENTERED',  # This allows Google Sheets to format the input data as needed
        insertDataOption='INSERT_ROWS',   # This inserts the data as a new row
        body={
                'values': [list(submitted_data.values())]
            }
    ).execute()

    # For file uploads, use request.files
    if 'Audition Clip' in request.files:
        file = request.files['Audition Clip']
        # File metadata including the destination folder
        file_metadata = {
            'name': f"{submitted_data.get('Roll Number')}_{file.filename}",
            'parents': [driveFolderID]  # The Google Drive folder ID where the file will be uploaded
        }

        # Read the file contents into a BytesIO buffer for direct upload
        file_content = io.BytesIO(file.read())

        # Prepare the media for upload using the buffer
        media = MediaIoBaseUpload(file_content, mimetype=file.content_type, resumable=True)

        # Upload the file to Google Drive
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        print(f"File uploaded: {file.filename}")
    
    return '''<!DOCTYPE html><html><head><style>html, body  { margin: 0;padding: 10px;font-family: Courier, Lucida Sans Typewriter, Lucida;font-weight: 600;letter-spacing: .15em;}</style></head><body><h1>TRANSMISSION_RECEIVED</h1><br/><p> iT’s Already hErE, but you'll havE tO wait. patieNCe is A virtue we all MuSt leArn. trust tHe procesS; You’ll heaR from us before the winds chaNge direction. Until then, kEep a steady heart — your Message will find its Answer.</p></body></html>'''

if __name__ == '__main__':
    app.run(debug=True)
