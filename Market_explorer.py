# coding: utf-8

# # Prove per il plotting scatter con selettori

# Importa altair pandas streamlit, pandas_datareader

# In[410]:


import altair as alt
import pandas as pd
import streamlit as st
import pandas_datareader as pdr
import numpy as np
import yahooquery as ya

stock = ya.Ticker('VTI')


# In[411]:


from PIL import Image
image = Image.open('Market.png')
st.sidebar.image(image, use_column_width=True)
image2 = Image.open('Striscia.png')
st.image(image2, use_column_width=True)


# In[412]:


st.title("Market Explorer")
pagina = st.sidebar.selectbox("""Menu""", ['Mappa della tendenza', 'Forze relative','Analisi asset', 'Validazione modello'])

# pagina = 'Analisi asset'

# In[414]:


#Stabilisco una data per generare l'aggiornamento (una volta ogni giorno)
oggi = pdr.get_data_yahoo('AAPL', start="2020-8-1")['Close']
oggi = pd.DataFrame(oggi)
oggi = oggi.tail(1).index


tickers = ['VCR','VHT','VGT','VNQ', 'VDC', 'VDE','VIS', 'VOX', 'VPU', 'VFH' ,'VT','VTI','VGK','VWO','AAXJ', 'MCHI', 'INDA','EWZ', 'EZA', 'GLD', 'USO']
tickers_name = ['Consumer disc.', 'Healthcare', 'Technology', 'Reits', 'Consumer staples', 'Energy', 'Industrials', 'Communications', 'Utilities', 'Financials','Global Market', 'US Market', 'Europe', 'Emerging Markets', 'Asia ex Jap.', 'China', 'India', 'Brazil', 'South Africa', 'Oro', 'Petrolio']
tickers_type = ['Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity', 'Sector Equity','Global Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Geo Equity', 'Commodities', 'Commodities']
type_unique = []
for i in tickers_type:
    tipo = i
    if tipo in type_unique:
        type_unique = type_unique
    else:
        type_unique.append(tipo)

url_dati = 'http://www.sphereresearch.net/Notebooks/dati_fondi.xlsx'

def importa_dati():
    data = pd.read_excel(url_dati)
    data=data.set_index('Date',1)
    return data


# In[415]:


data = importa_dati()
data = data.resample('M').last()
data = pd.DataFrame(data.values, columns = tickers_name, index= data.index)


# # Pagina - mappa della tendenza

# Creo una lista di date in stringa dal maggiore al minore

# In[457]:


if pagina == "Mappa della tendenza":

    lista_date=[]
    for i in range (len(data)):
        ii = len(data)-i-1
        da = str(data.index[ii].date())
        lista_date.append(da)

    #Creo i selettori

    tipologia= st.sidebar.multiselect("Seleziona le tipologie di asset da includere", type_unique, default=type_unique)
    data_scelta = st.sidebar.selectbox("Data su cui effettuare l'analisi", lista_date)


    # Creo le features

    data_1 = round(data/data.shift(1)-1,2)
    data_3 = round(data/data.shift(3)-1,2)
    data_6 = round(data/data.shift(6)-1,2)
    data_vola = round(data_1.rolling(10).std(),2)

    data_1 = data_1.sort_index(ascending=False)
    data_3 = data_3.sort_index(ascending=False)
    data_6 = data_6.sort_index(ascending=False)
    data_vola = data_vola.sort_index(ascending=False)

    data_1['index'] = lista_date
    data_3['index'] = lista_date
    data_6['index'] = lista_date
    data_vola['index'] = lista_date

    data_1 = data_1.set_index('index',drop=True)
    data_3 = data_3.set_index('index',drop=True)
    data_6 = data_6.set_index('index',drop=True)
    data_vola = data_vola.set_index('index',drop=True)

    data_1 = data_1.transpose()
    data_3 = data_3.transpose()
    data_6 = data_6.transpose()
    data_vola = data_vola.transpose()

    #creo il df per la scelta

    df_indicatori = pd.DataFrame(index = data.columns)

    df_indicatori['Tendenza 3 mesi'] = data_3[data_scelta]
    df_indicatori['Tendenza 6 mesi'] = data_6[data_scelta]
    df_indicatori['Volatility'] = data_vola[data_scelta]
    df_indicatori['Mercato']=df_indicatori.index
    df_indicatori[' ']=""
    df_indicatori['Tipologia']=tickers_type
    df_indicatori[' - ']=0
    
    #Mantengo solo le asset del tipo desiderato

    presente = []
    for i in df_indicatori.Tipologia:
        if i in tipologia:
            selezionato = 1
        else:
            selezionato = 0
        presente.append(selezionato)
    df_indicatori['Selected'] = presente
    df_indicatori = df_indicatori.loc[df_indicatori.Selected == 1]

    # Coloro diversamente i quattro gruppi
    gruppo = []
    for i in df_indicatori.index:

        if df_indicatori['Tendenza 3 mesi'][i] >=0 and df_indicatori['Tendenza 6 mesi'][i] >=0:
            gruppo_n = "Gruppo 1"
        if df_indicatori['Tendenza 3 mesi'][i] < 0 and  df_indicatori['Tendenza 6 mesi'][i] >=0:
            gruppo_n = "Gruppo 2"
        if df_indicatori['Tendenza 3 mesi'][i] < 0 and  df_indicatori['Tendenza 6 mesi'][i] < 0:
            gruppo_n = "Gruppo 3"
        if df_indicatori['Tendenza 3 mesi'][i] >= 0 and  df_indicatori['Tendenza 6 mesi'][i] < 0:
            gruppo_n = "Gruppo 4"
        gruppo.append(gruppo_n)
    df_indicatori['Gruppo'] = gruppo

    #selettore per le etichette si/no
    st.write("""## Mappa della tendenza""")
    etichette = st.checkbox("Visualizza le etichette")

    # Creo il grafico scatter

    if etichette == True:
        etichetta = ('Mercato')
        
    else:
        etichetta = (' ')
    
    # Creo il selettore per i colori delle bolle
