# Town system
# Add a place to hire characters, an inn to rest and recover HP/TP for money, a Shop to sell items and buy equipment.

# City Options; Tavern, Shop, Trainer
import CharacterSystem
import EquipmentSystem
import DungeonCrawl
import os

cancelterms = ["no","back","cancel","return","quit","n"]

shop_stock = EquipmentSystem.shop_stock

def tavern():

    os.system("cls")

    price = 0
    for n in CharacterSystem.party:
        price += n.level * 10
    price = int(price / len (CharacterSystem.party))
    
    print (f"Party Funds: {CharacterSystem.party_money} // It is currently {DungeonCrawl.hour_names[DungeonCrawl.hour]}\n")
    command = input(f"ONTAM: Are you resting here today? It'll cost you {price}, is that okay? (Y)es or (N)o  ").lower()

    if command in ("y","yes"):
        print ("ONTAM: Then please, come this way to the bedrooms.")
        if CharacterSystem.party_money >= price:
            CharacterSystem.party_money -= price
            for n in CharacterSystem.party:
                n.hp = n.maxhp
                n.tp = n.maxtp
            DungeonCrawl.hour += 2
            print ("Time passed and all characters in party have fully rested!")
            print ("\nONTAM: Thanks for your patronage. Hope to see you soon!")
        else:
            print("\nONTAM: Ah, sorry, you don't have enough money to pay for lodgings here. Maybe sell something at the shop or hunt a few more shades?")
    elif command in cancelterms:
        print ("ONTAM: Very well. Hope to see you soon!")

    input ("Press anything to continue")

    pass

