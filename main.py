from web3 import Web3, HTTPProvider
import json
import os
import time
from urllib.request import Request
from urllib.request import urlopen

# 合约交互函数

def adventure(token_id, address, skey):
    nonce = web3.eth.getTransactionCount(address)
    
    transaction = rarity.functions.adventure(int(token_id)).buildTransaction({
        "gas": rarity.functions.adventure(int(token_id)).estimateGas(),
        "gasPrice": int(web3.fromWei(web3.eth.gasPrice, 'WEI')),
        "nonce":nonce
    })
    
    signed_txn = web3.eth.account.signTransaction(transaction, skey)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    while True :
        attributeDict = web3.eth.get_transaction(txn_hash)
        if attributeDict['blockHash'] is not None :
            print('冒险成功...', attributeDict)
            break
        print('等待冒险中。。。', attributeDict)
        time.sleep(1)
    return

def level_up(token_id, address, skey):
    nonce = web3.eth.getTransactionCount(address)

    transaction = rarity.functions.level_up(int(token_id)).buildTransaction({
        "gas": rarity.functions.level_up(int(token_id)).estimateGas(),
        "gasPrice": int(web3.fromWei(web3.eth.gasPrice, 'WEI')),
        "nonce":nonce
    })
    
    signed_txn = web3.eth.account.signTransaction(transaction, skey)
    txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
    while True :
        attributeDict = web3.eth.get_transaction(txn_hash)
        if attributeDict['blockHash'] is not None :
            print('冒险成功...', attributeDict)
            break
        print('等待冒险中。。。', attributeDict)
        time.sleep(1)
    return

def next_adventure_time(token_id):
    return rarity.functions.adventurers_log(int(token_id)).call()

def current_xp(token_id):
    return rarity.functions.xp(int(token_id)).call()

def current_level(token_id):
    return rarity.functions.level(int(token_id)).call()

def level_up_xp(clevel):
    return rarity.functions.xp_required(clevel).call()



web3 = Web3(HTTPProvider('https://rpc.fantom.network'))

myAddress = ''
web3.eth.defaultAccount = myAddress
print(web3.isConnected())

with open("abi.json", 'r') as load_f :
    abi_dict = json.load(load_f)

contract_address = Web3.toChecksumAddress("0xce761D788DF608BD21bdd59d6f4B54b2e27F25Bb")
rarity = web3.eth.contract(address=contract_address, abi=abi_dict)


api_key = '' # ftmscan api key
req_url = 'https://api.ftmscan.com/api?module=account&action=tokennfttx&contractaddress=0xce761D788DF608BD21bdd59d6f4B54b2e27F25Bb&address={}&apikey={}'


while True:

    with open("account.json", 'r') as load_f :
        account_list = json.load(load_f)

    account_summoner_dict = {}

    # 监测是否有新的账号配置
    for account in account_list:
        if account["address"] in account_summoner_dict.keys() :
            continue
        else :
            account_summoner_dict[account["address"]]={}

    # 监测各个账号的 721 资产，获取角色 ID
    for account in account_list:
        req = Request(req_url.format(account['address'], api_key))
        with urlopen(req) as response :
            resp = json.load(response)
        
        if resp['status'] == '1' :
            s_list = resp['result']
            summoner_dict = account_summoner_dict[account["address"]]
            for summoner in s_list :
                if summoner['tokenID'] in summoner_dict.keys():
                    continue
                else :
                    summoner_dict[summoner['tokenID']] = {}
        else:
            print("error   " + resp)

    print(account_summoner_dict)

    # 确认角色冒险时间，自动冒险，升级监测，满足升级条件，进行 level up
    for account in account_list:
        summoner_dict = account_summoner_dict[account["address"]]
        for summoner in summoner_dict.keys():
            if 'next_adventure_time' not in summoner_dict[summoner].keys():
                summoner_dict[summoner]['next_adventure_time'] = next_adventure_time(summoner)
            
            if 'current_xp' not in summoner_dict[summoner].keys():
                summoner_dict[summoner]['current_xp'] = current_xp(summoner)

            if 'level_up_xp' not in summoner_dict[summoner].keys():
                summoner_dict[summoner]['level_up_xp'] = level_up_xp(current_level(summoner))

            if time.time() >= summoner_dict[summoner]['next_adventure_time'] :
                adventure(summoner, account['address'], account['skey'])
                summoner_dict[summoner]['next_adventure_time'] = next_adventure_time(summoner)
                summoner_dict[summoner]['current_xp'] = current_xp(summoner)
            
            if summoner_dict[summoner]['current_xp'] >= summoner_dict[summoner]['level_up_xp'] :
                level_up(summoner, account['address'], account['skey'])
                summoner_dict[summoner]['current_xp'] = current_xp(summoner)
                summoner_dict[summoner]['level_up_xp'] = level_up_xp(current_level(summoner))
                
    print(account_summoner_dict)
    time.sleep(600) # 10 分钟扫一遍
