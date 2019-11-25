# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import balanceGeneral, estadoCapital, estadoResulta, estadoComprobacion, Pan, CIF

from django.contrib import admin

# Register your models here.

admin.site.register(balanceGeneral)
admin.site.register(estadoResulta)
admin.site.register(estadoCapital)
admin.site.register(estadoComprobacion)

admin.site.register(Pan)
admin.site.register(CIF)
