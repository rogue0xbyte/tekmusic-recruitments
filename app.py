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


@app.route('/recieved/<submId>/<roll_number>')
def recieved(submId, roll_number):
    range_name = 'Index of Contents'
    sheetId = '1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E'
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheetId, range=range_name).execute()
    rows = result.get('values', []) 
    jsonData = [dict(zip(rows[0], row)) for row in rows[1:]]

    driveFolderID = jsonData[int(submId)-1]["Drive Folder"].split("folders/")[-1].split("?")[0]
    cat = jsonData[int(submId)-1]["Category"]

    result = spreadsheet_service.spreadsheets().values().get(
        spreadsheetId='1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E', range=cat).execute()
    rows = result.get('values', [])
    # print('rows',rows)
    roll_index = 2

    name = ''

    for row in rows:
        # print(row[roll_index], roll_number)
        # Ensure the row has data in the 'Roll Number' column
        if row[roll_index].upper() == roll_number.upper():
            name = row[0]

    message = f"iT’s Already hErE, <span style='text-decoration:underline'>{name.split(' ')[0].lower()}</span>_ (<span style='text-decoration:underline'>{roll_number.upper()}</span>), but you'll havE tO wait. patieNCe is A virtue we all MuSt leArn. trust tHe procesS; You’ll heaR from thE <span style='text-decoration:underline'>{cat.lower()}</span> teAm before the winds chaNge direction. Until then, kEep a steady heart — your Message will find its Answer."
    return str('''
<!DOCTYPE html> <html> <head> <style>html, body  { margin: 0;padding: 10px;font-family: Courier, Lucida Sans Typewriter, Lucida;font-weight: 600;letter-spacing: .15em;} .checkmark { width: 32px; height: 32px; border-radius: 50%; display: block; stroke-width: 2; stroke: #fff; stroke-miterlimit: 10; box-shadow: inset 0px 0px 0px #a83232; animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both; } .checkmark_circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 2; stroke-miterlimit: 10; stroke: #a83232; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; } .checkmark_check { transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards; } @keyframes stroke { 100% { stroke-dashoffset: 0; } } @keyframes scale { 0%, 100% { transform: none; } 50% { transform: scale3d(1.1, 1.1, 1); } } @keyframes fill { 100% { box-shadow: inset 0px 0px 0px 30px #a83232; } }</style> </head> <body> <h1 style="color:#a83232;display: flex;gap: 15px;">ER_ROR ! TRANSMISSION_RECEIVED <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52"><circle class="checkmark_circle" cx="26" cy="26" r="25" fill="none"/><path class="checkmark_check" fill="none" d="M14.1 14.1l23.8 23.8 m0,-23.8 l-23.8,23.8"/></svg></h1> <br/> <p>
''' + message + '</p><script>alert("Your submission has already been recieved. You can only make one submission.")</script></body></html>')


@app.route('/checkRoll/<submId>/<roll_number>')
def checkRoll(submId, roll_number):

    # usage: checkRoll(request.args.get("id"), "21Z202")

    range_name = 'Index of Contents'
    sheetId = '1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E'
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheetId, range=range_name).execute()
    rows = result.get('values', []) 
    jsonData = [dict(zip(rows[0], row)) for row in rows[1:]]

    driveFolderID = jsonData[int(submId)-1]["Drive Folder"].split("folders/")[-1].split("?")[0]
    cat = jsonData[int(submId)-1]["Category"]

    result = spreadsheet_service.spreadsheets().values().get(
        spreadsheetId='1Bo1voat5z-OQ4hiV5ldYb5hnqK9qxaL4n1Wsp3yu-5E', range=cat).execute()
    rows = result.get('values', [])
    # print('rows',rows)
    roll_index = 2

    for row in rows:
        # print(row[roll_index], roll_number)
        # Ensure the row has data in the 'Roll Number' column
        if row[roll_index].upper() == roll_number.upper():
            # print(f"Roll number {roll_number} found! Registered.")
            return jsonify({"found":True})

    # print(f"Roll number {roll_number} not found. Not registered.")
    return jsonify({"found":False})


@app.route('/')
def index():
    # Pass the form structure to the frontend
    data = getForm(request.args.get("id"))
    if data:
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
    
    return '''<!DOCTYPE html> <html> <head> <style>html, body  { margin: 0;padding: 10px;font-family: Courier, Lucida Sans Typewriter, Lucida;font-weight: 600;letter-spacing: .15em;} .checkmark__circle{ stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 2; stroke-miterlimit: 10; stroke: #7ac142; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards } .checkmark{ width: 32px; height: 32px; border-radius: 50%; stroke-width: 2; stroke: #fff; stroke-miterlimit: 10; margin-top: 25px; box-shadow: inset 0px 0px 0px #7ac142; animation: fill .4s ease-in-out .4s forwards, scale .3s ease-in-out .9s both } .checkmark__check{ transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards } @keyframes stroke{ 100%{ stroke-dashoffset: 0 } } @keyframes scale{ 0%, 100%{ transform: none } 50%{ transform: scale3d(1.1, 1.1, 1) } } @keyframes fill{ 100%{ box-shadow: inset 0px 0px 0px 30px #7ac142 } }  </style> </head> <body> <h1 style="color:#32a852">TRANSMISSION_RECEIVED <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52"> <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/> <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/></svg></h1> <br/> <p> iT’s Already hErE, but you'll havE tO wait. patieNCe is A virtue we all MuSt leArn. trust tHe procesS; You’ll heaR from us before the winds chaNge direction. Until then, kEep a steady heart — your Message will find its Answer.</p> </body> <script> alert('Submission Recieved. Await our response.') </script> </html>'''

if __name__ == '__main__':
    app.run(debug=True)
