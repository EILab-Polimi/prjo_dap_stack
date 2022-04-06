# TODO

1. Passare un parametro nelle route per definire se visualizzare il grafico nella pagina
`return fig.to_html(include_plotlyjs=True, full_html=True)` oppure per visualizzarlo in interfaccia drupal per cui plotly é già caricato e non c'è bisogno del full html `return fig.to_html(include_plotlyjs=False, full_html=False)`

## Errori di installazione development
Se non si riesce ad installare psycopg2 nel virtual environment (Pycharm) bisogna installare a livello di sitema
```
ilpise@neo:~/Projecto/prjo_dap$ sudo apt install python3-dev libpq-dev
```


## Attivazione della applicazione

Spostiamoci nella directory `DAP-fastapi` e
da console attiviamo l'applicazione FastAPI con il comando
```
/prjo_dap/DAP-fastapi$ uvicorn --port 5000 --host 0.0.0.0 app.main:app --reload
```

Spiegazione:

`--host 0.0.0.0` serve per esporre uvcorn su tutte le interfacce di rete, senza questo parametro uvicorn risponde solo da localhost


Possiamo raggiungere Swagger alla url `http://localhost:5000/docs`

## esempio di chiamate

http://localhost:5000/indicators/plot_def_drw_cycloM?scenF=rcp8.5&expF=s