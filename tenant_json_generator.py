import json
import csv
import re
import requests

VANITY_REGEX="^([\w-]+)\.on\.symphony\.com"
REGION_REGEX="^(prod|qa|uat|dev)"

ticket = "ESS-24981"

# First Tenant ID to use
tenantId = 75040
environment = "prod"
region = "us"

def checkTenantIDFree(tenantId: int) -> bool:
  return (requests.get(URL_UAT + "/v1/tenants/" + str(tenantId)).status_code == 404)

def chooseDeployment(region: str) -> str:
  match region:
    case "us":
      return "suse4"
    case "eu":
      return "seuw1"
    case "asia":
      return "azse1"

def generateProperties(companyName:str, vanityName:str, region:str) -> dict: 
  properties = {}
  properties["state"] = "ACTIVE"
  properties["kmIsInCloud"] = True
  properties["companyName"] = companyName
  properties["vanityName"] = vanityName
  properties["allowedUserEmailDomains"] = []
  properties["mobileAuthenticationDomains"] = []
  properties["whitelist"] = []
  properties["application"] = {"STApplications": [], "MTApplications": []}
  properties["deploymentUnitId"] = chooseDeployment(region)

  return properties

def generateInitialisationProperties() -> dict:
  initProperties = {}
  initProperties["env"] = environment
  initProperties["region"] = region
  initProperties["admin"] = {
    "email": "bizops.integration@symphony.com",
    "firstName": "BizOps",
    "lastName": "Integration"
  }
  initProperties["eula"] = "business"

  return initProperties

def validateTenantData(vanityName:str, environment:str):
  if(not re.match(VANITY_REGEX, vanityName)):
    print("Vanity name invalid")
    exit(1)
  if(not re.match(REGION_REGEX, environment)):
    print("Environment invalid, possible are: prod uat qa dev")
    exit(1)
  
def generateTenant(tenantId:int, companyName:str, vanityName:str, environment:str, region:str) -> dict:
    # First validate passed fields
    validateTenantData(vanityName, environment)

    tenant = {}
    tenant["properties"] = generateProperties(companyName, vanityName, region)
    tenant["initialisationProperties"] = generateInitialisationProperties()
    tenant["tenantId"] = tenantId

    return tenant

with open('tenants.csv', newline='') as csvfile:
  tenantReader = csv.reader(csvfile, delimiter=';')
  
  for tenantData in tenantReader:
    if checkTenantIDFree(tenantId):
      with open(ticket+"-"+str(tenantId)+".json", "w") as outfile:
        outfile.write(json.dumps(generateTenant(tenantId, tenantData[0], tenantData[1], environment, region), indent=2))
      tenantId += 1
    else:
      print("Tenant ID " + str(tenantId) + " is already in use, skip it")
