#Gestão de Estoque - versão 1.0
#versão Python 3.10.7
#apenas bibliotecas nativas dispensando salvar arquivo de requeriments.txt


from tkinter import *
from tkinter import ttk 
from tkinter import messagebox
from datetime import *

import sqlite3


""" alterar para estrutura de orientação a objeto, com classes para as telas, alterando os parâmetros de acordo com as mesas."""

#variáveis globais de configurações - posteriormente substiruir pelo método style
bt_lar = 60 #largura botoes
bt_alt = 30 #altura botoes
bt_bd = 3 #borda interna  botoes

bt_bg = '#33FF99' #background botões - cor dos botões
bt_fg = '#3A373A' #frontground (cor da fonte) - mesma cor fundo

tl_bg = '#3A373A' #background das telas , inclusive janela principal

#exemplo de um código de barras (13 caracteres) -> 7798304851543


raiz = Tk()



class Comandos():
    """comandos dos botões e funções de rotina"""

    def conecta_bd(self):
        """conecta no banco de dados"""
        self.conn = sqlite3.connect('estoque.db')
        self.cursor = self.conn.cursor() #habilita escrever em sql
    
    def desconecta_bd(self):
        """desconecta do banco de dados"""
        self.conn.close()
   
    def cria_tabelas(self):
        """cria tabelas produto, categoria e movimento, caso não existam"""

        self.conecta_bd()
        
        """cria tabela dentro do banco de dados por meio do sql. As aspas triplas em execute, serve para que, 
        caso necessário, use aspas dupla ou comum dentro do código sql"""
     
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                codigo TEXT PRIMARY KEY UNIQUE,
                categoria CHAR
            );
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY UNIQUE, 
                cod_barras CHAR(20) UNIQUE ,
                produto VARCHAR(50) NOT NULL,
                categoria CHAR,
                ativo INT,
                estoque INT         
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS movimento (
                num_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo CHAR(10) NOT NULL,
                cod_produto TEXT NOT NULL,
                produto VARCHAR(50),
                quantidade INT NOT NULL,
                data DATE NOT NULL,
                observacao CHAR(100),
                FOREIGN KEY (cod_produto) REFERENCES produtos(codigo)
            );
        """)

        self.conn.commit() # no sql ele valida essa informação no banco de dados
        
        self.desconecta_bd()

    """ funções para categoria"""

    def desabilita_campos(self):
        self.ent_data.config(state=DISABLED)
        self.ent_estoque.config(state=DISABLED)

    def habilita_campos(self):
        self.ent_data.config(state=NORMAL)
        self.ent_estoque.config(state=NORMAL)

    def limpa_ent_categ(self):
        self.ent_cod_categ.delete(0, END)
        self.ent_desc_categ.delete(0, END)

    def nova_categoria(self):
        """insere nova categoria no banco de dados"""
        
        #pega as entradas
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
        

        self.conecta_bd()        
      
        if self.codigo_cat == '' or self.desc_categoria == '':
            self.desconecta_bd()
            messagebox.showinfo('Atenção!',message='Preencha os campos')
            
        else:         
            #self.conn.execute("INSERT INTO categorias (categoria) VALUES ('"+self.categoria+"')")
            self.conn.execute("INSERT INTO categorias (codigo, categoria) VALUES ('"+self.codigo_cat+"','"+self.desc_categoria+"')")
            self.conn.commit()
            self.desconecta_bd()            
            self.atualiza_categ()
            self.limpa_ent_categ()
            messagebox.showinfo('Mensagem!',message='Categoria cadastrada!')
        


    def atualiza_categ(self):
        self.lt_categ.delete(*self.lt_categ.get_children()) #entender essa linha e ver alternativas
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT codigo, categoria FROM categorias ORDER BY categoria ASC; """)

        for i in lista_nova:
            self.lt_categ.insert('',END, values=i)

        self.desconecta_bd()

    def selec_categoria(self,event):
        """função chamada quando ocorre evento de duploc clique na treeview categoria"""
        self.limpa_ent_categ()
        self.lt_categ.selection()

        for n in self.lt_categ.selection():
            col1, col2 = self.lt_categ.item(n, 'values')
            self.ent_cod_categ.insert(END, col1)
            self.ent_desc_categ.insert(END,col2)

    def apaga_categoria(self):
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
        self.conecta_bd()
        
        if self.codigo_cat == '':
            messagebox.showinfo(title='Atenção', message='Clique duas vezes sobre uma categoria')            
        else:
            self.cursor.execute(" DELETE FROM categorias WHERE codigo = ('"+self.codigo_cat+"')")
            self.conn.commit()
            self.desconecta_bd()
            self.limpa_ent_categ()
            self.atualiza_categ()
            messagebox.showinfo(title='Mensagem', message='Registro apagado!')

    def altera_categoria(self):
        self.codigo_cat = self.ent_cod_categ.get()
        self.desc_categoria = self.ent_desc_categ.get()
        self.conecta_bd()

        self.cursor.execute(""" UPDATE categorias SET categoria = ? WHERE codigo = ? """, (self.desc_categoria, self.codigo_cat)) 
        self.conn.commit()
        self.desconecta_bd()
        self.atualiza_categ()
        self.limpa_ent_categ()
    
    
    def limpa_ent_prod(self):
        self.ent_cod_prod.delete(0, END)
        self.ent_cod_barra_p.delete(0, END)
        self.ent_produto_p.delete(0, END)
        self.comb_categoria.delete(0, END)
        #self.v_ativo.delete()
        #self.check_ativo.delete()

    def busca_prod_mov(self):
        """atualiza a treeview de busca e pega os dados do produto selecionado"""
        self.lt_busca.delete(*self.lt_busca.get_children())
        self.ent_produto.insert(END,'%') #colocar % no final do texto para buscar aproximado
        produto = self.ent_produto.get()
        self.ent_produto.delete(0,END)

        self.conecta_bd()

        self.cursor.execute("""SELECT produto, categoria, estoque, codigo, cod_barras, ativo FROM produtos
            WHERE produto LIKE '%s' ORDER BY produto ASC""" % produto)

        lista_prod = self.cursor.fetchall()

        for i in lista_prod:
            self.lt_busca.insert('',END,values=i)

        self.desconecta_bd()

    def novo_produto(self):
        """insere novo produto o banco de dados"""
        
        #pega as entradas
        self.cod_barras = self.ent_cod_barra_p.get()
        self.codigo = self.ent_cod_prod.get()
        self.produto = self.ent_produto_p.get()
        self.categoria = self.comb_categoria.get()
        self.ativo = self.v_ativo.get()

        self.estoque = int()
    

        self.conecta_bd()
        
        if self.codigo =='' or self.cod_barras=='' or self.produto =='':
            self.desconecta_bd()
            messagebox.showinfo('Atenção!', message='Preencha os campos obrigatórios')
        else:       
            
            try:
                self.conn.execute(""" INSERT INTO produtos (codigo, cod_barras, produto, categoria, ativo, estoque)
                            VALUES (?,?,?,?,?,?)""", (self.codigo, self.cod_barras, self.produto, self.categoria, self.ativo,self.estoque))
                self.conn.commit()
                self.desconecta_bd()
                self.atualiza_prod()
                self.limpa_ent_prod()
                messagebox.showinfo('Mensagem!', message='Produto cadastrado!')
            except:
               messagebox.showerror(title='Atenção!',message='Código de barras e/ou do produto já existente(s)')


    def atualiza_prod(self):
        """atualiza a lista treeview da tela produtos"""
        self.lt_prod.delete(*self.lt_prod.get_children())
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT produto, categoria, estoque, codigo, cod_barras, ativo FROM produtos ORDER BY produto ASC; """)

        for i in lista_nova:
            self.lt_prod.insert('',END, values=i)

        self.desconecta_bd()
    
    def selec_prod_mov(self, event):
        self.limpa_ent_mov()
        
        self.lt_busca.selection()

        data_atual = date.today()
        data_formatada = data_atual.strftime('%d/%m/%Y')

        for n in self.lt_busca.selection():
            col1, col2, col3, col4, col5, col6 = self.lt_busca.item(n,'values')

            self.ent_produto.insert(END,col1)
            self.ent_estoque.insert(END,col3)
            self.ent_cod.insert(END,col4)
            self.ent_cod_barra.insert(END,col5)
            self.ent_data.insert(0,data_formatada)
            self.ent_qtd.insert(0,'1')

        
        self.tl_bsc_mov.destroy()
        self.desabilita_campos()
    

        
        
    def selec_produto(self, event):
        """exibe os dados do produto selecionado com duplo clique na treeview"""
        
        self.limpa_ent_prod()
        self.lt_prod.selection()

        for n in self.lt_prod.selection():
            col1, col2, col3, col4, col5, col6 = self.lt_prod.item(n, 'values')
            self.ent_produto_p.insert(END, col1)
            self.comb_categoria.insert(END,col2)
            self.ent_cod_prod.insert(END, col4)
            self.ent_cod_barra_p.insert(END,col5)
            #self.check_ativo.setvar(self.v_ativo,'1') - tentar colocar o campo de acordo com o banco de dados
            
            
    def altera_produto(self):
        self.cod_barras = self.ent_cod_barra_p.get()
        self.codigo = self.ent_cod_prod.get()
        self.produto = self.ent_produto_p.get()
        self.categoria = self.comb_categoria.get()
        self.ativo = self.v_ativo.get()
        
        self.conecta_bd()

        self.cursor.execute(""" UPDATE produtos SET cod_barras = ?, produto = ?, categoria = ?, ativo = ? 
                        WHERE codigo = ? """, (self.cod_barras, self.produto, self.categoria, self.ativo, self.codigo))

        self.conn.commit()
        self.desconecta_bd()
        self.atualiza_prod()
        self.limpa_ent_prod()

    def calcula_estoque(self,estoque,qtd,codigo):
        self.estoque = int(estoque)
        self.qtd = int(qtd)
        self.cod = codigo
        self.estoque += int(self.qtd)
        
        self.conecta_bd()
        self.cursor.execute(""" UPDATE produtos SET estoque = ? WHERE codigo = ? """, (self.estoque, self.cod))
        self.conn.commit()

        self.desconecta_bd()


    def limpa_ent_mov(self):
        self.habilita_campos()
        self.ent_produto.delete(0, END)
        self.ent_qtd.delete(0, END)
        self.ent_data.delete(0, END)
        self.ent_nregistro.delete(0, END)
        self.ent_estoque.delete(0, END)
        self.ent_cod.delete(0, END)
        self.ent_obs.delete(0, END)
        self.ent_cod_barra.delete(0, END)

    def chama_cod(self,event):
        """chama os campos de produto na tela movimento a partir da inclusão do código do produto"""
        #depois criar uma função para única para o chama_cod() e o chama_cod_barra() alternando os campos por parâmetros
               
        cod_prod_mov = self.ent_cod.get()
        
        self.limpa_ent_mov()
        self.ent_cod.insert(END,cod_prod_mov)

        self.conecta_bd()
        self.cursor.execute(" SELECT cod_barras, produto, estoque FROM produtos WHERE codigo = ('"+cod_prod_mov+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código do produto após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado')
            self.limpa_ent_mov()
        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (cod_barras, produto, estoque) = registro
                self.ent_cod_barra.insert(0, cod_barras)  #pode-se colocar END no lugar de 0
                self.ent_produto.insert(0, produto)
                self.ent_estoque.insert(0, estoque)
                self.ent_data.insert(0,data_formatada)
                self.ent_qtd.insert(0,'1')

        self.desabilita_campos()

    def chama_cod_barra(self, event):
        """chama os campos de produto na tela movimento a partir da inclusão do código de barras"""        
        cod_barras_mov = self.ent_cod_barra.get()
        
        self.limpa_ent_mov()
        self.ent_cod_barra.insert(END, cod_barras_mov)
        

        self.conecta_bd()
        self.cursor.execute(" SELECT codigo, produto, estoque FROM produtos WHERE cod_barras = ('"+cod_barras_mov+"')")

        busca_prod = self.cursor.fetchall()
        existe_dados = len(busca_prod) #verifica se existe o código de barras após dar tab

        self.desconecta_bd()

        if existe_dados == 0:
            messagebox.showinfo(title='Mensagem', message='Código não cadastrado')
            self.limpa_ent_mov()
        else:
            data_atual = date.today()
            data_formatada = data_atual.strftime('%d/%m/%Y')

            #coloca os valores do produto e dos demais campos nas entrys
            for registro in busca_prod:
                (codigo, produto, estoque) = registro
                self.ent_cod.insert(0, codigo)  #pode-se colocar END no lugar de 0
                self.ent_produto.insert(0, produto)
                self.ent_estoque.insert(0, estoque)
                self.ent_data.insert(0,data_formatada)
                self.ent_qtd.insert(0,'1')
            
        self.desabilita_campos()

    def atualiza_mov(self):
        """ atualiza a lista treeview da tela movimento"""
        self.lt_movimento.delete(*self.lt_movimento.get_children())
        self.conecta_bd()
        lista_nova = self.cursor.execute(""" SELECT data, produto, quantidade, tipo, observacao, cod_produto, num_registro FROM movimento ORDER BY num_registro DESC;""")

        for i in lista_nova:
            self.lt_movimento.insert('',END, values=i)

        self.desconecta_bd()

    

    def novo_movimento(self):
        #pegar as entradas
        #self.cod_barras = self.ent_cod_barra.get()
        self.produto = self.ent_produto.get()
        self.qtd = self.ent_qtd.get() 
        self.data = self.ent_data.get()
        self.nregistro = self.ent_nregistro.get()
        self.estoque = self.ent_estoque.get() 
        self.cod = self.ent_cod.get() 
        self.obs = self.ent_obs.get()
        self.mov_num = self.tipo_mov.get()

        #converte valor do movimento para texto conforme dicionário
        self.mov_tex = self.dic_mov[self.mov_num]

        #converte ou não valor qtd para negativo conforme movimento
        self.qtd = int(self.qtd)

        if self.mov_num == 2:            
            self.qtd *= -1
        else:
            self.qtd = self.qtd

        self.conecta_bd()

        self.conn.execute(""" INSERT INTO movimento (tipo, cod_produto, produto, quantidade, data, 
                    observacao) VALUES (?,?,?,?,?,?) """, (self.mov_tex, self.cod, self.produto,self.qtd,self.data,
                     self.obs))
        self.conn.commit()
        self.desconecta_bd()
        self.atualiza_mov()
        self.limpa_ent_mov()
        self.calcula_estoque(self.estoque,self.qtd,self.cod) 
        
        messagebox.showinfo('Mensagem!', message='Movimento registrado!')
        
        self.habilita_campos()

class Aplicativo(Comandos):

    def __init__(self):
        self.raiz = raiz
        self.janela()
        self.quadros()
        self.lista()
        self.botoes()
        self.menu_principal()
        self.dados_movimento()
        self.cria_tabelas()
        self.atualiza_mov()
        
        
        self.raiz.mainloop() #verificar se pode ficar com self

    def janela(self):
        self.raiz.title('Gestão de Estoque')
        self.raiz.geometry('1000x600+150+50')
        self.raiz.config(bg=tl_bg)
        self.raiz.resizable(True,True)
        self.raiz.minsize(width=1000, height=600)


    def menu_principal(self):
        
        self.menu_barra = Menu(self.raiz)
        self.raiz.config(menu=self.menu_barra) #configurando a tela principal para este menu

        self.menu_cad = Menu(self.menu_barra, tearoff=0)
        self.menu_sobre = Menu(self.menu_barra,tearoff=0)

        self.menu_barra.add_cascade(label='Cadastro', menu=self.menu_cad)
        self.menu_barra.add_cascade(label='Sobre', menu=self.menu_sobre)

        #submenus
        self.menu_cad.add_command(label='Produto',command=self.tela_produtos)
        self.menu_cad.add_command(label='Categoria',command=self.tela_categorias)
        self.menu_cad.add_separator()
        self.menu_cad.add_command(label='Sair',command=raiz.quit)

    def quadros(self):

        #quadro para os dados de entrada do movimento
        self.qd_dados = Frame(self.raiz,bg=tl_bg, bd=3)
        self.qd_dados.place(height=165, width=740, relx=0.25, rely=0.01)

        #quadro para a lista do movimento
        self.qd_movimento = LabelFrame(self.raiz, text='Movimento',bd=3, fg='white', bg=tl_bg)
        self.qd_movimento.place(relheight=0.68, relwidth=0.95, relx=0.02, rely=0.28)



    def lista(self):
        
        self.barra_lt_mov = Scrollbar(self.qd_movimento)

        self.lt_movimento = ttk.Treeview(self.qd_movimento, 
                            columns=('col1','col2','col3','col4','col5','col6','col7'),
                           yscrollcommand=self.barra_lt_mov.set, show='headings') #.set atribui a scroll à lista
        
        self.barra_lt_mov.config(command=self.lt_movimento.yview) #configura a barra de rolagem para a lista de movimento

        
        self.lt_movimento.heading('#0', text='')
        self.lt_movimento.heading('#1', text='Data')
        self.lt_movimento.heading('#2', text='Produto')
        self.lt_movimento.heading('#3', text='Quant.')
        self.lt_movimento.heading('#4', text='Movimento')
        self.lt_movimento.heading('#5', text='Observação')
        self.lt_movimento.heading('#6', text='Código')
        self.lt_movimento.heading('#7', text='Nº Registro')

        self.lt_movimento.column('#0', width=1)
        self.lt_movimento.column('#1', width=70)
        self.lt_movimento.column('#2', width=200)
        self.lt_movimento.column('#3', width=50)
        self.lt_movimento.column('#4', width=50)
        self.lt_movimento.column('#5', width=200)
        self.lt_movimento.column('#6', width=70)
        self.lt_movimento.column('#7', width=70)


        #empacotamento da lista e barra de rolagem
        self.lt_movimento.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        
        self.barra_lt_mov.pack(side=RIGHT, fill=Y)
        


    def botoes(self):
        """ 
           botões da tela principal
        """
        self.bt_novo = Button(self.raiz,text='Novo',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.novo_movimento)
        self.bt_salvar = Button(self.raiz,text='Salvar',fg=bt_fg, bd=bt_bd, bg=bt_bg)
        self.bt_cancelar = Button(self.raiz,text='Cancelar',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.limpa_ent_mov)
        self.bt_buscar = Button(self.raiz, text='Buscar',fg='white', bd=bt_bd, bg='#3333FF',command=self.tela_busca_mov) #busca por nome do produto, vai abrir uma nova tela

        self.bt_novo.place(relx=0.03, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_salvar.place(relx=0.1, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_cancelar.place(relx=0.17, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.175, rely=0.058,width=bt_lar, height=bt_alt)
    
    

    def dados_movimento(self):
        """rotulos e entradas para a tela principal de movimento de estoque"""
       
        #rotulos
        self.rt_cod_barra = Label(self.raiz,text='Código de barras', bg=tl_bg, fg='white') #está fora do quadro, está na raiz
        self.rt_produto = Label(self.qd_dados,text='Produto', bg=tl_bg, fg='white')
        self.rt_qtd = Label(self.qd_dados,text='Quantidade', bg=tl_bg, fg='white')
        self.rt_data = Label(self.qd_dados,text="Data", bg=tl_bg, fg='white')
        self.rt_nregistro = Label(self.qd_dados, text='Nº Registro',bg=tl_bg, fg='white')
        self.rt_estoque = Label(self.qd_dados, text='Estoque',bg=tl_bg, fg='white')
        self.rt_cod = Label(self.qd_dados,text='Código do Produto', bg=tl_bg, fg='white')
        self.rt_obs = Label(self.qd_dados,text='Observação', bg=tl_bg, fg='white')



        #entradas
        self.ent_cod_barra = Entry(self.raiz, width=17) #está fora do quadro, está na raiz        
        self.ent_produto = Entry(self.qd_dados, width=80)
        self.ent_qtd = Entry(self.qd_dados, width=12)
        self.ent_data = Entry(self.qd_dados, width=10)
        self.ent_nregistro = Entry(self.qd_dados, width=15,bg=tl_bg)
        self.ent_estoque = Entry(self.qd_dados, width=10)
        self.ent_cod = Entry(self.qd_dados, width=17)
        self.ent_obs = Entry(self.qd_dados, width=103)


        #empacotamento rotulos e entradas
        self.rt_cod_barra.place(relx=0.03, rely=0.045) #está fora do quadro, está na raiz
        self.ent_cod_barra.place(relx=0.03, rely=0.0751)               
        self.rt_produto.place(relx=0,rely=0.11)
        self.ent_produto.place(relx=0, rely=0.22)
        self.rt_qtd.place(relx=0.84,rely=0.11)
        self.ent_qtd.place(relx=0.84, rely=0.22)
        self.rt_data.place(relx=0, rely=0.45)
        self.ent_data.place(relx=0, rely=0.58)
        self.rt_nregistro.place(relx=0.2, rely=0.45)
        self.ent_nregistro.place(relx=0.2, rely=0.58)
        self.rt_estoque.place(relx=0.5, rely=0.45)
        self.ent_estoque.place(relx=0.5, rely=0.58)
        self.rt_cod.place(relx=0.8, rely=0.45)
        self.ent_cod.place(relx=0.8, rely=0.58)
        self.rt_obs.place(relx=0, rely=0.81)
        self.ent_obs.place(relx=0.1, rely=0.81)

        #radiobutton para opção de tipo de movimento - entrada ou saída
        
        self.tipo_mov = IntVar(self.raiz,value=2) #ver melhor o uso do radiobutton
        self.dic_mov = {1:'Entrada',2:'Saída'}
        
        self.rb_mov_ent = Radiobutton(self.raiz, text='Entrada', variable=self.tipo_mov, command=None, 
                            bg=tl_bg, fg='white',value=1,selectcolor=tl_bg)
        self.rb_mov_saida = Radiobutton(self.raiz, text='Saída', variable=self.tipo_mov, command=None,
                            bg=tl_bg, fg='white',value=2,selectcolor=tl_bg)
        
        
        #empacotamento dos radiobutton
        self.rb_mov_ent.place(relx=0.025,rely=0.13)
        self.rb_mov_saida.place(relx=0.1,rely=0.13)

        #chama a função a partir do tab
        self.ent_cod_barra.bind("<Tab>",self.chama_cod_barra)
        self.ent_cod.bind('<Tab>',self.chama_cod)

        self.habilita_campos()

    def tela_produtos(self):
        """tela para cadastro de produtos"""
        
        
        """atualização da combobox categoria"""
        self.conecta_bd()
        self.dados = self.cursor.execute(""" SELECT DISTINCT(categoria) as categoria FROM categorias""")
        self.lista_combo = [r for r, in self.dados]
        self.desconecta_bd()

        """configurações da tela"""
        self.tl_prod = Toplevel(self.raiz)
        self.tl_prod.title('Cadastro de Produtos')
        self.tl_prod.geometry('700x650+400+30')
        self.tl_prod.config(bg=tl_bg)    
        self.tl_prod.minsize(width=600, height=600)
        self.tl_prod.resizable(False, False)
        
        #variável para o check button campo Ativo igual a 'S' ou 'N'
        self.v_ativo = IntVar(self.tl_prod,1)
        #self.dic_ativo = {1:'Ativo',0:'Inativo'}
        
        #rotulos, entradas, checkbutton e combobox de produtos
        self.rt_cod = Label(self.tl_prod,text='Código do Produto', bg=tl_bg, fg='white')
        self.rt_cod_barra = Label(self.tl_prod,text='Código de barras', bg=tl_bg, fg='white')
        self.rt_produto = Label(self.tl_prod,text='Produto', bg=tl_bg, fg='white')        
        self.rt_categoria = Label(self.tl_prod, text='Categoria',bg=tl_bg, fg='white')
     
        self.ent_cod_prod = Entry(self.tl_prod, width=17)
        self.ent_cod_barra_p = Entry(self.tl_prod, width=17)
        self.ent_produto_p = Entry(self.tl_prod, width=80)


        self.check_ativo = Checkbutton(self.tl_prod,text='Ativo',bg=tl_bg, fg='white',
                            variable=self.v_ativo, onvalue=1, offvalue=0,selectcolor=tl_bg)
    
        self.comb_categoria = ttk.Combobox(self.tl_prod,width=15,values=self.lista_combo)
        
        #empacotamento rotulos, entradas, combobox, checkbox
        self.rt_cod.place(x=10, y=10)
        self.ent_cod_prod.place(x=10, y=30)
        self.rt_cod_barra.place(x=550, y=10) 
        self.ent_cod_barra_p.place(x=550,y=30)     
        self.rt_produto.place(x=10, y=70)
        self.ent_produto_p.place(x=10, y=90)
        self.rt_categoria.place(x=550, y=70)
        self.comb_categoria.place(x=550,y=90)
        self.check_ativo.place(x=550,y=125)

        #quadro, lista, barra rolagem
        self.qd_prod = Frame(self.tl_prod, bg=tl_bg, highlightthickness=3)
        
        self.barra_lt_prod = Scrollbar(self.qd_prod)
        
        self.lt_prod = ttk.Treeview(self.qd_prod, columns=('col1','col2','col3','col4','col5','col6'),
                        yscrollcommand=self.barra_lt_prod.set, show='headings')
        

        self.barra_lt_prod.config(command=self.lt_prod.yview)

        self.lt_prod.heading('#0', text='')
        self.lt_prod.heading('#1', text='Produto')
        self.lt_prod.heading('#2', text='Categoria')
        self.lt_prod.heading('#3', text='Estoque')
        self.lt_prod.heading('#4', text='Código')
        self.lt_prod.heading('#5', text='Código Barras')
        self.lt_prod.heading('#6', text='Ativo')

        self.lt_prod.column('#0', width=1)
        self.lt_prod.column('#1', width=200)
        self.lt_prod.column('#2', width=100)
        self.lt_prod.column('#3', width=50)
        self.lt_prod.column('#4', width=50)
        self.lt_prod.column('#5', width=50)
        self.lt_prod.column('#6', width=10)
                 
        #empacotamento quadro, lista e barra rolagem
        self.qd_prod.place(height=470, width=680, relx=0.01, rely=0.25)
        self.lt_prod.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_prod.pack(side=RIGHT, fill=Y)


        #botões
        self.bt_novo = Button(self.tl_prod,text='Novo',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.novo_produto)
        self.bt_salvar = Button(self.tl_prod,text='Salvar',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.altera_produto)
        self.bt_cancelar = Button(self.tl_prod,text='Cancelar',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.limpa_ent_prod)
        self.bt_buscar = Button(self.tl_prod, text='Buscar',fg='white', bd=bt_bd, bg='#3333FF') #busca por nome do produto, vai abrir uma nova tela

        self.bt_novo.place(relx=0.03, rely=0.19,width=bt_lar, height=bt_alt)
        self.bt_salvar.place(relx=0.13, rely=0.19,width=bt_lar, height=bt_alt)
        self.bt_cancelar.place(relx=0.23, rely=0.19,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.2, rely=0.03,width=bt_lar, height=bt_alt)

        self.atualiza_prod()

        self.lt_prod.bind("<Double-1>", self.selec_produto) #chama a função selec_produto a partir de um duplo clique no registro

    def tela_categorias(self):
        """tela para cadastro de categorias de produtos"""
        self.tl_categ = Toplevel(self.raiz)
        self.tl_categ.title('Cadastro de Categorias')
        self.tl_categ.geometry('400x500+450+30')
        self.tl_categ.config(bg=tl_bg)    
        self.tl_categ.minsize(width=400, height=200)        
        self.tl_categ.resizable(False, False)



        #rotulos, entradas, botoes (colocar botao apagar)
        self.rt_cod = Label(self.tl_categ,text='Código', bg=tl_bg, fg='white')
        self.rt_categ = Label(self.tl_categ, text='Categoria',bg=tl_bg, fg='white')

        self.ent_cod_categ = Entry(self.tl_categ, width=10)
        self.ent_desc_categ = Entry(self.tl_categ, width=30)

        #empacotamento rotulos, entradas e botoes
        self.rt_cod.place(x=10, y=10)
        self.ent_cod_categ.place(x=10, y=30)

        self.rt_categ.place(x=200, y=10)
        self.ent_desc_categ.place(x=200,y=30)        


        #botões
        self.bt_novo = Button(self.tl_categ,text='Novo',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.nova_categoria)
        self.bt_salvar = Button(self.tl_categ,text='Salvar',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.altera_categoria)
        self.bt_cancelar = Button(self.tl_categ,text='Cancelar',fg=bt_fg, bd=bt_bd, bg=bt_bg, command=self.limpa_ent_categ)
        self.bt_apagar = Button(self.tl_categ, text='Apagar',fg='white', bd=bt_bd, bg='red',command=self.apaga_categoria)
        self.bt_buscar = Button(self.tl_categ, text='Buscar',fg='white', bd=bt_bd, bg='#3333FF')

        self.bt_novo.place(relx=0.03, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_salvar.place(relx=0.2, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_cancelar.place(relx=0.37, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_apagar.place(relx=0.54, rely=0.2,width=bt_lar, height=bt_alt)
        self.bt_buscar.place(relx=0.25, rely=0.05,width=bt_lar, height=bt_alt)


        #quadro, lista e barra de rolagem
        self.qd_categ = Frame(self.tl_categ, bg=tl_bg, highlightthickness=3)
       
        self.barra_lt_categ = Scrollbar(self.qd_categ)
        
        self.lt_categ = ttk.Treeview(self.qd_categ,columns=('col1','col2'),
                        yscrollcommand=self.barra_lt_categ.set,show='headings')       
        
        self.barra_lt_categ.config(command=self.lt_categ.yview)
       
        self.lt_categ.heading('#0', text='')
        self.lt_categ.heading('#1', text='Código')
        self.lt_categ.heading('#2', text='Categoria')

        self.lt_categ.column('#0', width=1)
        self.lt_categ.column('#1', width=5)
        self.lt_categ.column('#2', width=200)

        #empacotamento quadro, lista e barra rolagem
        self.qd_categ.place(height=350, width=390, relx=0.01, rely=0.29)
        self.lt_categ.place(relwidth=0.93, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_categ.pack(side=RIGHT, fill=Y)

        self.atualiza_categ()

        self.lt_categ.bind("<Double-1>", self.selec_categoria) #chama a função selec_categoria a partir de um duplo clique no registro

    def tela_busca_mov(self):
        """criando a tela. depois colocar tudo em uma única classe, e colocar parâmetros"""
        self.tl_bsc_mov = Toplevel(self.raiz)
        self.tl_bsc_mov.title('Buscar produto')
        self.tl_bsc_mov.geometry('700x650+400+30')
        self.tl_bsc_mov.config(bg=tl_bg)
        self.tl_bsc_mov.minsize(width=600, height=600)
        self.tl_bsc_mov.resizable(False, False)
       
        """ quadro, lista e barra de rolagem"""
        self.qd_bsc_mov = Frame(self.tl_bsc_mov,bg=tl_bg, highlightthickness=3)

        self.barra_lt_busca = Scrollbar(self.qd_bsc_mov)

        self.lt_busca = ttk.Treeview(self.qd_bsc_mov,columns=('col1','col2','col3','col4','col5','col6'),
                        yscrollcommand=self.barra_lt_busca.set, show='headings')

        self.barra_lt_busca.config(command=self.lt_busca.yview)

        self.lt_busca.heading('#0', text='')
        self.lt_busca.heading('#1', text='Produto')
        self.lt_busca.heading('#2', text='Categoria')
        self.lt_busca.heading('#3', text='Estoque')
        self.lt_busca.heading('#4', text='Código')
        self.lt_busca.heading('#5', text='Código Barras')
        self.lt_busca.heading('#6', text='Ativo')

        self.lt_busca.column('#0', width=1)
        self.lt_busca.column('#1', width=200)
        self.lt_busca.column('#2', width=100)
        self.lt_busca.column('#3', width=50)
        self.lt_busca.column('#4', width=50)
        self.lt_busca.column('#5', width=50)
        self.lt_busca.column('#6', width=10)

        #empacotamento quadro, lista e barra rolagem
        self.qd_bsc_mov.place(height=470, width=680, relx=0.01, rely=0.25)
        self.lt_busca.place(relwidth=0.96, relheight=0.95, relx=0.01, rely=0.03)
        self.barra_lt_busca.pack(side=RIGHT, fill=Y)

        self.busca_prod_mov()
        self.lt_busca.bind('<Double-1>', self.selec_prod_mov)

Aplicativo()
