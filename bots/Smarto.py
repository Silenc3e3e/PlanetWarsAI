from random import choice
import math

class Smarto(object):

    def update(self, gameinfo):
        #do I own at least one planet, with at least one unowned planet remaining?
        if gameinfo.my_planets and gameinfo.not_my_planets:
            #for every planet I own
            for mine in gameinfo.my_planets.values():
                #as long as the planet I own has at least 10 units
                if mine.num_ships > 10:
                    #effeciency
                    mineShips = mine.num_ships
                    #offensive from this planet
                    closestTakeable = None
                    closestTakeDistance = None
                    attacking = False

                    #loop through all other not owned, and attack the closest one if viable
                    for other in gameinfo.not_my_planets.values():
                        mineDistance = other.distance_to(mine)
                        
                        #am I the closests/equal closest? and is no fleet heading to it atm?
                        if not self.hasIncoming(other, gameinfo) and not self.hasCloserPlanet(gameinfo, mine, mineDistance, other):

                            #can I take it quicker than previous opponent planet?
                            #TODO take into account growth rate, cost effeciency
                            if closestTakeable == None or closestTakeDistance > mineDistance:
                                #make it the best option
                                closestTakeable = other
                                closestTakeDistance = mineDistance
                    if(closestTakeable != None):
                        if mineShips > 10 and mineShips > closestTakeable.num_ships+1:
                            attacking = True
                            additional = 0
                            if(closestTakeable.owner_id != 0):
                                additional = math.ceil(mine.distance_to(closestTakeable)*closestTakeable.growth_rate)
                            gameinfo.planet_order(mine, closestTakeable, closestTakeable.num_ships+1 + additional )

                    #defensive from this planet, assuming offensive action not taken
                    if(not attacking):
                        #TODO be less defensive of a given planet if it hasn't been scouted by the enemy
                        #loop through ally planets
                        lowest = None
                        shipNumLow = 99999999
                        MineNeighbors = self.returnAllyNeighbors(gameinfo, mine)
                        #TODO replace gameinfo.my_planets.values() with MineNeighbors
                        for allies in gameinfo.my_planets.values():
                            #lowest num AND has no fleet heading to it AND difference > 10
                            #TODO make the mine planet only reinforce neighbors
                            
                            if((not allies in MineNeighbors)
                                and (not self.checkEntitySame(allies, mine))
                                and allies.num_ships < shipNumLow
                                and (not self.hasIncoming(allies, gameinfo))
                                and mineShips - allies.num_ships > 10):
                                lowest = allies
                                shipNumLow=lowest.num_ships
                            elif(self.hasIncoming(allies, gameinfo)):
                                print("Has Reinforcements")#TODO remove
                        if lowest!=None:
                            amount = math.ceil((mineShips -lowest.num_ships)/2)
                            #print("Reinforce A: $s to B: $s with $s", str(mine.num_ships), str(lowest.num_ships), str(amount)) #TODO remove
                            gameinfo.planet_order(mine, lowest, amount)
        pass
    def hasIncoming(self, planet, gameinfo):
        for fleet in gameinfo.my_fleets.values():
            if(self.checkEntitySame(planet, fleet.dest)):
                return True
        return False
    def hasCloserPlanet(self, gameinfo, mine, mineDistance, other):
        for allies in gameinfo.my_planets.values():
            if(not self.checkEntitySame(allies, mine)):
                if other.distance_to(allies)<mineDistance:
                    return True
    def checkEntitySame(self, EntityA, EntityB):
        if(EntityA == EntityB or EntityA.id == EntityB.id):
            return True
        return False
    def returnAllyNeighbors(self, gameinfo, minePlanet):
        examinedPlanets = []
        #foreach unexamined ally planet
        for ally in gameinfo.my_planets.values():
            if not self.checkEntitySame(minePlanet, ally):
                removePlanets = []
                skip = False
                #go through all examined ally planets
                for item in examinedPlanets:
                    #if quicker (or equal to) to get to this planet by an examined planet
                    if minePlanet.distance_to(item)+item.distance_to(ally) <= minePlanet.distance_to(ally) and not skip:
                        #skip this ally planet
                        skip = True
                    #if quicker to get to examined planet by new found planet
                    elif minePlanet.distance_to(ally)+ally.distance_to(item) < minePlanet.distance_to(item):
                        #removed said examined planet (but do not add to examined planets here)
                        removePlanets.append(item)
                for planet in removePlanets:
                    examinedPlanets.remove(planet)
                if(not skip):
                    #add ally to examined planets
                    examinedPlanets.append(ally)
                
        return examinedPlanets