#     colorazione_scelta = st.sidebar.selectbox("Scegli come colorare il grafico", ['Gruppi tendenza', 'Macro asset'])
#     if colorazione_scelta == "Gruppi tendenza":
#         colore = ('Gruppo')
#     if colorazione_scelta == "Macro asset":
    colore = ('Tipologia')
        
    dimensione = st.sidebar.selectbox("Scegli le dimensioni dei punti", ['Pari dimensioni', 'Volatilità'])
    df_indicatori['dimensioni'] = 100
    
    if dimensione == "Volatilità":
        dim = ('Volatility')
    else:
        dim = ('dimensioni')
        
    fig1 = alt.Chart(df_indicatori).mark_circle(color = "red").encode(x='Tendenza 6 mesi', y='Tendenza 3 mesi',size=dim,color=colore,tooltip=['Mercato', 'Tendenza 3 mesi', 'Tendenza 6 mesi', 'Volatility']).properties(height=500).interactive()
    fig2 = alt.Chart(df_indicatori).mark_text().encode(x='Tendenza 6 mesi', y='Tendenza 3 mesi', text=etichetta,tooltip=['Mercato', 'Tendenza 3 mesi', 'Tendenza 6 mesi', 'Volatility']).properties(height=500).interactive()
    rule = alt.Chart(df_indicatori).mark_rule(color = 'red', style='dotted').encode( y=' - ',size=alt.value(0.3))
    rule2 = alt.Chart(df_indicatori).mark_rule(color = 'red').encode( x=' - ',size=alt.value(0.3))
    
    fig3 = fig1+fig2+rule+rule2

    #Mostro il grafico in streamlit

    
    st.altair_chart(fig3, use_container_width=True)
    df_indicatori


# # Pagina validazione modelli

# In[ ]:




if pagina == "Validazione modello":
    
    st.write("""## Validazione del modello""")
    
    asset = st.selectbox("Scegli l'asset da visualizzare", list(data.columns))

    data_6 = data/data.shift(6)-1
    roc6 = data_6
    roc6 = pd.DataFrame(roc6[asset].values, index = roc6.index, columns = ['roc6'])

    data_6_old = data.shift(1)/data.shift(1+6)-1
    roc6old = data_6_old
    roc6old = pd.DataFrame(roc6old[asset].values, index = roc6.index, columns = ['roc6 precedente'])

    roc6 = roc6.join(roc6old)
    list_date=[]
    for i in roc6.index:
        a = str(i.date())
        list_date.append(a)
    roc6['Data'] = list_date

    data_3 = data/data.shift(3)-1
    roc3 = data_3
    roc3 = pd.DataFrame(roc3[asset].values, index = roc6.index, columns = ['roc3'])

    data_3_old = data.shift(1)/data.shift(1+3)-1
    roc3old = data_3_old
    roc3old = pd.DataFrame(roc3old[asset].values, index = roc6.index, columns = ['roc3 precedente'])

    roc3 = roc3.join(roc3old)

    list_date=[]

    for i in roc3.index:
        a = str(i.date())
        list_date.append(a)
    roc3['Data'] = list_date
    
    roc3['Errore'] = abs(roc3['roc3 precedente'] / roc3['roc3'])
    roc6['Errore'] = abs(roc6['roc6 precedente'] / roc6['roc6'])

    # disegno gli scatter
    fig1 = alt.Chart(roc3).mark_circle(size = 200).encode(x='roc3', y='roc3 precedente', color='Errore', tooltip=['Data', 'roc3', 'roc3 precedente']).properties(height=500).interactive()

    fig2 = alt.Chart(roc6).mark_circle(size=200).encode(x='roc6', y='roc6 precedente', color='Errore', tooltip=['Data', 'roc6', 'roc6 precedente']).properties(height=500).interactive()

    # Stampo in altair

    st.write("""## Regressione tendenza a 3 mesi asset selezionato""")

    st.altair_chart(fig1, use_container_width=True)

    st.write("""## Regressione tendenza a 6 mesi asset selezionato""")
    st.altair_chart(fig2, use_container_width=True)


# In[429]:


if pagina == "Forze relative":

    st.write("""## Analisi della forza relativa fra due asset""")



    prima = st.sidebar.selectbox("Seleziona la prima asset per il confronto", data.columns)
    seconda = st.sidebar.selectbox("Seleziona la seconda asset per il confronto", data.columns)
    smooth = st.sidebar.number_input("Smoothing della tendenza", min_value = 1, max_value = 12, value = 5)

    st.write("""** Confronto fra """, prima, """ e """, seconda, """** """)

    data_ribasato = data.sort_index(ascending=True)

    data_ribasato = data_ribasato/data_ribasato.shift(1)
    data_ribasato = data_ribasato.cumprod()

    data_primo = pd.DataFrame(data[prima])
    data_secondo = pd.DataFrame(data[seconda])

    data_plot = pd.DataFrame(data_primo.values/data_secondo.values, columns=['Ratio'], index=data_primo.index)
    data_plot['Mean'] = data_plot.Ratio.rolling(smooth).mean()
    data_plot = data_plot/data_plot.shift(1)
    data_plot = data_plot.fillna(1)
    data_plot = data_plot.cumprod()
    data_plot = data_plot -1
    data_plot['Data'] = data_plot.index



    fig2 = alt.Chart(data_plot).mark_line().encode(x='Data', y='Mean', tooltip=['Data']).properties(height=500).interactive()
    # band = alt.Chart(data_plot).mark_errorband(band = True,extent='ci', color = 'red', opacity=100).encode(x='Data',y=('Ratio')).properties(height=500).interactive()
    #fig2 = fig2 + band
    st.altair_chart(fig2, use_container_width=True)
    #st.altair_chart(band, use_container_width=True)
    #data_plot
    
if pagina == "Analisi asset":

    #Seleziona l'asset

    selezionatore = pd.DataFrame(index=data.columns)
    selezionatore['ticker'] = tickers
    selezionatore['Type'] = tickers_type
    selezionatore['Asset'] = selezionatore.index

    tipo = st.sidebar.selectbox("Seleziona il tipo di asset", type_unique)
    selezionatore = selezionatore.loc[selezionatore.Type == tipo]


    asset = st.sidebar.selectbox("Seleziona l'asset desiderata", selezionatore.index)
    selezionatore = selezionatore.loc[selezionatore.Asset == asset]
    asset_selected = selezionatore.ticker.values[0]

    #Estrai il titolo scelto

    import yahooquery as ya
    stock = ya.Ticker(asset_selected)
    stock2 = ya.Ticker('VT')

    partecipazioni = pd.DataFrame(stock.fund_top_holdings)
    partecipazioni = partecipazioni.set_index('holdingName',1)
    partecipazioni = partecipazioni.drop('symbol',1)

    ratio_di_mercato_eq = pd.DataFrame(list((stock.fund_equity_holdings[asset_selected]).values()),index=list((stock.fund_equity_holdings[asset_selected]).keys()), columns = [asset])
    ratio_di_mercato_eq['Global market'] = (list((stock2.fund_equity_holdings['VT']).values()))
    ratio_di_mercato_bo = pd.DataFrame(list((stock.fund_bond_holdings[asset_selected]).values()),index=list((stock.fund_bond_holdings[asset_selected]).keys()), columns = [asset])


    interm = stock.technical_insights[asset_selected]['instrumentInfo']['technicalEvents']['intermediateTermOutlook']['scoreDescription']
    longterm = stock.technical_insights[asset_selected]['instrumentInfo']['technicalEvents']['longTermOutlook']['scoreDescription']
    shortterm = stock.technical_insights[asset_selected]['instrumentInfo']['technicalEvents']['shortTermOutlook']['scoreDescription']
    lista = [interm, longterm, shortterm]
    outlook = pd.DataFrame(lista, index = ['Intermediate', 'Long', 'Short'], columns=['Outlook'])

    # partecipazioni
    st.write("""## Asset selezionata: """, asset)
    st.write("""## Proxy fund:""", asset_selected)
    st.write("""## """)
    st.write("""## Principali partecipazioni""")
    partecipazioni
    st.bar_chart(data=partecipazioni, width=0, height=0, use_container_width=True)
    
    # Andamento
    st.write("""## Andamento di marcato: """)
    asset_x = pd.DataFrame(data[asset])
    asset_x['index']=asset_x.index
    asset_x = asset_x.set_index('index', drop=True)
    asset_x = asset_x.dropna()
    st.line_chart(asset_x)
    
    #Ratios
    if len(ratio_di_mercato_bo)>0:
        st.write("""## Ratios di mercato: bonds""")
        ratio_di_mercato_bo = ratio_di_mercato_bo.transpose()
        ratio_di_mercato_bo
        st.bar_chart(data=ratio_di_mercato_bo, width=0, height=0, use_container_width=True)
    
    if len(ratio_di_mercato_eq)>0:
        st.write("""## Ratios di mercato: equity""")
        ratio_di_mercato_eq = ratio_di_mercato_eq.transpose()
        ratio_di_mercato_eq
        st.bar_chart(data=ratio_di_mercato_eq, width=0, height=0, use_container_width=True)
    
    #Outlook
    st.write("""## Outlook analisti""")
    outlook
