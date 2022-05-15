import json
import random

def write(dictionary):
    with open("quiz_data/questions.json", "r", encoding="utf8") as a:
        local = json.load(a)

    with open("quiz_data/questions.json", "w") as f:
        json.dump({**local, **dictionary}, f, indent=2)
        print(dictionary, "\n\nDone!")

def script1():
    with open("quiz_data/questions.txt", "r") as f:
        text = f.readlines()


    data = {}

    temp = {"questions": [], "answers": []}

    start_questions = True
    start_answers = True

    for line in text:
        line = line.replace("\n", "")

        if len(temp["questions"]) == 10 and len(temp["answers"]) == 10:
            for q, a in zip(temp["questions"], temp["answers"]):
                data[q] = a
            temp = {"questions": [], "answers": []}

        if line == "=":
            start_questions = True
            start_answers = False
            continue
        elif line == "-":
            start_answers = True
            start_questions = False
            continue

        if start_questions:
            temp["questions"].append(line.replace("\n", "").replace("10", "1")[4:])

        elif start_answers:
            temp["answers"].append(line.replace("\n", "").replace("10", "1")[4:])

    write(data)

def script2():
    with open("quiz_data/questions2.txt", "r", encoding="utf8") as f:
        text = f.readlines()

    temp = {"questions": [], "answers": []}

    write_answer = False

    for line in text:
        if line == "\n":
            continue

        # line = line.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "")
        if line[1] == ")" or line[2] == ")":
           
            if line[1] == ")":
                line = line[3:]
            if line[2] == ")":
                line = line[4:]

            temp["questions"].append(line.replace("\n", ""))

        if line.startswith("Show Answer"):
            write_answer = True
            continue

        if write_answer:
            temp["answers"].append(line.replace("\n", ""))
            write_answer = False

    data = {}

    for q, a in zip(temp["questions"], temp["answers"]):
        data[q] = {"options": ["", "", a], "answer": a}
    
    write(data)

def script3():
    with open("quiz_data/questions3.txt", "r", encoding="utf8") as f:
        text = f.readlines()

    temp = {"questions": [], "answers": []}

    write_answer = False

    for line in text:
        if line == "\n":
            continue

        # line = line.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "")
        if line.startswith("Q."):
            temp["questions"].append(line[3:].replace("\n", ""))

        if line.startswith("Show Answer"):
            write_answer = True
            continue

        if write_answer:
            temp["answers"].append(line.replace("\n", ""))
            write_answer = False

    data = {}

    for q, a in zip(temp["questions"], temp["answers"]):
        data[q] = {"options": ["", "", a], "answer": a}
    
    write(data)

def script4():
    with open("quiz_data/questions_text/questions4.txt", "r", encoding="utf8") as f:
        text = f.readlines()

    temp = {"questions": [], "answers": []}

    for line in text:
        if line == "\n":
            continue

        if line[1] == "." or line[2] == ".":
           
            if line[1] == ".":
                line = line[len("4. Question: "):]
            if line[2] == ".":
                line = line[len("14. Question: "):]

            temp["questions"].append(line.replace("\n", ""))

        if line.startswith("Answer: "):
            temp["answers"].append(line.replace("\n", "").replace("Answer: ", "")[:-1])
            continue

    data = {}

    for q, a in zip(temp["questions"], temp["answers"]):
        data[q] = {"options": ["", "", a], "answer": a}
    
    write(data)

