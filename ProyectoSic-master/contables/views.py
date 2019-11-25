# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import PeriodoContable,Transaccion,Cuenta,detalleTransaccion,estadoComprobacion,estadoResulta,estadoCapital,balanceGeneral
from myauth.models import  MyUser
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Max,Count
from django.db import connection
from .models import Empleado,planillaGeneral,Pan,MateriaPrima,CIF,Final,Kardex,Entrada,Salida,Orden,materialUtilizado,productoTerminado,empleadosXorden
import datetime
# Create your views here.
@login_required
def index(request):
	userId=request.user.is_admin
	return render(request, 'contables/index.html', {'user':userId})

@login_required
def periodoConta(request):
	periodo = PeriodoContable.objects.all()
	cantidad= int(0)

	if request.method == 'POST':
		periodoParcial = PeriodoContable.objects.get(id_periodoContable=request.POST['idperiodo'])
		periodoParcial.estadoPeriodo = False
		periodoParcial.save()
		for periodos in periodo:
			if periodos.estadoPeriodo == True:
				cantidad= int(cantidad)+1
	else:
		for periodos in periodo:
			if periodos.estadoPeriodo == True:
				cantidad= int(cantidad)+1

	periodo = PeriodoContable.objects.all()

	return render(request, 'contables/periodoContable.html',{'periodoCont':periodo,'cant':cantidad})

@login_required
def nuevoPeriodo(request):
		if request.method == 'POST':
			PeriodoContable.objects.create(
				fechaInicio=request.POST['fechaIni'],
				fechaFin=request.POST['fechaFin'],
				estadoPeriodo=True
			)
			bal = estadoComprobacion.objects.get(id=1)
			bal.debe=0.00
			bal.haber= 0.00
			bal.save()
			cuenta = Cuenta.objects.all()
			for cuentas in cuenta:
				cuentaParcial=Cuenta.objects.get(id=cuentas.id)
				cuentaParcial.saldoAcreedor=0.00
				cuentaParcial.saldoDeudor=0.00
				cuentaParcial.debe=0.00
				cuentaParcial.haber=0.00
				cuentaParcial.save()
		return render(request, 'contables/nuevoPeriodo.html')

@login_required
def manejoTransaccion(request, periodoId):
	periodo=periodoId
	return render(request, 'contables/menu.html',{'periodoId':periodo})

@login_required
def consultarTransaccion(request,periodoId):
	periodo=periodoId
	transaccion=Transaccion.objects.filter(id_periodoContable=periodoId)
	return render(request, 'contables/consultarTransaccion.html',{'periodoId':periodo,'transacciones':transaccion})

@login_required
def consultaAfectado(request,periodoId,transaccionId):
	cuenta =Cuenta.objects.all()
	detalles = detalleTransaccion.objects.filter(id_Transaccion=transaccionId)
	return render (request, 'contables/detalleCuentaAfectada.html',{'detalle':detalles,'cuentas':cuenta,'periodoId':periodoId})

@login_required
def nuevaTransaccion(request,periodoId):
	periodo=periodoId
	#el periodoId sirve para validar que si esta cerrado no se puede hacer una nueva transaccion
	if request.method == 'POST':
			Transaccion.objects.create(
				descripcion=request.POST['descripcion'],
				fecha=request.POST['fechaTransaccion'],
				id_periodoContable= PeriodoContable.objects.get(id_periodoContable=request.POST['periodo']),
				is_inicial = False,
			)
			return HttpResponse('No se almacenaron los datos')
	return render(request,'contables/ingresarTransaccion.html',{'periodoId':periodo})

@login_required
def transacciones(request,periodoId):
	periodo=periodoId
	periodoCont=PeriodoContable.objects.filter(id_periodoContable=periodoId)
	transaccion=Transaccion.objects.filter(id_periodoContable=periodoId)
	return render(request, 'contables/transaccionLista.html',{'periodos':periodoCont,'periodoId':periodo,'transacciones':transaccion})

@login_required
def detallesTransaccion(request,periodoId,transaccionId):
	periodo=periodoId
	trans=transaccionId
	cuentas=Cuenta.objects.all()

	if request.method == 'POST':
		if request.POST['cuentaId1'] != request.POST['cuentaId2']:
			if request.POST['monto1'] == request.POST['monto2']:
				for x in range(0,2):
						if x == 0:
							detalleTransaccion.objects.create(
								debe =request.POST.get('monto'+str(x+1)),
								haber = 0.00,
								id_Transaccion =Transaccion.objects.get(id_Transaccion=request.POST['idtrans'+str(x+1)]) ,
								id_cuenta =Cuenta.objects.get(id=request.POST['cuentaId'+str(x+1)]),
								)
							cuentaActualizar = Cuenta.objects.get(id=request.POST['cuentaId'+str(x+1)])
							debeac = cuentaActualizar.getDebe()
							cuentaActualizar.debe=float(debeac)+float(request.POST['monto'+str(x+1)])
							cuentaActualizar.save()
						else:
							if x == 1:
								detalleTransaccion.objects.create(
								debe = 0.00,
								haber =request.POST.get('monto'+str(x+1)),
								id_Transaccion =Transaccion.objects.get(id_Transaccion=request.POST['idtrans'+str(x+1)]) ,
								id_cuenta =Cuenta.objects.get(id=request.POST['cuentaId'+str(x+1)]),
								)
							cuentaActualizar2 = Cuenta.objects.get(id=request.POST['cuentaId'+str(x+1)])
							haberac = cuentaActualizar2.getHaber()
							cuentaActualizar2.haber=float(haberac)+float(request.POST['monto'+str(x+1)])
							cuentaActualizar2.save()
	return render(request, 'contables/detalleTransaccion.html',{'periodoId':periodo,'transaccionId':trans,'cuenta':cuentas})

