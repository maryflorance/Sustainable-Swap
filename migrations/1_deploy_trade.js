const P2PEnergyTrading = artifacts.require("P2PEnergyTrading");

module.exports = function (deployer) {
  // Deploy the Trading contract
  deployer.deploy(P2PEnergyTrading);
};