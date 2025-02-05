import pandas as pd
import plotly.express as px
import random 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import Dash,html,dcc,Input,Output
import datetime
import math
import os

d1 = pd.read_excel('Vendas.xlsx')
d2 = pd.read_excel('Vendas - Dez.xlsx')

# dia da semana
def dia(a,m,d):
    """recebe o ano, mês e dia de uma data
    e retorna o nome do dia da semana"""
    sem = ("Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo")
    num = datetime.date(a, m, d).weekday()
    return sem[num]
# d1
d1['Data']=pd.to_datetime(d1['Data'])
d1['Ano']=d1['Data'].dt.year
d1['Mês']=d1['Data'].dt.month
d1['Dia']=d1['Data'].dt.day
for ind in list(d1.index):
    d1.loc[ind,'Dia da semana']=dia(d1.loc[ind,'Ano'], d1.loc[ind,'Mês'], d1.loc[ind,'Dia'])
# d2
d2['Data']=pd.to_datetime(d2['Data'])
d2['Ano']=d2['Data'].dt.year
d2['Mês']=d2['Data'].dt.month
d2['Dia']=d2['Data'].dt.day
for ind in list(d2.index):
    d2.loc[ind,'Dia da semana']=dia(d2.loc[ind,'Ano'], d2.loc[ind,'Mês'], d2.loc[ind,'Dia'])

# sexo do comprador
for c in range(0,93910):
    if c<63910:
        d1.loc[c,'Sexo']='Mulher'
    else:
        d1.loc[c,'Sexo']='Homem'
for c in range(0,7089):
    if c<4089:
        d2.loc[c,'Sexo']='Mulher'
    else:
        d2.loc[c,'Sexo']='Homem'
# idade do comprador
idades=[]
for c in range(0,20000):
    idades.append(random.randint(18,25))
for c in range(0,40000):
    idades.append(random.randint(26,35))
for c in range(0,20000):
    idades.append(random.randint(36,45))
for c in range(0,13910):
    idades.append(random.randint(46,65))
for c in range(0,93910):
    d1.loc[c,'Idade']= random.choice(idades)
for c in range(0,7089):
    d2.loc[c,'Idade']= random.choice(idades)

# metodos de pagamento
pag = ['Pix','Crédito','Débito','Dinheiro']
for c in range(0,93910):
    d1.loc[c,'Pagamento']=random.choice(pag)
for c in range(0,7089):
    d2.loc[c,'Pagamento']=random.choice(pag)
# custo
for c in range(0,93910):
    n = random.randint(10,60)
    d1.loc[c,'Custo']=d1.loc[c,'Valor Unitário']*(n/100)
for c in range(0,7089):
    n = random.randint(10,60)
    d2.loc[c,'Custo']=d2.loc[c,'Valor Unitário']*(n/100)

dados = pd.concat([d1,d2], axis=0)
# data
dados['Data']=pd.to_datetime(dados['Data'])
dados['Mês']=dados['Data'].dt.month
# lucro
dados['Lucro']=dados['Valor Final']-(dados['Custo']*dados['Quantidade'])

lojas = ['Shopping Vila Velha','Norte Shopping','Iguatemi Campinas','Salvador Shopping','Bourbon Shopping SP']
dados.rename(columns={'ID Loja':'Loja'}, inplace=True)
vendasinit = dados.query('Loja in ["Shopping Vila Velha","Norte Shopping","Iguatemi Campinas","Salvador Shopping","Bourbon Shopping SP"]')
vendas = vendasinit.query('Mês == 2')


cyan=[]
darkcyan=[]
for c in range(0,28):
    cyan.append('cyan')
    darkcyan.append('darkcyan')
# faturamento/lucro diário
fatfev = vendas[['Dia','Valor Final','Lucro']].groupby('Dia').sum()
for d in list(fatfev.index):
    fatfev.loc[d,'Dia']=d
fatfev.rename(columns={'Valor Final':'Faturamento diário'}, inplace=True)
fattotal = fatfev['Faturamento diário'].sum()
luctotal = fatfev['Lucro'].sum()
fatxdfev = px.bar(fatfev, x='Dia', y='Faturamento diário', template='plotly_dark', color_discrete_sequence=darkcyan, title=f'Faturamento diário do mês Fevereiro (total = R${fattotal})',
                 height=600)