@login_required
def generadorEstados(request,periodoId):
	periodo= periodoId
	return render(request,'contables/generadorEstados.html',{'periodoId':periodo})

@login_required
def balancesComprobacion(request,periodoId):
	periodo = PeriodoContable.objects.get(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	cuentas=Cuenta.objects.all()
	haberParcial = float(0.00)
	debeParcial = float(0.00)
	sumaHaber=float(0.00)
	sumaDebe=float(0.00)


	for cuenta in cuentas:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.saldoDeudor=0.00
		cuentaSet.save()
		bal=estadoComprobacion.objects.get(id=int(1))
		bal.debe=float(0.00)
		bal.haber=float(0.00)
		bal.save()

	for cuenta in cuentas:
		bal=estadoComprobacion.objects.get(id=int(1))
		cuentaParcial=Cuenta.objects.get(id=cuenta.id)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id == cuenta.id:
					if detalle.id_Transaccion_id == transacciones.id_Transaccion:
						haberParcial=float(haberParcial) + float(detalle.haber)
						debeParcial=float(debeParcial) + float(detalle.debe)
		if haberParcial > debeParcial:
			cuentaParcial.saldoAcreedor=float(haberParcial)-float(debeParcial)
			cuentaParcial.save()
			bal.haber=float(bal.haber)+float(cuentaParcial.saldoAcreedor)
			bal.save()
		if debeParcial > haberParcial:
			cuentaParcial.saldoDeudor=float(debeParcial)-float(haberParcial)
			cuentaParcial.save()
			bal.debe=float(bal.debe)+float(cuentaParcial.saldoDeudor)
			bal.save()
		if debeParcial == haberParcial:
			cuentaParcial.saldoAcreedor=0.00
			cuentaParcial.saldoDeudor=0.00
			cuentaParcial.save()
			bal.debe=float(bal.debe)+float(cuentaParcial.saldoDeudor)
			bal.haber=float(bal.haber)+float(cuentaParcial.saldoAcreedor)
			bal.save()
		haberParcial=0.00
		debeParcial=0.00

	balanceC= estadoComprobacion.objects.all()
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	cuentas=Cuenta.objects.all()
	return render(request, 'contables/balanceComprobacion.html',{'cuenta':cuentas,'estados':balanceC,'periodoId':periodoId, 'periodo': periodo})

@login_required
def estadosResultado(request,periodoId):
	periodo=periodoId
	periodo = PeriodoContable.objects.get(id_periodoContable=periodoId)
	cuentasResultadoDeudor = Cuenta.objects.filter(descripcion__iexact='Costo de Venta')
	cuentasResultadoAcreedor = Cuenta.objects.filter(descripcion__iexact='Ingreso')
	cuentasResultadoDeudorAdministracion = Cuenta.objects.filter(descripcion__iexact='Gastos de Administracion')
	cuentasResultadoDeudorFinanciero = Cuenta.objects.filter(descripcion__iexact='Gastos Financieros')
	cuentasResultadoDeudorVenta = Cuenta.objects.filter(descripcion__iexact='Gasto de Venta')
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	result=estadoResulta.objects.all()
	haberParcial= float(0.00)
	debeParcial= float(0.00)
	estadoRes = estadoResulta.objects.get(id=1)
	estadoRes.debe= float(0.00)
	estadoRes.haber=float(0.00)
	estadoRes.utilidades=float(0.00)
	estadoRes.save()
	reservaLegal=Cuenta.objects.filter(descripcion__iexact='Reserva Legal')
	impuesto=Cuenta.objects.filter(nombre__iexact='Impuesto sobre Renta')

	for cuenta in cuentasResultadoDeudor:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()
	for cuenta in cuentasResultadoAcreedor:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()

	for cuenta in cuentasResultadoAcreedor:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						haberParcial=float(haberParcial)+float(detalle.haber)
		cuentaParcial.saldoAcreedor=float(haberParcial)
		cuentaParcial.save()
		estadoRes.haber=float(estadoRes.haber)+ float(cuentaParcial.saldoAcreedor)
		estadoRes.utilidades=float(estadoRes.utilidades)+float(cuentaParcial.saldoAcreedor)
		estadoRes.save()
		haberParcial=0.00


	for cuenta in cuentasResultadoDeudor:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoRes.debe=float(estadoRes.debe)+ float(cuentaParcial.saldoDeudor)
		estadoRes.utilidades=float(estadoRes.utilidades)-float(cuentaParcial.saldoDeudor)
		estadoRes.save()
		debeParcial=0.00

	for cuenta in cuentasResultadoDeudorAdministracion:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoRes.debe=float(estadoRes.debe)+ float(cuentaParcial.saldoDeudor)
		estadoRes.utilidades=float(estadoRes.utilidades)-float(cuentaParcial.saldoDeudor)
		estadoRes.save()
		debeParcial=0.00

	for cuenta in cuentasResultadoDeudorFinanciero:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoRes.debe=float(estadoRes.debe)+ float(cuentaParcial.saldoDeudor)
		estadoRes.utilidades=float(estadoRes.utilidades)-float(cuentaParcial.saldoDeudor)
		estadoRes.save()
		debeParcial=0.00

	for cuenta in cuentasResultadoDeudorVenta:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoRes.debe=float(estadoRes.debe)+ float(cuentaParcial.saldoDeudor)
		estadoRes.utilidades=float(estadoRes.utilidades)-float(cuentaParcial.saldoDeudor)
		estadoRes.save()
		debeParcial=0.00

	for cuenta in reservaLegal:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						haberParcial=float(haberParcial)+float(detalle.haber)
		cuentaParcial.saldoAcreedor=float(haberParcial)
		cuentaParcial.save()
		estadoRes.utilidadNeta=float(estadoRes.utilidades)-float(cuentaParcial.saldoAcreedor)
		estadoRes.save()

	for cuenta in impuesto:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoRes.utilidadNeta=float(estadoRes.utilidadNeta)-float(cuentaParcial.saldoDeudor)
		estadoRes.save()

	cuentasResultadoDeudor = Cuenta.objects.filter(descripcion__iexact='Costo de Venta')
	cuentasResultadoAcreedor = Cuenta.objects.filter(descripcion__iexact='Ingreso')
	cuentasResultadoDeudorAdministracion = Cuenta.objects.filter(descripcion__iexact='Gastos de Administracion')
	cuentasResultadoDeudorFinanciero = Cuenta.objects.filter(descripcion__iexact='Gastos Financieros')
	cuentasResultadoDeudorVenta = Cuenta.objects.filter(descripcion__iexact='Gasto de Venta')
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	estado = estadoResulta.objects.all()
	reservaLegal=Cuenta.objects.filter(descripcion__iexact='Reserva Legal')
	impuesto=Cuenta.objects.filter(nombre__iexact='Impuesto sobre Renta')

	return render(request, 'contables/estadoResultado.html', {'impuestoRenta':impuesto,'capital':reservaLegal,'Gasto':cuentasResultadoDeudor,'Gasto2':cuentasResultadoDeudorAdministracion,'Gasto3':cuentasResultadoDeudorFinanciero,'Gasto4':cuentasResultadoDeudorVenta,'resultado':estado,'Ingreso':cuentasResultadoAcreedor,'periodoId':periodoId, 'periodo': periodo})

@login_required
def estadoCapita(request,periodoId):
	periodo=periodoId
	inversiones = Cuenta.objects.filter(descripcion__iexact='Inversion')
	desinversiones = Cuenta.objects.filter(descripcion__iexact='Desinversion')
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	estadoCa = estadoCapital.objects.all()
	haberParcial= float(0.00)
	debeParcial= float(0.00)
	estadoCapi = estadoCapital.objects.get(id=1)
	estadoCapi.debe= float(0.00)
	estadoCapi.haber=float(0.00)
	estadoCapi.capitalContable=float(0.00)
	estadoCapi.UtilidadRetenida=float(0.00)
	estadoCapi.save()

	for cuenta in inversiones:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()
	for cuenta in desinversiones:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()

	for cuenta in inversiones:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoCapi= estadoCapital.objects.get(id=1)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						haberParcial=float(haberParcial)+float(detalle.haber)
		cuentaParcial.saldoAcreedor=float(haberParcial)
		cuentaParcial.save()
		estadoCapi.haber=float(estadoCapi.haber)+ float(cuentaParcial.saldoAcreedor)
		estadoRes.save()
		haberParcial=0.00
	if estadoRes.utilidadNeta >=0.00:
		estadoCapi.haber= float(estadoCapi.haber)+float(estadoRes.utilidadNeta)*float(0.6)
		estadoCapi.capitalContable= float(estadoCapi.capitalContable)+float(estadoCapi.haber)
		estadoCapi.UtilidadRetenida=float(estadoRes.utilidadNeta)-float(estadoRes.utilidadNeta)*float(0.6)
		estadoCapi.save()
		Neta=float(estadoRes.utilidadNeta)*float(0.6)
	else:
		Neta=0.00
		estadoCapi.haber=float(estadoCapi.haber)
		estadoCapi.capitalContable=float(estadoCapi.capitalContable)+float(estadoCapi.haber)
		estadoCapi.save()


	for cuenta in desinversiones:
		cuentaParcial = Cuenta.objects.get(id=cuenta.id)
		estadoCapi = estadoCapital.objects.get(id=1)
		estadoRes = estadoResulta.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id ==cuenta.id:
					if detalle.id_Transaccion_id==transacciones.id_Transaccion:
						debeParcial=float(debeParcial)+float(detalle.debe)
		cuentaParcial.saldoDeudor=float(debeParcial)
		cuentaParcial.save()
		estadoCapi.debe=float(estadoCapi.debe)+ float(cuentaParcial.saldoDeudor)
		estadoCapi.save()
		debeParcial=0.00
	if estadoRes.utilidadNeta < 0.00:
		estadoCapi.debe=float(estadoCapi.debe)-float(estadoRes.utilidadNeta)
		estadoCapi.capitalContable=float(estadoCapi.capitalContable)-float(estadoCapi.debe)
		estadoCapi.UtilidadRetenida=float(0.00)
		estadoCapi.save()
	else:
		estadoCapi.debe=float(estadoCapi.debe)
		estadoCapi.capitalContable=float(estadoCapi.capitalContable)-float(estadoCapi.debe)
		estadoCapi.save()

	inversiones = Cuenta.objects.filter(descripcion__iexact='Inversion')
	desinversiones = Cuenta.objects.filter(descripcion__iexact='Desinversion')
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	estadoCa = estadoCapital.objects.all()
	estado = estadoResulta.objects.all()
	return render(request,'contables/estadoCapital.html',{'neta':Neta,'periodoId':periodoId,'utilidades':estado,'capitalContable':estadoCa,'inver':inversiones,'desinver':desinversiones})

@login_required
def balanceGral(request,periodoId):
	periodo=periodoId
	periodo = PeriodoContable.objects.get(id_periodoContable=periodoId)
	activosCorrientes = Cuenta.objects.filter(codigo_dependiente__iexact=1)
	pasivosCorrientes = Cuenta.objects.exclude(codigo=20104).filter(codigo_dependiente__iexact=2)
	capitalContable = estadoCapital.objects.all()
	estadoGeneral = balanceGeneral.objects.all()
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	estadoG = balanceGeneral.objects.get(id=1)
	estadoG.debe=float(0.00)
	estadoG.haber=float(0.00)
	estadoG.save()
	haberParcial= float(0.00)
	debeParcial= float(0.00)
	estadoCapi= estadoCapital.objects.get(id=1)


	for cuenta in pasivosCorrientes:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()

	for cuenta in activosCorrientes:
		cuentaSet=Cuenta.objects.get(id=cuenta.id)
		cuentaSet.saldoDeudor=0.00
		cuentaSet.saldoAcreedor=0.00
		cuentaSet.save()

	for cuenta in activosCorrientes:
		cuentaParcial=Cuenta.objects.get(id=cuenta.id)
		estadoG = balanceGeneral.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id == cuenta.id:
					if detalle.id_Transaccion_id == transacciones.id_Transaccion:
						haberParcial=float(haberParcial) + float(detalle.haber)
						debeParcial=float(debeParcial) + float(detalle.debe)
		if haberParcial > debeParcial:
			cuentaParcial.saldoAcreedor=float(haberParcial)-float(debeParcial)
			cuentaParcial.save()
			estadoG.haber=float(estadoG.haber)+float(cuentaParcial.saldoAcreedor)
			estadoG.save()
		if debeParcial > haberParcial:
			print(haberParcial)
			print(debeParcial)
			cuentaParcial.saldoDeudor=float(debeParcial)-float(haberParcial)
			cuentaParcial.save()
			estadoG.debe=float(estadoG.debe)+float(cuentaParcial.saldoDeudor)
			estadoG.save()
			print(estadoG.debe)
		if debeParcial == haberParcial:
			cuentaParcial.saldoAcreedor=0.00
			cuentaParcial.saldoDeudor=0.00
			cuentaParcial.save()
			estadoG.debe=float(estadoG.debe)+float(cuentaParcial.saldoDeudor)
			estadoG.haber=float(estadoG.haber)+float(cuentaParcial.saldoAcreedor)
			estadoG.save()
		haberParcial=0.00
		debeParcial=0.00

	for cuenta in pasivosCorrientes:
		cuentaParcial=Cuenta.objects.get(id=cuenta.id)
		estadoG = balanceGeneral.objects.get(id=1)
		for transacciones in transaccion:
			for detalle in detalles:
				if detalle.id_cuenta_id == cuenta.id:
					if detalle.id_Transaccion_id == transacciones.id_Transaccion:
						haberParcial=float(haberParcial) + float(detalle.haber)
						debeParcial=float(debeParcial) + float(detalle.debe)
		if haberParcial > debeParcial:
			cuentaParcial.saldoAcreedor=float(haberParcial)-float(debeParcial)
			cuentaParcial.save()
			estadoG.haber=float(estadoG.haber)+float(cuentaParcial.saldoAcreedor)
			estadoG.save()
		if debeParcial > haberParcial:
			print(haberParcial)
			print(debeParcial)
			cuentaParcial.saldoDeudor=float(debeParcial)-float(haberParcial)
			cuentaParcial.save()
			estadoG.debe=float(estadoG.debe)+float(cuentaParcial.saldoDeudor)
			estadoG.save()
			print(estadoG.debe)
		if debeParcial == haberParcial:
			cuentaParcial.saldoAcreedor=0.00
			cuentaParcial.saldoDeudor=0.00
			cuentaParcial.save()
			estadoG.debe=float(estadoG.debe)+float(cuentaParcial.saldoDeudor)
			estadoG.haber=float(estadoG.haber)+float(cuentaParcial.saldoAcreedor)
			estadoG.save()
		haberParcial=0.00
		debeParcial=0.00

	estadoG.haber=float(estadoG.haber)+ float(estadoCapi.capitalContable)+float(estadoCapi.UtilidadRetenida)
	estadoG.save()

	activosCorrientes = Cuenta.objects.filter(codigo_dependiente__iexact=1)
	pasivosCorrientes = Cuenta.objects.exclude(codigo=20104).filter(codigo_dependiente__iexact=2)
	capitalContable = estadoCapital.objects.all()
	estadoGeneral = balanceGeneral.objects.all()
	transaccion = Transaccion.objects.filter(id_periodoContable=periodoId)
	detalles = detalleTransaccion.objects.all()
	return render(request,'contables/balanceGeneral.html', {'estadoGral':estadoGeneral,'periodoId':periodoId,'cap':capitalContable,'activos':activosCorrientes,'pasivos':pasivosCorrientes, 'periodo' : periodo})

@login_required
def historialCuenta(request,periodoId):
	cuentas = Cuenta.objects.all()
	periodo=periodoId
	return render(request,'contables/historialCuentas.html',{'cuenta':cuentas,'periodoId':periodo})

@login_required
def catalogoCuenta(request):
	cuentas = Cuenta.objects.all()
	return render(request, 'contables/catalogoCuentas.html',{'cuenta':cuentas})

@login_required
def agregarCuentaPadre(request):
	if request.method == 'POST':
		Cuenta.objects.create(
			codigo =request.POST['codigoCuenta'],
			nombre =request.POST['nombreCuenta'],
			debe =0.00,
			haber=0.00,
			saldoDeudor=0.00,
			saldoAcreedor=0.00,
			descripcion=request.POST['descripcionCuenta']
			)
	return render(request, 'contables/agregarCuenta.html')

@login_required
def agregarCuentaHija(request,cuentaId):
	cuenta=Cuenta.objects.get(id=cuentaId)
	cuentaid=cuentaId

	if request.method == 'POST':
		Cuenta.objects.create(
			codigo =request.POST['codigoCuenta'],
			nombre =request.POST['nombreCuenta'],
			debe =0.00,
			haber=0.00,
			saldoDeudor=0.00,
			saldoAcreedor=0.00,
			codigo_dependiente=cuentaId,
			descripcion=request.POST['descripcionCuenta']
			)
	return render(request, 'contables/agregarCuentaHija.html',{'cuentas':cuenta,'cuentaId':cuentaid})

@login_required
def modificarCuenta(request,cuentaId):
	cuentaid=cuentaId
	cuentas = Cuenta.objects.filter(id=cuentaId)
	maximo =Transaccion.objects.all().aggregate(Max('id_Transaccion'))

	if request.method == 'POST':
		periodo=PeriodoContable.objects.all()
		for  periodos in periodo:
			if periodos.estadoPeriodo == True:
				transaccion=Transaccion.objects.filter(id_periodoContable=periodos.id_periodoContable,is_inicial=False)
				tamano = len(transaccion)
				if tamano == 0:
					cuentaParcial = Cuenta.objects.get(id=cuentaId)
					cuentaParcial.codigo= request.POST['codigoCuenta']
					cuentaParcial.nombre= request.POST['nombreCuenta']
					cuentaParcial.descripcion= request.POST['descripcionCuenta']
					cuentaParcial.debe= request.POST['debeCuenta']
					cuentaParcial.haber= request.POST['haberCuenta']
					cuentaParcial.save()
					trans=Transaccion.objects.create(
						descripcion='Inicio',
						fecha=periodos.fechaInicio,
						id_periodoContable=PeriodoContable.objects.get(id_periodoContable=periodos.id_periodoContable),
						is_inicial=True,
						)
					detalleTransaccion.objects.create(
						debe =request.POST['debeCuenta'],
						haber =request.POST['haberCuenta'],
						id_Transaccion =Transaccion.objects.get(id_Transaccion=trans.id_Transaccion),
						id_cuenta =Cuenta.objects.get(id=cuentaId),
						)
				else:
					print('ya hay transacciones solo puede modificar el nombre y descripcion')
					cuentaParcial = Cuenta.objects.get(id=cuentaId)
					cuentaParcial.codigo= request.POST['codigoCuenta']
					cuentaParcial.nombre= request.POST['nombreCuenta']
					cuentaParcial.descripcion= request.POST['descripcionCuenta']
					cuentaParcial.save()

	return render (request, 'contables/modificarCuenta.html',{'cuenta':cuentas,'max':maximo})


def contabilidadGeneral(request,periodoId):
	periodos= periodoId
	return render(request,'contables/contabilidadGeneral.html', {'periodoId':periodos})


def contabilidadCost(request,periodoId):
	periodo= PeriodoContable.objects.filter(id_periodoContable=periodoId)
	return render(request, 'contables/contabilidadCostos.html',{'periodoId':periodoId,'period':periodo})

def manejoOrden(request,periodoId):
	if request.method == 'POST':
		cif=CIF.objects.get(id=1)
		ordenParcial=Orden.objects.get(id=request.POST['idorden'])
		ordenParcial.terminado=True
		ordenParcial.CMOD= float(ordenParcial.diasTrabajados)*float(ordenParcial.cantEmpleados)*10
		ordenParcial.CIF_O=float(cif.porcentaje)*float(ordenParcial.CMOD)
		ordenParcial.save()
		productoTerminado.objects.create(
			orden=Orden.objects.get(id=request.POST['idorden']),
			cantidadProducto=0.00,
			costoUnitarioProducto=0.00,
			costoTotalProducto=float(ordenParcial.CMOD)+float(ordenParcial.CIF_O)+float(ordenParcial.CMP),
			porcentajeGanancia=0.00,
			precioVenta=0.00
			)
	ordenes=Orden.objects.all()
	periodo= PeriodoContable.objects.filter(id_periodoContable=periodoId)
	return render (request, 'contables/manejoOrden.html',{'periodoId':periodoId,'orden':ordenes, 'period':periodo})

def compraMateriaPrima(request,periodoId):
	mp=MateriaPrima.objects.all()

	if request.method == 'POST':
		final=Final.objects.filter(kardex_id=request.POST.get('productoId'),es_Actual=True)
		tamano=len(final)
		print('hola' + str(tamano))
		cantidadAux=int(0)
		costoUnitario=float(0.00)
		costoTotal=float(0.00)

		if tamano != 0:
			final=Final.objects.get(kardex_id=request.POST['productoId'],es_Actual=True)
			cantidadAux=int(final.cantidadFinal)
			costoUnitario=float(final.costoUnitarioFinal)
			costoTotal=float(cantidadAux)*float(costoUnitario)
			final.es_Actual=False
			final.save()

		entry=Entrada.objects.create(
			kardex=Kardex.objects.get(materiaPrima=request.POST['productoId']),
			fechaEntrada= request.POST['fechaEntrada'],
			costoUnitarioEntrada= request.POST['preciUnit'],
			cantidadEntrada= request.POST['cantidadMP'],
			costoTotalEntrada= float(request.POST['preciUnit'])*float(request.POST['cantidadMP'])
			)

		if request.POST['Compra'] == 'Credito':

			Transaccion.objects.create(
				descripcion='CompraMP'+ str(entry.id),
				fecha=request.POST['fechaEntrada'],
				id_periodoContable=PeriodoContable.objects.get(id_periodoContable=periodoId),
				is_inicial=False,
				)

			transaccion= Transaccion.objects.get(fecha=request.POST['fechaEntrada'], descripcion__iexact="CompraMP"+ str(entry.id))
			detalleTransaccion.objects.create(
				haber = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP']))*1.13,
				debe =float(0.00),
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta= Cuenta.objects.get(codigo=20101),
				)
			detalleTransaccion.objects.create(
				debe = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP'])),
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10102),
				)
			detalleTransaccion.objects.create(
				debe = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP']))*0.13,
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10104),
				)
		else:

			Transaccion.objects.create(
				descripcion='CompraMP'+str(entry.id),
				fecha=request.POST['fechaEntrada'],
				id_periodoContable=PeriodoContable.objects.get(id_periodoContable=periodoId),
				is_inicial=False,
				)

			transaccion= Transaccion.objects.get(fecha=request.POST['fechaEntrada'], descripcion__iexact="CompraMP"+str(entry.id))
			detalleTransaccion.objects.create(
				haber = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP']))*1.13,
				debe =float(0.00),
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta= Cuenta.objects.get(codigo=10101),
				)
			detalleTransaccion.objects.create(
				debe = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP'])),
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10102),
				)
			detalleTransaccion.objects.create(
				debe = (float(request.POST['preciUnit'])*float(request.POST['cantidadMP']))*0.13,
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10104),
				)

		if tamano == 0:
			Final.objects.create(
				kardex=Kardex.objects.get(materiaPrima=request.POST['productoId']),
				fechaFinal= request.POST['fechaEntrada'],
				costoUnitarioFinal= request.POST['preciUnit'],
				cantidadFinal= request.POST['cantidadMP'],
				costoTotalFinal= float(request.POST['preciUnit'])*float(request.POST['cantidadMP']),
				es_Actual=True
				)
		else:
			Final.objects.create(
				kardex=Kardex.objects.get(materiaPrima=request.POST['productoId']),
				fechaFinal= request.POST['fechaEntrada'],
				costoUnitarioFinal= (float(request.POST['preciUnit'])*float(request.POST['cantidadMP'])+float(cantidadAux)*float(costoUnitario))/(int(request.POST['cantidadMP'])+int(cantidadAux)),
				cantidadFinal= int(request.POST['cantidadMP'])+int(cantidadAux),
				costoTotalFinal= (float(request.POST['preciUnit'])*float(request.POST['cantidadMP'])+float(cantidadAux)*float(costoUnitario)),
				es_Actual=True
				)
	return render(request, 'contables/compraMP.html',{'periodoId':periodoId,'product':mp})

