import json
import requests
import settings

def lambda_handler(event, context):
    settings.debug_logger.debug(f'event: {event}')

    # チャンネルID取得
    channel = event['event']['channel']
    # スレッドのタイムスタンプ取得
    ts = event['event']['ts']
    settings.debug_logger.debug(f'channel: {channel}')
    settings.debug_logger.debug(f'ts: {ts}')


    # 会話内容を取得
    blocks = event['event']['blocks']
    # メンションされたユーザーIDを取得
    user_ids = []
    for block in blocks:
        user_ids += get_user_ids_from_mention(block['elements'])
    settings.debug_logger.debug(f'user_ids: {user_ids}')

    # APIを使用してユーザーIDからトークン取得
    tokens = get_api_tokens(user_ids)
    settings.debug_logger.debug(f'tokens: {tokens}')

    if tokens is None:
        return {
            'status_code': 500,
            'message': 'tokens is None',
        }

    # リアクションをする
    for token in tokens:
        response = add_reaction(token, 'thumbsup', channel, ts)

        if response.status_code != 200:
            settings.debug_logger.error('failed to connect reaction api')
            return {
                'status_code': response.status_code,
                'message': message,
            }

        # dict化
        response_data = response.json()
        settings.debug_logger.debug(f'reaction_response_data: {response_data}')

        if response_data['ok']:
            settings.debug_logger.info('success to add reaction')
        else:
            message = 'failed to add reaction'
            settings.debug_logger.error(message)
            settings.debug_logger.error(f'api error: {response_data['error']}')
            continue

    return {
        'status_code': 200,
        'message': 'success to add all reactions',
    }

def get_user_ids_from_mention(elements):
    user_ids = []
    for element in elements:
        if element['type'] == 'user':
            # ユーザーIDを追加
            user_ids.append(element['user_id'])

        # elementsキーがないなら飛ばす
        if not 'elements' in element:
            continue
        # 深く潜る
        user_ids += get_user_ids_from_mention(element['elements'])

    return user_ids

def get_api_tokens(user_ids):
    tokens = []
    for user_id in user_ids:
        data = {
            'user_id': user_id,
            'password': settings.api_password,
        }
        response = requests.get(settings.get_slack_access_token_api_uri, params=data)

        # 接続失敗なら
        if response.status_code != 200:
            settings.debug_logger.error('failed to connect api.')
            settings.debug_logger.error(f'http error: {response.text} {response.status_code}')
            return tokens
        
        # dict化
        response_data = response.json()
        settings.debug_logger.debug(f'token_response_data: {response_data}')
        
        # API処理に失敗したら飛ばす
        if not response_data['ok']:
            settings.debug_logger.error(f'api error: {response_data['error']}')
            continue

        tokens.append(response_data['user']['access_token'])

    return tokens

def add_reaction(token, name, channel, timestamp):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    data = {
        'name': name,
        'channel': channel,
        'timestamp': timestamp,
    }
    response = requests.post(settings.slack_reactions_add_api_uri, headers=headers, params=data)
    
    return response