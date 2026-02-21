from ast import Str
from distutils.command.config import config
from urllib import response

from fastapi import FastAPI, File,UploadFile
# from markupsafe import Markup
import re
import io
# from numpy.core.setup_common import file
from starlette.responses import Response
import io
from PIL import Image
import torch
from torchvision import transforms
import pickle
from utils.disease import disease_dic
from utils.fertilizer import fertilizer_dic
from utils.model import ResNet9
import pandas as pd
import requests
import json
from fastapi.middleware.cors import CORSMiddleware

disease_classes = ['Apple___Apple_scab',
                   'Apple___Black_rot',
                   'Apple___Cedar_apple_rust',
                   'Apple___healthy',
                   'Blueberry___healthy',
                   'Cherry_(including_sour)___Powdery_mildew',
                   'Cherry_(including_sour)___healthy',
                   'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
                   'Corn_(maize)___Common_rust_',
                   'Corn_(maize)___Northern_Leaf_Blight',
                   'Corn_(maize)___healthy',
                   'Grape___Black_rot',
                   'Grape___Esca_(Black_Measles)',
                   'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
                   'Grape___healthy',
                   'Orange___Haunglongbing_(Citrus_greening)',
                   'Peach___Bacterial_spot',
                   'Peach___healthy',
                   'Pepper,_bell___Bacterial_spot',
                   'Pepper,_bell___healthy',
                   'Potato___Early_blight',
                   'Potato___Late_blight',
                   'Potato___healthy',
                   'Raspberry___healthy',
                   'Soybean___healthy',
                   'Squash___Powdery_mildew',
                   'Strawberry___Leaf_scorch',
                   'Strawberry___healthy',
                   'Tomato___Bacterial_spot',
                   'Tomato___Early_blight',
                   'Tomato___Late_blight',
                   'Tomato___Leaf_Mold',
                   'Tomato___Septoria_leaf_spot',
                   'Tomato___Spider_mites Two-spotted_spider_mite',
                   'Tomato___Target_Spot',
                   'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
                   'Tomato___Tomato_mosaic_virus',
                   'Tomato___healthy']

disease_model_path = 'Pickle\Plant_Diseas.pth'
disease_model = ResNet9(3, len(disease_classes))
disease_model.load_state_dict(torch.load(disease_model_path, map_location=torch.device('cpu')))
disease_model.eval()

pipe=pickle.load(open('Pickle/Crop_Rec.pkl','rb'))
pipe1=pickle.load(open('Pickle/Yield_final.pkl','rb'))

df=pd.read_csv('Data/crop_recommendation.csv')
req=pd.read_csv('Data/FertilizerData.csv')
data3=pd.read_excel('Data/Gujarat_Village_Final.xlsx')

lb=pipe.classes_.tolist()

app1 = FastAPI(
    title="Agriculture Service by Grow Farm",
    description="""Take soil parameters from farmer and recommand crop""",
    version="0.0.1",
)
origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]


app1.add_middleware(
     CORSMiddleware,
     allow_origins=origins,
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)
# apiid='b56e6807765bfa742b5c07f6b3f58deb'
#
#     #####################  weather start
# URL=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiid}"
# def predict_image(img, model=disease_model):
#     """
#     Transforms image to tensor and predicts disease label
#     :params: image
#     :return: prediction (string)
#     """
#     transform = transforms.Compose([
#         transforms.Resize(256),
#         transforms.ToTensor(),
#     ])
#     image = Image.open(io.BytesIO(img))
#     img_t = transform(image)
#     img_u = torch.unsqueeze(img_t, 0)
#
#     # Get predictions from model
#     yb = model(img_u)
#     # Pick index with highest probability
#     _, preds = torch.max(yb, dim=1)
#     prediction = disease_classes[preds[0].item()]
#     # Retrieve the class label
#     return prediction

def predict_yield(dic):
    city=dic.get('location')
    season=dic.get('season')
    area=dic.get('Area')
    crop=dic.get('crop')
    nit=dic.get('nit')
    pot=dic.get('pot')
    phos=dic.get('phos')
    ph=dic.get('ph')
    apiid = 'b56e6807765bfa742b5c07f6b3f58deb'
    state="Gujarat"
    #####################  weather start
    url1= f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiid}"

    response= requests.get(url1).json()
    calvin1 = response['main']['temp']
    temp1 = float(calvin1-273)
    data = pd.DataFrame(
        {"State_Name":state, "District_Name":city, "Crop_Year":2022, "Season": season,"Crop":crop,"Area":area,"N":[nit],"P":[pot],
         "K":[phos],"PH":[ph],"TEM":[temp1]})
    res = pipe1.predict(data)
    print(type(res))
    return {season:res.tolist()}