lucxdfev = px.bar(fatfev, x='Dia', y='Lucro', template='plotly_dark', color_discrete_sequence=cyan, title=f'Lucro diário do mês Fevereiro (total = R${luctotal:.0f})',
                 height=600)

# CONTRIBUIÇÃO DE CADA LOJA NO LUCRO/FATURAMENTO
lojac = vendas[['Loja','Valor Final','Lucro']].groupby('Loja').sum()
lojac.rename(columns={'Valor Final':'Faturamento'}, inplace=True)
lista = list(lojac.index)
for c in range(0,5):
    lojac.loc[lista[c],'Loja']=lista[c]
    
CT = make_subplots(rows=2, cols=2, specs=[[{'rowspan':2,'type':'domain'}, {'rowspan':2,'type':'domain'}],[None, None]], subplot_titles=('Participação no faturamento', 'Participação no lucro'))
CT.add_trace(go.Pie(labels=lojac['Loja'], values=lojac['Faturamento'], marker=dict(colors=('lightcyan','cyan', 'royalblue','darkblue','lightgreen'))), row=1, col=1)
CT.add_trace(go.Pie(labels=lojac['Loja'], values=lojac['Lucro'], marker=dict(colors=('lightcyan','cyan', 'royalblue','darkblue','lightgreen'))), row=1, col=2)
CT.update_annotations(font_size=20)

CT.update_layout(template='plotly_dark')

# menos vendidos
prod1 = vendas[['Produto','Quantidade']].groupby('Produto').sum()
x1=[]
y1=[]
for c in range(0,10):
    x1.append(prod1.idxmin().to_dict()['Quantidade'])
    y1.append(prod1.min().to_dict()['Quantidade'])
    for i in list(prod1.index):
        if prod1.loc[i,'Quantidade']==prod1.min().to_dict()['Quantidade']:
            prod1 = prod1.drop(i)
            break
dic1 = {}
dic1['Produtos']=x1
dic1['Quantidade']=y1
data1 = pd.DataFrame(dic1)
# mais vendidos
prod = vendas[['Produto','Quantidade']].groupby('Produto').sum()
x=[]
y=[]
for c in range(0,10):
    x.append(prod.idxmax().to_dict()['Quantidade'])
    y.append(prod.max().to_dict()['Quantidade'])
    for i in list(prod.index):
        if prod.loc[i,'Quantidade']==prod.max().to_dict()['Quantidade']:
            prod = prod.drop(i)
            break
dic = {}
dic['Produtos']=x
dic['Quantidade']=y
data = pd.DataFrame(dic)
# gráfico
fig = make_subplots(rows=4, cols=2, specs=[[{'rowspan':2}, {"rowspan": 4, 'type':'domain'}],
           [None, None], [{'rowspan':2,'type':'xy'}, None], [None, None]], print_grid=True, subplot_titles=('PRODUTOS MAIS/MENOS VENDIDOS','métodos de pagamento'),
                   vertical_spacing=0.33)
fig.update_layout(template='plotly_dark')
axis1 = list(data['Produtos'].values)
axis2 = list(data['Quantidade'].values)
axis3 = list(data1['Produtos'].values)
axis4 = list(data1['Quantidade'].values)
# pagamentos
holed = pd.DataFrame(vendas['Pagamento'].value_counts())

l = list(holed.index)
v = list(holed['count'].values)
fig.add_trace(go.Bar(x=axis1, y=axis2, marker=dict(color='cyan'), name='MAIS VENDIDOS'), row=1, col=1)
fig.add_trace(go.Bar(x=axis3, y=axis4, marker=dict(color='red'), name='MENOS VENDIDOS'), row=3, col=1)
fig.add_trace(go.Pie(labels=l, values=v, hole=.3, marker=dict(colors=('cyan','royalblue','lightblue','lightcyan'))), row=1, col=2)
fig.update_annotations(font_size=20)
fig.update_layout(template='plotly_dark')

# dia da semana que mais vende / % de vendas por canal
DS = ['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo']
VD = []
for dia in DS:
    VD.append(vendas['Dia da semana'].value_counts()[f'{dia}'])
