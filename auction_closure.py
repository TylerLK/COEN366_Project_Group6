import socket
from auction_update_server import listed_items, client_bids

def getHighestBid(itemName):
    if itemName in listed_items and client_bids.get(itemName):
        return max(client_bids[itemName].items(), key=lambda x: x[1])
    return None


def notifyWinner(buyerName, itemName, RQ):
    highestBid = getHighestBid(itemName)
    if highestBid:
        buyerName, finalPrice = highestBid
        seller_name = listed_items[itemName]["seller"]
        winnerMsg = f"WINNER {RQ} {itemName} {finalPrice} {seller_name}"
        return winnerMsg


def notifySeller(sellerName, itemName, RQ):
    highestBid = getHighestBid(itemName)
    seller_name = listed_items[itemName]["seller"]

    if highestBid:
        buyerName, finalPrice = highestBid
        sellerMsg = f"SOLD {RQ} {itemName} {finalPrice} {buyerName}"
        return sellerMsg
    else:
        non_offer_msg = f"NON_OFFER {RQ} {itemName}"
        return non_offer_msg