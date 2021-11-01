# import web3
import streamlit as st
import requests, json
from web3 import Web3
import pandas as pd
# Most expensive NFT
# Slider for specify the range of price 
# Add the bundles as Endpoint => done
# ##on sale as filter
# ##owner as filter

st.sidebar.header("Endpoints")
endpoint_choices = ['Most Expnsive NFT', 'Assets', 'Events', 'Rarity', 'Bundles']
endpoint = st.sidebar.selectbox("Choose an Endpoint", endpoint_choices)

st.title(f"OpenSea API Explorer - {endpoint}")
# function for rendering assests info.
def render_asset(asset):
    if asset['name'] is not None:
        st.subheader(asset['name'])
    else:
        st.subheader(f"{asset['collection']['name']} #{asset['token_id']}")

    if asset['description'] is not None:
        st.write(asset['description'])
    else:
        st.write(asset['collection']['description'])

    if asset['image_url'].endswith('mp4') or asset['image_url'].endswith('mov'):
        st.video(asset['image_url'])
    elif asset['image_url'].endswith('svg'):
        svg = requests.get(asset['image_url']).content.decode()
        st.image(svg)
    elif asset['image_url']:
        st.image(asset['image_url'])

# function for rendering assests from image_url for different types of media.
def render_img(asset):
    if asset.endswith('mp4') or asset.endswith('mov'):
        st.video(asset)
    elif asset.endswith('svg'):
        svg = requests.get(asset).content.decode()
        st.image(svg)
    elif asset:
        st.image(asset)


if endpoint == 'Events':
    collection = st.sidebar.text_input("Collection")
    asset_contract_address = st.sidebar.text_input("Contract Address")
    token_id = st.sidebar.text_input("Token ID")
    event_type = st.sidebar.selectbox("Event Type", ['','offer_entered', 'cancelled', 'bid_withdrawn', 'transfer', 'approve'])
    params = {}
    if collection:
        params['collection_slug'] = collection
    if asset_contract_address:
        params['asset_contract_address'] = asset_contract_address
    if token_id:
        params['token_id'] = token_id
    if event_type:
        params['event_type'] = event_type
    
    r = requests.get('https://api.opensea.io/api/v1/events', params=params)

    events = r.json()
    event_list = []
    for event in events['asset_events']:
        if event_type == 'offer_entered':
            if event['bid_amount']:
                bid_amount = Web3.fromWei(int(event['bid_amount']), unit='ether')
            if event['from_account']['user']:
                bidder = event['from_account']['user']['username']
            else:
                bidder = event['from_account']['address']

            event_list.append([event['created_date'], bidder, float(bid_amount), event['asset']['collection']['name'], event['asset']['token_id']])
    # improvement 1 make table display just if there is data 
    if len(event_list) != 0:
        df = pd.DataFrame(event_list, columns=['time', 'bidder', 'bid_amount', 'collection', 'token_id'])
        st.write(df)
    # if events is not None:
    st.write(events)

if endpoint == 'Assets':
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner")
    collection = st.sidebar.text_input("Collection")
    params = {'owner': owner}
    if collection:
        params['collection'] = collection

    r = requests.get('https://api.opensea.io/api/v1/assets', params=params)

    assets = r.json()['assets']
    for asset in assets:                
        render_asset(asset)

    st.subheader("Raw JSON Data")
    st.write(r.json())

if endpoint == 'Rarity':
    with open('assets.json') as f:
        data = json.loads(f.read())
        asset_rarities = []

        for asset in data['assets']:
            asset_rarity = 1

            for trait in asset['traits']:
                trait_rarity = trait['trait_count'] / 8888
                asset_rarity *= trait_rarity

            asset_rarities.append({
                'token_id': asset['token_id'],
                'name': f"Wanderers {asset['token_id']}",
                'description': asset['description'],
                'rarity': asset_rarity,
                'traits': asset['traits'],
                'image_url': asset['image_url'],
                'collection': asset['collection']
            })

        assets_sorted = sorted(asset_rarities, key=lambda asset: asset['rarity']) 

        for asset in assets_sorted[:20]:
            render_asset(asset)
            st.subheader(f"{len(asset['traits'])} Traits")
            for trait in asset['traits']:
                st.write(f"{trait['trait_type']} - {trait['value']} - {trait['trait_count']} have this")

if endpoint == 'Bundles':
    st.sidebar.header('Filters')
    owner = st.sidebar.text_input("Owner")
    numBun = st.sidebar.text_input("Number of Bundles")
    price = st.sidebar.slider(label ='Current Price - (ETH)', min_value= 0.0, max_value= 100.0, step=0.01)
    params = {}
    if owner:
        params['owner'] = owner
    if numBun:
        params['limit'] = int(numBun)

    r = requests.get('https://api.opensea.io/api/v1/bundles', params=params)
    price_list=[]
    nowPrice=0.0
    events = r.json()['bundles']
    number =0
    for event in events:
        number= number+1
        for currP in event['sell_orders']:
            currPeth = Web3.fromWei(float(currP['current_price']), unit='ether')
            price_list.append({currP['current_price'] ,currPeth})
            
        if price > currPeth:
            # bundle info
            st.header(f'*** BUNDLE {number} *** | {event["name"]}')
            st.write(event["description"])
            st.write(f'** Current Price {str(currPeth)} ETH')
            # assets info
            for asset in event['assets']:
                st.subheader(asset['name'])
                st.write("number of sales "+str(asset['num_sales']))
                render_img(asset['image_url'])
            st.write("**************************************")

if endpoint == 'Most Expnsive NFT':
    r= requests.get('https://api.opensea.io/wyvern/v1/orders')
    events = r.json()['orders']
    expen=0.0
    nft_obj = {}

    # process to get most expensive NFT
    for event in events:
        price = Web3.fromWei(float(event['current_price']), unit='ether')
        if expen < price:
            expen =price
            nft_obj = event

    # display most expensive NFT info 
    st.subheader(nft_obj['asset']['name'])
    st.write(nft_obj['asset']['description'])
    st.write(render_img(nft_obj['asset']['image_url']))
    st.write("Current Price "+str(expen))
    st.write("Owner Address: "+nft_obj['asset']['owner']['address'])
    # st.write(nft_obj['asset'])

        




