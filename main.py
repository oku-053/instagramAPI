import requests
import json
import datetime
from pprint import pprint
import config
import csv


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
    res["json_data"]              = json.loads(req.content)
    # 出力
    return res

def debugAT():
    # エンドポイントに送付するパラメータ
    Params = dict()
    Params["input_token"]  = config.ACCESS_TOKEN
    Params["access_token"] = config.ACCESS_TOKEN
    # エンドポイントURL
    url = config.GRAPH_DOMAIN + "/debug_token"

    return InstagramApiCall(url, Params, 'GET')

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

def writeCSV(field_name,list,file_name,write_type) :
    with open(file_name, write_type, encoding='utf-8', newline='')as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = field_name)
        writer.writeheader()
        writer.writerows(list)

if __name__ == '__main__':
    
    # 【要修正】検索したいハッシュタグワードを記述
    hashtag_word = '写ルンです'

    # ハッシュタグIDを取得
    hashtag_id = get_hashtag_id(hashtag_word)

    # パラメータセット
    params = basic_info() 

    field_name = ['id','children','like_count','media_type', 'caption','permalink','media_url']
    # ハッシュタグ情報取得
    hashtag_response_top = get_hashtag_media_top(params,hashtag_id)
    hashtag_response_recent = get_hashtag_media_recent(params,hashtag_id)
    writeCSV(field_name,hashtag_response_top['json_data']['data'],'result_top.csv','w')
    writeCSV(field_name,hashtag_response_recent['json_data']['data'],'result_recent.csv','w')
    for i in range(40):
        hashtag_response_top = InstagramApiCallPaging(hashtag_response_top['json_data']['paging']['next'], 'GET')
        hashtag_response_recent = InstagramApiCallPaging(hashtag_response_recent['json_data']['paging']['next'], 'GET')
        writeCSV(field_name,hashtag_response_top['json_data']['data'],'result_top.csv','a')
        writeCSV(field_name,hashtag_response_recent['json_data']['data'],'result_recent.csv','a')
