import csv

INPUT = "datasets/prepped/prepped.csv"   # ← 换成你的输入文件名

# Output files
OUT_EXPLORABLE = "datasets/prepped/explorable.csv"
OUT_ACCESSIBLE_NOT_EXP = "datasets/prepped/non_explorable.csv"
OUT_DEAD = "datasets/prepped/dead_links.csv"

with open(INPUT, newline="") as f:
    reader = csv.DictReader(f)
    explorable = []
    non_explorable = []
    dead = []

    for row in reader:
        acc = row["accessible"].strip().lower() == "true"
        exp = row["is_explorable"].strip().lower() == "true"

        if acc and exp:
            explorable.append(row)
        elif acc and not exp:
            non_explorable.append(row)
        elif not acc and not exp:
            dead.append(row)
        else:
            # theoretically unreachable 4th case: accessible=False, explorable=True
            dead.append(row)

header = ["field", "link", "accessible", "is_explorable"]

def write_csv(filename, rows):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)

write_csv(OUT_EXPLORABLE, explorable)
write_csv(OUT_ACCESSIBLE_NOT_EXP, non_explorable)
write_csv(OUT_DEAD, dead)

print("Done!")
print(f"explorable.csv: {len(explorable)} rows")
print(f"non_explorable.csv: {len(non_explorable)} rows")
print(f"dead_links.csv: {len(dead)} rows")