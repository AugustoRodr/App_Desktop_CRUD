from tkinter import *
from tkinter import ttk
import sqlite3

class Product:
  db_name='app_db.db'
  def __init__(self,window):
    #envio la ventana al constructor para luego poder manipularla
    self.wind=window
    self.wind.title('Products Application')
    #Creo un frame que sea un contenedor. Frame es recuadro que adentro me permite poder tener elementos
    #parametros: 1_donde va a estar el frame;2_ el titulo del frame
    frame=LabelFrame(self.wind, text='Registra un nuevo producto')
    frame.grid(row=0, column=0, columnspan=3, pady=20)# con el metodo grid podemos posicionar nuestro frame
    # pady-->padding y: es el espaciado interno de cada elemento, esto solo para que no se vean tan juntos
    
    #Name input
    Label(frame, text='Nombre: ').grid(row=1, column=0)# Creo una etiquea
    self.name=Entry(frame)# Creo un espacio de input o entrada
    self.name.focus()#Esto hara que cuando apenas se ejecute la aplicacion el cursor estara parpadeando en nombre
    self.name.grid(row=1,column=1)# Posiciono el espacio de entrada

    #Price input
    Label(frame, text='Precio: ').grid(row=2, column=0)
    self.price=Entry(frame)
    self.price.grid(row=2,column=1)

    #Button add Product
    #parametros Button:1_dentro de donde tiene que estar;2_texto que va a mostrar
    ttk.Button(frame, text='Guardar Producto',command=self.add_product).grid(row=3,columnspan=2,sticky=W+E)
    # propiedad 'sticky': sirve para indicar desde donde hasta donde queremos que ocupe nuestro boton;W es oeste y E es este
    #nota: en command tengo que poner la funcion a ejecutar cuando haga click en el boton pero sin los parentecis

    #mensajes de salida/ esto es para que envie un mensaje cuando haya modificado la base de datos
    self.message=Label(text='',fg='red')
    self.message.grid(row=3,column=0,columnspan=2,sticky=W+E)

    #Creo una tabla para poder visualizar
    self.tree = ttk.Treeview(height=10,columns=2)
    self.tree.grid(row=4,column=0,columnspan=2)
    self.tree.heading('#0',text='Nombre',anchor=CENTER)# agrego el nombre de las columnas
    self.tree.heading('#1',text='Precio',anchor=CENTER)

    # otros botones
    ttk.Button(text='ELIMINAR',command=self.delete_product).grid(row=5,column=0,sticky=W+E)
    ttk.Button(text='EDITAR',command=self.edit_product).grid(row=5,column=1,sticky=W+E)



    #llenando la tabla
    self.get_products()

  def run_query(self, query, valores={}):
    with sqlite3.connect(self.db_name) as conn:
      cursor=conn.cursor()
      resultado=cursor.execute(query,valores)
      conn.commit()
      return resultado
  
  def get_products(self):
    # lo que hago aqui es limpiar la tabla en caso de que tenga basura y se deja limpio que despues mostrar los nuevos datos que queremos.
    records= self.tree.get_children()
    for elem in records:
      self.tree.delete(elem)
    #consultando los datos
    query='select * from productos order by nombre'
    db_rows=self.run_query(query)
    # llenando la tabla
    for row in db_rows:
      self.tree.insert('',0,text=row[1], values=row[2])    

  def validation(self):
    return len(self.name.get())!=0 and len(self.price.get())!=0

  def add_product(self):
    if self.validation():
      query='insert into productos values(null,?,?)'
      valores=(self.name.get(),self.price.get())
      self.run_query(query,valores)
      #en el codigo de message puedo acceder a su artibuto de la siguiente forma para cambiarla
      self.message['text']=f'El Producto {self.name.get()} se guardo satisfactoriamente'
      self.name.delete(0,END)
      self.price.delete(0,END)# esto lo que hara es vaciar los casilleros de entry una vez que se envie la informacion.
    else:
      self.message['text']='El nombre y el precio son requeridos'
    self.get_products()

  def delete_product(self):
    self.message['text']=''# si ya hay un mensaje lo limpio
    try:
      self.tree.item(self.tree.selection())['text'][0]
      #sin ['text'] lo que obtenemos del codigo anterior es un diccionario con diferentes keys y sus values
    except IndexError as e:
      self.message['text']='Porfavor selecciones un registro'
      return
    name=self.tree.item(self.tree.selection())['text']
    query='delete from productos where nombre=?'
    self.run_query(query,(name,))
    self.message['text']=f'Registro {name} se a borrado satisfactoriamente'
    self.get_products()


  def edit_product(self):
    self.message['text']=''
    try:
      self.tree.item(self.tree.selection())['text'][0]
      #sin ['text'] lo que obtenemos del codigo anterior es un diccionario con diferentes keys y sus values
    except IndexError as e:
      self.message['text']='Porfavor selecciones un registro'
      return
    old_name= self.tree.item(self.tree.selection())['text']
    old_price= self.tree.item(self.tree.selection())['values'][0]
    #con Toplevel puedo abrir otra ventana encima de la principal
    self.edit_wind=Toplevel()
    self.edit_wind.title='Editar Producto'
    
    #nombre anterior
    Label(self.edit_wind, text='Nombre anterior: ').grid(row=0,column=1)
    # en el atributo state colocamos el valor 'readonly' para que el usuario solo pueda ver el valor anterior
    # en el atributo de textVariable expecificamos que valor se mostrara en el entry
    Entry(self.edit_wind, textvariable= StringVar(self.edit_wind,value=old_name),state='readonly').grid(row=0,column=2)

    #nuevo nombre
    Label(self.edit_wind,text='Nuevo Nombre: ').grid(row=1,column=1)
    new_name=Entry(self.edit_wind)
    new_name.grid(row=1,column=2)

    #precio anterior
    Label(self.edit_wind, text='Precio anterior: ').grid(row=2,column=1)
    Entry(self.edit_wind, textvariable= StringVar(self.edit_wind,value=old_price),state='readonly').grid(row=2,column=2)

    #nuevo precio
    Label(self.edit_wind,text='Nuevo Precio: ').grid(row=3,column=1)
    new_price= Entry(self.edit_wind)
    new_price.grid(row=3,column=2)
    #debo de usar la funcion lambda sino dara un error ya que apenas se lee el codigo se ejecuta la funcion sin abrir la ventana y/o enviar los datos
    Button(self.edit_wind,text='Actualizar', command= lambda: self.edit_records(new_name.get(),old_name,new_price.get(),old_price)).grid(row=4,column=2, sticky=W)


  def edit_records(self,new_name,old_name,new_price,old_price):
    query='update productos set nombre=?, precio=? where nombre=? and precio=?'
    valores=(new_name,new_price,old_name,old_price)
    self.run_query(query,valores)
    self.edit_wind.destroy()
    self.message['text']=f'Registro {old_name} actualizado satisfactoriamente'
    self.get_products()

if __name__=='__main__':
  window=Tk()# devuelve una ventana. Esta ventana es la perteneciente a mi aplicacion
  aplication=Product(window)# esto es por si devuelve algun dato
  window.mainloop()# con esto la ventana empezara a ejecutarse