def predict_res(inp):
    city=inp.get("location")

    n=inp.get("nit")
    p=inp.get("pot")
    k=inp.get("phos")
    ph=inp.get("ph")
    rain=inp.get("rain")
    apiid = 'b56e6807765bfa742b5c07f6b3f58deb'

    #####################  weather start
    URL = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={apiid}"

    response=requests.get(URL).json()
    calvin=response['main']['temp']
    temp=float(calvin-273)
    humi=response['main']['humidity']



    # print(response)


    ####################  weather end
    # data = np.array([[n,p, k, 23.603016, 60.3, ph, 140.91]])
    data=pd.DataFrame({"N":[n],"P":[p],"K":[k],"temperature":temp,"humidity":humi,"ph":[ph],"rainfall":[rain]})
    res=pipe.predict(data)
    probab=pipe.predict_proba(data)

    final_crop=sorted(list(enumerate(probab[0])) ,reverse=True,key=lambda x:x[1])[0:5]
    result=[]   #facult=data.loc[filt,'Faculties']
    for i in final_crop:
        crp=lb[i[0]]
        filt=req['Crop']==crp
        nitrogen=req.loc[filt,"N"]
        nitrogen=nitrogen.tolist()

        phosp=req.loc[filt,"P"]
        phosp=phosp.tolist()

        calsh=req.loc[filt,"K"]
        calsh=calsh.tolist()

        ph=req.loc[filt,"pH"]
        ph=ph.tolist()

#         filt2=df['label']==
        temp=df[df['label']==crp]['temperature'].mean()
        hum=df[df['label']==crp]['humidity'].mean()
        rain=df[df['label']==crp]['rainfall'].mean()
        
        # print(type(nitrogen))
        result.append({'Crop':lb[i[0]],'Prob':i[1],'Requir_Nitro':nitrogen[0],'Require_Phosp':phosp[0],'Require_cal':calsh[0],'Requir_Ph':ph[0],
                  'Require_temp':temp.tolist(),'Require_humidity':hum.tolist(),'Require_rain':rain.tolist(),'User_temp':temp,'User_humidity':humi})

    
    # result1=result.to_json()
    print(type(result))
    return result
@app1.get('/<id>')
def index(id):
    return{'id':id}

api_key_forcast='7ec233d4e007782a359aac89def2d631'

@app1.get('/weather/<city>')
def Weather_forecast(city):
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key_forcast}'
    req = requests.get(url)
    data = req.json()

    #Let's get the name, the longitude and latitude
    name = data['name']
    lon = data['coord']['lon']
    lat = data['coord']['lat']
    url2 = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key_forcast}'
    req2=requests.get(url2)
    data2=req2.json()
    final=[]
    for i in range(40):
        wet=data2['list'][i]['weather'][0]['main']
        disc=data2['list'][i]['weather'][0]['description']
        temp_min=data2['list'][i]['main']['temp_min']
        temp_max=data2['list'][i]['main']['temp_max']
        time=data2['list'][i]['dt_txt'].split(' ')
        wind=data2['list'][0]['wind']['speed']
        final.append({time[0]:{time[1]:{'Weather':disc,'temp_min':temp_min,'temp_max':temp_max,'wind':wind,'Allover':wet}}})
    return final
@app1.get('/District/<dist>')
def find_city(dist):
    # dist_list=['Kachchh' 'Banas Kantha' 'Patan' 'Mahesana' 'Sabar Kantha' 'Gandhinagar'
    #       'Ahmadabad' 'Surendranagar' 'pune' 'Jamnagar' 'Porbandar' 'Junagadh'
    #       'Amreli' 'Bhavnagar' 'Anand' 'Kheda' 'Panch Mahals' 'Dohad' 'Vadodara'
    #        'Narmada' 'Bharuch' 'The Dangs' 'Navsari' 'Valsad' 'Surat' 'Tapi']


    print(data3['District'].unique())
    temp = data3[data3['District'] == dist]
    res = temp['Taluka'].unique().tolist()
    village_map=[]
    for i in res:
        temp2=data3[data3['Taluka'] ==i]
        village=temp2['Village'].unique().tolist()
        village_map.append({i:village})

    return res,village_map

