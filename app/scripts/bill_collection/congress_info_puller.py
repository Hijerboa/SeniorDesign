from util.cred_handler import get_secret
from apis.propublica_api import ProPublicaAPI
from db.database_connection import create_session, initialize
from db.models import CongressMemberData, CongressMemberInstance
from db.db_utils import get_or_create, create_single_object


def store_member(member, session, congress, chamber):
    member_data = {
        'propublica_id': member['id'],
        'first_name': member['first_name'],
        'middle_name': member['middle_name'],
        'last_name': member['last_name'],
        'suffix': member['suffix'],
        'date_of_birth': member['date_of_birth'],
        'gender': member['gender'],
        'party': member['party'],
        'twitter_account': member['twitter_account'],
        'facebook_account': member['facebook_account'],
        'youtube_account': member['youtube_account'],
        'govtrack_id': member['govtrack_id'],
        'cspan_id': member['cspan_id'],
        'votesmart_id': member['votesmart_id'],
        'icpsr_id': member['icpsr_id'],
        'crp_id': member['crp_id'],
        'google_entity_id': member['google_entity_id'],
        'fec_canidate_id': member['fec_candidate_id']
    }
    member_object, created = get_or_create(session, CongressMemberData, propublica_id=member['id'], defaults=member_data)
    session.commit()
    member_instance_data = {
        'congress_member_id': member_object.id,
        'congress': congress,
        'chamber': chamber,
        'title': member['title'],
        'short_title': member['short_title'],
        'leadership_role': member['leadership_role'],
        'seniority': member['seniority'],
        'total_votes': member['total_votes'],
        'missed_votes': member['missed_votes'],
        'total_present': member['total_present']
    }
    keys = member.keys()
    if 'senate_rank' in keys:
        member_instance_data['senate_rank'] = member['senate_rank']
    if 'senate_class' in keys:
        member_instance_data['senate_class'] = member['senate_class']
    if 'next_election' in keys:
        member_instance_data['next_election'] = member['next_election']
    if 'missed_votes_pct' in keys:
        member_instance_data['missed_votes_pct'] = member['missed_votes_pct']
    if 'votes_with_party_pct' in keys:
        member_instance_data['votes_with_party_pct'] = member['votes_with_party_pct']
    if 'votes_against_party_pct' in keys:
        member_instance_data['votes_against_party_pct'] = member['votes_against_party_pct']

    member_instance_object = create_single_object(session, CongressMemberInstance, defaults=member_instance_data)
    session.commit()


def get_congress_members():
    initialize()
    session = create_session()
    propublica_api: ProPublicaAPI = ProPublicaAPI(get_secret("pro_publica_url"), get_secret("pro_publica_api_key"))
    for i in range(117, 118):
        congress_members = propublica_api.get_congress_members(i, 'senate')['data']['results'][0]['members']
        for member in congress_members:
            store_member(member, session, i, 'senate')
        if i > 101:
            congress_members = propublica_api.get_congress_members(i, 'house')['data']['results'][0]['members']
            for member in congress_members:
                store_member(member, session, i, 'house')
