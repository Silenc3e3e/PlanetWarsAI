from random import choice
import math

class Smarto(object):

    def update(self, gameinfo):
        #do I own at least one planet, with at least one unowned planet remaining?
        if gameinfo.my_planets and (gameinfo.not_my_planets or gameinfo.enemy_fleets):
            myPlanetsList = gameinfo.my_planets.values()
            ShipTotal = 0
            ownId = -1
            for planet in myPlanetsList:
                ShipTotal = ShipTotal + self.returnPlanetNumShipsPlusIncoming(gameinfo, planet)
                ownId = planet.owner_id
            # for fleet in gameinfo.my_fleets.values():
            #     if fleet.dest.owner_id == ownId:
            #         ShipTotal = ShipTotal + fleet.num_ships
            MyShipAverageBetweenPlanet = math.floor(ShipTotal / len(myPlanetsList))

            #for every planet I own
            for mine in myPlanetsList:
                mineShips = mine.num_ships
                #as long as the planet I own has at least 10 units
                if mineShips > 2:
                    
                    
                    #defensive from this planet, assuming offensive action not taken
                    if(not self.Attack(gameinfo, mine, mineShips) and mineShips > MyShipAverageBetweenPlanet):
                        self.Defend(gameinfo, mine, mineShips, MyShipAverageBetweenPlanet)
                       
        pass
    def Attack(self, gameinfo, rootPlanet, shipsOnPlanet):
        #offensive from this planet
        MostCostEffective = None
        MostEffecientCostToTake = None
        QuickestCostReturn = None
        DistanceToMostCostEffective = None

        #loop through all other not owned, and attack the closest one if viable
        for other in self.findClosestEnemyPlanets(gameinfo, rootPlanet):#gameinfo.not_my_planets.values():
            mineDistanceToOther = math.ceil(other.distance_to(rootPlanet))
            
            #am I the closests/equal closest? and is no fleet heading to it atm?
            if not self.hasIncoming(other, gameinfo) and not self.hasCloserPlanet(gameinfo, rootPlanet, other.distance_to(rootPlanet), other):
                #can I take it quicker than previous opponent planet?
                otherGrowthRate = other.growth_rate

                #TODO take into account growth rate, cost effeciency
                #calculate the number of ships needed to take the planet being examined.
                additional = 0
                if(other.owner_id != 0):
                    additional = mineDistanceToOther * (otherGrowthRate)
                costToTake = other.num_ships + 1 + additional
                
                #if "mine" doesn't have enough ships to take planet, how long will it take?
                additionalTime = 0
                mineGrowthRate = rootPlanet.growth_rate
                if mineGrowthRate == 0:
                    mineGrowthRate == 0.001
                if costToTake > (shipsOnPlanet+1):
                    additionalTime = math.ceil((costToTake - shipsOnPlanet) / mineGrowthRate)
                

                returnTime = 0
                if otherGrowthRate > 0:
                    returnTime = math.ceil(costToTake / otherGrowthRate)
                else:
                    returnTime = math.ceil(costToTake * 2)
                ecenomicReturnTime = returnTime + mineDistanceToOther + additionalTime


                if MostCostEffective == None or QuickestCostReturn > ecenomicReturnTime:
                    #make it the best option
                    MostCostEffective = other
                    QuickestCostReturn = ecenomicReturnTime
                    MostEffecientCostToTake = costToTake
                    DistanceToMostCostEffective = mineDistanceToOther
            #else:TODO REMOVE
                #print("hasincoming:%s hasCloserPlanet:%s mine.%s other.%s" % (self.hasIncoming(other, gameinfo), self.hasCloserPlanet(gameinfo, mine, mineDistanceToOther, other), mine.id, other.id))
        if(MostCostEffective != None):
            if shipsOnPlanet > 2 and shipsOnPlanet > MostCostEffective.num_ships+1:
                
                #amount to to take planet + even out between the two planets
                MostEffecientCostToTake = MostEffecientCostToTake + math.floor((self.returnPlanetNumWithGrowth(gameinfo, rootPlanet, DistanceToMostCostEffective) - MostEffecientCostToTake)/2)
                #since the evening out is based on future result that's being added on, it's possible for the demand to be greater than the possible supply at that second
                if(MostEffecientCostToTake > shipsOnPlanet):
                    MostEffecientCostToTake = shipsOnPlanet
                gameinfo.planet_order(rootPlanet, MostCostEffective, MostEffecientCostToTake)
                return True
                #TODO REMOVE below line
                #print("ATTACK. mine.%s MostCostEffective.%s MostCostEffective.num_ships=%s MostCostEffective.growth_rate=%s distancetoclosest=%s additional=%s" % (mine.id, MostCostEffective.id, MostCostEffective.num_ships,MostCostEffective.growth_rate,mine.distance_to(MostCostEffective), additional))

        return False
    def Defend(self, gameinfo, rootPlanet, shipsOnPlanet, shipForceAverage):
        #TODO be less defensive of a given planet if it hasn't been scouted by the enemy
        #loop through ally planets
        lowest = None
        shipNumLow = 99999999
        MineNeighbors = self.returnAllyNeighbors(gameinfo, rootPlanet)
        for allies in MineNeighbors:
            #lowest num AND has no fleet heading to it AND difference > 10
            growthOnArrival = allies.growth_rate * math.ceil(rootPlanet.distance_to(allies))
            alliesShipNum = allies.num_ships
            alliesCurrentPlusGrowth = alliesShipNum + growthOnArrival
            if((not self.checkEntitySame(allies, rootPlanet))
                and ((alliesCurrentPlusGrowth < shipNumLow and alliesCurrentPlusGrowth < shipForceAverage) or lowest == None)
                and (not self.hasIncoming(allies, gameinfo))
                and (shipsOnPlanet - alliesCurrentPlusGrowth) > 10):
                lowest = allies
                shipNumLow=alliesCurrentPlusGrowth
        if lowest!=None:
            amount = shipsOnPlanet - math.ceil((shipsOnPlanet + shipNumLow)/2)
            if amount > 0:
                gameinfo.planet_order(rootPlanet, lowest, amount)

    def hasIncoming(self, planet, gameinfo):
        for fleet in gameinfo.my_fleets.values():
            if(self.checkEntitySame(planet, fleet.dest)):
                return True
            elif planet.id == fleet.dest.id: #TODO remove
                print("hasIncoming same dest. planet = %s fleet.dest = %s ERROR" % (planet.id, fleet.dest.id))
        return False
    def hasCloserPlanet(self, gameinfo, mine, mineDistance, other):
        for allies in gameinfo.my_planets.values():
            if(not self.checkEntitySame(allies, mine)):
                if other.distance_to(allies)<mineDistance:
                    return True
        return False
    def returnPlanetNumShipsPlusIncoming(self, gameinfo, planet):
        ShipTotal = planet.num_ships
        for fleet in gameinfo.my_fleets.values():
            if fleet.dest.id == planet.id:
                ShipTotal = ShipTotal + fleet.num_ships
        return ShipTotal
    def returnPlanetNumWithGrowth(self, gameinfo, planet, time):
        ShipTotal = self.returnPlanetNumShipsPlusIncoming(gameinfo, planet)
        ShipTotal = ShipTotal + planet.growth_rate * math.ceil(time)
        return ShipTotal
    def findClosestEnemyPlanets (self, gameinfo, planet):
        EnemyPlanets = []
        for EnemyPlanet in gameinfo.not_my_planets.values():
            if not self.hasCloserPlanet(gameinfo, planet, EnemyPlanet.distance_to(planet), EnemyPlanet) and not self.immenantDoom(gameinfo, EnemyPlanet):
                EnemyPlanets.append(EnemyPlanet)
        return EnemyPlanets
    def immenantDoom(self, gameinfo, EnemyPlanet):
        remainingShips = EnemyPlanet.num_ships
        longestDuration = 0
        for fleet in gameinfo.my_fleets.values():
            if fleet.dest.id == EnemyPlanet.id:
                TravelTime = math.ceil(fleet.distance_to(EnemyPlanet))
                remainingShips = remainingShips - fleet.num_ships
                if TravelTime > longestDuration:
                    longestDuration = TravelTime
                if remainingShips + TravelTime * EnemyPlanet.growth_rate <= 0:
                    return True
        remainingShips = remainingShips + (EnemyPlanet.growth_rate * longestDuration)
        if remainingShips <= 0:
            return True
        return False
    def checkEntitySame(self, EntityA, EntityB):
        if(EntityA == EntityB or EntityA.id == EntityB.id):
            return True
        if EntityB.id == EntityA.id: #TODO remove
            print("EntityCheck A.%s B.%s" % (EntityA.id, EntityB.id))
        return False
    def returnAllyNeighbors(self, gameinfo, minePlanet):
        examinedPlanets = []
        #foreach unexamined ally planet
        for ally in gameinfo.my_planets.values():
            #TODO remove
            #for ex in examinedPlanets:
                #print ("minePlanet:%s ally: %s examined:%s" % (minePlanet.id, ally.id, ex.id))
            if not self.checkEntitySame(minePlanet, ally):
                #print("-"*40)
                removePlanets = []
                skip = False
                #go through all examined ally planets
                for item in examinedPlanets:
                    mineToItem = minePlanet.distance_to(item)
                    allyToItem = ally.distance_to(item)
                    mineToAlly = minePlanet.distance_to(ally)
                    #if both planets being examined are within 90 degree arc
                    if(self.AandBwithinC90Degrees(item, ally, minePlanet)):
                        #mine --> ally --> item > mine --> item * 2
                        if mineToItem > mineToAlly: #(mineToAlly + allyToItem) > (mineToItem * 2) and mineToItem > allyToItem:
                            removePlanets.append(item)
                            #TODO REMOVE print("removing item minePlanet.%s ally.%s item.%s mineToAlly=%s allyToItem=%s mineToItem*2=%s" % (minePlanet.id, ally.id, item.id, mineToAlly, allyToItem, mineToItem*2))
                        #mine --> item --> ally > mine --> ally * 2
                        elif mineToAlly > mineToItem: #(mineToItem + allyToItem > mineToAlly *2) and mineToAlly > mineToItem:
                            skip = True
                            #TODO REMOVE print("removing skip minePlanet.%s ally.%s item.%s mineToItem=%s allyToItem=%s mineToAlly*2=%s" % (minePlanet.id, ally.id, item.id, mineToItem, allyToItem, mineToAlly*2))
                for planet in removePlanets:
                    examinedPlanets.remove(planet)
                if(not skip):
                    #add ally to examined planets
                    examinedPlanets.append(ally)
        #TODO remove the debug below
        #print("minePlanet: %s examined planets are:" % (minePlanet.id))
        #for examine in examinedPlanets:
            #print("Planet id: %s" % examine.id)
            #input("Continue")
        #for ex in examinedPlanets:
            #print ("FINAL minePlanet:%s ally: %s examined:%s" % (minePlanet.id, ally.id, ex.id))
        return examinedPlanets
    def AandBwithinC90Degrees(self, A, B, C):
        ax = A.x - C.x
        ay = A.y - C.y
        bx = B.x - C.x
        by = B.y - C.y
        dotprod = ((ax * bx) + (ay * by))
        #TODO REMOVE print("home is:%s item:%s ally:%s dotprod:%s return:%s" % (C.id, A.id, B.id, dotprod, ((ax * bx) + (ay * by)) > 0))
        return (((ax * bx) + (ay * by)) > 0)