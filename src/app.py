from flask import Flask, render_template, request, jsonify
from web3 import Web3

# Initialize Flask app
app = Flask(__name__)

# Connect to Ethereum Blockchain (use local Ganache or QuickNode)
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Replace with your blockchain provider

# Load the smart contract ABI and contract address
contract_address = "0x9487B885fDcab573Fae0a621cAc9BcbEebf92FFe"  # Replace with your contract address
abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint256", "name": "offerId", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "seller", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "energyAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "price", "type": "uint256"}
        ],
        "name": "OfferCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint256", "name": "offerId", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "buyer", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "energyAmount", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "price", "type": "uint256"}
        ],
        "name": "OfferFulfilled",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "offers",
        "outputs": [
            {"internalType": "address payable", "name": "seller", "type": "address"},
            {"internalType": "uint256", "name": "energyAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "price", "type": "uint256"},
            {"internalType": "bool", "name": "fulfilled", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_energyAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "_price", "type": "uint256"}
        ],
        "name": "createOffer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "_offerId", "type": "uint256"}],
        "name": "fulfillOffer",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function",
        "payable": True
    },
    {
        "inputs": [],
        "name": "getOffers",
        "outputs": [
            {
                "components": [
                    {"internalType": "address payable", "name": "seller", "type": "address"},
                    {"internalType": "uint256", "name": "energyAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "bool", "name": "fulfilled", "type": "bool"}
                ],
                "internalType": "struct P2PEnergyTrading.Offer[]",
                "name": "",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "view",
        "type": "function",
        "constant": True
    }
]

contract = web3.eth.contract(address=contract_address, abi=abi)

# Your account details (for testing purposes only)
ACCOUNT_ADDRESS = "0xf33b979a79e9Bc058d51603cE82fBAEa02d27fc1"
PRIVATE_KEY = "0x3488b75cfd37c7970949ea54ba893667aefcd5a91079ff1ecb84da0133cdebac"

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/offers', methods=['GET'])
def get_offers():
    offers = contract.functions.getOffers().call()
    return jsonify(offers)

@app.route('/create_offer', methods=['POST'])
def create_offer():
    # Use the hard-coded private key for the seller
    seller = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    energy_amount = int(request.form['energy_amount'])
    price = web3.toWei(request.form['price'], 'ether')

    txn = contract.functions.createOffer(energy_amount, price).buildTransaction({
        'from': seller,
        'nonce': web3.eth.getTransactionCount(seller),
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei')
    })

    signed_txn = web3.eth.account.signTransaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify({"status": "Offer created", "transaction": tx_hash.hex()})

@app.route('/fulfill_offer/<int:offer_id>', methods=['POST'])
def fulfill_offer(offer_id):
    buyer = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address
    offer_price = contract.functions.getOffers().call()[offer_id][2]

    txn = contract.functions.fulfillOffer(offer_id).buildTransaction({
        'from': buyer,
        'value': offer_price,
        'nonce': web3.eth.getTransactionCount(buyer),
        'gas': 2000000,
        'gasPrice': web3.toWei('20', 'gwei')
    })

    signed_txn = web3.eth.account.signTransaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    return jsonify({"status": "Offer fulfilled", "transaction": tx_hash.hex()})

if __name__ == '__main__':
    app.run(debug=True)