# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class PeriodoContable(models.Model):
	id_periodoContable = models.AutoField(primary_key= True)
	fechaInicio = models.DateField('Fecha de inicio', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	fechaFin = models.DateField('Fecha de Fin', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	estadoPeriodo= models.NullBooleanField(null = True);
	def __str__(self):
		return '{}{}'.format(self.fechaInicio,' hasta el ', self. fechaFin)

class Transaccion(models.Model):
	id_Transaccion= models.AutoField(primary_key=True)
	descripcion = models.CharField(max_length = 256)
	fecha = models.DateField('Fecha de Transaccion', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	id_periodoContable = models.ForeignKey(PeriodoContable, null=True, blank=True,on_delete= models.CASCADE)
	is_inicial= models.NullBooleanField(null = True);
	def __str__(self):
		return '{}{}'.format(self.id_Transaccion,self.descripcion, self.fecha,self.id_periodoContable)

		
class Cuenta(models.Model):
	id = models.AutoField(primary_key=True)
	codigo = models.IntegerField()
	nombre = models.CharField(max_length = 256)
	debe = models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=False, validators=[MinValueValidator(0)])
	haber = models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=False, validators=[MinValueValidator(0)])
	saldoDeudor = models.DecimalField('saldo_deudor', max_digits =50, decimal_places=2,blank=False,null=False,validators=[MinValueValidator(0)],default=0.00)
	saldoAcreedor = models.DecimalField('saldo_acreedor', max_digits =50, decimal_places=2,blank=False,null=False,validators=[MinValueValidator(0)],default=0.00)
	codigo_dependiente = models.IntegerField(null= True)
	descripcion = models.CharField(max_length= 256, null=False, blank=False, default='null')
	def __str__(self):
		return '{}{}'.format(self.nombre)

	def getHaber(self):
		return self.haber

	def getDebe(self):
		return self.debe

	def getSaldoAcreedor(self):
		return self.saldoAcreedor

	def getSaldoDeudor(self):
		return self.saldoDeudor

class detalleTransaccion(models.Model):
	id_detalle = models.AutoField(primary_key = True)
	debe = models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	haber = models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])  
	id_Transaccion = models.ForeignKey(Transaccion, null=True, blank=True,on_delete= models.CASCADE)
	id_cuenta = models.ForeignKey(Cuenta, null=True, blank=True, on_delete=models.CASCADE)
	def __str__(self):
		return '{}{}'.format(self.id_detalle)