def script5():
    data = {
        "Which item can't be used to catch fish?": {
            "options": [
            "Bucket",
            "Fishing Rod",
            "Bamboo"
            ],
            "answer": "Bamboo"
        },
        "Which mob cannot eat wheat?": {
            "options": [
            "Sheep",
            "Mooshrooms",
            "Player"
            ],
            "answer": "Player"
        },
        "Who is Minecraft's final boss?": {
            "options": [
            "The Wither",
            "Elder Guardian",
            "Ender Dragon"
            ],
            "answer": "Ender Dragon"
        },
        "Can you use pigs for transportation?": {
            "options": [
            "Nope",
            "Yes, if you give them wheat",
            "Yes, with a saddle"
            ],
            "answer": "Yes, with a saddle"
        },
        "What is the default Minecraft name?": {
            "options": [
            "Mario",
            "Herobrine",
            "Steve"
            ],
            "answer": ""
        },
        "What would happen if you sleep in the Nether?": {
            "options": [
            "Zombie Pigmen will attack you",
            "Your bed will explode",
            "You will see a dream sequence"
            ],
            "answer": "Your bed will explode"
        },
        "What's the best way for zombies to survive the daylight?": {
            "options": [
            "By swimming in water",
            "No, they can't",
            "Find some shades"
            ],
            "answer": "By swimming in water"
        },
        "Is it okay to jump into the water from a high place?": {
            "options": [
            "No, you'll die",
            "No, you'll drown",
            "Yes, if you land in water"
            ],
            "answer": "Yes, if you land in water"
        },
        "Can a bed save you when falling from a high place?": {
            "options": [
            "Yes, if it is too high",
            "No, the bed will break",
            "No, you'll still take damage"
            ],
            "answer": ""
        },
        "Can you dig straight down?": {
            "options": [
            "No, that's against Minecraft rules",
            "Heck yeah! I'm a Minecraft veteran",
            "No, you might fall into lava or get killed by mobs"
            ],
            "answer": "No, you might fall into lava or get killed by mobs"
        },
        "What is the weakness of Enderman?": {
            "options": [
            "Water",
            "Diamond Sword",
            "Lava Bucket"
            ],
            "answer": "Water"
        },
        "What is the crafting recipe for a beacon?": {
            "options": [
            "Nether Star",
            "Blaze Powder",
            "Wood"
            ],
            "answer": "Nether Star"
        },
        "How can you get the raid event?": {
            "options": [
            "By killing an illager captain",
            "By killing a villager",
            "By stealing the wheat"
            ],
            "answer": "By killing an illager captain"
        },
        "What will happen if you throw an egg?": {
            "options": [
            "It might hatch a baby chicken",
            "Nothing",
            "It will break"
            ],
            "answer": "It might hatch a baby chicken"
        },
        "Which of these jobs are not real in Minecraft?": {
            "options": [
            "Unemployed",
            "Medic",
            "Nitwit"
            ],
            "answer": "Medic"
        },
        "Can you make a Nether Portal in any size and shape?": {
            "options": [
            "As long as it's rectangular",
            "Yes, even with a circle",
            "No, it won't do a thing"
            ],
            "answer": "As long as it's rectangular"
        },
        "What food item can you use to make the stairs?": {
            "options": [
            "Watermelon",
            "Beatroot soup",
            "Pumpkin Pie"
            ],
            "answer": "Watermelon"
        },
        "At what height (Y-coordinate) do diamonds appear most?": {
            "options": [
            "Y-12",
            "Y-13",
            "Y-11"
            ],
            "answer": "Y-12"
        },
        "How do you stay invisible from the Enderman?": {
            "options": [
            "Run fast!",
            "Drink Milk",
            "Wear a Carved Pumpkin"
            ],
            "answer": "Wear a Carved Pumpkin"
        },
        "How many items are there in a stack?": {
            "options": [
            "69",
            "420",
            "64"
            ],
            "answer": "64"
        },
        "Which item cannot be used as fuel?": {
            "options": [
            "Boat",
            "Chest",
            "Sapling"
            ],
            "answer": "Boat"
        },
        "What is the piston push limit?": {
            "options": [
            "12",
            "13",
            "11"
            ],
            "answer": "12"
        },
        "Which item is not blast resistant?": {
            "options": [
            "Cobblestone",
            "Anvil",
            "Enchantment Table"
            ],
            "answer": "Cobblestone"
        },
        "How many blocks do players usually travel to get to a Woodland Mansion?": {
            "options": [
            "20,000 blocks",
            "20,001 blocks",
            "500, as long as they have the map"
            ],
            "answer": "20,200 blocks"
        },
        "Which Pickaxe mines the fastest?": {
            "options": [
            "Netherite Pickaxe",
            "Gold Pickaxe",
            "Diamond Pickaxe"
            ],
            "answer": "Gold Pickaxe"
        },
        "Can you find a Creeper spawner?": {
            "options": [
            "No, Creeper spawners don't exist",
            "Yes, if you look hard enough",
            "No, you'll find TNT instead"
            ],
            "answer": "No, Creeper spawners don't exist"
        },
        "Why would you want to keep doors in your inventory while underwater?": {
            "options": [
            "They light up the way",
            "To repel hostile mobs",
            "To breath underwater"
            ],
            "answer": "To breath underwater"
        },
        "Who is the creator of the game? ": {
            "options": [
            "Notch",
            "Mojang",
            "Steve"
            ],
            "answer": "Notch"
        },
        "How do iron golems spawn naturally?": {
            "options": [
            "If the village has 21 doors and 15 villagers",
            "If you kidnap more villagers",
            "When a villager dies"
            ],
            "answer": "If the village has 21 doors and 15 villagers"
        },
        "Which item can you use to make a Nether Portal without mining?": {
            "options": [
            "Bucket of Water",
            "Jack o'Lantern",
            "Fire Charge"
            ],
            "answer": "Bucket of Water"
        },
        }
    write(data)

