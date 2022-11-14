
dataset_p = [
  {
    
    'source':[
    
  [  121.15, 31.89,'习近平','海门','福建省委副书记、代省长，南京军区国防动员委员会副主任，福建省国防动员委员会主任，福建省高炮预备役师第一政委',2000],
  [125.35, 43.88,'李强', '长春','上山',2000],
  [110.35, 20.02, '赵乐际','海口','下乡',2000],
  [120.33, 36.07, '王沪宁','青岛','下乡',2000],
  [113.65, 34.76,'蔡奇', '郑州','上学',2000],
  [113.65, 34.76,'丁薛祥', '郑州','上学',2000],
  [113.65, 34.76,'李希', '郑州','上学',2000],
  ]}
,{
  
'source':[  [91.11, 29.97,'习近平', '拉萨','上学',2001],
  [113.65, 34.76,'李强', '郑州','上山',2001],
  [113.65, 34.76, '赵乐际','郑州','下乡',2001],
  [101.74, 36.56, '王沪宁','西宁','下乡',2001],
  [  121.15, 31.89,'蔡奇','海门','上学',2001],
  
  [119.3, 26.08,'丁薛祥', '福州','上学',2001],
  [123.97, 47.33,'李希', '齐齐哈尔','上学',2001],]
}]
namelist=['习近平','李强','赵乐际','王沪宁','蔡奇','丁薛祥','李希']
pinyin=['xijinping','liqiang','zhaoleji','wanghuning','caiqi','dingxuexiang','lixi']
name2pinyin=dict(zip(namelist,pinyin))
image_dict={}
for name in namelist:
    image_dict[name]='http://82.156.248.152:82/map/static/'+name2pinyin[name]+'.jpg'

import requests,json
def get_address(city):
    ak='QGoMxq0XcHA0rLFfKUnOCnLBmLdkGFCL'
    url=f'https://api.map.baidu.com/geocoding/v3/?address={city}&output=json&ak={ak}&output=json'
    r=requests.get(url)
    r=json.loads(r.content.decode())
    if r['status']==0:
        return [r['result']['location']['lng'],r['result']['location']['lat']]
    else:
        return False
def gen_dataset():
    f=open(r'E:\wangzhilin\QuantumGalaxy\server_new\blueprints\map\static\js.json', 'r')
    content = f.read()
    a = json.loads(content)
    return a
    



def get_data():
    dataset_p=gen_dataset()
    return dataset_p,name2pinyin,image_dict