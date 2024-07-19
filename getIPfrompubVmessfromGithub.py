import base64
import json
import requests,os,re,random
from collections import OrderedDict



# URL of the text file containing base64 encoded vmess links
xxxurl = 'https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Splitted-By-Protocol/vmess.txt'
#########################################【addRecord_url】###################################
addRecord_url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['cloudflare_zone_id']}/dns_records"
addRecord_payload = {
        "content": "172.64.34.213",
        "name": os.environ['cloudflare_target_domain'],  # 移除大括号，直接使用变量
        "proxied": False,
        "type": "A",
        "comment": "Domain verification record",
        "ttl": 60
    }
addRecord_headers = {
    "Content-Type": "application/json",
    "X-Auth-Email": os.environ['cloudflare_email'],
    "X-Auth-Key": os.environ['cloudflare_api_key']
}

def addRecord_Func(ipaddress):
    addRecord_payload['content'] = ipaddress
    response = requests.post(addRecord_url, json=addRecord_payload, headers=addRecord_headers)  # 使用 POST 请求
    print(response.text)
    if 'success":true' in response.text:
        print('记录添加成功')
    else:
        print('记录添加失败')

###################################【deleteRecord_Func】##################################
def deleteRecord_Func():
    filtered_dnsid = ListRecord_Func()
    for dnsid in filtered_dnsid:
        deleteRecord_url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['cloudflare_zone_id']}/dns_records/{dnsid}"
        response = requests.delete(deleteRecord_url, headers=addRecord_headers)
        print(response.text)
        if 'success":true' in response.text:
            print('记录删除成功')
        else:
            print('记录删除失败')


#########################################【listRecord_url】###################################
listRecord_url = f"https://api.cloudflare.com/client/v4/zones/{os.environ['cloudflare_zone_id']}/dns_records"
# 设置请求参数
xxparams = {
    # 可选参数：
    "page": 1,
    "per_page": 200
}
# 列出所有dns id
def ListRecord_Func():
    response = requests.request("GET", listRecord_url, headers=addRecord_headers, params=xxparams)
    print(response.text)
    # 解析 JSON
    data = json.loads(response.text)
    # 获取所有记录
    records = data["result"]
    # 筛选出 name 为 "域名" 的记录中的每个 id 值  
    filtered_ids = [record["id"] for record in records if record["name"] == str(os.environ['cloudflare_target_domain'])]
    # 打印结果
    print(filtered_ids)
    return filtered_ids




def decode_vmess_links(vmess_links):
    decoded_data = []
    for link in vmess_links:
        # Remove the 'vmess://' prefix
        link = link.replace('vmess://', '')
        # Decode the base64 encoded string
        decoded_str = base64.b64decode(link).decode()
        decoded_data.append(decoded_str)
        
        # Parse the JSON data
        vmess_data = json.loads(decoded_str)
        
        if 'add' in vmess_data:
             # 过滤包含域名，只保留数字，大部分域名都不可用。
            if not re.search('[a-zA-Z]', vmess_data['add']):
                iplist_values.append(vmess_data['add'])

def fetch_and_decode_vmess_links(url):
    # Step 1: Fetch the content from the URL
    vmesslinks_list = []

    response_cf = requests.get(url)
    if response_cf.status_code == 200:
        # Step 2: Decode the base64 encoded strings
        lines = response_cf.text.strip()
        # decoded_data =base64.b64decode(lines).decode()
        decoded_bytes = base64.b64decode(lines).decode().split('\n')
        # decoded_string = decoded_bytes.decode('utf-8')  # 解码为UTF-8字符串
        for data in decoded_bytes:
        # add_values.append(data)
            if 'vmess' in data:
                vmesslinks_list.append(data)

        decode_vmess_links(vmesslinks_list)


iplist_values = []
# 先清空所有dns
deleteRecord_Func()
# 生成所有ip
fetch_and_decode_vmess_links(xxxurl)

iplist_values = list(OrderedDict.fromkeys(iplist_values))

# 初始化计数器
count = 0
for ip in iplist_values:
    # 如果 IP 地址包含 '104'，则调用 addRecord_Func 函数并增加计数器
       
    if count >=200:
        break

    if '104' in ip:
        addRecord_Func(ip)
        count += 1