def contratacionEmpleado(request,periodoId):
	if request.method=='POST':
		Empleado.objects.create(
			dui=request.POST['dui'],
			nombreEmpleado= request.POST['nombres'],
			apellidoEmpleado=  request.POST['apellidos'],
			puesto = request.POST['Puesto'],
			)
		empAux=Empleado.objects.get(dui=request.POST['dui'])

		planillaGeneral.objects.create(
			dui=Empleado.objects.get(dui=empAux.dui),
			AFP_general=float(0.00),
			ISSS_general=float(0.00),
			salarioTotal=float(0.00),
			vacaciones=float(0.00),
			salarioNominal=float(0.00)
			)
	return render(request, 'contables/contratacionEmpleados.html',{'periodoId':periodoId})

def planilla(request,periodoId):
	empleado=Empleado.objects.all()
	return render (request, 'contables/planillaGeneral.html',{'periodoId':periodoId,'emp':empleado})

def manejoKardex(request,periodoId):
	mp = MateriaPrima.objects.all()
	return render(request, 'contables/kardex.html',{'periodoId':periodoId,'materia':mp})

def detalleKardex(request,materiaId, periodoId):
	fin=Final.objects.filter(kardex_id=materiaId)
	entry=Entrada.objects.filter(kardex_id=materiaId)
	out=Salida.objects.filter(kardex_id=materiaId)
	mp=MateriaPrima.objects.get(id=materiaId)
	return render(request, 'contables/detalleKardex.html',{'materia':mp,'final':fin,'entrada':entry,'salida':out, 'periodoId':periodoId})

