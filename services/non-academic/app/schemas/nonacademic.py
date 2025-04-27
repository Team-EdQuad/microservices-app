def individual_sport(sport):
    return{
        "sport_id": sport["sport_id"],
        "sport_name": sport["sport_name"],
        "description" : sport["description"],
        "location" : sport["location"],
        "schedule" : sport["schedule"],
        "type": sport["type"],
        "category" : sport["category"]
    
    }


def all_sports(sports):
    return [individual_sport(sport) for sport in sports]


def individual_club(club):
    return{
        "club_id" : club["club_id"],
        "club_name" : club["club_name"],
        "description" : club["description"],
        "location" : club["location"],
        "schedule": club["schedule"],
    }

def all_clubs(clubs):
    return [individual_club(club) for club in clubs]
    