def script6():
    data = {
        "Which one of these is a hostile mob?":
        {"options": ["Iron Golem", "Snow golem", "Stray"], "answer": "Stray"},
        "How many blocks high is the world in Minecraft?":
        {"options": ["64", "128", "256"], "answer": "128"},
        "Which unbreaking enchantment increased an item's lifetime by 300%?":
        {"options": ["Unbreaking 1", "Unbreaking 3", "Unbreaking 4"], "answer": "Unbreaking 3"},
        "How many hunger chops does a steak replenish?":
        {"options": ["6", "2", "4"], "answer": "4"},
        "How many hunger chops does rabbit stew replenish?":
        {"options": ["8", "10", "6"], "answer": "10"},
        "How many hunger chops does raw mutton replenish?":
        {"options": ["1", "2", "3"], "answer": "2"},
        "Which of these materials is not involved in crafting a powered rail?":
        {"options": ["Silver", "Gold", "Stick"], "answer": "Silver"},
        "Which of these maps includes a floating island where players must survive with limited resources?":
        {"options": ["Skyblocks", "Cube Survival", "Stranded Raft"], "answer": "Skyblocks"},
        "Can combine two damaged fishing rods to create a new fishing rod?":
        {"options": ["Yes", "No", "Yes, in previous versions"], "answer": "Yes"},
        "Can you trun a zombie villager back into a villager?":
        {"options": ["Yes, if you use a golden apple", "Yes, if you get a medic", "No, a dead man stays dead."], "answer": "Yes, if you use a golden apple"},
        "How many hearts does the ender dragon have?":
        {"options": ["100", "50", "200"], "answer": "100"},
        "How tall is a GHAST (not including tentacles)?":
        {"options": ["6 blocks", "4 blocks", "3 blocks"], "answer": "4 blocks"},
        "In which country do they let you play Minecraft in school?":
        {"options": ["Sweden", "United States", "Norway"], "answer": "Sweden"},
        "What is the rarest ore in Minecraft?":
        {"options": ["Diamond", "Emerald", "Nether Gold"], "answer": "Emerald"},
        "How tall is Steve in feet and inches according to the game's scale?":
        {"options": ["5'9″", "6'1″", "5'11”"], "answer": "5'11”"},
        "Daniel Rosenfeld, the German composer responsible for much of Minecraft's music and sound, is better known by what name?":
        {"options": ["RC39P0", "RJD2", "C418"], "answer": "C418"},
        "How many iron ingots do you need to craft an iron sword?":
        {"options": ["2", "4", "8"], "answer": "2"},
        "What are creepers scared of?":
        {"options": ["Cats", "Villagers", "Ocelots"], "answer": "Ocelots"},
        "Which is the only hostile mob in the game unable to deal you damage?":
        {"options": ["Small Slime", "Baby Hoglin", "Small Magma Cube"], "answer": "Small Slime"},
        "What are skeletons immune to?":
        {"options": ["Impailing", "Arrows", "Drowning"], "answer": "Drowning"}}

    write(data)