def crearOrd(request,periodoId):
	x=Pan.objects.all()
	cif=CIF.objects.all()
	if request.method=='POST':
		Orden.objects.create(
			pan=Pan.objects.get(id=request.POST['productoId']),
			cif=CIF.objects.get(porcentaje=request.POST['cif']),
			descripcion=request.POST['descripcion'],
			diasTrabajados=request.POST['diasTrabajados'],
			cantEmpleados=0,
			terminado=False,
			fechaEntrega=request.POST['fechaEntrega'],
			fechaCreacion=request.POST.get('fechaCreacio'),
			CMOD=0.0,
			CIF_O=0.0,
			CMP=0.0
			)


	return render(request, 'contables/crearOrden.html',{'periodoId':periodoId,'tipoPan':x,'cif':cif})

def modificarCif(request, periodoId):
	if request.method == 'POST':
		cif = CIF.objects.get(id=1)
		cif.porcentaje=request.POST['cif']
		cif.save()
	return render(request, 'contables/cif.html',{'periodoId':periodoId})

def gestionOrden(request,ordenId, periodoId):
	orden= Orden.objects.filter(id=ordenId)
	periodo= PeriodoContable.objects.filter(id_periodoContable=periodoId)
	return render(request, 'contables/gestionarOrden.html',{'orden':orden,'ordenId':ordenId,  'periodoId':periodoId, 'period':periodo})

