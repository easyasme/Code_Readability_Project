texto=  """
Por cada cliente, se van ingresando los productos, finalizando la carga de datos cuando se ingresa el cero.
Al finalizar, si el cliente quiere pagar con efectivo, se le aplica un descuento del 18%, si el cliente presenta la tarjeta del local, el descuento es del 22%, si paga con crédito se le recarga el 10%", no lo expliques solo crea el código.
El programa deberá ir imprimiendo lo siguiente, a medida que se cagan los clientes:
- nombre del cliente.
- cantidad total de productos comprados.
- valor de la venta total por cliente con un solo decimal.

una vez finalizada la carga por cliente el programa deberá mostrar:
- promedio de ventas hechas en efectivo (con un decimal).
- promedio de ventas hechas en crédito (con un decimal).
  """

print(texto)

ventas_efectivo = []
ventas_tarjeta = []
ventas_credito = []

while True:
    nombre_cliente = input("Ingrese el nombre del cliente (ingrese 0 para finalizar): ")
    if nombre_cliente == "0":
        break
    
    cantidad_productos = 0
    valor_total = 0
    
    while True:
        producto = input("Ingrese el producto (ingrese 0 para finalizar): ")
        if producto == "0":
            break
        
        cantidad_productos += 1
        precio = float(input("Ingrese el precio del producto: "))
        valor_total += precio
    
    forma_pago = input("Ingrese la forma de pago (efectivo, tarjeta, credito): ").lower()
    if forma_pago == "efectivo":
        descuento = valor_total * 0.18
        valor_total -= descuento
        ventas_efectivo.append(valor_total)
    elif forma_pago == "tarjeta":
        descuento = valor_total * 0.22
        valor_total -= descuento
        ventas_tarjeta.append(valor_total)
    elif forma_pago == "credito":
        recargo = valor_total * 0.10
        valor_total += recargo
        ventas_credito.append(valor_total)
    
    print("Nombre del cliente:", nombre_cliente.upper())
    print("Cantidad total de productos comprados:", cantidad_productos)
    print("Valor de la venta total por cliente:", "{:.1f}".format(valor_total))
    print()

promedio_efectivo = sum(ventas_efectivo) / len(ventas_efectivo) if ventas_efectivo else 0
promedio_tarjeta = sum(ventas_tarjeta) / len(ventas_tarjeta) if ventas_tarjeta else 0
promedio_credito = sum(ventas_credito) / len(ventas_credito) if ventas_credito else 0

print("Promedio de ventas hechas en efectivo:", "{:.1f}".format(promedio_efectivo))
print("Promedio de ventas hechas en crédito:", "{:.1f}".format(promedio_credito))
