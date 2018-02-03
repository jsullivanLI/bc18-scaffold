import battlecode as bc
import random
import sys
import traceback

directions = list(bc.Direction)
max_workers = 5

def count_units(units, unitType):
    # counting units of a certain type
    result = 0
    for unit in units:
        if unit.unit_type == unitType:
            result = result + 1

    return result

def get_random_directions():
    result = []
    rnum = random.randint(0, 8)
    for x in range(9):
        result.append(directions[(x + rnum) % 8])

    return result

def do_planet_tasks(gc: bc.GameController):
    my_team = gc.team()

    if my_team == bc.Team.Red:
        enemy_team = bc.Team.Blue
    else:
        enemy_team = bc.Team.Red

    for unit in gc.my_units():
        location = unit.location

        # Unload the rockets
        if unit.unit_type == bc.UnitType.Rocket and len(unit.structure_garrison()) > 0:
            for d in directions:
                if gc.can_unload(unit.id, d):
                    gc.unload(unit.id, d)
                    print("Unloaded a " + unit.unit_type.to_json())
            if len(unit.structure_garrison()) == 0:
                gc.disintegrate_unit(unit.id)  # Destroy the empty rockets

        # Logic for Robots
        if location.is_on_map():

            # Robots should attack everything in range
            if unit.unit_type != bc.UnitType.Worker and unit.unit_type != bc.UnitType.Rocket:
                nearby_enemies = gc.sense_nearby_units_by_team(location, unit.attack_range(), enemy_team)
                if len(nearby_enemies) != 0:
                    for enemy in nearby_enemies:
                        if gc.can_attack(unit.id, enemy.id) and gc.is_attack_ready(unit.id):
                            gc.attack(unit.id, enemy.id)
                            print('attacked a thing!')
                            continue
                elif gc.is_move_ready(unit.id):
                    for d in get_random_directions():
                        if gc.can_move(unit.id, d):
                            gc.move_robot(unit.id, d)

            # Workers have these priorities:
            # 1. Collect karbonite
            # 2. Move
            if unit.unit_type == bc.UnitType.Worker:
                # Mine karbonite
                for d in directions:
                    if gc.can_harvest(unit.id, d):
                        gc.harvest(unit.id, d)
                        print('collected karbonite!')
                # Move
                for d in get_random_directions():
                    if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
                        gc.move_robot(unit.id, d)
