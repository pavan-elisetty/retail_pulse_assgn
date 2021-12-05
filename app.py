import requests
from flask import Flask,request
from flask_restful import Api, Resource, reqparse
import json
from PIL import Image
import random

app=Flask(__name__)
api=Api(app)
nums=[]
good_jb_db={}
bad_jb_db={}

def json_create(args):

    json_object = json.dumps(args)
    with open("sample.json","w") as outfile:
        outfile.write(json_object)
    return
def json_data_handle():
    with open('sample.json') as json_file:
        data = json.load(json_file)
    return data
def handler(data):
    flag=True
    err=""
    try:
        count = data['count']
    except:
        err="There is no count"
        ls = [400, err]
        return ls
    if count!=len(data['visits']):
        flag=False
        err+="Length of visits is not equal to the count."
    for i in range(count):
        try:
            store_id=data['visits'][i]['store_id']
        except:
            flag=False
            err+="There is no store_id."

        try:
            visit_time=data['visits'][i]['visit_time']
        except:
            flag=False
            err+= "There is no visit time."

        try:
            img_data=data['visits'][i]['image_url']
        except:
            flag=False
            err+= "There is no Image_urls."

        num_urls = len(data['visits'][i]['image_url'])
        if num_urls==0:
            flag=False
            err+="Missing the image_urls"
        else:
            pass

    if flag==False:
        ls=[400,err]
        return ls
    if flag==True:
        err=""
        ls=[201,err]
        return ls
def img_prcs(job_id,data):
    count = data['count']
    err=""
    flag=True
    err_ls=[]
    for i in range(count):
        store_id = data['visits'][i]['store_id']
        for i in data['visits'][i]['image_url']:
             try:
                 response=requests.get(i)
                 file=open("sample_image.png","wb")
                 file.write(response.content)
                 file.close()
                 img=Image.open("sample_image.png")
                 width=img.width
                 height=img.height
                 perm=2*(width+height)
             except:
                 flag=False
                 err="Unable to parse image"
             if flag==False:
                 err_ls.append({"store_id":store_id,"error":err})

    if flag==True:
        good_jb_db[job_id]={"status":"Completed","job_id":job_id }
    if flag==False:
        bad_jb_db[job_id]={"status":"Failed","job_id":job_id,"error":err_ls}
def gen_jobid():
    while True:
        num = random.randint(1, 1000)
        if num in nums:
            continue
        else:
            nums.append(num)
            break
    return num

class Submit(Resource):
    parser=reqparse.RequestParser()
    parser.add_argument('count',
                        type=int,
                        required=True,
                        help="This field cannot be left blank"
                        )
    parser.add_argument('visits',required=True,help="This cannot be left blank")

    def post(self):
        args = request.get_json()
        json_create(args)
        data=json_data_handle()
        tmp=handler(data)
        if tmp[0]==400:
            return{"error":tmp[1]},400
        elif tmp[0] == 201:
            job_id = gen_jobid()
            img_prcs(job_id, data)
            return {"job_id": job_id}, 201

class Access(Resource):

    def get(self):
        args=request.args
        job_id= int(args['jobid'])
        if job_id in good_jb_db:
            return good_jb_db[job_id],200
        elif job_id in bad_jb_db:
            return bad_jb_db[job_id],200
        else:
            return {},400
class Home(Resource):
    def get(self):
        return {"message":"api end points are similar to that of assignment , please use them"}

api.add_resource(Submit,'/api/submit')
api.add_resource(Access,'/api/status')
api.add_resource(Home,'/')
app.run() #if you want to enable debugger add debug=True as parameter
