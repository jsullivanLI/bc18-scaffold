import battlecode as bc
import random
import sys
import traceback

directions = list(bc.Direction)
max_rockets = 5

def count_units(units, unitType):
    # counting units of a certain type
    result = 0
    for unit in units:
        if unit.unit_type == unitType:
            result = result + 1

    return result

def do_planet_tasks(gc: bc.GameController):
    my_team = gc.team()
    # walk through our units:
    if gc.round() < 500:
        for unit in gc.my_units():
            # send some rockets
            if unit.unit_type == bc.UnitType.Rocket:
                if not unit.rocket_is_used():
                    if len(unit.structure_garrison()) > 7:
                        mars_map = gc.starting_map(bc.Planet.Mars)
                        # try 100 times to find a good landing location
                        for i in range(100):
                            x = random.randint(0, mars_map.width)
                            y = random.randint(0, mars_map.height)
                            landing = bc.MapLocation(bc.Planet.Mars, x, y)
                            if gc.can_launch_rocket(unit.id, landing):
                                print('launched a rocket with {} robots!'.format(len(unit.structure_garrison())))
                                gc.launch_rocket(unit.id, landing)
                                break
                            else:
                                print('cant land rocket at {}'.format(landing.to_json()))
                else:
                    gc.disintegrate_unit(unit.id)

            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a robot!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Worker):
                    gc.produce_robot(unit.id, bc.UnitType.Worker)
                    print('produced a worker!')
                    continue

            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 3)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        print('built a {}!'.format(other.unit_type.to_json()))
                        # move onto the next unit
                        continue
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue
                    if other.unit_type == bc.UnitType.Rocket and gc.can_load(other.id, unit.id):
                        if not other.rocket_is_used():
                            gc.load(other.id, unit.id)
                            break

            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(directions)

            # or, try to build a rocket:
            if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d) and count_units(gc.my_units(), bc.UnitType.Rocket) < max_rockets:
                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
            elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            elif gc.can_harvest(unit.id, d):
                print("Harvesting Karbonite")
                gc.harvest(unit.id, d)
            # and if that fails, try to move
            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)
