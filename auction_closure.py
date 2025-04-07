import socket

from auction_update_server import listed_items, client_bids
from server import registered_clients # Why it's not working???


def getHighestBid(itemName):
    # Retrieve the highest bid from the dictionary as well as all the info
    if itemName in listed_items and client_bids[itemName]:
        highestBid = max(client_bids[itemName], key = client_bids[1])
        return highestBid
    return None # if no bids were placed


def notifyActionClosure(itemName, RQ):
    highestBid = getHihestBid(itemName)

    if highestBid is not None:
        buyerName, finalPrice = highestBid
        winnerMsg = f"WINNER {RQ} {itemName} {finalPrice} {listed_items[2]}"
        selletMsg = f"SOLD {RQ} {itemName} {listed_items[3]}"
        send_tcp_message(buyerName, winnerMsg)
        send_tcp_message(seller_name, selletMsg)

    else:
        non_offer_msg = f"NON_OFFER {request_number} {item_name}"
        send_tcp_message(seller_name, non_offer_msg)
