// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract P2PEnergyTrading {

    struct Offer {
        address payable seller;  // Change to address payable
        uint256 energyAmount;    // Energy in kWh
        uint256 price;           // Price in ETH
        bool fulfilled;
    }

    Offer[] public offers;

    event OfferCreated(uint256 offerId, address indexed seller, uint256 energyAmount, uint256 price);
    event OfferFulfilled(uint256 offerId, address indexed buyer, uint256 energyAmount, uint256 price);

    // Create an energy offer
    function createOffer(uint256 _energyAmount, uint256 _price) public {
        offers.push(Offer({
            seller: payable(msg.sender),  // Set msg.sender as payable
            energyAmount: _energyAmount,
            price: _price,
            fulfilled: false
        }));

        emit OfferCreated(offers.length - 1, msg.sender, _energyAmount, _price);
    }

    // Fulfill an energy offer
    function fulfillOffer(uint256 _offerId) public payable {
        Offer storage offer = offers[_offerId];
        require(!offer.fulfilled, "Offer already fulfilled");
        require(msg.value == offer.price, "Incorrect ETH sent");

        offer.seller.transfer(msg.value);  // Transfer ETH to the seller
        offer.fulfilled = true;

        emit OfferFulfilled(_offerId, msg.sender, offer.energyAmount, offer.price);
    }

    // View all offers
    function getOffers() public view returns (Offer[] memory) {
        return offers;
    }
}