diacanal = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'xy'}, {'rowspan':2,'colspan':2,'type':'domain'}, None],
                                               [None, None, None]], subplot_titles=('5 produtos com maior faturamento','Vendas por canal',''))
diacanal.update_layout(template='plotly_dark')
diacanal.update_annotations(font_size=20)
nom=[]
fatr=[]
pfat = vendas[['Produto','Valor Final']].groupby('Produto').sum()
for c in range(0,5):
    nom.append(pfat.idxmax()['Valor Final'])
    fatr.append(pfat.max()['Valor Final'])
    for i in list(pfat.index):
        if pfat.loc[i,'Valor Final']==pfat.max()['Valor Final']:
            pfat = pfat.drop(i)
            break
dicp2 = {}
dicp2['Produto']=nom
dicp2['Faturamento']=fatr
datap2 = pd.DataFrame(dicp2)
diacanal.add_trace(go.Bar(x=list(datap2['Produto']), y=list(datap2['Faturamento']), marker=dict(color=('cyan','royalblue','blue','lightcyan','darkcyan'))), row=1, col=1)
diacanal.update_yaxes(title_text='Faturamento', row=1, col=1)

# adicionar canais de venda
canais = ['Loja fisica','Loja fisica','Loja fisica','Loja fisica','Instagram','Instagram','Instagram','Anúncios','Anúncios','Recomendação de amigos']
for i in list(vendas.index):
    vendas.loc[i,'Canal']=random.choice(canais)
c = ['Loja fisica','Instagram','Anúncios','Recomendação de amigos']
v = []
v.append(vendas['Canal'].value_counts()['Loja fisica'])
v.append(vendas['Canal'].value_counts()['Instagram'])
v.append(vendas['Canal'].value_counts()['Anúncios'])
v.append(vendas['Canal'].value_counts()['Recomendação de amigos'])
diacanal.add_trace(go.Pie(labels=c, values=v, marker=dict(colors=('cyan','royalblue','blue','lightcyan'))), row=1, col=2)

# faturamento/lucro ao longo do ano
fla = vendas[['Data','Valor Final','Lucro']].groupby('Data').sum()
fla.rename(columns={'Valor Final':'Faturamento diário'}, inplace=True)
fla.rename(columns={'Lucro':'Lucro diário'}, inplace=True)
lista1 = list(fla.index)
for d in lista1:
    fla.loc[d,'Data']=d
fla['Mês']=fla['Data'].dt.month

line1 = px.line(fla, x='Data', y='Faturamento diário', template='plotly_dark', color_discrete_sequence=['cyan'], title='Faturamento ao longo do ano')
line2 = px.line(fla, x='Data', y='Lucro diário', template='plotly_dark', color_discrete_sequence=['darkcyan'], title='Lucro ao longo do ano')

# quantidade vendida de cada produto por categoria

quant = vendas[['Produto','Quantidade']].groupby('Produto').sum()

ber = []
cal = []
cam = []
cams = []
casa = []
chin = []
cint = []
cuec = []
gor = []
mei = []
moch = []
pol = []
puls = []
rel = []
sap = []
sho = []
sung = []
ter = []
teni = []
for n in list(quant.index):
    quant.loc[n,'Produto']=n
    if 'Bermuda' in n:
        ber.append(n)
    if 'Calça' in n:
        cal.append(n)
    if 'Camisa' in n:
        cam.append(n)
    if 'Camiseta' in n:
        cams.append(n)
    if 'Casaco' in n:
        casa.append(n)
    if 'Chinelo' in n:
        chin.append(n)
    if 'Cinto' in n:
        cint.append(n)
    if 'Cueca' in n:
        cuec.append(n)
    if 'Gorro' in n:
        gor.append(n)
    if 'Meia' in n:
        mei.append(n)
    if 'Mochila' in n:
        moch.append(n)
    if 'Polo' in n:
        pol.append(n)
    if 'Pulseira' in n:
        puls.append(n)
    if 'Relógio' in n:
        rel.append(n)
    if 'Sapato' in n:
        sap.append(n)
    if 'Short' in n:
        sho.append(n)
    if 'Sunga' in n:
        sung.append(n)
    if 'Terno' in n:
        ter.append(n)
    if 'Tênis' in n:
        teni.append(n)