def script7():
    with open("quiz_data/questions_text/questions5.txt", "r", encoding="utf8") as f:
        text = f.readlines()

    def process_block(lines_list):
        all_options = []; answer = ""; question = ""; target_answer = False
        
        for _ln in lines_list:
            if _ln.startswith("Q "):
                if _ln[3] == ".":
                    question = _ln[5:].replace("\n", ""); continue
                elif _ln[4] == ".":
                    question = _ln[6:].replace("\n", ""); continue
            
            elif (_ln == "\n") or (_ln.startswith("Option:-")) or (_ln.startswith("Enter Your Answer:-")):
                continue

            elif _ln.startswith("Hide Answer"):
                target_answer = True; continue

            if target_answer:
                answer = _ln.replace("\n", ""); target_answer = False; continue

            if _ln != "\n":
                all_options.append(_ln.replace("\n", ""))
        
        if len(all_options) < 3:
            while len(all_options) != 3:
                all_options.append("")
        elif len(all_options) > 3:
            all_options = all_options[:3]
            if answer not in all_options:
                all_options[random.randint(0, 2)] = answer

        return {question.lower().capitalize(): {"options": all_options, "answer": answer}}

    build_block = []
    build = False

    data = {}

    for line in text:
        
        if build and (len(build_block) != 0) and line.startswith("Q "):
            build = False
            data = {**data, **process_block(build_block)}
            build_block = []

        if not build:
            if line == "\n":
                continue

            if line.startswith("Q "):
                build = True
        
        if build:
            build_block.append(line)
    
    write(data)

def len_q():
    with open("quiz_data/questions.json", "r", encoding="utf8") as f:
        data = json.load(f)
    return len(data.keys())

def fix_unicode():
    with open("quiz_data/questions.json", "r", encoding="utf8") as f:
        data = json.load(f)

    for key, value in data.copy().items():
        if key.count("\u201c") >= 1 or key.count("\u201d") >= 1:
            del data[key]
            data[key.replace("\u201c", "\"").replace("\u201d", "\"")] = value
            key = value
            print(key)

        for pos in range(len(value["options"])):
            var = value["options"][pos]
            if (var.count("\u201c") >= 1) or (var.count("\u201d") >= 1) or (var.count("\u2018") >= 1) or (var.count("\u2019") >= 1) or (var.count("\u2033") >= 1):
                print(var)
                value["options"][pos] = var.replace("\u201c", "\"").replace("\u201d", "\"").replace("\u2018", "'").replace("\u2019", "'").replace("\u2033", "\"")
                data[key] = value
        
        try:
            var = value["answer"]
            if (var.count("\u201c") >= 1) or (var.count("\u201d") >= 1) or (var.count("\u2018") >= 1) or (var.count("\u2019") >= 1) or (var.count("\u2033") >= 1):
                data[key]["answer"] = var.replace("\u201c", "\"").replace("\u201d", "\"").replace("\u2018", "'").replace("\u2019", "'").replace("\u2033", "\"")
                print(var)
        except KeyError:
            print(key)
            break

    with open("quiz_data/questions.json", "w", encoding="utf8") as f:
        json.dump(data, f, indent=2)


def check_dupes():
    with open("quiz_data/questions.json", "r", encoding="utf8") as f:
        data = json.load(f)

    dupes = []

    all_li = list(data.keys())
    for key in data.keys():
        if all_li.count(key) > 1:
            dupes.append(key)

    print("\n".join(dupes))

    return len(dupes)


def final_script():

    main_path = "quiz_data/difficulties/"
    with open(main_path + "easy.json", "r", encoding="utf8") as f:
        easy = json.load(f)

    with open(main_path + "normal.json", "r", encoding="utf8") as f:
        normal = json.load(f)

    with open(main_path + "hard.json", "r", encoding="utf8") as f:
        hard = json.load(f)

    data = {}

    data["easy"] = easy
    data["normal"] = normal
    data["hard"] = hard

    with open("quiz_data/final_questions.json", "w") as f:
        json.dump(data, f, indent=2)

    print("File compiled!")

print(f"There are {check_dupes()} dupes")

print(f"There are {len_q()} questions")