@app1.get('/Crop_Recommandation/<city>/<int:N>/<int:P>/<int:K>/<string:Ph>/<string:rain>')

def predict(city,N,P,K,Ph,rain):

    result_crop=predict_res({"location":city,"nit":N,"pot":P,"phos":K,"ph":float(Ph),"rain":float(rain)})
    #return result_crop
    print(type(result_crop))
    # data1=result_crop.pandas().to_json(orient="records")
    data1=json.dumps(result_crop)
    data=json.loads(data1)
    print(data)
    return data

@app1.get('/Crop_Yield/<dist>/<season>/<crop>/<int:area>/<int:N>/<int:P>/<int:K>/<string:Ph>')
def production(dist,season,crop,area,N,P,K,Ph):
    print('abcbqkfkwbefkhbwakbfajwfkjabksfvbkhabfhkwaebkfebskbchawbekfjwkebfckwabkejfbkesb ckhwebefk wKHBCKWbfkhwbHKF BWKjfbkwbFKBWfbkWHBFEK WkfehbkhWBFKb ekfhbwhebfkq FBKHFEBKHWEBFKbWKHFVHKWB KFehbkHWBFKh bkefsbiywBFEKSD BFJKeb')
    total_production=predict_yield({"location":dist,"season":season,"crop":crop,"Area":area,"nit":N,"pot":P,"phos":K,"ph":float(Ph)})
    print(total_production)
    return {'Yield':total_production}

@app1.post('/Crop_Diseas')
async def prediction_view(file:UploadFile = File(...)): #file:UploadFile = File(...)
    # # img = file.read()
    bytes_str = io.BytesIO(await file.read())
    # img = Image.open(bytes_str)
    # prediction = predict_image(img)
    # sol= Markup(str(disease_dic[prediction]))

    # img = file.read()
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.ToTensor(),
    ])
    image = Image.open(bytes_str)
    img_t = transform(image)
    img_u = torch.unsqueeze(img_t, 0)

    # Get predictions from model
    yb = disease_model (img_u)
    # Pick index with highest probability
    _, preds = torch.max(yb, dim=1)
    prediction = disease_classes[preds[0].item()]

    # prediction = predict_image(img)
    diseas=str(prediction)
    final=diseas.replace('___',' ')
    final=final.replace('_',' ')

    prediction1 = (str(disease_dic[prediction]))
    to_clean = re.compile('<.*?>')
    cleantext = re.sub(to_clean, '', prediction1)
    
    return {"Diseas":final,"Steps & Suggestions":cleantext}
    # bytes_str = io.BytesIO(file.read())
    

# ========================================
# EMAIL OTP VERIFICATION ENDPOINT
# ========================================
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Store OTPs temporarily (in production, use Redis or database)
otp_storage = {}

@app1.get('/verify/{email}')
def send_email_otp(email: str):
    """
    Send OTP to email address for verification
    """
    try:
        # Generate 4-digit OTP
        otp = str(random.randint(1000, 9999))
        
        # Store OTP for this email
        otp_storage[email] = otp
        
        # 🔔 LOG OTP TO TERMINAL FOR TESTING
        print('\n========================================')
        print('📧 EMAIL OTP GENERATED')
        print('========================================')
        print(f'Email: {email}')
        print(f'OTP: {otp}')
        print('========================================\n')
        
        # For hackathon/testing: Just return OTP without actually sending email
        # In production, uncomment the email sending code below
        
        return {
            "status": "ok",
            "message": "OTP sent successfully",
            "OTP": otp,  # Remove this in production!
            "email": email
        }
        
        # PRODUCTION CODE (requires SMTP setup):
        # Uncomment below to actually send emails
        """
        sender_email = "your-email@gmail.com"
        sender_password = "your-app-password"
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "GrowFarm - Email Verification OTP"
        
        body = f'''
        Hello,
        
        Your OTP for GrowFarm registration is: {otp}
        
        This OTP is valid for 10 minutes.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        GrowFarm Team
        '''
        
        message.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, message.as_string())
        
        return {
            "status": "ok",
            "message": "OTP sent to your email",
            "email": email
        }
        """
        
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return {
            "status": "error",
            "error": f"Failed to send OTP: {str(e)}"
        }