def merchant():
    os.system("cls")

    in_merchant = True

    while in_merchant:

        os.system("cls")
        print (f"Party Funds: {CharacterSystem.party_money} // It is currently {DungeonCrawl.hour_names[DungeonCrawl.hour]}\n")
        command = ""
        command = input(f"MERCHANT: What (C)onsumables are yer buyin'?\nJust (Q)uit when yer' done.  ").lower()

        if command == "":
            pass

        elif command in ("c"):
            list_offer = []
            for n in shop_stock:
                if n.type in ("Healing","Reviving","Rest","Return"):
                    list_offer.append(n)

            if list_offer != []:
                print (f"MERCHANT: What'ryer havin'?")
                for n in list_offer:
                    itemstats = ""
                    itemstats += f"({list_offer.index(n)}) {n.name} // Description: {n.lore}"
                    itemstats += f" // Cost: {n.value*5}"

                    print (itemstats)

                try:
                    item = int(input())
                except ValueError:
                    item = None

                if item in range(0,len(list_offer)):
                    item = list_offer[item]

                    if CharacterSystem.party_money >= item.value:
                        command = input(f"Buy {item.name} for {item.value*5}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.consumables.append(item)
                            CharacterSystem.party_money -= item.value*5

                    else:
                        print ("SYLAS: Ah, you don't have the money for that...")

        elif command in ("s","sell"):
            
            print(f"I'm not looking to buy, mate. 'sides, I can just loot yer' corpses when you die in there. \n")
            
            pass

        elif command in ("q"):
            in_merchant = False

        pass

def shop():
    os.system("cls")

    inshop = True

    while inshop:

        os.system("cls")
        print (f"Party Funds: {CharacterSystem.party_money} // It is currently {DungeonCrawl.hour_names[DungeonCrawl.hour]}\n")
        command = ""
        command = input(f"SYLAS: Are you shopping for (C)onsumables, or (W)eapons, (A)rmor, (Ac)cessories, or are you (S)elling?\nIf you're done, feel free to (Q)uit my shop.  ").lower()

        if command == "":
            pass

        elif command in ("c"):
            list_offer = []
            for n in shop_stock:
                if n.type in ("Healing","Reviving","Rest","Return"):
                    list_offer.append(n)

            if list_offer != []:
                print (f"SYLAS: What are you buying?")
                for n in list_offer:
                    itemstats = ""
                    itemstats += f"({list_offer.index(n)}) {n.name} // Description: {n.lore}"
                    itemstats += f" // Cost: {n.value}"

                    print (itemstats)

                try:
                    item = int(input())
                except ValueError:
                    item = None

                if item in range(0,len(list_offer)):
                    item = list_offer[item]

                    if CharacterSystem.party_money >= item.value:
                        command = input(f"Buy {item.name} for {item.value}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.consumables.append(item)
                            CharacterSystem.party_money -= item.value

                    else:
                        print ("SYLAS: Ah, you don't have the money for that...")

        elif command in ("w"):
            list_weapon = []
            for n in shop_stock:
                if n.type == "Weapon":
                    list_weapon.append(n)

            if list_weapon != []:
                print (f"SYLAS: What Weapon are you buying?")
                for n in list_weapon:
                    weaponstat = ""
                    weaponstat += f"({list_weapon.index(n)}) {n.name} // STR: {n.str} (DMG: {n.dmg})"
                    if n.tec != 0:
                        weaponstat += f" / TEC: {n.tec}"
                    if n.vit != 0:
                        weaponstat += f" / VIT: {n.vit}"
                    if n.agi != 0:
                        weaponstat += f" / AGI: {n.agi}"
                    if n.lck != 0:
                        weaponstat += f" / LCK: {n.lck}"
                    if n.weak != None:
                        weaponstat += f" / WEAK: {str(n.weak)}"
                    if n.resist != None:
                        weaponstat += f" / RESIST: {str(n.resist)}"
                    weaponstat += f" // Cost: {n.value}\n Description: {n.lore}"

                    print (weaponstat)

                try:
                    wpn = int(input())
                except ValueError:
                    wpn = None

                if wpn in range(0,len(list_weapon)):
                    wpn = list_weapon[wpn]

                    if CharacterSystem.party_money >= wpn.value:
                        command = input(f"Buy {wpn.name} for {wpn.value}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.inventory.append(wpn)
                            CharacterSystem.party_money -= wpn.value

                    else:
                        print ("SYLAS: Ah, you don't have the money for that...")

                
            pass

        elif command in ("a"):
            list_offer = []
            for n in shop_stock:
                if n.type == "Armor":
                    list_offer.append(n)

            if list_offer != []:
                print (f"SYLAS: What Armor are you buying?")
                for n in list_offer:
                    itemstats = ""
                    itemstats += f"({list_offer.index(n)}) {n.name} //"
                    if n.str != 0 or n.dmg != 0:
                       itemstats += f" / STR: {n.str} (DMG: {n.dmg})"
                    if n.tec != 0:
                        itemstats += f" / TEC: {n.tec}"
                    if n.vit != 0:
                        itemstats += f" / VIT: {n.vit}"
                    if n.agi != 0:
                        itemstats += f" / AGI: {n.agi}"
                    if n.lck != 0:
                        itemstats += f" / LCK: {n.lck}"
                    if n.weak != None:
                        itemstats += f" / WEAK: {str(n.weak)}"
                    if n.resist != None:
                        itemstats += f" / RESIST: {str(n.resist)}"
                    itemstats += f" // Cost: {n.value}\n Description: {n.lore}"

                    print (itemstats)

                try:
                    item = int(input())
                except ValueError:
                    item = None

                if item in range(0,len(list_offer)):
                    item = list_offer[item]

                    if CharacterSystem.party_money >= item.value:
                        command = input(f"Buy {item.name} for {item.value}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.inventory.append(item)
                            CharacterSystem.party_money -= item.value

                    else:
                        print ("SYLAS: Ah, you don't have the money for that...")

        elif command in ("ac"):
            list_offer = []
            for n in shop_stock:
                if n.type == "Accessory":
                    list_offer.append(n)

            if list_offer != []:
                print (f"SYLAS: What Accessory are you buying?")
                for n in list_offer:
                    itemstats = ""
                    itemstats += f"({list_offer.index(n)}) {n.name} //"
                    if n.str != 0 or n.dmg != 0:
                       itemstats += f" / STR: {n.str} (DMG: {n.dmg})"
                    if n.tec != 0:
                        itemstats += f" / TEC: {n.tec}"
                    if n.vit != 0:
                        itemstats += f" / VIT: {n.vit}"
                    if n.agi != 0:
                        itemstats += f" / AGI: {n.agi}"
                    if n.lck != 0:
                        itemstats += f" / LCK: {n.lck}"
                    if n.weak != None:
                        itemstats += f" / WEAK: {str(n.weak)}"
                    if n.resist != None:
                        itemstats += f" / RESIST: {str(n.resist)}"
                    itemstats += f" // Cost: {n.value}\n Description: {n.lore}"

                    print (itemstats)

                try:
                    item = int(input())
                except ValueError:
                    item = None

                if item in range(0,len(list_offer)):
                    item = list_offer[item]

                    if CharacterSystem.party_money >= item.value:
                        command = input(f"Buy {item.name} for {item.value}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.inventory.append(item)
                            CharacterSystem.party_money -= item.value

                    else:
                        print ("SYLAS: Ah, you don't have the money for that...")

        elif command in ("s"):
            
            choice = input("Are you selling (E)quipment or (C)onsumables?").lower()

            if choice in ("e"):
                
                list_equip = []
                for n in EquipmentSystem.inventory:
                    if n.type == "Weapon" or n.type == "Armor" or n.type == "Accessory":
                        list_equip.append(n)

                if list_equip != []:
                    print (f"SYLAS: What Weapon are you buying?")
                    for n in list_equip:
                        eqpstat = ""
                        eqpstat += f"({list_equip.index(n)}) {n.name} // STR: {n.str} (DMG: {n.dmg})"
                        if n.tec != 0:
                            eqpstat += f" / TEC: {n.tec}"
                        if n.vit != 0:
                            eqpstat += f" / VIT: {n.vit}"
                        if n.agi != 0:
                            eqpstat += f" / AGI: {n.agi}"
                        if n.lck != 0:
                            eqpstat += f" / LCK: {n.lck}"
                        if n.weak != None:
                            eqpstat += f" / WEAK: {str(n.weak)}"
                        if n.resist != None:
                            eqpstat += f" / RESIST: {str(n.resist)}"
                        eqpstat += f" // Cost: {n.value}" #\n Description: {n.lore}

                        print (eqpstat)

                    try:
                        eqp = int(input())
                    except ValueError:
                        eqp = None

                    if eqp in range(0,len(list_equip)):
                        eqp = list_equip[eqp]

                        command = input(f"Sell {eqp.name} for {eqp.value//2}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.inventory.remove(eqp)
                            CharacterSystem.party_money += eqp.value//2
                
                pass

            elif choice in ("c"):
                
                list_offer = []
                for n in EquipmentSystem.consumables:
                    if n.type in ("Healing","Reviving","Rest","Return"):
                        list_offer.append(n)

                if list_offer != []:
                    print (f"SYLAS: What are you selling?")
                    for n in list_offer:
                        itemstats = ""
                        itemstats += f"({list_offer.index(n)}) {n.name} // Description: {n.lore}"
                        itemstats += f" // Cost: {n.value}"

                        print (itemstats)

                    try:
                        item = int(input())
                    except ValueError:
                        item = None

                    if item in range(0,len(list_offer)):
                        item = list_offer[item]

                        command = input(f"Sell {item.name} for {item.value//2}? Y/N  ").lower()

                        if command in ("y"):
                            print ("SYLAS: Thanks for the purchase!")
                            EquipmentSystem.consumables.remove(item)
                            CharacterSystem.party_money += item.value//2

                pass
            
            pass

        elif command in ("q"):
            inshop = False

        pass

def trainer():
    
    inTrainer = True

    while inTrainer:

        os.system("cls")
        print (f"Party Funds: {CharacterSystem.party_money} // It is currently {DungeonCrawl.hour_names[DungeonCrawl.hour]}\n")
        command = input("CHROMDUR: Welcome to the Training Grounds. Are you here to (R)ecruit new vagranteers, or (M)anage your group?\nYou can train Perks there too.\nYou can simply (Q)uit when you're done.  ").lower()

        if command == "":
            pass

        elif command in ("r"):
            
            choice = input (f"CHROMDUR: I can put in the word to find new vagranteers. It'll be 10 Cr to find someone. How does that sounds? (Y/N)  ")

            if choice in ("y") and CharacterSystem.party_money >= 10:
                print ("CHROMDUR: All right, just a moment.")
                input ("Press anything to continue.")
                
                if len(CharacterSystem.party)>= 20:
                    print ("CHROMDUR: Unfortunately, your roster is full. Please dismiss someone before trying to recruit new Vagranteers.")

                else:
                    vagranteer = CharacterSystem.createCharacter()

                if vagranteer != None:
                    CharacterSystem.party_money -= 10
                    print ("CHROMDUR: The new vagranteer is ready to join your group.")


            elif CharacterSystem.party_money <10:
                print ("CHROMDUR: I can't send word for new vagranteers without money.\n")

            elif choice in ("n"):
                print ("CHROMDUR: Well then.")
            
            pass

        elif command in ("m"):
            CharacterSystem.checkRoster()
            pass

        elif command in ("q"):
            inTrainer = False

def runTown():
    running_town = True

    while running_town:
        os.system("cls")
        print (f"Party Funds: {CharacterSystem.party_money} // It is currently {DungeonCrawl.hour_names[DungeonCrawl.hour]}\n")
        command = input(f"Welcome to Tarmouth. What would you like do to?\n (R)est at the Tavern, visit the (S)hop, the (T)rainer, or return to the (D)ungeon?\n You can also (O)pen the Party Menu.  ").lower()

        if command == "":
            pass

        elif command in ("r","rest"):
            tavern()
        elif command in ("s","shop"):
            shop()
        elif command in ("t","trainer"):
            trainer()

        elif command in ("o"):
            EquipmentSystem.runEquipment()

        elif command in ("d","dungeon"):
            running_town = False
            os.system('cls')
            input ("Travelling to the Dungeon. Press anything to continue.")
            from DungeonCrawl import exploreDungeon
            exploreDungeon()


## TESTING
# runTown()

##