function map_init(map, options) {

    function onEachFeature(feature, layer) {
      if (feature.properties && feature.properties.popupContent) {
        layer.bindPopup(feature.properties.popupContent.content, {minWidth: 256});
      }
    }

    const base_map = L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 19,
      }).addTo(map);

    const marker_layer = L.layerGroup().addTo(map);

    function getCollections() {
      // add objects to layers
      collection = JSON.parse(document.getElementById("marker_data").textContent);
      for (marker of collection.features) {
        L.geoJson(marker, {onEachFeature: onEachFeature}).addTo(marker_layer);
      }
      // fit bounds
      map.fitBounds(L.geoJson(collection).getBounds(), {padding: [30,30]});
    }

    getCollections()

}