class estadoComprobacion(models.Model):
	id= models.AutoField(primary_key=True)
	debe =models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	haber= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class estadoResulta(models.Model):
	id=models.AutoField(primary_key=True)
	debe =models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	haber= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	utilidades=models.DecimalField('Utilildad', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	utilidadNeta=models.DecimalField('Utilildad', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class estadoCapital(models.Model):
	id=models.AutoField(primary_key=True)
	debe =models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	haber= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	capitalContable=models.DecimalField('Capital Contable', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	UtilidadRetenida=models.DecimalField('Utilildad Retenida', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class balanceGeneral(models.Model):
	id=models.AutoField(primary_key=True)
	debe =models.DecimalField('debe', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	haber= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class Empleado(models.Model):
	dui=models.AutoField(primary_key=True)
	nombreEmpleado= models.CharField(max_length = 256)
	apellidoEmpleado= models.CharField(max_length = 256)
	puesto = models.CharField(max_length = 256, null=True)
	fecha = models.DateField('Fecha de Contratacion', help_text='Formato: AAAA/MM/DD', blank=False, null=False, auto_now_add=True)
	def __str__(self):
		return '{} {} {} {}'.format(self.dui, self.nombreEmpleado,self.apellidoEmpleado,self.puesto)

class planillaGeneral(models.Model):
	id=models.AutoField(primary_key=True)
	dui= models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.CASCADE)
	AFP_general=models.DecimalField('AFP', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	ISSS_general=models.DecimalField('ISSS', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	salarioTotal=models.DecimalField('SalarioTotal', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	vacaciones=models.DecimalField('Vacaciones', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	salarioNominal=models.DecimalField('Salario Nominal', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	insaforp=models.DecimalField('INSAFORP', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	aguinaldo=models.DecimalField('Aguinaldo', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class Pan(models.Model):
	id=models.AutoField(primary_key=True)
	descripcion = models.CharField(max_length = 256)
	def __str__(self):
		return '{}'.format(self.descripcion)


class MateriaPrima(models.Model):
	id=models.AutoField(primary_key=True)
	nombreMateriaPrima= models.CharField(max_length = 256)
	cantidad = models.IntegerField()
	precioUnitario= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class CIF(models.Model):
	id=models.AutoField(primary_key=True)
	porcentaje=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class Kardex(models.Model):
	id=models.AutoField(primary_key=True)
	materiaPrima= models.ForeignKey(MateriaPrima, null=True, blank=True, on_delete=models.CASCADE)

class Entrada(models.Model):
	id=models.AutoField(primary_key=True)
	kardex=models.ForeignKey(Kardex, null=True, blank=True, on_delete=models.CASCADE)
	fechaEntrada= models.DateField('Fecha de Entrada', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	cantidadEntrada= models.IntegerField()
	costoTotalEntrada= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	costoUnitarioEntrada= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class Salida(models.Model):
	id=models.AutoField(primary_key=True)
	kardex=models.ForeignKey(Kardex, null=True, blank=True, on_delete=models.CASCADE)
	fechaSalida= models.DateField('Fecha de Entrada', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	cantidadSalida= models.IntegerField()
	costoTotalSalida= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	costoUnitarioSalida= models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class Final(models.Model):
	id=models.AutoField(primary_key=True)
	kardex=models.ForeignKey(Kardex, null=True, blank=True, on_delete=models.CASCADE)
	fechaFinal= models.DateField('Fecha de Final', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	cantidadFinal= models.IntegerField()
	costoTotalFinal= models.DecimalField('Costo Final', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	costoUnitarioFinal= models.DecimalField('Costo Unitario FInal', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	es_Actual= models.NullBooleanField(null = True, default=False);

class Orden(models.Model):
	id=models.AutoField(primary_key=True)
	pan=models.ForeignKey(Pan, null=True, blank=True, on_delete=models.CASCADE)
	cif=models.ForeignKey(CIF, null=True, blank=True, on_delete=models.CASCADE)
	descripcion=models.CharField(max_length = 256)
	CMOD=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	cantEmpleados= models.IntegerField()
	diasTrabajados=  models.IntegerField()
	fechaCreacion= models.DateField('Fecha de Creacion', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	fechaEntrega= models.DateField('Fecha de Entrega', help_text='Formato: AAAA/MM/DD', blank=False, null=False)
	CIF_O=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	CMP=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	terminado= models.NullBooleanField(null = False);

	
class materialUtilizado(models.Model):
	id=models.AutoField(primary_key=True)
	orden=models.ForeignKey(Orden, null=True, blank=True, on_delete=models.CASCADE)
	materiaPrima= models.ForeignKey(MateriaPrima, null=True, blank=True, on_delete=models.CASCADE)

class productoTerminado(models.Model):
	id=models.AutoField(primary_key=True)
	orden=models.ForeignKey(Orden, null=True, blank=True, on_delete=models.CASCADE)
	cantidadProducto=models.IntegerField()
	costoUnitarioProducto=models.DecimalField('Costo Unitario', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	costoTotalProducto=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	porcentajeGanancia=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])
	precioVenta=models.DecimalField('haber', max_digits=50, decimal_places=2, blank=False, null=True, validators=[MinValueValidator(0)])

class empleadosXorden(models.Model):
	id=models.AutoField(primary_key=True)
	orden=models.ForeignKey(Orden, null=True, blank=True, on_delete=models.CASCADE)
	dui= models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.CASCADE)
	def __str__(self):
		return '{}'.format(self.dui)

