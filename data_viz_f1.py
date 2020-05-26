# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import doctest
import matplotlib.pyplot as plt

!apt-get -qq install python-cartopy python3-cartopy
!pip uninstall -y shapely;    # cartopy and shapely aren't friends (early 2020)
!pip install shapely --no-binary shapely;

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

vencedores = pd.read_csv("https://github.com/godoy42/cst_cd_3p_dv/raw/master/resultados_f1.csv", encoding="UTF8", index_col=0)

primeiros = vencedores[vencedores["position"] == 1]
podium = vencedores[vencedores["position"] < 4]

from pathlib import Path
picPath = "./pics"
Path(picPath).mkdir(exist_ok=True)

grupo = "nome_piloto"
topQuantos = 10
my_dpi = 96

maioresVencedores = podium.groupby(by=grupo).count()[["raceId"]].sort_values(by="raceId", ascending=False).reset_index()
topMaiores = maioresVencedores.iloc[:topQuantos]

fig = plt.figure(figsize=(1280/my_dpi, 720/my_dpi), dpi=my_dpi)
plt.bar(topMaiores["nome_piloto"], topMaiores["raceId"])
#plt.xticks(x, maioresVencedores["nome_piloto"])
plt.xlabel('Piloto')
plt.ylabel('Podiums')
plt.xticks(rotation=90)
plt.title('Quantidade de podiums conquistados (top {tq})'.format(tq=topQuantos))
plt.savefig("{pp}/1.jpg".format(pp=picPath), dpi=my_dpi, bbox_inches='tight', pad_inches=.2)
plt.show()

soOsMaiores = maioresVencedores[grupo].values[:topQuantos]
primeiroAno = sorted(podium[podium[grupo].apply(lambda v: v in soOsMaiores)].groupby(by="driverId")["year"].min())[0]

podiums = podium.groupby(by=["year", grupo]).count()[["raceId"]].reset_index()
podiums = podiums.sort_values(by=["year", "raceId", grupo],  ascending=[True, False, True])

anos = podiums["year"].unique()
dfAnos = pd.DataFrame(anos, anos, columns=["ano"])
dfAnos = dfAnos[dfAnos["ano"] >= primeiroAno]
anos = dfAnos["ano"].unique()

fig = plt.figure(figsize=(1280/my_dpi, 720/my_dpi), dpi=my_dpi)
linestyles = ['-', '--', '-.', ':']

for iCnt,valor in enumerate(soOsMaiores):
  pdEq = podiums[podiums[grupo] == valor].join(dfAnos, on="year", how="right").sort_values(by="ano", ascending=True)
  y1 = pdEq[["raceId"]].values.squeeze()
  estilo = linestyles[int(len(linestyles) * ((iCnt) / topQuantos))]
  largura = 10 - 8 * iCnt / len(soOsMaiores)

  plt. plot(anos, y1, label = valor, linestyle=estilo, linewidth=largura, alpha=0.8)

plt.xlabel('Ano')
plt.ylabel('Podiums')
plt.title('Quantidade de podiums conquistados (top {tq}), por ano'.format(tq=topQuantos))
plt.legend(loc=3,bbox_to_anchor=(1,0))
plt.grid(b=True, which="both", axis="y")

plt.savefig("{pp}/2.jpg".format(pp=picPath), dpi=my_dpi, bbox_inches='tight', pad_inches=.2)
plt.show()

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Build a dataframe with your connections
topPodium = podium[podium["nome_piloto"].apply(lambda x: x in soOsMaiores)]
pilotoPais = topPodium[["nome_piloto", "pais_piloto"]].drop_duplicates().rename(columns={"nome_piloto": "from", "pais_piloto": "to"})
equipePais = topPodium[["nome_equipe", "pais_equipe"]].drop_duplicates().rename(columns={"nome_equipe": "from", "pais_equipe": "to"})
pilotoEquipe = topPodium[["nome_piloto", "nome_equipe"]].drop_duplicates().rename(columns={"nome_piloto": "from", "nome_equipe": "to"})

dfTudo = pd.concat([pilotoPais, equipePais, pilotoEquipe], axis=0).reset_index()
 
# Constroi um grafo a partir do dataframe
G=nx.from_pandas_edgelist(dfTudo, 'from', 'to', edge_attr=True)
cores = []
formas = []
for node in G:
    if node in pilotoPais["from"].values:
        cores.append("blue")
        formas.append("s")
    elif node in equipePais["from"].values:
        cores.append("green")
        formas.append("s")
    else: 
      cores.append("red")
      formas.append("s")

# Desenha o grafo:
fig = plt.figure(figsize=(1280/my_dpi, 720/my_dpi), dpi=my_dpi)
nx.draw(G, with_labels=True, node_size=42, node_color=cores, node_shape="o", alpha=0.5, linewidths=40)
plt.title('Relação de Pilotos x Equipes x Países'.format(tq=topQuantos))

class HandlerEllipse(HandlerPatch):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        center = 0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent
        p = mpatches.Ellipse(xy=center, width=height + xdescent, height=height + xdescent)
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]

colors = ["r", "g", "b"]
texts = ["País", "Equipe", "Piloto"]

c = [ mpatches.Circle((5, 5), radius = 5, facecolor="none", edgecolor=colors[i] ) for i in range(len(texts))]
plt.legend(c, texts, loc=3, bbox_to_anchor=(1,0), handler_map={mpatches.Circle: HandlerEllipse()})

plt.savefig("{pp}/3.jpg".format(pp=picPath), dpi=my_dpi, bbox_inches='tight', pad_inches=.2)
plt.show()

#por fim, plot nos autódromos com quantidade de podiums somente destes pilotos
dadosMapa = topPodium.groupby(by=["nome_circuito", "lng", "lat"]).count()[["raceId"]].sort_values(by="raceId", ascending=False).reset_index()
lon, lat, tam = dadosMapa["lng"].values, dadosMapa["lat"].values, dadosMapa["raceId"].values

fig = plt.figure(figsize=(1280/my_dpi, 720/my_dpi), dpi=my_dpi)

tipoProjecao = ccrs.PlateCarree()

ax = plt.subplot(1, 1, 1, projection=tipoProjecao)
ax.add_feature(cartopy.feature.OCEAN)
ax.add_feature(cartopy.feature.LAND)
ax.add_feature(cartopy.feature.COASTLINE, linestyles="-")
ax.add_feature(cartopy.feature.BORDERS, linestyle=':')

ax.scatter(lon, lat, transform=tipoProjecao, zorder=2, color='red', s=tam * 4, marker="o", alpha=.8)

plt.title('Autódromos x podiums dos pilotos selecionados'.format(tq=topQuantos))

plt.savefig("{pp}/4.jpg".format(pp=picPath), dpi=my_dpi, bbox_inches='tight', pad_inches=.2)
plt.show()
