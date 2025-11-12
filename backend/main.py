from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json

app = FastAPI(title="LoL 1v1 Simulator API")

# -------------------------------
# Riot 데이터 로드
# -------------------------------
# https://ddragon.leagueoflegends.com/cdn/14.22.1/data/en_US/champion.json

with open("C://Users/cpprh/Documents/GitHub/1v1-sim/backend/data/champion.json", encoding="utf-8") as f:
    CHAMPIONS = json.load(f)

with open("C://Users/cpprh/Documents/GitHub/1v1-sim/backend/data/items.json", encoding="utf-8") as f:
    ITEMS = json.load(f)

class ChampionRequest(BaseModel):
    name: str
    level: int
    items: List[str]
    buffs: List[str]


class SimulationRequest(BaseModel):
    champ1: ChampionRequest
    champ2: ChampionRequest


class Champion:
    def __init__(self, name, level, items, buffs):
        base = CHAMPIONS["data"][name]["stats"]

        self.name = name
        self.level = level
        self.hp = base["hp"] + (level - 1) * base["hpperlevel"]
        self.ad = base["attackdamage"] + (level - 1) * base["attackdamageperlevel"]
        self.armor = base["armor"] + (level - 1) * base["armorperlevel"]
        self.aspd = base["attackspeed"] + (level - 1) * base["attackspeedperlevel"]
        self.items = items
        self.buffs = buffs

        # 아이템 스탯 적용
        for item_name in items:
            if item_name not in ITEMS:
                continue
            item_data = ITEMS[item_name]
            stats = item_data.get("stats", {})
            self.hp += stats.get("FlatHPPoolMod", 0)
            self.ad += stats.get("FlatPhysicalDamageMod", 0)
            self.armor += stats.get("FlatArmorMod", 0)
            self.aspd += stats.get("PercentAttackSpeedMod", 0)

        # 버프 적용
        if "red" in buffs:
            self.ad *= 1.08
        if "blue" in buffs:
            self.aspd *= 1.05

    def attack(self, target):
        damage = self.ad * (100 / (100 + target.armor))
        target.hp -= damage
        return damage


def simulate_fight(c1: Champion, c2: Champion):
    time = 0.0
    tick = 0.1
    cd1 = cd2 = 0.0
    while c1.hp > 0 and c2.hp > 0 and time < 30:
        cd1 -= tick
        cd2 -= tick

        if cd1 <= 0:
            c1.attack(c2)
            cd1 = 1 / c1.aspd
        if cd2 <= 0:
            c2.attack(c1)
            cd2 = 1 / c2.aspd

        time += tick

    if c1.hp <= 0 and c2.hp <= 0:
        winner = "draw"
    elif c1.hp > c2.hp:
        winner = c1.name
    else:
        winner = c2.name

    return {
        "winner": winner,
        "duration": round(time, 2),
        c1.name: round(max(c1.hp, 0), 1),
        c2.name: round(max(c2.hp, 0), 1),
    }

# 추가된 상세 로그 기능 
# def simulate_fight(c1: Champion, c2: Champion):
#     time = 0.0
#     tick = 0.1
#     cd1 = cd2 = 0.0
#     logs = []
#     while c1.hp > 0 and c2.hp > 0 and time < 30:
#         cd1 -= tick
#         cd2 -= tick

#         if cd1 <= 0:
#             dmg = c1.attack(c2)
#             logs.append({"time": round(time, 1), "attacker": c1.name, "damage": round(dmg, 1), "target_hp": round(c2.hp, 1)})
#             cd1 = 1 / c1.aspd
#         if cd2 <= 0:
#             dmg = c2.attack(c1)
#             logs.append({"time": round(time, 1), "attacker": c2.name, "damage": round(dmg, 1), "target_hp": round(c1.hp, 1)})
#             cd2 = 1 / c2.aspd

#         time += tick

#     if c1.hp <= 0 and c2.hp <= 0:
#         winner = "draw"
#     elif c1.hp > c2.hp:
#         winner = c1.name
#     else:
#         winner = c2.name

#     return {
#         "winner": winner,
#         "duration": round(time, 2),
#         "final_hp": {c1.name: round(max(c1.hp, 0), 1), c2.name: round(max(c2.hp, 0), 1)},
#         "logs": logs
#     }

# -------------------------------
# API 엔드포인트
# -------------------------------
@app.get("/")
def root():
    return {"message": "LoL 1v1 Simulation API"}

@app.get("/champions")
def get_champions():
    return list(CHAMPIONS.keys())

@app.get("/items")
def get_items():
    return list(ITEMS.keys())

@app.post("/simulate")
def simulate(req: SimulationRequest):
    c1 = Champion(req.champ1.name, req.champ1.level, req.champ1.items, req.champ1.buffs)
    c2 = Champion(req.champ2.name, req.champ2.level, req.champ2.items, req.champ2.buffs)
    result = simulate_fight(c1, c2)
    return result