comp3 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Bermudas','Calças','Camisas'))
comp3.update_annotations(font_size=20)
comp3.update_layout(template='plotly_dark')

comp6 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Camisetas','Casacos','Chinelos'))
comp6.update_annotations(font_size=20)
comp6.update_layout(template='plotly_dark')

comp9 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Cintos','Cuecas','Gorros'))
comp9.update_annotations(font_size=20)
comp9.update_layout(template='plotly_dark')

comp12 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Meias','Mochilas','Polos'))
comp12.update_annotations(font_size=20)
comp12.update_layout(template='plotly_dark')

comp15 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Pulseiras','Relógios','Sapatos'))
comp15.update_annotations(font_size=20)
comp15.update_layout(template='plotly_dark')

comp18 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}, {'rowspan':2,'type':'bar'}],
                                             [None, None, None]],
                                           subplot_titles=('Shorts','Sungas','Ternos'))
comp18.update_annotations(font_size=20)
comp18.update_layout(template='plotly_dark')

comp21 = make_subplots(rows=2, cols=3, specs=[[{'rowspan':2, 'colspan':2,'type':'bar'}, None, {'rowspan':2, 'type':'domain'}],
                                             [None, None, None]],
                                           subplot_titles=('Tênis','Quantidade de vendas X Gênero'))
comp21.update_annotations(font_size=20)
comp21.update_layout(template='plotly_dark')

bermuda = quant.query(f"Produto in {ber}")
calça = quant.query(f"Produto in {cal}")
camisa = quant.query(f"Produto in {cam}")
camiseta = quant.query(f"Produto in {cams}")
casaco = quant.query(f"Produto in {casa}")
chinelo = quant.query(f"Produto in {chin}")
cinto = quant.query(f"Produto in {cint}")
cueca = quant.query(f"Produto in {cuec}")
gorro = quant.query(f"Produto in {gor}")
meia = quant.query(f"Produto in {mei}")
mochila = quant.query(f"Produto in {moch}")
polo = quant.query(f"Produto in {pol}")
pulseira = quant.query(f"Produto in {puls}")
relogio = quant.query(f"Produto in {rel}")
sapato = quant.query(f"Produto in {sap}")
short = quant.query(f"Produto in {sho}")
sunga = quant.query(f"Produto in {sung}")
terno = quant.query(f"Produto in {ter}")
tenis = quant.query(f"Produto in {teni}")
comp3.add_trace(go.Bar(x=bermuda['Produto'], y=bermuda['Quantidade'], marker=dict(color='lightcyan'), name='Bermudas'), row=1, col=1)
comp3.add_trace(go.Bar(x=calça['Produto'], y=calça['Quantidade'], marker=dict(color='cyan'), name='Calças'), row=1, col=2)
comp3.add_trace(go.Bar(x=camisa['Produto'], y=camisa['Quantidade'], marker=dict(color='royalblue'), name='Camisas'), row=1, col=3)

comp6.add_trace(go.Bar(x=camiseta['Produto'], y=camiseta['Quantidade'], marker=dict(color='lightcyan'), name='Camisetas'), row=1, col=1)
comp6.add_trace(go.Bar(x=casaco['Produto'], y=casaco['Quantidade'], marker=dict(color='cyan'), name='Casacos'), row=1, col=2)
comp6.add_trace(go.Bar(x=chinelo['Produto'], y=chinelo['Quantidade'], marker=dict(color='royalblue'), name='Chinelos'), row=1, col=3)

comp9.add_trace(go.Bar(x=cinto['Produto'], y=cinto['Quantidade'], marker=dict(color='lightcyan'), name='Cintos'), row=1, col=1)
comp9.add_trace(go.Bar(x=cueca['Produto'], y=cueca['Quantidade'], marker=dict(color='cyan'), name='Cuecas'), row=1, col=2)
comp9.add_trace(go.Bar(x=gorro['Produto'], y=gorro['Quantidade'], marker=dict(color='royalblue'), name='Gorros'), row=1, col=3)

comp12.add_trace(go.Bar(x=meia['Produto'], y=meia['Quantidade'], marker=dict(color='lightcyan'), name='Meias'), row=1, col=1)
comp12.add_trace(go.Bar(x=mochila['Produto'], y=mochila['Quantidade'], marker=dict(color='cyan'), name='Mochilas'), row=1, col=2)
comp12.add_trace(go.Bar(x=polo['Produto'], y=polo['Quantidade'], marker=dict(color='royalblue'), name='Polos'), row=1, col=3)

