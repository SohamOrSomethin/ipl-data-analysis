import json

with open("player_name_map.json") as f:
    data = json.load(f)

low_confidence=0
med_confidence=0

print("=== LOW CONFIDENCE ===")
for raw, v in data.items():
    if v["confidence"] == "low":
        low_confidence+=1
        print(f'  "{raw}" → "{v["full_name"]}" | {v["reason"]}')

print("\n=== MEDIUM CONFIDENCE ===")
for raw, v in data.items():
    if v["confidence"] == "medium":
        med_confidence+=1
        print(f'  "{raw}" → "{v["full_name"]}" | {v["reason"]}')

print(low_confidence)
print(med_confidence)