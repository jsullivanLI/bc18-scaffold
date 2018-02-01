import battlecode as bc
import random
import sys
import traceback

directions = list(bc.Direction)


def do_planet_tasks(gc: bc.GameController):
    my_team = gc.team()
    print("Working On Earth")
    # walk through our units:
    for unit in gc.my_units():

        # send some rockets
        if unit.unit_type == bc.UnitType.Rocket:
            mars_map = gc.starting_map(bc.Planet.Mars)
            x = random.randint(0, mars_map.width)
            y = random.randint(0, mars_map.height)
            landing = bc.MapLocation(bc.Planet.Mars, x, y)
            if gc.can_launch_rocket(unit.id, landing):
                gc.launch_rocket(unit.id, landing)

        # first, factory logic
        if unit.unit_type == bc.UnitType.Factory:
            garrison = unit.structure_garrison()
            if len(garrison) > 0:
                d = random.choice(directions)
                if gc.can_unload(unit.id, d):
                    print('unloaded a knight!')
                    gc.unload(unit.id, d)
                    continue
            elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                gc.produce_robot(unit.id, bc.UnitType.Knight)
                print('produced a knight!')
                continue

        # first, let's look for nearby blueprints to work on
        location = unit.location
        if location.is_on_map():
            nearby = gc.sense_nearby_units(location.map_location(), 2)
            for other in nearby:
                if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                    gc.build(unit.id, other.id)
                    print('built a factory!')
                    # move onto the next unit
                    continue
                if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                    print('attacked a thing!')
                    gc.attack(unit.id, other.id)
                    continue

        # okay, there weren't any dudes around
        # pick a random direction:
        d = random.choice(directions)

        # or, try to build a rocket:
        if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
            gc.blueprint(unit.id, bc.UnitType.Rocket, d)
        elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
            gc.blueprint(unit.id, bc.UnitType.Factory, d)
        # and if that fails, try to move
        elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            gc.move_robot(unit.id, d)