comp15.add_trace(go.Bar(x=pulseira['Produto'], y=pulseira['Quantidade'], marker=dict(color='lightcyan'), name='Pulseiras'), row=1, col=1)
comp15.add_trace(go.Bar(x=relogio['Produto'], y=relogio['Quantidade'], marker=dict(color='cyan'), name='Relógios'), row=1, col=2)
comp15.add_trace(go.Bar(x=sapato['Produto'], y=sapato['Quantidade'], marker=dict(color='royalblue'), name='Sapatos'), row=1, col=3)

comp18.add_trace(go.Bar(x=short['Produto'], y=short['Quantidade'], marker=dict(color='lightcyan'), name='Shorts'), row=1, col=1)
comp18.add_trace(go.Bar(x=sunga['Produto'], y=sunga['Quantidade'], marker=dict(color='cyan'), name='Sungas'), row=1, col=2)
comp18.add_trace(go.Bar(x=terno['Produto'], y=terno['Quantidade'], marker=dict(color='royalblue'), name='Ternos'), row=1, col=3)
piem = vendas['Sexo'].value_counts()['Mulher']
# pieh = vendas['Sexo'].value_counts()['Homem']
comp21Py = [] 
# comp21Py.append(pieh) NÃO HOUVE COMPRAS 
comp21Py.append(piem)

comp21.add_trace(go.Bar(x=tenis['Produto'], y=tenis['Quantidade'], marker=dict(color='cyan'), name='Tênis'), row=1, col=1)
comp21.add_trace(go.Pie(labels=['Mulher'], values=comp21Py, marker=dict(colors=('red','red'))), row=1, col=3)

# Quantidade de vendas por idade
vxi = px.histogram(vendas, x='Idade', color='Sexo',color_discrete_map={'Mulher':'red','Homem':'cyan'}, template='plotly_dark',title='Quantidade de vendas X idade')

# 10 produtos mais vendidos pro perfil de cliente ideal
perfil = vendas.query('Sexo == "Mulher" and 18<=Idade<=35')
prodperfil = list(perfil['Produto'].value_counts().index)
quantperfil = list(perfil['Produto'].value_counts().values)
eixoxperfil = []
eixoyperfil = []
for c in range(0,10):
    eixoxperfil.append(prodperfil[c])
    eixoyperfil.append(quantperfil[c])
pperfil = px.bar(x=eixoxperfil, y=eixoyperfil, color_discrete_sequence=['yellow'], template='plotly_dark', labels={'x':'Produtos','y':'Quantidade de vendas'},
                title='Produtos mais vendidos para o perfil de cliente ideal (Mulher entre 18 e 35 anos)')

# ticket médio ao longo dos dias
for c in range(1,29):
    fatfev.loc[c,'Quant vendas']=vendas['Dia'].value_counts()[c]
fatfev['Ticket'] = fatfev['Faturamento diário']//fatfev['Quant vendas']
tic = px.line(x=fatfev['Dia'], y=fatfev['Ticket'], template='plotly_dark', labels={'x':'Dia do mês','y':'Ticket médio diário'},
             color_discrete_sequence=['yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow',
                                     'yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow',
                                     'yellow','yellow','yellow','yellow','yellow','yellow','yellow','yellow'], markers=True, title='Ticket médio ao longo do mês')

# Controle de estoque
est = vendas[['Produto','Quantidade']].groupby('Produto').sum()
for c in list(est.index):
    est.loc[c,'Estoque inicial']=est.loc[c,'Quantidade']*(1 + random.randint(50,70)/100)
for p in list(est.index):
    est.loc[p,'Estoque inicial']=math.floor(est.loc[p,'Estoque inicial'])
for p in list(est.index):
    est.loc[p,'Estoque atual']=est.loc[p,'Estoque inicial']-est.loc[p,'Quantidade']
for p in list(est.index):
    est.loc[p,'Produto']=p
est.rename(columns={'Quantidade':'Quantidade vendida'}, inplace=True)
listp1 = []
listp2 = []
for pos,p in enumerate(list(est.index)):
    if pos<=60:
        listp1.append(p)
    else:
        listp2.append(p)

