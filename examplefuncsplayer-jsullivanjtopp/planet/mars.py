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

def do_planet_tasks(gc: bc.GameController):
    print("Working On Mars")
    for unit in gc.my_units():
        my_location = unit.location

        # Unload the rockets
        if unit.unit_type == bc.UnitType.Rocket and len(unit.structure_garrison()) > 0:
            for d in directions:
                if gc.can_unload(unit.id, d):
                    gc.unload(unit.id, d)

