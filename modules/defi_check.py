import logging
import json
import requests
from notifypy import Notify
import os
import errno
import time
from modules.defi_check_dir.amen_gui import _ as AmenGui
import threading

# Taken from https://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')

def ConvertToCRO(number):
	return round(number/100000000, 4)

def ConvertCROtoUSD(croAmount):
	response = json.loads(requests.get("https://api.crypto.com/v2/public/get-ticker?instrument_name=CRO_USDT").text)
	croPrice = response['result']['data']['b']
	return croPrice*croAmount

def SendNotification(title, message):
	"""	
	notification = Notify()
	notification.application_name = "DeFi CRO"
	notification.title = title
	notification.message = message
	notification.icon = "modules/icons/crypto.png"
	notification.send(block=True)
	"""

	logging.info("Trying to send notification with title '%s' and with message '%s'", title, message)
	x = threading.Thread(target=AmenGui, args=(title,message,"Understood"))
	x.start()

def CreateConfigFile(path):
	try:
		with safe_open_w(path) as f:
			f.write(json.dumps({
				"CROaccountId":"cro1nlrmj80w45qtfj8rddqq0mjvktq7yhfk93xqrz", # FIXME: Account ID shouldn't be hardcoded.
				"CROvalidatorId":"crocncl1xkavscemvn45mva83q0zhpv0lgpnwzfs57j5yc", # FIXME: Validator ID shouldn't be hardcoded.
				}))
			return
	except Exception as err:
		logging.error("Couldn't create new config file ('%s'). Error: %s", path, err)
		logging.info("Exiting...")
		exit()

def GetWalletInfo(walletAddress):
	walletResponse = requests.get("https://crypto.org/explorer/api/v1/accounts/" + walletAddress)
	walletNew = json.loads(walletResponse.text)

	unusedBalance = ConvertToCRO(float(walletNew["result"]["balance"][0]["amount"]))
	totalRewards = ConvertToCRO(float(walletNew["result"]["totalRewards"][0]["amount"]))
	totalBondBalance = ConvertToCRO(float(walletNew["result"]["bondedBalance"][0]["amount"]))
	totalBalance = ConvertToCRO(float(walletNew["result"]["totalBalance"][0]["amount"]))

	return {
		"unusedBalance":unusedBalance,
		"totalRewards":totalRewards,
		"totalBondBalance":totalBondBalance,
		"totalBalance":totalBalance
		}

def GetValidatorInfo(validatorAddress):
	validatorResponse = requests.get("https://crypto.org/explorer/api/v1/validators/" + validatorAddress) 
	validatorNew = json.loads(validatorResponse.text)

	return {
		"jailed": str(validatorNew["result"]["jailed"]),
		"bondedStatus": validatorNew["result"]["status"],
		"commission": float(validatorNew["result"]["commissionRate"])*100
	}

def LoadConfig(configPath):
	validatorAddress = ""
	walletAddress = ""

	if os.path.isfile(configPath):
		with open(configPath) as f:
			try:
				settings = json.load(f)
			except json.decoder.JSONDecodeError as err: # Empty config file
				logging.warning("Caught JSONDecodeError (%s). Empty config file found in '%s'.", err, configPath)
				#logging.info("Creating new config file in '%s'.", configPath)
				#CreateConfigFile(configPath) # TODO: Can't read config file after creating it.
				logging.info("Exiting...")
				exit()
			try:
				walletAddress = settings["CROaccountId"]
				validatorAddress = settings["CROvalidatorId"]
			except KeyError as err:
				logging.error("Corrupt config file ('%s'). Missing key: %s.", configPath, err)
				logging.info("Exiting...")
				exit()
			logging.info("Succesfully loaded settings from config file ('%s').", configPath)
	else:
		logging.info("Creating new config file in '%s'.", configPath)
		logging.info("No config file found in '%s'.", configPath)
		CreateConfigFile(configPath)

	
	return [walletAddress, validatorAddress]

def LoadWalletInfo(walletPath, walletAddress):
	if os.path.isfile(walletPath):
		with open(walletPath) as f:
			walletInfo = json.load(f)
			return walletInfo
	else:
		# If there is no wallet info saved, then return the currently
		# queried one, so less code is written and there won't be
		# any changes in infos anyways.
		walletInfo = GetWalletInfo(walletAddress)
		with safe_open_w(walletPath) as f:
			f.write(json.dumps(walletInfo))
		return walletInfo
		

def _():
	walletJsonPath = "modules/defi_check_dir/wallet.json"
	configPath = "modules/defi_check_dir/config.json"
	walletAddress, validatorAddress = LoadConfig(configPath)

	while True:
		logging.info("Checking wallet info.")
		oldWalletInfo = LoadWalletInfo(walletJsonPath, walletAddress)
		newWalletInfo = GetWalletInfo(walletAddress)

		# TODO: Compare old wallet info with newWalletInfo fully.
		oldTotalRewardsCro = oldWalletInfo["totalRewards"]
		newTotalRewardsCro = newWalletInfo["totalRewards"]
		newRewards = newTotalRewardsCro - oldTotalRewardsCro
		
		# In requests it rounds to 4 decimal points. E.g. 0.1035. See: wallet.json
		if newRewards < 0.0001: 
			logging.info("No new rewards have been issued.")
			newRewards = 0
		
		if newRewards:
			newRewards = round(newRewards, 6)
			newRewardsUsd = round(ConvertCROtoUSD(newRewards), 2)
			SendNotification("New Rewards!", "Amount: %s CRO (%s USD)" % (newRewards, newRewardsUsd))

		with safe_open_w(walletJsonPath) as f:
			f.write(json.dumps(newWalletInfo))
		
		logging.info("Waiting 300 seconds until checking account again...")
		time.sleep(300) 
		# TODO: Only show it once daily
		# TODO: Make a GUI for it to check all info.


		#validatorInfo = GetValidatorInfo(validatorAddress)

if __name__ == '__main__':
	_()
	