def asignarMP(request,ordenId, periodoId):

	mp=MateriaPrima.objects.all()

	if request.method == 'POST':
		final=Final.objects.filter(kardex_id=request.POST.get('productoId'),es_Actual=True)
		tamano=len(final)
		print(tamano)
		if tamano != 0:
			cantidadAux=int(0)
			costoUnitario=float(0.00)
			costoTotal=float(0.00)
			if tamano != 0:
				final=Final.objects.get(kardex_id=request.POST['productoId'],es_Actual=True)
				cantidadAux=int(final.cantidadFinal)
				costoUnitario=float(final.costoUnitarioFinal)
				costoTotal=float(cantidadAux)*float(costoUnitario)
				final.es_Actual=False
				final.save()
			Salida.objects.create(
				kardex=Kardex.objects.get(materiaPrima=request.POST['productoId']),
				fechaSalida= request.POST['fechaSalida'],
				costoUnitarioSalida= (float(costoUnitario)),
				cantidadSalida= request.POST['cantidadMP'],
				costoTotalSalida= (float(costoUnitario))*float(request.POST['cantidadMP'])
			)

			Final.objects.create(

				kardex=Kardex.objects.get(materiaPrima=request.POST['productoId']),
				fechaFinal= request.POST['fechaSalida'],
				costoUnitarioFinal= (float(costoUnitario)),
				cantidadFinal=int(cantidadAux)-int(request.POST['cantidadMP']),
				costoTotalFinal= (int(cantidadAux)-int(request.POST['cantidadMP']))*float(costoUnitario),
				es_Actual=True
				)
			materialUtilizado.objects.create(
				orden=Orden.objects.get(id=ordenId),
				materiaPrima=MateriaPrima.objects.get(id=request.POST['productoId'])
				)

			orde=Orden.objects.get(id=ordenId)
			orde.CMP=float(orde.CMP)+(float(costoUnitario)*float(request.POST['cantidadMP']))
			orde.save()

	return render(request, 'contables/asignarMP.html',{'ordenId':ordenId,'product':mp, 'periodoId':periodoId})

