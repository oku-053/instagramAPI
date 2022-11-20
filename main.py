import requests
import json
import datetime
from pprint import pprint
import config
import csv
import re


def basic_info():
    info = dict()
    info["access_token"]         = config.ACCESS_TOKEN
    info["app_id"]               = config.APP_ID
    info["app_secret"]           = config.APP_SECRET
    info['instagram_account_id'] = config.INSTAGRAM_BUSINESS_ACCOUNT_ID
    info["version"]              = config.VERSION  
    info["graph_domain"]         = config.GRAPH_DOMAIN
    info["endpoint_base"]        = config.ENDPOINT_BASE
    return info

# APIリクエスト用の関数
def InstagramApiCall(url, params, request_type):
    # リクエスト
    if request_type == 'POST' :
        # POST
        req = requests.post(url,params)
    else :
        # GET
        req = requests.get(url,params)
    # レスポンス
    res = dict()
    res["url"] = url
    res["endpoint_params"]        = params
    res["endpoint_params_pretty"] = json.dumps(params, indent=4)
    res["json_data"]              = json.loads(req.content)
    res["json_data_pretty"]       = json.dumps(res["json_data"], indent=4)
    # 出力
    return res

#instagramのAPIを呼び出す
def InstagramApiCallPaging(url,request_type):
        # リクエスト
    if request_type == 'POST' :
        # POST
        req = requests.post(url)
    else :
        # GET
        req = requests.get(url)
    # レスポンス
    res = dict()
    res["url"] = url
    res["json_data"] = json.loads(req.content)
    # 出力
    return res

#リクエストデバッグ用
def debugAT():
    # エンドポイントに送付するパラメータ
    Params = dict()
    Params["input_token"]  = config.ACCESS_TOKEN
    Params["access_token"] = config.ACCESS_TOKEN
    # エンドポイントURL
    url = config.GRAPH_DOMAIN + "/debug_token"

    return InstagramApiCall(url, Params, 'GET')

#指定したワードのハッシュタグIDを取得する
def get_hashtag_id(hashtag_word):
    
    """
    ***********************************************************************************
    【APIのエンドポイント】
    https://graph.facebook.com/{graph-api-version}/ig_hashtag_search?user_id={user-id}&q={hashtag-name}&fields={fields}
    ***********************************************************************************
    """
    # リクエスト
    Params = basic_info()                   # リクエストパラメータ
    Params['hashtag_name'] = hashtag_word   # ハッシュタグ情報
    
    # エンドポイントに送付するパラメータ
    Params['user_id'] = Params['instagram_account_id']  # インスタユーザID
    Params['q'] = Params['hashtag_name']                # ハッシュタグ名
    Params['fields'] = 'id,name'                        # フィールド情報
    url = Params['endpoint_base'] + 'ig_hashtag_search' # エンドポイントURL

    # レスポンス
    response = InstagramApiCall(url, Params, 'GET')
    # 戻り値（ハッシュタグID）
    return response['json_data']['data'][0]['id']

#トップ投稿を取得
def get_hashtag_media_top(params,hashtag_id) :
    
    """
    ***********************************************************************************
    【APIのエンドポイント】
    https://graph.facebook.com/{graph-api-version}/{ig-hashtag-id}/top_media?user_id={user-id}&fields={fields}
    ***********************************************************************************
    """
    # パラメータ
    Params = dict()
    Params['user_id'] = params['instagram_account_id']
    Params['fields'] = 'id,children,caption,comment_count,like_count,media_type,media_url,permalink'
    Params['access_token'] = params['access_token']
    
    # エンドポイントURL
    url = params['endpoint_base'] + hashtag_id + '/' + 'top_media'
    
    return InstagramApiCall(url, Params, 'GET')

#最新投稿を取得
def get_hashtag_media_recent(params,hashtag_id) :
    
    """
    ***********************************************************************************
    【APIのエンドポイント】
    https://graph.facebook.com/{graph-api-version}/{ig-hashtag-id}/recent_media?user_id={user-id}&fields={fields}
    ***********************************************************************************
    """
    # パラメータ
    Params = dict()
    Params['user_id'] = params['instagram_account_id']
    Params['fields'] = 'id,children,caption,comment_count,like_count,media_type,media_url,permalinks'
    Params['access_token'] = params['access_token']
    
    # エンドポイントURL
    url = params['endpoint_base'] + hashtag_id + '/' + 'recent_media'
    
    return InstagramApiCall(url, Params, 'GET')

#CSVに書き出す
def writeCSV(field_name,list,file_name,write_type) :
    with open(file_name, write_type, encoding='utf-8', newline='')as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_name)
        writer.writeheader()
        writer.writerows(list)

#ハッシュタグを抽出する
def extract_hash_tag(caption) :
    #pattern = r'\#(.*?)[\#|[\s]|[\r|\n|\r\n]]' 
    pattern = r"#[^#\s]*"
    res = re.findall(pattern, caption)
    return res

#ハッシュタグを削除する
def remove_hash_tag(caption) :
    pattern = r"#[^#\s]*"
    res = re.sub(pattern, '', caption)
    return res

def execute(params, hashtag_id, select, page) :
    if select == "top":
        hashtag_response = get_hashtag_media_top(params,hashtag_id)
        file_name = 'result_top.csv'
    else:
        hashtag_response = get_hashtag_media_recent(params,hashtag_id)
        file_name = 'result_recent.csv'


    field_name = ['id','like_count', 'caption', 'hash_tag','permalink']
    writeCSV(field_name,append_list(hashtag_response),file_name,'w')
    
    for i in range(page):
        if select == "top":
            hashtag_response_next = InstagramApiCallPaging(hashtag_response['json_data']['paging']['next'], 'GET')
        else:
            hashtag_response_next = InstagramApiCallPaging(hashtag_response['json_data']['paging']['next'], 'GET')
        writeCSV(field_name,append_list(hashtag_response_next),file_name,'a')   
    return 0

def append_list(hashtag_response) :
    results = []
    for element in hashtag_response['json_data']['data'] :
        try:
            like_count = element['like_count']
        except:
            like_count = '0'
        try:
            hash_tags = extract_hash_tag(element['caption'])
            tags = ','.join(hash_tags)
        except:
            element['caption'] = ''
            tags = ''
        try:
            permalink = element['permalink']
        except:
            permalink = ''
        result = {'id':element['id'], 'like_count':like_count, 'caption':remove_hash_tag(element['caption']), 'hash_tag':tags , 'permalink':permalink}
        results.append(result)
    return results

if __name__ == '__main__':
    
    # 【要修正】検索したいハッシュタグワードを記述
    hashtag_word = '写ルンです'

    # ハッシュタグIDを取得
    hashtag_id = get_hashtag_id(hashtag_word)

    # パラメータセット
    params = basic_info() 

    execute(params, hashtag_id, "top", 2)
    execute(params, hashtag_id, "recent", 2)
