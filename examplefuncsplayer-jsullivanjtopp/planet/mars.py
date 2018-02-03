import battlecode as bc
import random
import sys
import traceback

directions = list(bc.Direction)
max_workers = 5
max_factories = 5

def count_units(units, unitType):
    # counting units of a certain type
    result = 0
    for unit in units:
        if unit.unit_type == unitType:
            result = result + 1

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

        # Factory logic
        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            # Unload produced units
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a robot!')
                    gc.unload(unit.id, d)
            # Focus on creating rangers
            if count_units(gc.my_units(), bc.UnitType.Worker) >= max_workers:
                if gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                    gc.produce_robot(unit.id, bc.UnitType.Ranger)
                    print('produced a ranger!')
                    continue
            # If we need to, make some workers
            elif gc.can_produce_robot(unit.id, bc.UnitType.Worker):
                gc.produce_robot(unit.id, bc.UnitType.Worker)
                print('produced a worker!')

        # Logic for Robots
        if location.is_on_map():

            # Rangers should attack everything in range
            if unit.unit_type == bc.UnitType.Ranger:
                nearby_enemies = gc.sense_nearby_units_by_team(location, unit.attack_range(), enemy_team)
                if len(nearby_enemies) != 0:
                    for enemy in nearby_enemies:
                        if gc.can_attack(unit.id, enemy.id):
                            gc.attack(unit.id, enemy.id)
                            print('attacked a thing!')
                            continue
                elif gc.is_move_ready(unit.id):
                    for d in directions:
                        if gc.can_move(unit.id, d):
                            gc.move_robot(unit.id, d)

            # Workers have these priorities:
            # 1. Build blueprints
            # 2. Blueprint factories
            # 3. Collect karbonite
            # 4. Move
            if unit.unit_type == bc.UnitType.Worker:

                # Look for blueprints
                nearby = gc.sense_nearby_units(location.map_location(), 1)
                for other in nearby:
                    if gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        print('built a ' + other.unit_type.to_json())

                # Lay blueprints
                for d in directions:
                    if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                        gc.blueprint(unit.id, bc.UnitType.Factory, d)
                        print('laid a blueprint!')

                # Mine karbonite
                for d in directions:
                    if gc.can_harvest(unit.id, d):
                        gc.harvest(unit.id, d)
                        print('collected karbonite!')

                # Move
                for d in directions:
                    if gc.can_move(unit.id, d) and gc.is_move_ready(unit.id):
                        gc.move_robot(unit.id, d)