def asignarMOD(request,ordenId, periodoId):
	emp=Empleado.objects.filter(puesto="Sastre")
	empleados= empleadosXorden.objects.filter(orden_id=ordenId)
	if request.method=='POST':
		orde=Orden.objects.get(id=ordenId)
		orde.cantEmpleados=int(orde.cantEmpleados)+int(1)
		orde.save()

		empleadosXorden.objects.create(
			orden= Orden.objects.get(id=request.POST['idOrden']),
			dui= Empleado.objects.get(dui=request.POST['empleadoId'])
			)
	empleados= empleadosXorden.objects.filter(orden_id=ordenId)

	return render(request, 'contables/asignarMOD.html',{'ordenId':ordenId,'empleado':emp,'empx':empleados, 'periodoId':periodoId})

def prodTerminado(request,ordenId,periodoId):
	producto = productoTerminado.objects.get(orden_id=ordenId)
	orden= Orden.objects.get(id=ordenId)
	if request.method == 'POST':
		producto = productoTerminado.objects.get(orden_id=ordenId)
		producto.cantidadProducto=request.POST['cantProd']
		producto.costoUnitarioProducto=float(producto.costoTotalProducto)/int(request.POST['cantProd'])
		producto.porcentajeGanancia=request.POST['ganancia']
		producto.save()
		producto.precioVenta=float(producto.costoUnitarioProducto)+(float(producto.costoUnitarioProducto)*float(producto.porcentajeGanancia))
		producto.save()

		if request.POST['Venta']=='Credito':
			Transaccion.objects.create(
				descripcion='Venta'+str(orden.id),
				fecha=orden.fechaEntrega,
				id_periodoContable=PeriodoContable.objects.get(id_periodoContable=periodoId),
				is_inicial=False,
				)

			transaccion= Transaccion.objects.get(fecha=orden.fechaEntrega, descripcion__iexact="Venta"+str(orden.id))
			detalleTransaccion.objects.create(
				debe = float(producto.precioVenta)*float(producto.cantidadProducto)*1.13,
				haber =float(0.00),
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta= Cuenta.objects.get(codigo=10103),
				)
			detalleTransaccion.objects.create(
				haber = float(producto.precioVenta)*float(producto.cantidadProducto),
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=50101),
				)
			detalleTransaccion.objects.create(
				haber = float(producto.precioVenta)*float(producto.cantidadProducto)*0.13,
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=20102),
				)

			detalleTransaccion.objects.create(
				haber = float(producto.costoUnitarioProducto)*float(producto.cantidadProducto),
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10102),
				)

			detalleTransaccion.objects.create(
				debe = float(producto.costoUnitarioProducto)*float(producto.cantidadProducto),
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=40101),
				)



		else:
			Transaccion.objects.create(
				descripcion='Venta'+str(orden.id),
				fecha=orden.fechaEntrega,
				id_periodoContable=PeriodoContable.objects.get(id_periodoContable=periodoId),
				is_inicial=False,
				)

			transaccion= Transaccion.objects.get(fecha=orden.fechaEntrega, descripcion__iexact="Venta"+str(orden.id))
			detalleTransaccion.objects.create(
				debe = float(producto.precioVenta)*float(producto.cantidadProducto)*1.13,
				haber =float(0.00),
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta= Cuenta.objects.get(codigo=10101),
				)
			detalleTransaccion.objects.create(
				haber = float(producto.precioVenta)*float(producto.cantidadProducto),
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=50101),
				)
			detalleTransaccion.objects.create(
				haber = float(producto.precioVenta)*float(producto.cantidadProducto)*0.13,
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=20102),
				)

			detalleTransaccion.objects.create(
				haber = float(producto.costoUnitarioProducto)*float(producto.cantidadProducto),
				debe =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=10102),
				)

			detalleTransaccion.objects.create(
				debe = float(producto.costoUnitarioProducto)*float(producto.cantidadProducto),
				haber =0.00,
				id_Transaccion =Transaccion.objects.get(id_Transaccion=transaccion.id_Transaccion),
				id_cuenta =Cuenta.objects.get(codigo=40101),
				)

	producto = productoTerminado.objects.get(orden_id=ordenId)
	pan= Pan.objects.get(id=orden.pan_id)
	return render(request, 'contables/gestionProdTerminado.html',{'prod':producto,'ord':orden,'pan':pan})