est1 = est.loc[listp1,['Estoque inicial','Quantidade vendida','Estoque atual','Produto']]
est2 = est.loc[listp2,['Estoque inicial','Quantidade vendida','Estoque atual','Produto']]

grafest1 = px.bar(est1, x='Produto', y=['Estoque inicial','Quantidade vendida','Estoque atual'], barmode='group', template='plotly_dark',
                labels={'value':'Valor','variable':'Variáveis'}, color_discrete_sequence=('yellow','darkcyan','purple'),
                 title='Controle de Estoque')
grafest2 = px.bar(est2, x='Produto', y=['Estoque inicial','Quantidade vendida','Estoque atual'], barmode='group', template='plotly_dark',
                labels={'value':'Valor','variable':'Variáveis'}, color_discrete_sequence=('yellow','darkcyan','purple'))

# quantidade de vendas totais e % por categoria
dic2 = {}
axis5 = ['Bermudas','Calças','Camisas','Camisetas','Casacos','Chinelos','Cintos','Cuecas','Gorros','Meias','Mochilas','Polos','Pulseiras',
        'Relógios','Sapatos','Shorts','Sungas','Ternos','Tênis']
axis6 = []
axis6.append(bermuda['Quantidade'].sum())
axis6.append(calça['Quantidade'].sum())
axis6.append(camisa['Quantidade'].sum())
axis6.append(camiseta['Quantidade'].sum())
axis6.append(casaco['Quantidade'].sum())
axis6.append(chinelo['Quantidade'].sum())
axis6.append(cinto['Quantidade'].sum())
axis6.append(cueca['Quantidade'].sum())
axis6.append(gorro['Quantidade'].sum())
axis6.append(meia['Quantidade'].sum())
axis6.append(mochila['Quantidade'].sum())
axis6.append(polo['Quantidade'].sum())
axis6.append(pulseira['Quantidade'].sum())
axis6.append(relogio['Quantidade'].sum())
axis6.append(sapato['Quantidade'].sum())
axis6.append(short['Quantidade'].sum())
axis6.append(sunga['Quantidade'].sum())
axis6.append(terno['Quantidade'].sum())
axis6.append(tenis['Quantidade'].sum())
dic2['Produtos']=[]
dic2['Quantidade vendida']=[]
for pos,n in enumerate(axis5):
    dic2['Produtos'].append(n)
    dic2['Quantidade vendida'].append(axis6[pos])
dic2df = pd.DataFrame(dic2)
prodtotal = dic2df['Quantidade vendida'].sum()
VC = px.pie(dic2df, names='Produtos', values='Quantidade vendida', color='Produtos', template='plotly_dark', hole=0.3, title=f'{prodtotal} produtos vendidos',
           height=500)

# APP
app = dash.Dash(__name__)
server = app.server

# INSIDE
app.layout = html.Div(children=[
    html.H1(children='ANÁLISE DE VENDAS (mês: fevereiro)'),
    dcc.Graph(id = 'G0', figure = fatxdfev),
    dcc.Graph(id = 'G1', figure = lucxdfev),
    dcc.Graph(id = 'G2', figure = tic),
    dcc.Graph(id = 'subplot1', figure = CT),
    dcc.Graph(id = 'subplot2', figure = fig),
    dcc.Graph(id = 'comp3', figure = comp3),
    dcc.Graph(id = 'comp6', figure = comp6),
    dcc.Graph(id = 'comp9', figure = comp9),
    dcc.Graph(id = 'comp12', figure = comp12),
    dcc.Graph(id = 'comp15', figure = comp15),
    dcc.Graph(id = 'comp18', figure = comp18),
    dcc.Graph(id = 'comp21', figure = comp21),
    dcc.Graph(id = 'G3', figure = VC),
    dcc.Graph(id = 'G4', figure = vxi),
    dcc.Graph(id = 'subplot3', figure = diacanal),
    dcc.Graph(id = 'G5', figure = pperfil),
    dcc.Graph(id= 'G6', figure = grafest1),
    dcc.Graph(id = 'G7', figure = grafest2)
])


# callbacks


# RODANDO
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050)) 
    app.run_server(debug=True, host="0.0.0.0", port=port)