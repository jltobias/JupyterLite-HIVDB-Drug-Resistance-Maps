# Maps, globes, scenes, and learning resources

The notebooks implement 2D surveillance maps. The 3D links below are external tools and documentation for further exploration; they are not additional HIVDR datasets or completed repository analyses. Linked images, example models, terrain, imagery, and tiles remain with their providers and are not copied into this project.

| View | Start here | Connection to this project |
|---|---|---|
| **2D Maps** | [Notebook 02 in JupyterLite](https://jltobias.github.io/JupyterLite-HIVDB-Drug-Resistance-Maps/lab/index.html?path=02_global_tdr_choropleth.ipynb), [Plotly choropleth documentation](https://plotly.com/python/choropleth-maps/), [Stanford surveillance map](https://hivdb.stanford.edu/page/surveillance-map/) | Explore country-level evidence; keep coverage and prevalence distinct. |
| **3D Maps** | [deck.gl ColumnLayer](https://deck.gl/docs/api-reference/layers/column-layer), [pydeck documentation](https://deckgl.readthedocs.io/en/latest/) | Learn about extruded geographic displays. Heights require explicit units and denominators; a tall column is not a disease burden estimate by itself. |
| **Globes** | [CesiumJS](https://cesium.com/platform/cesiumjs/), [Plotly map projections](https://plotly.com/python/map-configuration-and-styling/) | Explore globe views and orthographic projections. Country-level values still describe aggregate evidence. |
| **3D Scenes** | [Three.js documentation](https://threejs.org/docs/), [deck.gl ScenegraphLayer](https://deck.gl/docs/api-reference/layers/scenegraph-layer), [Stanford reverse-transcriptase structures](https://hivdb.stanford.edu/pages/3DStructures/rt.html) | Explore scene composition or molecular structure resources; molecular and geographic coordinates describe different spaces. |

## Data and interpretation

- [Rhee et al. 2015 study](https://doi.org/10.1371/journal.pmed.1001810) and [S1 Table](https://doi.org/10.1371/journal.pmed.1001810.s004): the historical baseline used here.
- [Natural Earth](https://www.naturalearthdata.com/) and its [public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/): geographic context, not HIVDR measurements.
- [Stanford HIVDB](https://hivdb.stanford.edu/), [mutation interpretation](https://hivdb.stanford.edu/hivdb/by-mutations/), and [Sierra documentation](https://hivdb.stanford.edu/page/graphiql/): interpretation resources, separate from surveillance denominators.
- [NIH ClinicalInfo life cycle](https://clinicalinfo.hiv.gov/en/glossary/life-cycle) and [WHO HIV drug resistance brief report 2024](https://www.who.int/publications/i/item/9789240086319): background for Notebook 00.
- [JupyterLite documentation](https://jupyterlite.readthedocs.io/en/stable/) and [Jupyter Book 1 documentation](https://jupyterbook.org/v1/): the browser runtime and the pinned book builder used here.

External libraries have their own software licenses; their example datasets and hosted services may have separate terms. No provider's logo, screenshot, video, 3D model, or proprietary basemap is included in the splash image. The project's source and asset attributions are recorded in the [repository README](https://github.com/jltobias/JupyterLite-HIVDB-Drug-Resistance-Maps#citation-and-attribution).