def asignarPlanilla(request,empleadoId, periodoId):
	porcentaje_afp=float(0.0675)
	porcentaje_insaforp=float(0.01)
	porcentaje_isss=float(0.075)
	planilla=planillaGeneral.objects.get(dui_id=empleadoId)
	empleado=Empleado.objects.get(dui=empleadoId)
	cantidad=int(0)
	fechaEmpleado=empleado.fecha
	fechaActual=datetime.datetime.now()

	anio=(int(fechaActual.year)-int(fechaEmpleado.year))
	if anio > 0:
		if fechaEmpleado.month > fechaActual.month:
			anio=int(anio)-int(1)
		if fechaEmpleado.month == fechaActual.month:
			if fechaEmpleado.day > fechaActual.day:
				anio=int(anio)-int(1)


	if empleado.puesto == "Sastre":
		planilla.salarioNominal=float(300.00)
		planilla.save()
		saliDia=planilla.salarioNominal/30
		if anio ==0:
			planilla.aguinaldo=float(0.00)
		if anio >= 1  and anio <=3:
			planilla.aguinaldo=(float(saliDia*15))/12
			planilla.save()
		if anio > 3 and anio <=10:
			planilla.aguinaldo=(float(saliDia*19))/12
			planilla.save()
		if anio >=10:
			planilla.aguinaldo=(float(saliDia*21))/12
			planilla.save()
		planilla.AFP_general=float(planilla.salarioNominal)*porcentaje_afp
		planilla.ISSS_general=float(planilla.salarioNominal)*porcentaje_isss
		planilla.insaforp=float(planilla.salarioNominal)*porcentaje_insaforp
		planilla.save()
		planilla.vacaciones=float((float(saliDia*15)+float(saliDia*15*porcentaje_afp)+float(saliDia*15*porcentaje_isss)+ float(saliDia*15*porcentaje_insaforp)+float(saliDia*15*0.3))/12)
		planilla.save()
		planilla.salarioTotal=float(float(planilla.salarioNominal)+float(planilla.AFP_general)+float(planilla.ISSS_general)+float(planilla.insaforp)+float(planilla.vacaciones)+float(planilla.aguinaldo))
		planilla.save()
	if empleado.puesto == "Gerente":
		planilla.salarioNominal=float(400.00)
		planilla.save()
		saliDia=planilla.salarioNominal/30
		if anio ==0:
			planilla.aguinaldo=float(0.00)
		if anio >= 1  and anio <=3:
			planilla.aguinaldo=(float(saliDia*15))/12
			planilla.save()
		if anio > 3 and anio <=10:
			planilla.aguinaldo=(float(saliDia*19))/12
			planilla.save()
		if anio >=10:
			planilla.aguinaldo=(float(saliDia*21))/12
			planilla.save()
		planilla.AFP_general=float(planilla.salarioNominal)*porcentaje_afp
		planilla.ISSS_general=float(planilla.salarioNominal)*porcentaje_isss
		planilla.insaforp=float(planilla.salarioNominal)*porcentaje_insaforp
		planilla.save()
		planilla.vacaciones=((float(planilla.salarioNominal)/2+float(planilla.AFP_general)/2+float(planilla.ISSS_general)/2+float(planilla.insaforp)/2)/12)+(float(planilla.salarioNominal)*1.3*0.5/12)/12
		planilla.save()
		planilla.salarioTotal=float(float(planilla.salarioNominal)+float(planilla.AFP_general)+float(planilla.ISSS_general)+float(planilla.insaforp)+float(planilla.vacaciones)+float(planilla.aguinaldo))
		planilla.save()
	planilla=planillaGeneral.objects.get(dui_id=empleadoId)

	return render (request,'contables/asignarPlanilla.html',{'planillaGeneral':planilla,'emp':empleado, 'periodoId': periodoId})
