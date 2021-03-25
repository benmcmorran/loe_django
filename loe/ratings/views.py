import datetime
from django.http import HttpResponse
from django.template import loader
from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Prediction, Match, Team


def index(request):
    return upcoming(request)


def upcoming(request):
    upcoming_matches = (Match.objects
            .filter(match_datetime__gte=timezone.now(), match_datetime__lte=timezone.now() + datetime.timedelta(days=14))
            .order_by('match_datetime')
            .values('pk', 'match_datetime', 'team1__short_name', 'team2__short_name', 'region'))
    template = loader.get_template('ratings/upcoming.html')
    context = {
        'matches': upcoming_matches
    }
    return HttpResponse(template.render(context, request))


def leaderboard(request):
    brier_leaderboard = Prediction.objects.all().values('user__username').annotate(brier=Avg('brier')).order_by('brier')[:30]
    for entry in brier_leaderboard:
        entry['analyst_rating'] = 100 - int(200 * entry['brier'])
    template = loader.get_template('ratings/leaderboard.html')
    context = {
        'leaderboard': brier_leaderboard,
    }
    return HttpResponse(template.render(context, request))

def user_page(request, username):
    user_predictions = Prediction.objects.filter(user__username=username)
    prior_pred = (user_predictions.filter(match__match_datetime__lte=timezone.now())
            .values('match__region', 'match__match_info', 'match__team1__short_name', 'match__team2__short_name', 'predicted_t1_win_prob', 'brier')
            .order_by('-match__match_datetime'))[:50]
    future_pred = (user_predictions.filter(match__match_datetime__gte=timezone.now())
            .values('match__region', 'match__match_info', 'match__team1__short_name', 'match__team2__short_name', 'predicted_t1_win_prob')
            .order_by('-match__match_datetime'))
    context = {
        'prior_preds': prior_pred,
        'future_preds': future_pred
    }
    template = loader.get_template('ratings/user_page.html')
    return HttpResponse(template.render(context, request))

# REST API Views

@api_view(['POST'])
def hello_world(request):
    print(request.data)
    return Response(status=status.HTTP_200_OK)

