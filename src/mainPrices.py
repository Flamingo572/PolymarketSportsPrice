import src.marketRead as marketRead
import src.sportsRead as sportsRead
import src.findIDs as findIDs
import threading
import time

#make to put slug and get prices and scores
def main(slug):
    gameId, clobTokenIds, outcomes = findIDs.findIdsBySlug(slug)
    print(gameId, clobTokenIds, outcomes)
    i = 0
    clobTokenId = clobTokenIds[clobTokenIds.index('\"')+1: (clobTokenIds[clobTokenIds.index('\"')+1: ].index('\"')) + 2]
    marketRead.startMarketRead(clobTokenId)
    sportsRead.startMarketRead(gameId)
    #TODO Figure out how to read both wss at the same time

if __name__ == "__main__":
    slug = "cs2-bb3-fnc-2026-02-20"
    main(slug)
