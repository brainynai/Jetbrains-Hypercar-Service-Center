from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
import json
from django.conf import settings


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html', context={})


class IssueTicketView(View):
    def get(self, request, ticket_type, *args, **kwargs):
        with open(settings.TICKETS_JSON_PATH) as f:
            ticketDict = json.load(f)

        ticketNum = sum(len(i) for i in ticketDict.values())+1
        ticketDict[ticket_type] += [ticketNum]

        with open(settings.TICKETS_JSON_PATH, 'w') as f:
            json.dump(ticketDict, f)

        ticketDict[ticket_type].pop()
        waitTime = 0
        if ticket_type == 'change_oil':
            waitTime = len(ticketDict['change_oil']) * 2
        elif ticket_type == 'inflate_tires':
            waitTime = len(ticketDict['change_oil']) * 2 + len(ticketDict['inflate_tires']) * 5
        elif ticket_type == 'diagnostic':
            waitTime = len(ticketDict['change_oil']) * 2 \
                       + len(ticketDict['inflate_tires']) * 5 \
                       + len(ticketDict['diagnostic']) * 30

        return render(request, 'tickets/ticket.html', context={'ticketnum':ticketNum,
                                                               'waittime':waitTime})


class OperatorView(View):
    def get(self, request, *args, **kwargs):
        with open(settings.TICKETS_JSON_PATH) as f:
            ticketDict = json.load(f)

        return render(request, 'tickets/operator.html', context={'ticketDict':ticketDict})

    def post(self, request, *args, **kwargs):
        with open(settings.TICKETS_JSON_PATH) as f:
            ticketDict = json.load(f)

        nextTicket = None
        if ticketDict['change_oil']:
            nextTicket = ticketDict['change_oil'].pop(0)
        elif ticketDict['inflate_tires']:
            nextTicket = ticketDict['inflate_tires'].pop(0)
        elif ticketDict['diagnostic']:
            nextTicket = ticketDict['diagnostic'].pop(0)
        else:
            message = "Waiting for the next client"

        ticketDict['discards'] += [nextTicket]

        with open(settings.TICKETS_JSON_PATH, 'w') as f:
            json.dump(ticketDict, f)

        if nextTicket is not None:
            message = f"Next ticket #{nextTicket}"

        settings.MESSAGE = message

        return redirect('/next')

class CustView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/customer.html', context={'message':settings.MESSAGE})


