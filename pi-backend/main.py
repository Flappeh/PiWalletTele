from modules.pi_python import PiNetwork

api_key="djsqloslqab3kcrgihbiiy7q1y8lybttxzzaqcksythnysvffcbleprsf5qyv9or"
wallet_private_seed = "SCCYUCLGE7TPEVJYVWRIY7AXF2T6XPNAFCJGJG46ABGUZG2UXYRHOVHB"

pi = PiNetwork()
pi.initialize(api_key=api_key,wallet_private_key=wallet_private_seed,network="Pi Testnet")
data = pi.get_balance()
print(data)