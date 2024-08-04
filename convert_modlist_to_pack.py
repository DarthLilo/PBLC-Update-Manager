import os,json

def convert(text_location = ""):

    new_instructions = {
        "instructions": []
    }

    if os.path.exists(text_location):
        text = open(text_location).read().split("\n")
        for line in text:
            split_line = line.split("-")
            new_instructions["instructions"].append(f"url_add_mod|{split_line[0]}|{split_line[1]}|{split_line[2]}")
    else:
        print("Invalid path location")
    
    with open("output_instructions.json",'a') as output_instructions:
        output_instructions.write(json.dumps(new_instructions,indent=4))

convert("C:\\Users\\darth\\Downloads\\message.txt")