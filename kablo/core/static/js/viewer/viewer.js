initMap = function (host) {

    /* Use swiss projection */

    const swissProjection = new ol.proj.Projection({
        code: 'EPSG:2056',
        extent: [485869.5728, 76443.1884, 837076.5648, 299941.7864],
        units: 'm'
    });

    ol.proj.addProjection(swissProjection);

    let mapProjection = swissProjection;
    mapProjection.setExtent([485869.5728, 76443.1884, 837076.5648, 299941.7864]);

    const track_url = `${host}/oapif/collections/network.track/items?format=json`;
    const tube_url = `${host}/oapif/collections/network.tube/items?format=json`;
    const cable_url = `${host}/oapif/collections/network.cable/items?format=json`;

    /* setup wmts base layer from swisstopo capabilities */

    const base_layer = new ol.layer.Tile({
    });

    const parser = new ol.format.WMTSCapabilities();

    async function setUpBaseLayer() {
        const response = await fetch("https://wmts.geo.admin.ch/EPSG/2056/1.0.0/WMTSCapabilities.xml");
        const capabilities = await response.text();
        const result = parser.read(capabilities);
        const options = ol.source.WMTS.optionsFromCapabilities(result, {
            layer: 'ch.swisstopo.swissimage',
            matrixSet: 'EPSG:2056',
            projection: "EPSG:2056",
        });
        base_layer.setSource(
            new ol.source.WMTS(/** @type {!olx.source.WMTSOptions} */ (options))
        );
    }

    setUpBaseLayer();

    /* setup map */
    let map = new ol.Map({
        view: new ol.View({
            projection: 'EPSG:2056',
            center: [2539085, 1181785],
            zoom: 9
        }),
        layers: [
            base_layer,
        ],
        target: 'map'
    });

    const selectStyle = new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(255, 20, 0, 0.8)',
            width: 4,
          }),
    });

    /* basic get feature example */
    let selected = null;
    let detailsDiv = document.getElementById("detailsDiv");
    let detailsLink = document.getElementById("detailsLink");
    let detailsCable = document.getElementById("detailsCable");
    detailsDiv.style.display = 'none';
    detailsCable.style.display = 'none';
    map.on('click', function (e) {
        if (selected !== null) {
          selected.setStyle(undefined);
          selected = null;
        }

        map.forEachFeatureAtPixel(e.pixel, function (f) {
          hit = true;
          selected = f;
          f.setStyle(selectStyle);
          return true;
        },
        {
            hitToleance: 20,
            layerFilter: function(layer){
                if (layer.className_ == 'tubes') {
                    return true;
                } else {
                    return false;
                }
            }
        });


        if (selected) {
        // TODO: set model name from OL layer
            detailsLink.setAttribute("href", `${host}/admin/network/tube/${selected.id_}`);
            detailsDiv.style.display = 'block';
            detailsCable.innerHTML = '';
            cables_list = '<hr><p>Câbles</p><ul>';
            if (selected.values_.cables && selected.values_.cables.length > 0) {
                selected.values_.cables.forEach(async (cable) => {
                    cables_list += `<li><a href="${host}/admin/network/cable/${cable}" target="_blank">${cable}</a></li>`;
                });
                cables_list += '</ul>'
                detailsCable.innerHTML = cables_list;
                detailsCable.style.display = 'block'
            } else {
                detailsCable.style.display = '';
            }

        } else {
            detailsDiv.style.display = 'none';
        }
      });


    /* load tracks, tubes and cables from django oapif, set basic ol styling*/

    (async () => {
        const tracks = await fetch(track_url, {
        headers: {
            'Accept': 'application/json'
        }
        }).then(response => response.json());

        const tubes = await fetch(tube_url, {
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => response.json());

        const cables = await fetch(cable_url, {
            headers: {
                'Accept': 'application/json'
            }
        }).then(response => response.json());

        var tracks_layer = new ol.layer.Vector({
            source: new ol.source.Vector({
                features: new ol.format.GeoJSON().readFeatures(tracks),
            }),
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'black',
                    width: 2,
                }),
            }),
            className: 'tracks',
        })

        map.addLayer(tracks_layer);

        map.addLayer(new ol.layer.Vector({
            source: new ol.source.Vector({
                features: new ol.format.GeoJSON().readFeatures(tubes),
            }),
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: '#e246da',
                    width: 1,
                }),
            }),
            className: 'tubes',
        }));

        map.addLayer(new ol.layer.Vector({
            source: new ol.source.Vector({
                features: new ol.format.GeoJSON().readFeatures(cables),
            }),
            style: new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: 'blue',
                    width: 1,
                }),
            }),
            className: 'cables',
        }));

        /* Center map on tracks */
        map.getView().fit(tracks_layer.getSource().getExtent() , map.getSize());


    })();
}
