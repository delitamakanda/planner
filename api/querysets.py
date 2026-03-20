from accounts.permissions import is_admin, is_hr, manages_team_ids

def scope_to_user_teams(qs, user, *, user_field='user'):
    if is_hr(user) or is_admin(user):
        return qs
    team_ids = manages_team_ids(user)
    if team_ids:
        return qs.filter(**{f'{user_field}__team_memberships__team_id__in': team_ids})
    return qs.filter(**{f'{user_field}_id': user.id})