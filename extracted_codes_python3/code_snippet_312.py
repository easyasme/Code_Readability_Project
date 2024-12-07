import requests
import re
import json
import TAX_RETURN
import os

#fetching data directly from file
def fetch_finn_data():
    json_file_path = 'data/BMW_SEARCH.json'
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("Error: The JSON file was not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

#fetching from olx (several pages of JSON)
def fetch_olx_data(max_pages=47):
    olx_url = 'https://olx.ba/api/search'
    params = {
            'attr': '3228323031302d393939393939293a372844697a656c29',
            'attr_encoded': '1',
            'category_id': '18',
            'brand': '11',
            'models': '0',
            'brands': '11',
            'page': 1,
            'per_page': 175
        }
    
    olx_data = []
    
    while params['page'] <= max_pages:
        try:
            response = requests.get(olx_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            #car entries are under data in the olx api
            page_data = data.get('data', [])
            olx_data.extend(page_data)
            params['page'] += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from OLX API: {e}")
            break
        except ValueError as e:
            print(f"Error parsing JSON from OLX API: {e}")
            break
    
    return olx_data

models = {
    "1 Series 116i", "1 Series 118i", "1 Series 120i", "1 Series 125i", "1 Series M135i", 
    "2 Series 218i", "2 Series 220i", "2 Series 228i", "2 Series 230i", "2 Series M235i", 
    "3 Series 316i", "3 Series 318i", "3 Series 320i", "3 Series 330i", "3 Series 340i", "3 Series M3", 
    "4 Series 420i", "4 Series 430i", "4 Series 440i", "4 Series M4", 
    "5 Series 520i", "5 Series 530i", "5 Series 540i", "5 Series M5", 
    "6 Series 640i", "6 Series 650i", "6 Series M6", 
    "7 Series 730i", "7 Series 740i", "7 Series 750i", "7 Series 760i", 
    "8 Series 840i", "8 Series M850i", "8 Series M8", 
    "X1 sDrive18i", "X1 sDrive20i", "X1 xDrive20i", "X1 xDrive25i", 
    "X2 sDrive18i", "X2 sDrive20i", "X2 xDrive20i", "X2 xDrive25i", "X2 M35i", 
    "X3 sDrive20i", "X3 xDrive20i", "X3 xDrive30i", "X3 M40i", "X3 M", 
    "X4 xDrive20i", "X4 xDrive30i", "X4 M40i", "X4 M", 
    "X5 xDrive30i", "X5 xDrive40i", "X5 xDrive50i", "X5 M", 
    "X6 xDrive30i", "X6 xDrive40i", "X6 xDrive50i", "X6 M", 
    "X7 xDrive40i", "X7 xDrive50i", "X7 M50i", 
    "Z4 sDrive20i", "Z4 sDrive30i", "Z4 M40i", 
    "i3 94 Ah", "i3 120 Ah", 
    "i4 eDrive40", "i4 M50", 
    "i8", 
    "iX3", 
    "iX xDrive40", "iX xDrive50", 
    "i7 xDrive60", "i7 M70", 
    "i5 eDrive40", "i5 M60", 
    "iX1 xDrive30", 
    "2 Series Active Tourer 218i", "2 Series Active Tourer 220i", "2 Series Active Tourer 225i", "2 Series Gran Tourer 218i", "2 Series Gran Tourer 220i", "2 Series Gran Tourer 225i"
}
def normalize_name(name):
    name = re.sub(r'(?i)\b(4matic|masse|utstyr|eu|ny|kontroll|service|oljeskift|cdi|tdi|dci|mpi|gdi|tdci|tfsi|tsi|td|cd|thp|blueefficiency|novi|model|triptonic|stanje|top|gtd|god|2008|2009|2010|2011|2012|2013|2014|2015|2016|2017|2018|2019|2020|2021|2022|2023|2024|quattro|facelift|mercedes|benz|motion|tek|uvezana|uvoz|limited|edition|luxury|premium|base|sport|advanced|line|drive|paket|paket|edition|automatic|manual|diesel|sedan|hatchback|coupe|convertible|wagon|suv|compact|electric|hybrid|awd|fwd|rwd|l|xl|xxl|plus|pro|classic|comfort|executive|elegance|exclusive|design|performance|dynamic|style|active|emotion|innovation|limited|classic|supreme|highline|comfortline|trendline|elite|cosmo|prestige|cross|drive|line|connect|base|executive|essential|value|p|performance|track|trail|sportback|touring|all4|countryman|clubman|john|cooper|works|crosstrek|outback|forester|brz|wrx|sti|limited|touring|premium|black|edition|signature|select|preferred|standard|touring|cx|forester|sport|special|series|2dr|4dr|5dr|7dr|12dr|15dr|21dr|23dr|32dr|40dr|45dr|5seater|7seater|compact|mpv|minivan|roadster|crossover|gtline|cabrio|cabriolet|estate|estate|saloon|super|base|lifestyle|lux|xdrive|xdrive20d|d|rline|spaceback|vision|entry|entryline|life|light|ultimate|evo|ambiente|sve|sve|emotion|dynamic|action|line|tek|tronic|select|stand|entry|vtx|ls|dl|sx|hx|xe|xt|kt|xt|tm|hk|tl|luxe|intense|shine|pure|prestige|legend|premium|premium|supreme|gt|sline|audi|bmw|volkswagen|vw|peugeot|opel|mazda|mitsubishi|toyota|honda|kia|hyundai|nissan|seat|skoda|volvo|renault|suzuki|mini|subaru|chrysler|dodge|jeep|ram|chevrolet|ford|gmc|lincoln|buick|cadillac|lexus|infiniti|acura|jaguar|land|rover|alfa|romeo|fiat|maserati|ferrari|lamborghini|porsche|bugatti|aston|martin|bentley|rolls|royce|polestar|tesla|lucid|rivian|bollinger|canoo|byton|faraday|future|karma|nikola|nobe|regen|gordon|murray|automotive|hendrickson|hewes|hill|hino|hisun|honda|husqvarna|indian|infiniti|ironhorse|isuzu|jaguar|jeep|jensen|john|deere|karma|kia|lancia|land|rover|lincoln|lotus|lucid|mclaren|maserati|mazda|mercedes|mg|mini|mitsubishi|morgan|nimble|nissan|peugeot|pontiac|porsche|ram|renault|rolls|royce|saab|saturn|scion|seat|skoda|smart|ssangyong|subaru|suzuki|tesla|toyota|triumph|vauxhall|volkswagen|volvo|smart|uaz|ura|vespa|vortex|volkswagen|westfield|yamaha|yellow|zastava|zaz|zins|zundapp|zundapp|)\b', '', name)

    name = re.sub(r'\W+', ' ', name)
    name = re.sub(r'\b\d+hk\b', '', name, flags=re.IGNORECASE)
    return ' '.join(name.lower().split())

def match_car(finn_car, olx_car):
    finn_name = set(normalize_name(finn_car.get('heading', '')).split())
    olx_name = set(normalize_name(olx_car.get('title', '')).split())

    # Check for any common words, including model names
    common_words = finn_name.issubset(olx_name) or olx_name.issubset(finn_name)
    model_match = bool((finn_name & olx_name) & models)

    if common_words or model_match:
        finn_year = finn_car.get('year', 0)
        olx_year = olx_car.get('special_labels', [])
        olx_year = next((int(label.get('value')) for label in olx_year if label.get('label') == 'Godište'), 0)
        return abs(finn_year - olx_year) <= 0
    return False

def pair_car_data(finn_data, olx_data):
    car_pairs = {}

    if not isinstance(finn_data, list) or not isinstance(olx_data, list):
        print("Error: Expected list format for API data")
        return car_pairs

    for car in finn_data:
        car_name = car.get('heading', '')
        car_price = car.get('price', {}).get('amount')
        car_link = car.get('canonical_url', '')
        car_year = car.get('year', 0)
        car_image_url = car.get('image', {}).get('url', '')
        car_regno = car.get('regno', '')
        car_mileage = car.get('mileage', '')
        if car_name and car_price is not None:
            car_pairs[car_name] = {
                'finn_price': car_price,
                'olx_prices': [],
                'olx_ids': [],
                'olx_names': [],
                'olx_mileages':[],
                'olx_images':[],
                'year': car_year,
                'link': car_link,
                'image_url': car_image_url,
                'regno': car_regno,
                'mileage' : car_mileage,
            }

    for car in olx_data:
        if isinstance(car, dict):
            olx_name = car.get('title', '')
            olx_price = car.get('price')
            olx_id = car.get('id')
            olx_image = car.get('image')
            olx_mileage = next((label["value"] for label in car["special_labels"] if label["label"] == "Kilometraža"), None)

            if olx_name and olx_price is not None:
                for finn_name, data in car_pairs.items():
                    if match_car({'heading': finn_name, 'year': data['year']}, car):
                        car_pairs[finn_name]['olx_prices'].append(olx_price)
                        car_pairs[finn_name]['olx_ids'].append(olx_id)
                        car_pairs[finn_name]['olx_names'].append(olx_name)
                        car_pairs[finn_name]['olx_images'].append(olx_image)
                        car_pairs[finn_name]['olx_mileages'].append(olx_mileage)

    return car_pairs

finn_data = fetch_finn_data()
olx_data = fetch_olx_data()

paired_data = pair_car_data(finn_data, olx_data)

olx_finn_output = []
for car_name, data in paired_data.items():
    olx_prices = data['olx_prices']
    if olx_prices:
        finn_price = data['finn_price']
        year = data['year']
        link = data['link']
        image_url = data['image_url']
        regno = data['regno']
        olx_ids = data['olx_ids']
        mileage = data['mileage']
        olx_names = data['olx_names']
        olx_images = data['olx_images']
        olx_mileages = data['olx_mileages']

        car_entry = {
            'car_name': car_name,
            'year': year,
            'finn_price': finn_price,
            'finn_link': link,
            'image_url': image_url,
            'regno': regno,
            'mileage' : mileage,
            'olx_prices': olx_prices,
            'olx_ids' : olx_ids,
            'olx_names' : olx_names,
            'olx_images' : olx_images,
            'olx_mileages' : olx_mileages,
        }
        olx_finn_output.append(car_entry)

for car in olx_finn_output:
    if car['year'] >= 2015 and car.get('regno'):
            registration_number = car['regno'] 
            tax_return = TAX_RETURN.fetch_tax_return(registration_number)
            car['tax_return'] = tax_return
    
    else:
        car['tax_return'] = None

current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')
os.makedirs(data_dir, exist_ok=True)

print("length of list: ", len(olx_finn_output))
with open(os.path.join(data_dir, '=OLX_BMW.json'), 'w', encoding='utf-8') as json_file:
	if olx_finn_output:
	    json.dump(olx_finn_output, json_file, ensure_ascii=False, indent=4)


import datetime
with open('__LOG__.txt', 'a', encoding='utf-8') as file:
    file.write(f"{datetime.datetime.now()} - =OLX_BMW.py ran\n")

